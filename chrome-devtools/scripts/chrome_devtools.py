#!/usr/bin/env python3
"""
Chrome DevTools MCP Command-Line Tool

mcp-proxy経由でHTTPサーバーモードで動作するChrome DevTools MCPへのCLI

Usage:
    chrome_devtools <tool_name> [arguments...]

Examples:
    # Navigate to URL
    chrome_devtools navigate --url "https://example.com"

    # Take snapshot
    chrome_devtools snapshot

    # Take screenshot
    chrome_devtools screenshot

    # Click element
    chrome_devtools click --uid "e1"

    # Fill input
    chrome_devtools fill --uid "e2" --value "hello"

    # List available tools
    chrome_devtools list-tools
"""

import argparse
import json
import sys
import os

from chrome_devtools_http_client import ChromeDevToolsHTTPClient


# CLI短縮名 → MCPツール名マッピング
TOOL_NAME_MAP = {
    # Input
    "click": "click",
    "drag": "drag",
    "fill": "fill",
    "fill-form": "fill_form",
    "dialog": "handle_dialog",
    "hover": "hover",
    "key": "press_key",
    "upload": "upload_file",
    # Navigation
    "navigate": "navigate_page",
    "new-page": "new_page",
    "close": "close_page",
    "pages": "list_pages",
    "select-page": "select_page",
    "wait": "wait_for",
    # Debugging
    "snapshot": "take_snapshot",
    "screenshot": "take_screenshot",
    "eval": "evaluate_script",
    "console-msg": "get_console_message",
    "console": "list_console_messages",
    # Network
    "network-req": "get_network_request",
    "network": "list_network_requests",
    # Emulation
    "emulate": "emulate",
    "resize": "resize_page",
    # Performance
    "perf-start": "performance_start_trace",
    "perf-stop": "performance_stop_trace",
    "perf-analyze": "performance_analyze_insight",
}


def parse_param(param_str: str) -> tuple:
    """--param key=value 形式の引数をパース"""
    if '=' not in param_str:
        raise argparse.ArgumentTypeError(f"Invalid format: '{param_str}'. Expected 'key=value'")
    key, value = param_str.split('=', 1)
    # 数値・真偽値の自動変換
    if value.lower() == 'true':
        return key, True
    if value.lower() == 'false':
        return key, False
    try:
        return key, int(value)
    except ValueError:
        pass
    try:
        return key, float(value)
    except ValueError:
        pass
    return key, value


def main():
    parser = argparse.ArgumentParser(
        description="Chrome DevTools MCP Command-Line Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "tool",
        type=str,
        help="Tool name to execute (use 'list-tools' to see available tools)"
    )

    parser.add_argument(
        "--server",
        type=str,
        default=os.environ.get("CHROME_DEVTOOLS_SERVER_URL"),
        help="MCP server URL (default: $CHROME_DEVTOOLS_SERVER_URL)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    # 名前付き引数
    parser.add_argument("--uid", type=str, help="Element unique identifier")
    parser.add_argument("--url", type=str, help="URL")
    parser.add_argument("--value", type=str, help="Value to set")
    parser.add_argument("--key", type=str, help="Key to press")
    parser.add_argument("--text", type=str, help="Text content")
    parser.add_argument("--selector", type=str, help="CSS selector")
    parser.add_argument("--expression", type=str, help="JavaScript expression")
    parser.add_argument("--filename", type=str, help="File name for screenshot")
    parser.add_argument("--device", type=str, help="Device name for emulation")
    parser.add_argument("--width", type=int, help="Viewport width")
    parser.add_argument("--height", type=int, help="Viewport height")
    parser.add_argument("--timeout", type=int, help="Wait timeout in ms")
    parser.add_argument("--accept", action="store_true", default=None, help="Accept dialog")
    parser.add_argument("--dismiss", action="store_true", default=None, help="Dismiss dialog")

    # 汎用パラメータ
    parser.add_argument(
        "--param",
        action="append",
        type=parse_param,
        metavar="key=value",
        help="Additional parameter (can be specified multiple times)"
    )

    args = parser.parse_args()

    # サーバーURLの検証
    if not args.server:
        print("Error: Server URL is required. Set --server or CHROME_DEVTOOLS_SERVER_URL.", file=sys.stderr)
        print("Example: export CHROME_DEVTOOLS_SERVER_URL='http://localhost:8941/mcp'", file=sys.stderr)
        sys.exit(1)

    # list-tools: 利用可能ツール一覧
    if args.tool == "list-tools":
        try:
            with ChromeDevToolsHTTPClient(base_url=args.server, debug=args.debug) as client:
                tools = client.list_tools()
                for tool in tools:
                    name = tool.get("name", "")
                    desc = tool.get("description", "")
                    print(f"  {name:<30} {desc}")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # 名前付き引数を辞書に変換（None・Falseを除外）
    named_args = {}
    for key in ["uid", "url", "value", "key", "text", "selector", "expression",
                 "filename", "device", "width", "height", "timeout"]:
        val = getattr(args, key)
        if val is not None:
            named_args[key] = val

    # accept/dismiss の処理
    if args.accept:
        named_args["accept"] = True
    if args.dismiss:
        named_args["accept"] = False

    # --param による汎用引数を追加（名前付き引数より優先）
    if args.param:
        for key, value in args.param:
            named_args[key] = value

    # ツール名をMCPツール名に変換
    mcp_tool_name = TOOL_NAME_MAP.get(args.tool, args.tool)

    try:
        with ChromeDevToolsHTTPClient(base_url=args.server, debug=args.debug) as client:
            result = client.call_tool(mcp_tool_name, named_args)

            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("Success (no output)")

        sys.exit(0)

    except Exception as e:
        error_result = {
            "error": str(e),
            "tool": mcp_tool_name,
            "arguments": named_args
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
