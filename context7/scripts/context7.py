#!/usr/bin/env python3
"""
Context7 MCP Server Wrapper

npx @upstash/context7-mcp を使用してライブラリドキュメントを検索・取得するラッパースクリプト

Usage:
    context7 resolve <library_name>
    context7 docs <library_id> [--topic <topic>] [--tokens <tokens>]

Examples:
    # ライブラリIDを解決
    context7 resolve react

    # ライブラリドキュメントを取得
    context7 docs /reactjs/react.dev

    # トピック指定でドキュメント取得
    context7 docs /reactjs/react.dev --topic "useState hook"
"""

import argparse
import json
import os
import sys
import subprocess


def call_mcp_tool(tool_name, arguments=None):
    """
    Context7 MCPサーバーのツールを呼び出す

    npx @upstash/context7-mcp@latest を起動し、JSON-RPCでツールを呼び出す
    """
    if arguments is None:
        arguments = {}

    # MCP初期化リクエスト
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "context7-cli", "version": "1.0.0"}
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
            ["npx", "-y", "@upstash/context7-mcp@latest"],
            input=messages,
            capture_output=True,
            text=True,
            env=env,
            timeout=60
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
            stderr_lines = [l for l in result.stderr.split("\n") if "error" in l.lower()]
            if stderr_lines:
                return {"error": True, "message": "\n".join(stderr_lines)}

        return {"error": True, "message": "No response from MCP server", "raw_output": result.stdout}

    except subprocess.TimeoutExpired:
        return {"error": True, "message": "MCP server timeout"}
    except FileNotFoundError:
        return {"error": True, "message": "npx not found. Please install Node.js"}
    except Exception as e:
        return {"error": True, "message": str(e)}


def resolve_library(library_name):
    """ライブラリ名からIDを解決"""
    print(f"Resolving library: {library_name}\n")

    result = call_mcp_tool("resolve-library-id", {
        "query": library_name,
        "libraryName": library_name
    })

    return result


def get_library_docs(library_id, topic=None, tokens=None):
    """ライブラリのドキュメントを取得"""
    print(f"Getting docs for: {library_id}")
    if topic:
        print(f"   Topic: {topic}")
    if tokens:
        print(f"   Max tokens: {tokens}")
    print()

    params = {"libraryId": library_id}
    if topic:
        params["query"] = topic
    else:
        params["query"] = "overview"

    result = call_mcp_tool("query-docs", params)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Context7 MCP Server Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # resolve コマンド
    resolve_parser = subparsers.add_parser(
        "resolve",
        help="Resolve library name to ID"
    )
    resolve_parser.add_argument(
        "library",
        type=str,
        help="Library name (e.g., react, vue, express)"
    )

    # docs コマンド
    docs_parser = subparsers.add_parser(
        "docs",
        help="Get library documentation"
    )
    docs_parser.add_argument(
        "library_id",
        type=str,
        help="Library ID (e.g., /reactjs/react.dev)"
    )
    docs_parser.add_argument(
        "--topic",
        type=str,
        help="Topic to focus documentation on"
    )
    docs_parser.add_argument(
        "--tokens",
        type=int,
        help="Maximum number of tokens to retrieve (default: 5000)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "resolve":
            result = resolve_library(args.library)
        elif args.command == "docs":
            result = get_library_docs(
                args.library_id,
                args.topic if hasattr(args, 'topic') else None,
                args.tokens if hasattr(args, 'tokens') else None
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
