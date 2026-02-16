#!/usr/bin/env python3
"""
Playwright MCP Command-Line Tool

HTTPサーバーモードで動作するPlaywright MCPへのコマンドラインインターフェース

Usage:
    playwright <tool_name> [arguments...]

Examples:
    # Navigate to URL
    playwright navigate --url "https://example.com"

    # Take snapshot
    playwright snapshot

    # Click element
    playwright click --element "Login button" --ref "e1"

    # Type text
    playwright type --element "Username" --ref "e2" --text "myuser"

Available Tools:
    navigate, snapshot, click, type, screenshot, press_key, hover,
    select_option, fill_form, wait_for, tabs, close, etc.
"""

import argparse
import json
import sys
import os

from playwright_http_client import PlaywrightHTTPClient


def main():
    parser = argparse.ArgumentParser(
        description="Playwright MCP Command-Line Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "tool",
        type=str,
        help="Tool name to execute"
    )

    parser.add_argument(
        "--server",
        type=str,
        default=os.environ.get("PLAYWRIGHT_SERVER_URL"),
        help="MCP server URL (default: $PLAYWRIGHT_SERVER_URL environment variable)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    # 残りの引数をツール引数として扱う
    args, tool_args = parser.parse_known_args()

    # サーバーURLの検証
    if not args.server:
        print("Error: Server URL is required. Set --server option or PLAYWRIGHT_SERVER_URL environment variable.", file=sys.stderr)
        print("Example: export PLAYWRIGHT_SERVER_URL='http://localhost:8932/mcp'", file=sys.stderr)
        sys.exit(1)

    # ツール引数をパース
    tool_parser = argparse.ArgumentParser()

    # 共通引数
    tool_parser.add_argument("--url", type=str, help="URL")
    tool_parser.add_argument("--element", type=str, help="Element description")
    tool_parser.add_argument("--ref", type=str, help="Element reference")
    tool_parser.add_argument("--text", type=str, help="Text to type")
    tool_parser.add_argument("--key", type=str, help="Key to press")
    tool_parser.add_argument("--filename", type=str, help="Screenshot filename")
    tool_parser.add_argument("--full-page", action="store_true", help="Full page screenshot")
    tool_parser.add_argument("--button", type=str, help="Mouse button (left/right/middle)")
    tool_parser.add_argument("--double-click", action="store_true", help="Double click")
    tool_parser.add_argument("--values", type=str, nargs="+", help="Values for select option")
    tool_parser.add_argument("--time", type=float, help="Time to wait (seconds)")
    tool_parser.add_argument("--action", type=str, help="Tab action (list/new/close/select)")
    tool_parser.add_argument("--index", type=int, help="Tab index")

    tool_arguments = tool_parser.parse_args(tool_args)

    # 引数を辞書に変換（None・Falseを除外）
    arguments = {
        k: v for k, v in vars(tool_arguments).items()
        if v is not None and v is not False and k not in ["debug", "server"]
    }

    # tool名を適切なMCPツール名に変換
    tool_name_map = {
        "navigate": "browser_navigate",
        "snapshot": "browser_snapshot",
        "click": "browser_click",
        "type": "browser_type",
        "screenshot": "browser_take_screenshot",
        "press_key": "browser_press_key",
        "hover": "browser_hover",
        "select_option": "browser_select_option",
        "fill_form": "browser_fill_form",
        "wait_for": "browser_wait_for",
        "tabs": "browser_tabs",
        "close": "browser_close",
        "resize": "browser_resize",
        "console": "browser_console_messages",
        "network": "browser_network_requests",
        "dialog": "browser_handle_dialog",
        "evaluate": "browser_evaluate",
        "drag": "browser_drag",
        "upload": "browser_file_upload",
        "back": "browser_navigate_back",
        "install": "browser_install",
    }

    mcp_tool_name = tool_name_map.get(args.tool, f"browser_{args.tool}")

    try:
        with PlaywrightHTTPClient(base_url=args.server, debug=args.debug) as client:
            result = client.call_tool(mcp_tool_name, arguments)

            # 結果を整形して出力
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("Success (no output)")

        sys.exit(0)

    except Exception as e:
        error_result = {
            "error": str(e),
            "tool": mcp_tool_name,
            "arguments": arguments
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
