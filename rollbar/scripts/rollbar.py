#!/usr/bin/env python3
"""
Rollbar MCP Server Wrapper

npx @rollbar/mcp-server を使用してRollbarデータを取得・管理するラッパースクリプト

Usage:
    rollbar url <rollbar_url>
    rollbar item <item_number> [--max-tokens <tokens>]
    rollbar top [--env <environment>]
    rollbar list [--status <status>] [--env <environment>] [--query <query>]
    rollbar deploys
    rollbar version <version> [--env <environment>]
    rollbar update <item_number> --status <status>

Examples:
    # URLからアイテム詳細を取得
    rollbar url "https://app.rollbar.com/a/pharumo/fix/item/every_pharumo_com/4906"

    # production環境のトップエラーを取得
    rollbar top --env production

    # activeなアイテムを一覧表示
    rollbar list --status active --env production
"""

import argparse
import json
import os
import re
import subprocess
import sys


def call_mcp_tool(tool_name, arguments=None):
    """
    Rollbar MCPサーバーのツールを呼び出す

    npx @rollbar/mcp-server@latest を起動し、JSON-RPCでツールを呼び出す
    """
    if arguments is None:
        arguments = {}

    token = os.environ.get("ROLLBAR_ACCESS_TOKEN")
    if not token:
        print("Error: ROLLBAR_ACCESS_TOKEN environment variable is not set", file=sys.stderr)
        print("\nSet the token with:", file=sys.stderr)
        print("  export ROLLBAR_ACCESS_TOKEN=<your-project-token>", file=sys.stderr)
        sys.exit(1)

    # MCP初期化リクエスト
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "rollbar-cli", "version": "1.0.0"}
        },
        "id": 1
    }

    # ツール呼び出しリクエスト
    tool_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 2
    }

    messages = json.dumps(init_request) + "\n" + json.dumps(tool_request) + "\n"

    try:
        env = os.environ.copy()
        result = subprocess.run(
            ["npx", "-y", "@rollbar/mcp-server@latest"],
            input=messages,
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        responses = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                try:
                    responses.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        for resp in responses:
            if resp.get("id") == 2:
                if "error" in resp:
                    return {"error": True, "message": resp["error"]}
                return resp.get("result", {})

        if result.stderr:
            return {"error": True, "message": result.stderr}

        return {"error": True, "message": "No response from MCP server", "raw_output": result.stdout}

    except subprocess.TimeoutExpired:
        return {"error": True, "message": "MCP server timeout"}
    except FileNotFoundError:
        return {"error": True, "message": "npx not found. Please install Node.js"}
    except Exception as e:
        return {"error": True, "message": str(e)}


def parse_rollbar_url(url):
    """RollbarのURLからアイテム番号を抽出"""
    match = re.search(r'/fix/item/[^/]+/(\d+)', url)
    if match:
        return int(match.group(1))

    match = re.search(r'/items/(\d+)', url)
    if match:
        return int(match.group(1))

    return None


def get_item_from_url(url):
    """RollbarのURLからアイテム詳細を取得"""
    print(f"🔗 Parsing URL: {url}\n")

    item_number = parse_rollbar_url(url)
    if item_number is None:
        return {"error": True, "message": f"Could not parse item number from URL: {url}"}

    print(f"   Item: #{item_number}\n")
    return get_item_details(item_number)


def get_item_details(item_number, max_tokens=None):
    """アイテム番号から詳細を取得"""
    print(f"🔍 Getting item details: #{item_number}\n")

    args = {"counter": item_number}
    if max_tokens:
        args["max_tokens"] = max_tokens

    return call_mcp_tool("get-item-details", args)


def get_top_items(environment=None):
    """トップエラーを取得"""
    print("📊 Getting top items")
    if environment:
        print(f"   Environment: {environment}")
    print()

    args = {}
    if environment:
        args["environment"] = environment

    return call_mcp_tool("get-top-items", args)


def list_items(status=None, environment=None, query=None):
    """アイテム一覧を取得"""
    print("📋 Listing items")
    if status:
        print(f"   Status: {status}")
    if environment:
        print(f"   Environment: {environment}")
    if query:
        print(f"   Query: {query}")
    print()

    args = {}
    if status:
        args["status"] = status
    if environment:
        args["environment"] = environment
    if query:
        args["query"] = query

    return call_mcp_tool("list-items", args)


def get_deploys():
    """デプロイ一覧を取得"""
    print("🚀 Getting deploys\n")
    return call_mcp_tool("get-deployments")


def get_version(version, environment=None):
    """バージョン詳細を取得"""
    print(f"📦 Getting version details: {version}")
    if environment:
        print(f"   Environment: {environment}")
    print()

    args = {"version": version}
    if environment:
        args["environment"] = environment

    return call_mcp_tool("get-version", args)


def update_item(item_number, status=None, level=None, title=None):
    """アイテムを更新"""
    print(f"✏️  Updating item: #{item_number}")
    if status:
        print(f"   Status: {status}")
    if level:
        print(f"   Level: {level}")
    print()

    args = {"item_number": str(item_number)}
    if status:
        args["status"] = status
    if level:
        args["level"] = level
    if title:
        args["title"] = title

    if len(args) == 1:
        return {"error": True, "message": "No update parameters provided"}

    return call_mcp_tool("update-item", args)


def main():
    parser = argparse.ArgumentParser(
        description="Rollbar MCP Server Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # url コマンド
    url_parser = subparsers.add_parser("url", help="Get item details from Rollbar URL")
    url_parser.add_argument("url", type=str, help="Rollbar item URL")

    # item コマンド
    item_parser = subparsers.add_parser("item", help="Get item details")
    item_parser.add_argument("item_number", type=int, help="Item number")
    item_parser.add_argument("--max-tokens", type=int, help="Maximum tokens for response")

    # top コマンド
    top_parser = subparsers.add_parser("top", help="Get top error items")
    top_parser.add_argument("--env", "-e", type=str, dest="environment", help="Environment filter")

    # list コマンド
    list_parser = subparsers.add_parser("list", help="List items with filters")
    list_parser.add_argument("--status", "-s", type=str,
                            choices=["active", "resolved", "muted", "archived"], help="Status filter")
    list_parser.add_argument("--env", "-e", type=str, dest="environment", help="Environment filter")
    list_parser.add_argument("--query", "-q", type=str, help="Search query")

    # deploys コマンド
    subparsers.add_parser("deploys", help="Get deployment history")

    # version コマンド
    version_parser = subparsers.add_parser("version", help="Get version details")
    version_parser.add_argument("version", type=str, help="Version string")
    version_parser.add_argument("--env", "-e", type=str, dest="environment", help="Environment filter")

    # update コマンド
    update_parser = subparsers.add_parser("update", help="Update item properties")
    update_parser.add_argument("item_number", type=int, help="Item number to update")
    update_parser.add_argument("--status", "-s", type=str,
                              choices=["active", "resolved", "muted", "archived"], help="New status")
    update_parser.add_argument("--level", "-l", type=str,
                              choices=["critical", "error", "warning", "info", "debug"], help="New level")
    update_parser.add_argument("--title", "-t", type=str, help="New title")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "url":
            result = get_item_from_url(args.url)
        elif args.command == "item":
            result = get_item_details(args.item_number, getattr(args, 'max_tokens', None))
        elif args.command == "top":
            result = get_top_items(args.environment)
        elif args.command == "list":
            result = list_items(args.status, args.environment, args.query)
        elif args.command == "deploys":
            result = get_deploys()
        elif args.command == "version":
            result = get_version(args.version, args.environment)
        elif args.command == "update":
            result = update_item(
                args.item_number,
                status=args.status,
                level=getattr(args, 'level', None),
                title=getattr(args, 'title', None)
            )
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
