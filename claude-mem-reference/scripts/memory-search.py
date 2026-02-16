#!/usr/bin/env python3
"""
Claude-Mem HTTP API Wrapper

claude-memのWorker HTTP API（localhost:37777）を使用して永続メモリを検索・取得するスクリプト

Usage:
    claude-mem search <query> [--limit N] [--project NAME] [--type TYPE]
    claude-mem timeline --anchor <ID> [--before N] [--after N]
    claude-mem timeline --query <query> [--before N] [--after N]
    claude-mem observation <id>
    claude-mem observations <id> [<id>...]
    claude-mem recent [--project NAME] [--limit N]
    claude-mem session <id>
    claude-mem prompt <id>
    claude-mem help

Examples:
    # 検索
    claude-mem search "authentication" --limit 10

    # タイムライン
    claude-mem timeline --anchor 123 --before 5 --after 5

    # 複数観察をバッチ取得
    claude-mem observations 1 2 3
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error

WORKER_BASE_URL = "http://localhost:37777"


def http_get(endpoint, params=None):
    """HTTP GETリクエストを送信"""
    url = f"{WORKER_BASE_URL}{endpoint}"
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{query}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        return {"error": True, "message": f"Connection failed: {e.reason}. Is claude-mem worker running?"}
    except json.JSONDecodeError as e:
        return {"error": True, "message": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"error": True, "message": str(e)}


def http_post(endpoint, data):
    """HTTP POSTリクエストを送信"""
    url = f"{WORKER_BASE_URL}{endpoint}"

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        return {"error": True, "message": f"Connection failed: {e.reason}. Is claude-mem worker running?"}
    except json.JSONDecodeError as e:
        return {"error": True, "message": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"error": True, "message": str(e)}


def search(query, limit=None, project=None, obs_type=None):
    """メモリを検索"""
    print(f"Searching: {query}")
    if project:
        print(f"  Project: {project}")
    if obs_type:
        print(f"  Type: {obs_type}")
    print()

    params = {"query": query}
    if limit:
        params["limit"] = limit
    if project:
        params["project"] = project
    if obs_type:
        params["type"] = obs_type

    return http_get("/api/search", params)


def timeline(anchor=None, query=None, depth_before=None, depth_after=None, project=None):
    """タイムラインを取得"""
    if anchor:
        print(f"Timeline around anchor: {anchor}")
    elif query:
        print(f"Timeline for query: {query}")
    if depth_before or depth_after:
        print(f"  Depth: {depth_before or 10} before, {depth_after or 10} after")
    print()

    params = {}
    if anchor:
        params["anchor"] = anchor
    if query:
        params["query"] = query
    if depth_before:
        params["depth_before"] = depth_before
    if depth_after:
        params["depth_after"] = depth_after
    if project:
        params["project"] = project

    return http_get("/api/timeline", params)


def get_observation(obs_id):
    """観察を取得"""
    print(f"Getting observation: {obs_id}\n")
    return http_get(f"/api/observation/{obs_id}")


def get_observations(ids):
    """複数観察をバッチ取得"""
    print(f"Getting observations: {ids}\n")
    return http_post("/api/observations/batch", {"ids": ids})


def get_recent_context(project=None, limit=None):
    """最近のコンテキストを取得"""
    print("Getting recent context")
    if project:
        print(f"  Project: {project}")
    if limit:
        print(f"  Limit: {limit}")
    print()

    params = {}
    if project:
        params["project"] = project
    if limit:
        params["limit"] = limit

    return http_get("/api/context/recent", params)


def get_session(session_id):
    """セッションを取得"""
    print(f"Getting session: {session_id}\n")
    return http_get(f"/api/session/{session_id}")


def get_prompt(prompt_id):
    """プロンプトを取得"""
    print(f"Getting prompt: {prompt_id}\n")
    return http_get(f"/api/prompt/{prompt_id}")


def get_help():
    """API仕様を取得"""
    print("Getting API help\n")
    return http_get("/api/search/help")


def main():
    parser = argparse.ArgumentParser(
        description="Claude-Mem HTTP API Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # search コマンド
    search_parser = subparsers.add_parser("search", help="Search memory")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=20, help="Number of results (default: 20)")
    search_parser.add_argument("--project", "-p", type=str, help="Filter by project name")
    search_parser.add_argument("--type", "-t", type=str, choices=["observations", "sessions", "prompts"],
                               help="Search type")

    # timeline コマンド
    timeline_parser = subparsers.add_parser("timeline", help="Get timeline")
    timeline_parser.add_argument("--anchor", "-a", type=int, help="Anchor observation ID")
    timeline_parser.add_argument("--query", "-q", type=str, help="Query to find anchor automatically")
    timeline_parser.add_argument("--before", "-b", type=int, default=10, help="Depth before anchor (default: 10)")
    timeline_parser.add_argument("--after", "-A", type=int, default=10, help="Depth after anchor (default: 10)")
    timeline_parser.add_argument("--project", "-p", type=str, help="Filter by project name")

    # observation コマンド
    obs_parser = subparsers.add_parser("observation", help="Get observation by ID")
    obs_parser.add_argument("id", type=int, help="Observation ID")

    # observations コマンド
    obs_batch_parser = subparsers.add_parser("observations", help="Get multiple observations by IDs")
    obs_batch_parser.add_argument("ids", type=int, nargs="+", help="Observation IDs")

    # recent コマンド
    recent_parser = subparsers.add_parser("recent", help="Get recent context")
    recent_parser.add_argument("--project", "-p", type=str, help="Project name")
    recent_parser.add_argument("--limit", "-l", type=int, default=3, help="Number of sessions (default: 3)")

    # session コマンド
    session_parser = subparsers.add_parser("session", help="Get session by ID")
    session_parser.add_argument("id", type=int, help="Session ID")

    # prompt コマンド
    prompt_parser = subparsers.add_parser("prompt", help="Get prompt by ID")
    prompt_parser.add_argument("id", type=int, help="Prompt ID")

    # help コマンド
    subparsers.add_parser("help", help="Get API documentation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "search":
            result = search(args.query, args.limit, args.project, args.type)
        elif args.command == "timeline":
            if not args.anchor and not args.query:
                print("Error: Either --anchor or --query is required", file=sys.stderr)
                sys.exit(1)
            result = timeline(args.anchor, args.query, args.before, args.after, args.project)
        elif args.command == "observation":
            result = get_observation(args.id)
        elif args.command == "observations":
            result = get_observations(args.ids)
        elif args.command == "recent":
            result = get_recent_context(args.project, args.limit)
        elif args.command == "session":
            result = get_session(args.id)
        elif args.command == "prompt":
            result = get_prompt(args.id)
        elif args.command == "help":
            result = get_help()
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)

        print("=" * 50)
        print("Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        if isinstance(result, dict) and result.get("error"):
            sys.exit(1)
        sys.exit(0)

    except Exception as e:
        error_result = {"error": str(e), "command": args.command}
        print(json.dumps(error_result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
