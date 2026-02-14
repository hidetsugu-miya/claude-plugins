#!/usr/bin/env python3
"""
Figma MCP Command-Line Tool

SSEサーバーモードで動作するFigma MCPへのコマンドラインインターフェース

Usage:
    figma <tool_name> [arguments...]

Examples:
    # ツール一覧を取得
    figma list-tools

    # Figmaファイルのデータを取得
    figma get_figma_data --file-url "https://www.figma.com/file/xxx/..."

    # 画像をダウンロード
    figma download_figma_images --file-url "https://www.figma.com/file/xxx/..." --node-id "1:2"
"""

import argparse
import json
import sys
import os

# スクリプトディレクトリをパスに追加
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from figma_sse_client import FigmaSSEClient


def main():
    parser = argparse.ArgumentParser(
        description="Figma MCP Command-Line Tool",
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
        default=os.environ.get("FIGMA_SERVER_URL", "http://127.0.0.1:3845"),
        help="MCP server URL (default: $FIGMA_SERVER_URL or http://127.0.0.1:3845)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    # 残りの引数をツール引数として扱う
    args, tool_args = parser.parse_known_args()

    # ツール引数をパース
    tool_parser = argparse.ArgumentParser()

    # Figma共通引数
    tool_parser.add_argument("--file-url", type=str, help="Figma file URL")
    tool_parser.add_argument("--file-key", type=str, help="Figma file key")
    tool_parser.add_argument("--node-id", type=str, help="Node ID")
    tool_parser.add_argument("--node-ids", type=str, nargs="+", help="Multiple node IDs")
    tool_parser.add_argument("--depth", type=int, help="Depth of nodes to retrieve")
    tool_parser.add_argument("--format", type=str, help="Image format (png, jpg, svg, pdf)")
    tool_parser.add_argument("--scale", type=float, help="Image scale")
    tool_parser.add_argument("--output-dir", type=str, help="Output directory for downloads")
    tool_parser.add_argument("--force-code", action="store_true", help="Force code generation")
    tool_parser.add_argument("--client-languages", type=str, help="Client languages (e.g., typescript,javascript)")
    tool_parser.add_argument("--client-frameworks", type=str, help="Client frameworks (e.g., react,vue)")
    tool_parser.add_argument("--dir-for-asset-writes", type=str, help="Directory for asset writes")

    tool_arguments = tool_parser.parse_args(tool_args)

    # 引数を辞書に変換（Noneでないもののみ、キーをキャメルケースに変換）
    def to_camel_case(snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    arguments = {}
    for k, v in vars(tool_arguments).items():
        if v is not None:
            # スネークケースをキャメルケースに変換（node_id -> nodeId）
            camel_key = to_camel_case(k)
            arguments[camel_key] = v

    try:
        with FigmaSSEClient(base_url=args.server, debug=args.debug) as client:
            # 特殊コマンド: list-tools
            if args.tool == "list-tools":
                tools = client.list_tools()
                print("Available tools:")
                for tool in tools:
                    name = tool.get("name", "unknown")
                    desc = tool.get("description", "No description")
                    print(f"  - {name}: {desc}")
                sys.exit(0)

            # 通常のツール呼び出し
            result = client.call_tool(args.tool, arguments)

            # 結果を整形して出力
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("Success (no output)")

        sys.exit(0)

    except Exception as e:
        error_result = {
            "error": str(e),
            "tool": args.tool,
            "arguments": arguments
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
