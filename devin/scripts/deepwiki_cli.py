#!/usr/bin/env python3
"""
Devin MCP CLI

MCP Streamable HTTPクライアントのCLIエントリーポイント。
Devin MCPに接続してGitHubリポジトリのドキュメント取得・質問応答を行う。
Session API経由でタスク委任も可能。

Usage:
    python deepwiki_cli.py tools
    python deepwiki_cli.py structure <owner/repo>
    python deepwiki_cli.py read <owner/repo>
    python deepwiki_cli.py ask <owner/repo> "質問文"
    python deepwiki_cli.py run "タスク指示"
    python deepwiki_cli.py status <session_id>
    python deepwiki_cli.py message <session_id> "メッセージ"
"""

import sys
import os
import json
import argparse

sys.path.insert(0, sys.path[0] or ".")
from deepwiki_client import DeepWikiMCPClient, DeepWikiMCPError
from devin_session_client import DevinSessionClient, DevinSessionError


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


def get_api_key(args) -> str:
    """argsまたは環境変数からAPI keyを取得"""
    return args.api_key or os.environ.get("DEVIN_API_KEY") or ""


def make_client(args) -> DeepWikiMCPClient:
    """argsからMCPクライアントを生成"""
    return DeepWikiMCPClient(
        base_url=args.server,
        debug=args.debug,
        api_key=get_api_key(args),
    )


def make_session_client(args) -> DevinSessionClient:
    """argsからSession APIクライアントを生成"""
    return DevinSessionClient(
        api_key=get_api_key(args),
        debug=args.debug,
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


def cmd_run(args):
    """セッションを作成してタスクを実行"""
    client = make_session_client(args)

    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",")]

    result = client.create_session(
        prompt=args.prompt,
        title=args.title,
        tags=tags,
        idempotent=args.idempotent,
    )

    session_id = result.get("session_id", "")
    url = result.get("url", "")
    is_new = result.get("is_new_session", True)

    print(f"Session ID: {session_id}")
    print(f"URL: {url}")
    if not is_new:
        print("(既存セッションを再利用)")

    if args.wait:
        print(f"\n完了待機中（interval={args.interval}s, timeout={args.timeout}s）...")
        final = client.wait_for_completion(session_id, interval=args.interval, timeout=args.timeout)
        _print_session_summary(final)


def cmd_status(args):
    """セッション状態を確認"""
    client = make_session_client(args)
    result = client.get_session(args.session_id)
    _print_session_summary(result)


def cmd_message(args):
    """セッションにメッセージを送信"""
    client = make_session_client(args)
    client.send_message(args.session_id, args.message)
    print(f"Message sent to session {args.session_id}")


def _print_session_summary(session: dict):
    """セッション情報を整形出力"""
    print(f"\nSession: {session.get('session_id', '')}")
    print(f"Status: {session.get('status_enum', session.get('status', ''))}")
    print(f"Title: {session.get('title', '')}")

    pr = session.get("pull_request")
    if pr and pr.get("url"):
        print(f"PR: {pr['url']}")

    structured = session.get("structured_output")
    if structured:
        print(f"Output: {json.dumps(structured, ensure_ascii=False, indent=2)}")

    messages = session.get("messages", [])
    if messages:
        print(f"\n--- Messages ({len(messages)}) ---")
        for msg in messages[-5:]:  # 最新5件のみ表示
            role = msg.get("role", "") or msg.get("type", "") or msg.get("origin", "")
            content = msg.get("content", "") or msg.get("message", "")
            # 長いメッセージは切り詰め
            if len(content) > 500:
                content = content[:500] + "..."
            print(f"[{role}] {content}")


def main():
    parser = argparse.ArgumentParser(
        description="Devin MCP CLI - リポジトリのドキュメント取得・質問・タスク委任",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Wiki問い合わせ
  %(prog)s structure anthropics/claude-code
  %(prog)s ask anthropics/claude-code "How does the hook system work?"

  # Session API（タスク委任）
  %(prog)s run "docsディレクトリの中身を確認して報告してください"
  %(prog)s status <session_id>
  %(prog)s message <session_id> "追加の指示"

  # 環境変数 DEVIN_API_KEY が設定されていれば --api-key は省略可
        """
    )
    parser.add_argument("--debug", action="store_true", help="デバッグログを出力")
    parser.add_argument("--server", default=None, help="MCPサーバーURL（デフォルト: Devin MCP）")
    parser.add_argument("--api-key", default=None, help="Bearer認証用APIキー（環境変数 DEVIN_API_KEY でも可）")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Wiki問い合わせコマンド
    subparsers.add_parser("tools", help="利用可能なツール一覧を表示")

    p_structure = subparsers.add_parser("structure", help="リポジトリのドキュメント構造を取得")
    p_structure.add_argument("repo", help="リポジトリ (owner/repo)")

    p_read = subparsers.add_parser("read", help="リポジトリのドキュメント内容を取得")
    p_read.add_argument("repo", help="リポジトリ (owner/repo)")

    p_ask = subparsers.add_parser("ask", help="リポジトリについて質問")
    p_ask.add_argument("repo", help="リポジトリ (owner/repo)")
    p_ask.add_argument("question", help="質問文")

    # Session APIコマンド
    p_run = subparsers.add_parser("run", help="セッション作成・タスク実行")
    p_run.add_argument("prompt", help="タスク指示")
    p_run.add_argument("--title", default=None, help="セッションタイトル")
    p_run.add_argument("--tags", default=None, help="タグ（カンマ区切り）")
    p_run.add_argument("--idempotent", action="store_true", help="べき等モード")
    p_run.add_argument("--wait", action="store_true", help="完了まで待機")
    p_run.add_argument("--interval", type=int, default=15, help="ポーリング間隔秒数（デフォルト: 15）")
    p_run.add_argument("--timeout", type=int, default=600, help="ポーリングタイムアウト秒数（デフォルト: 600）")

    p_status = subparsers.add_parser("status", help="セッション状態確認")
    p_status.add_argument("session_id", help="セッションID")

    p_message = subparsers.add_parser("message", help="セッションにメッセージ送信")
    p_message.add_argument("session_id", help="セッションID")
    p_message.add_argument("message", help="メッセージ本文")

    args = parser.parse_args()

    commands = {
        "tools": cmd_tools,
        "structure": cmd_structure,
        "read": cmd_read,
        "ask": cmd_ask,
        "run": cmd_run,
        "status": cmd_status,
        "message": cmd_message,
    }

    try:
        commands[args.command](args)
    except (DeepWikiMCPError, DevinSessionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
