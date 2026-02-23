#!/usr/bin/env python3
"""
Figma MCP CLI

Figma MCPクライアントのCLIエントリーポイント。
OAuth認証、認証管理、Figmaツール実行を行う。

Usage:
    python figma_cli.py login
    python figma_cli.py logout
    python figma_cli.py status
    python figma_cli.py tools
    python figma_cli.py call <tool_name> --arg key=value
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from token_store import TokenStore, TokenStoreError
from oauth import login, OAuthError
from figma_client import FigmaMCPClient, FigmaMCPError


def extract_text(content: list) -> str:
    """MCPレスポンスのcontentリストからテキストを抽出"""
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(item["text"])
        elif isinstance(item, str):
            parts.append(item)
    return "\n".join(parts) if parts else json.dumps(content, ensure_ascii=False, indent=2)


def parse_arg_value(value_str: str):
    """引数値を適切な型に変換（数値・bool・JSON）"""
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


def cmd_login(args):
    """OAuth PKCEフローでログイン"""
    login()


def cmd_logout(args):
    """認証トークンを削除"""
    store = TokenStore()
    if store.is_authenticated():
        store.remove_auth()
        print("Logged out successfully.")
    else:
        print("Not currently authenticated.")


def cmd_status(args):
    """認証状態を表示"""
    store = TokenStore()
    auth = store.get_auth()
    creds = store.get_client_credentials()

    if not auth or not auth.get("access_token"):
        print("Status: Not authenticated")
        print("Run 'login' to authenticate with Figma.")
        return

    import time
    expires_at = auth.get("expires_at", 0)
    remaining = expires_at - int(time.time())

    print("Status: Authenticated")
    print(f"  Scope: {auth.get('scope', 'N/A')}")
    if remaining > 0:
        minutes = remaining // 60
        print(f"  Token expires in: {minutes} minutes")
    else:
        print("  Token: expired (will auto-refresh)")
    if creds:
        print(f"  Client ID: {creds['client_id'][:16]}...")


def cmd_tools(args):
    """利用可能なFigma MCPツール一覧を表示"""
    with FigmaMCPClient(debug=args.debug) as client:
        tools = client.list_tools()
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
    """Figma MCPツールを実行"""
    # --arg key=value を辞書に変換
    arguments = {}
    if args.arg:
        for item in args.arg:
            if "=" not in item:
                print(f"Error: Invalid argument format: {item} (expected key=value)", file=sys.stderr)
                sys.exit(1)
            key, value = item.split("=", 1)
            arguments[key] = parse_arg_value(value)

    with FigmaMCPClient(debug=args.debug) as client:
        result = client.call_tool(args.tool_name, arguments)
        print(extract_text(result))


def main():
    parser = argparse.ArgumentParser(
        description="Figma MCP CLI - Figmaデザイン操作（コンテキスト取得・スクリーンショット等）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # ログイン（初回はクライアント登録も実行）
  %(prog)s login

  # 認証状態確認
  %(prog)s status

  # ツール一覧
  %(prog)s tools

  # デザインコンテキスト取得
  %(prog)s call get_design_context --arg nodeId="21146:88120"

  # スクリーンショット取得
  %(prog)s call get_screenshot --arg nodeId="21146:88120"

  # ログアウト
  %(prog)s logout
        """
    )
    parser.add_argument("--debug", action="store_true", help="デバッグログを出力")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # login
    subparsers.add_parser("login", help="OAuth PKCEフローでログイン")

    # logout
    subparsers.add_parser("logout", help="認証トークンを削除")

    # status
    subparsers.add_parser("status", help="認証状態を表示")

    # tools
    subparsers.add_parser("tools", help="利用可能なFigma MCPツール一覧")

    # call
    p_call = subparsers.add_parser("call", help="Figma MCPツールを実行")
    p_call.add_argument("tool_name", help="ツール名")
    p_call.add_argument("--arg", action="append", help="ツール引数 (key=value形式、複数指定可)")

    args = parser.parse_args()

    commands = {
        "login": cmd_login,
        "logout": cmd_logout,
        "status": cmd_status,
        "tools": cmd_tools,
        "call": cmd_call,
    }

    try:
        commands[args.command](args)
    except (TokenStoreError, OAuthError, FigmaMCPError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
