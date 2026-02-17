#!/usr/bin/env python3
"""
Claude-Mem HTTP API Wrapper

claude-memのWorker HTTP API（localhost:37777）を使用して永続メモリを検索・取得するスクリプト

Usage:
    claude-mem search <query> [--limit N] [--project NAME] [--type TYPE]
    claude-mem by-concept <concept> [--limit N] [--project NAME]
    claude-mem by-file <path> [--limit N] [--project NAME]
    claude-mem by-type <type> [--limit N] [--project NAME]
    claude-mem timeline --anchor <ID> [--before N] [--after N] [--project NAME]
    claude-mem timeline --query <query> [--mode MODE] [--before N] [--after N] [--project NAME]
    claude-mem observation <id>
    claude-mem recent [--project NAME] [--limit N]
    claude-mem session <id>
    claude-mem prompt <id>
    claude-mem help

Examples:
    # observations検索（デフォルト）
    claude-mem search "authentication" --limit 10

    # sessions検索
    claude-mem search "authentication" --type sessions

    # concept検索
    claude-mem by-concept "bugfix" --limit 5

    # ファイルパス検索
    claude-mem by-file "src/auth.ts"

    # タイムライン（アンカー指定）
    claude-mem timeline --anchor 123 --before 5 --after 5

    # タイムライン（クエリ指定、モード付き）
    claude-mem timeline --query "authentication" --mode auto
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


def search(query, limit=None, project=None, search_type=None):
    """メモリを検索（observations/sessions/prompts）"""
    endpoint_map = {
        None: "/api/search/observations",
        "observations": "/api/search/observations",
        "sessions": "/api/search/sessions",
        "prompts": "/api/search/prompts",
    }
    endpoint = endpoint_map.get(search_type, "/api/search/observations")
    label = search_type or "observations"

    print(f"Searching {label}: {query}")
    if project:
        print(f"  Project: {project}")
    print()

    params = {"query": query}
    if limit:
        params["limit"] = limit
    if project:
        params["project"] = project

    return http_get(endpoint, params)


def search_by_concept(concept, limit=None, project=None):
    """concept(タグ)で検索"""
    print(f"Searching by concept: {concept}")
    if project:
        print(f"  Project: {project}")
    print()

    params = {"concept": concept}
    if limit:
        params["limit"] = limit
    if project:
        params["project"] = project

    return http_get("/api/search/by-concept", params)


def search_by_file(file_path, limit=None, project=None):
    """ファイルパスで検索"""
    print(f"Searching by file: {file_path}")
    if project:
        print(f"  Project: {project}")
    print()

    params = {"filePath": file_path}
    if limit:
        params["limit"] = limit
    if project:
        params["project"] = project

    return http_get("/api/search/by-file", params)


def search_by_type(obs_type, limit=None, project=None):
    """観察タイプで検索"""
    print(f"Searching by type: {obs_type}")
    if project:
        print(f"  Project: {project}")
    print()

    params = {"type": obs_type}
    if limit:
        params["limit"] = limit
    if project:
        params["project"] = project

    return http_get("/api/search/by-type", params)


def timeline(anchor=None, query=None, mode=None, depth_before=None, depth_after=None, project=None):
    """タイムラインを取得"""
    if anchor:
        print(f"Timeline around anchor: {anchor}")
        params = {"anchor": anchor}
        if depth_before:
            params["depth_before"] = depth_before
        if depth_after:
            params["depth_after"] = depth_after
        if project:
            params["project"] = project
        return http_get("/api/context/timeline", params)
    elif query:
        print(f"Timeline for query: {query}")
        if mode:
            print(f"  Mode: {mode}")
        params = {"query": query}
        if mode:
            params["mode"] = mode
        if depth_before:
            params["depth_before"] = depth_before
        if depth_after:
            params["depth_after"] = depth_after
        if project:
            params["project"] = project
        return http_get("/api/timeline/by-query", params)


def get_observation(obs_id):
    """観察を取得"""
    print(f"Getting observation: {obs_id}\n")
    return http_get(f"/api/observation/{obs_id}")


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
    search_parser = subparsers.add_parser("search", help="Search memory (observations/sessions/prompts)")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=20, help="Number of results (default: 20)")
    search_parser.add_argument("--project", "-p", type=str, help="Filter by project name")
    search_parser.add_argument("--type", "-t", type=str, choices=["observations", "sessions", "prompts"],
                               help="Search type (default: observations)")

    # by-concept コマンド
    concept_parser = subparsers.add_parser("by-concept", help="Search by concept tag")
    concept_parser.add_argument("concept", type=str, help="Concept tag (discovery/decision/bugfix/feature/refactor)")
    concept_parser.add_argument("--limit", "-l", type=int, default=10, help="Number of results (default: 10)")
    concept_parser.add_argument("--project", "-p", type=str, help="Filter by project name")

    # by-file コマンド
    file_parser = subparsers.add_parser("by-file", help="Search by file path")
    file_parser.add_argument("path", type=str, help="File path or partial path")
    file_parser.add_argument("--limit", "-l", type=int, default=10, help="Number of results (default: 10)")
    file_parser.add_argument("--project", "-p", type=str, help="Filter by project name")

    # by-type コマンド
    type_parser = subparsers.add_parser("by-type", help="Search by observation type")
    type_parser.add_argument("type", type=str, help="Observation type (discovery/decision/bugfix/feature/refactor)")
    type_parser.add_argument("--limit", "-l", type=int, default=10, help="Number of results (default: 10)")
    type_parser.add_argument("--project", "-p", type=str, help="Filter by project name")

    # timeline コマンド
    timeline_parser = subparsers.add_parser("timeline", help="Get timeline")
    timeline_parser.add_argument("--anchor", "-a", type=str, help="Anchor point: observation ID, session ID (S123), or ISO timestamp")
    timeline_parser.add_argument("--query", "-q", type=str, help="Query to find anchor automatically")
    timeline_parser.add_argument("--mode", "-m", type=str, choices=["auto", "observations", "sessions"],
                                 help="Search mode for --query (default: auto)")
    timeline_parser.add_argument("--before", "-b", type=int, default=10, help="Depth before anchor (default: 10)")
    timeline_parser.add_argument("--after", "-A", type=int, default=10, help="Depth after anchor (default: 10)")
    timeline_parser.add_argument("--project", "-p", type=str, help="Filter by project name")

    # observation コマンド
    obs_parser = subparsers.add_parser("observation", help="Get observation by ID")
    obs_parser.add_argument("id", type=int, help="Observation ID")

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
        elif args.command == "by-concept":
            result = search_by_concept(args.concept, args.limit, args.project)
        elif args.command == "by-file":
            result = search_by_file(args.path, args.limit, args.project)
        elif args.command == "by-type":
            result = search_by_type(args.type, args.limit, args.project)
        elif args.command == "timeline":
            if not args.anchor and not args.query:
                print("Error: Either --anchor or --query is required", file=sys.stderr)
                sys.exit(1)
            result = timeline(args.anchor, args.query, args.mode, args.before, args.after, args.project)
        elif args.command == "observation":
            result = get_observation(args.id)
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
