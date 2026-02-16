#!/usr/bin/env python3
"""
DeepWiki / Devin MCP CLI

MCP Streamable HTTPクライアントのCLIエントリーポイント。
DeepWiki（公開）またはDevin MCP（プライベートリポジトリ対応）に接続。

Usage:
    python deepwiki_cli.py tools
    python deepwiki_cli.py structure <owner/repo>
    python deepwiki_cli.py read <owner/repo>
    python deepwiki_cli.py ask <owner/repo> "質問文"
    python deepwiki_cli.py --server https://mcp.devin.ai/mcp --api-key $DEVIN_API_KEY ask <owner/repo> "質問文"
"""

import sys
import os
import json
import argparse

sys.path.insert(0, sys.path[0] or ".")
from deepwiki_client import DeepWikiMCPClient, DeepWikiMCPError


def extract_text(content: list) -> str:
    """MCPレスポンスのcontentリストからテキストを抽出"""
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(item["text"])
        elif isinstance(item, str):
            parts.append(item)
    return "\n".join(parts) if parts else json.dumps(content, ensure_ascii=False, indent=2)


def parse_repo(repo_str: str) -> tuple:
    """'owner/repo' 形式をパースして (owner, repo) を返す"""
    parts = repo_str.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        print(f"Error: リポジトリは 'owner/repo' 形式で指定してください: {repo_str}", file=sys.stderr)
        sys.exit(1)
    return parts[0], parts[1]


def make_client(args) -> DeepWikiMCPClient:
    """argsからクライアントを生成"""
    api_key = args.api_key
    # --api-key 未指定の場合、Devinサーバー指定時のみ環境変数から自動取得
    if not api_key and args.server and "devin.ai" in args.server:
        api_key = os.environ.get("DEVIN_API_KEY")
    return DeepWikiMCPClient(
        base_url=args.server,
        debug=args.debug,
        api_key=api_key,
    )


def cmd_tools(args):
    """利用可能なツール一覧を表示"""
    with make_client(args) as client:
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


def cmd_structure(args):
    """リポジトリのドキュメント構造を取得"""
    parse_repo(args.repo)
    with make_client(args) as client:
        result = client.read_structure(args.repo)
        print(extract_text(result))


def cmd_read(args):
    """リポジトリのドキュメント内容を取得"""
    parse_repo(args.repo)
    with make_client(args) as client:
        result = client.read_contents(args.repo)
        print(extract_text(result))


def cmd_ask(args):
    """リポジトリについて質問"""
    parse_repo(args.repo)
    with make_client(args) as client:
        result = client.ask_question(args.repo, args.question)
        print(extract_text(result))


def main():
    parser = argparse.ArgumentParser(
        description="MCP Streamable HTTP CLI - GitHubリポジトリのドキュメントを取得・質問",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 公開リポジトリ（DeepWiki）
  %(prog)s structure anthropics/claude-code
  %(prog)s ask anthropics/claude-code "How does the hook system work?"

  # プライベートリポジトリ（Devin MCP）
  %(prog)s --server https://mcp.devin.ai/mcp ask myorg/myrepo "What does this do?"

  # 環境変数 DEVIN_API_KEY が設定されていれば --api-key は省略可
        """
    )
    parser.add_argument("--debug", action="store_true", help="デバッグログを出力")
    parser.add_argument("--server", default=None, help="MCPサーバーURL（デフォルト: DeepWiki）")
    parser.add_argument("--api-key", default=None, help="Bearer認証用APIキー（環境変数 DEVIN_API_KEY でも可）")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("tools", help="利用可能なツール一覧を表示")

    p_structure = subparsers.add_parser("structure", help="リポジトリのドキュメント構造を取得")
    p_structure.add_argument("repo", help="リポジトリ (owner/repo)")

    p_read = subparsers.add_parser("read", help="リポジトリのドキュメント内容を取得")
    p_read.add_argument("repo", help="リポジトリ (owner/repo)")

    p_ask = subparsers.add_parser("ask", help="リポジトリについて質問")
    p_ask.add_argument("repo", help="リポジトリ (owner/repo)")
    p_ask.add_argument("question", help="質問文")

    args = parser.parse_args()

    commands = {
        "tools": cmd_tools,
        "structure": cmd_structure,
        "read": cmd_read,
        "ask": cmd_ask,
    }

    try:
        commands[args.command](args)
    except DeepWikiMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
