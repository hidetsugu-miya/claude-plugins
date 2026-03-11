#!/usr/bin/env python3
"""
Atlassian MCP CLI

mcp-remote プロキシ経由で Atlassian Rovo MCP サーバーに接続し、
Jira・Confluenceツールを実行するCLI。

OAuth 2.1認証は mcp-remote が自動で処理する（初回はブラウザが開く）。

Usage:
    python atlassian_cli.py login
    python atlassian_cli.py tools
    python atlassian_cli.py call <tool_name> --arg key=value
"""

import argparse
import json
import os
import select
import subprocess
import sys
import time


MCP_SERVER_URL = "https://mcp.atlassian.com/v1/mcp"


def _run_mcp(requests, timeout=120, show_stderr=False):
    """
    mcp-remote経由でMCPリクエストを実行（Popenベース）

    mcp-remoteはstdinが閉じると即シャットダウンするため、
    Popenでstdinを開いたままレスポンスを読み取る。

    Args:
        requests: 送信するJSON-RPCリクエストのリスト [{"method": ..., "id": ...}, ...]
        timeout: タイムアウト秒数
        show_stderr: stderrをターミナルに直接表示するか

    Returns:
        (responses_dict, error_message)
        responses_dict: {request_id: response_data} のマッピング
    """
    try:
        proc = subprocess.Popen(
            ["npx", "-y", "mcp-remote", MCP_SERVER_URL],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None if show_stderr else subprocess.DEVNULL,
            text=True,
        )
    except FileNotFoundError:
        return None, "npx not found. Please install Node.js (v18+)"

    def _read_response(deadline):
        """stdoutから1つのJSON-RPCレスポンスを読む"""
        while time.time() < deadline:
            ready, _, _ = select.select([proc.stdout], [], [], 1.0)
            if ready:
                line = proc.stdout.readline()
                if not line:
                    return None
                line = line.strip()
                if line:
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            if proc.poll() is not None:
                return None
        return None

    try:
        responses = {}
        deadline = time.time() + timeout

        # リクエストを1つずつ送信し、レスポンスを待ってから次を送る
        for req in requests:
            proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()

            if "id" in req:
                resp = _read_response(deadline)
                if resp and "id" in resp:
                    responses[resp["id"]] = resp

        return responses, None

    except Exception as e:
        return None, str(e)
    finally:
        proc.stdin.close()
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def extract_text(content):
    """MCPレスポンスのcontentリストからテキストを抽出"""
    if not isinstance(content, list):
        return json.dumps(content, ensure_ascii=False, indent=2)
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(item["text"])
        elif isinstance(item, str):
            parts.append(item)
    return "\n".join(parts) if parts else json.dumps(content, ensure_ascii=False, indent=2)


def parse_arg_value(value_str):
    """引数値を適切な型に変換"""
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False
    try:
        return int(value_str)
    except ValueError:
        pass
    try:
        return float(value_str)
    except ValueError:
        pass
    try:
        return json.loads(value_str)
    except (json.JSONDecodeError, ValueError):
        pass
    return value_str


def _init_request():
    """initializeリクエストを生成"""
    return {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "atlassian-mcp-cli", "version": "1.0.0"}
        },
        "id": 1
    }


def cmd_login(args):
    """OAuth 2.1認証を実行（mcp-remoteが自動でブラウザを開く）"""
    print("Atlassian MCPサーバーに接続中...")
    print("初回はブラウザが開きます。Atlassianアカウントで認証してください。\n")

    responses, error = _run_mcp([_init_request()], timeout=180, show_stderr=True)

    if responses is None:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    resp = responses.get(1)
    if resp and "result" in resp:
        server_info = resp["result"].get("serverInfo", {})
        print("\nLogin successful!")
        print(f"  Server: {server_info.get('name', 'N/A')}")
        print(f"  Version: {server_info.get('version', 'N/A')}")
    elif resp and "error" in resp:
        print(f"\nError: {resp['error'].get('message', resp['error'])}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nError: No response from MCP server (timeout or auth failed)", file=sys.stderr)
        sys.exit(1)


def cmd_tools(args):
    """利用可能なAtlassian MCPツール一覧を表示"""
    requests = [
        _init_request(),
        {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2},
    ]
    responses, error = _run_mcp(requests)

    if responses is None:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    resp = responses.get(2)
    if not resp:
        print("Error: No tools/list response", file=sys.stderr)
        sys.exit(1)

    if "error" in resp:
        print(f"Error: {resp['error']}", file=sys.stderr)
        sys.exit(1)

    tools = resp.get("result", {}).get("tools", [])
    for tool in tools:
        name = tool.get("name", "?")
        desc = tool.get("description", "")
        print(f"  {name}")
        if desc:
            first_line = desc.strip().split("\n")[0]
            print(f"    {first_line}")
        schema = tool.get("inputSchema", {})
        props = schema.get("properties", {})
        required = schema.get("required", [])
        if props:
            for pname, pinfo in props.items():
                req_mark = "*" if pname in required else " "
                ptype = pinfo.get("type", "")
                pdesc = pinfo.get("description", "")
                print(f"    {req_mark} {pname} ({ptype}): {pdesc}")
        print()


def cmd_call(args):
    """Atlassian MCPツールを実行"""
    arguments = {}
    if args.arg:
        for item in args.arg:
            if "=" not in item:
                print(f"Error: Invalid argument format: {item} (expected key=value)", file=sys.stderr)
                sys.exit(1)
            key, value = item.split("=", 1)
            arguments[key] = parse_arg_value(value)

    requests = [
        _init_request(),
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": args.tool_name, "arguments": arguments},
            "id": 2,
        },
    ]
    responses, error = _run_mcp(requests)

    if responses is None:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    resp = responses.get(2)
    if not resp:
        print("Error: No tool response", file=sys.stderr)
        sys.exit(1)

    if "error" in resp:
        err = resp["error"]
        print(f"Error: {err.get('message', err)}", file=sys.stderr)
        sys.exit(1)

    content = resp.get("result", {}).get("content", [])
    print(extract_text(content))


def main():
    parser = argparse.ArgumentParser(
        description="Atlassian MCP CLI - Jira・Confluence操作（mcp-remote経由）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # ログイン（初回はブラウザが開く）
  %(prog)s login

  # ツール一覧
  %(prog)s tools

  # Jiraイシュー検索
  %(prog)s call search_jira_issues --arg query="project = PROJ AND status = Open"

  # Confluenceページ検索
  %(prog)s call search_confluence --arg query="meeting notes"
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # login
    subparsers.add_parser("login", help="OAuth 2.1認証を実行")

    # tools
    subparsers.add_parser("tools", help="利用可能なAtlassian MCPツール一覧")

    # call
    p_call = subparsers.add_parser("call", help="Atlassian MCPツールを実行")
    p_call.add_argument("tool_name", help="ツール名")
    p_call.add_argument("--arg", action="append", help="ツール引数 (key=value形式、複数指定可)")

    args = parser.parse_args()

    commands = {
        "login": cmd_login,
        "tools": cmd_tools,
        "call": cmd_call,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
