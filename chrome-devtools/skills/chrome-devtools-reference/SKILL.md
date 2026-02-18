---
name: chrome-devtools-reference
description: Chrome DevTools MCPのコマンド詳細・オプションのリファレンス。
user-invocable: false
---

# Chrome DevTools リファレンス

## コマンド一覧

### Input（入力操作）

- `click --uid <id>` - 要素をクリック（MCP: `click`）
- `drag --uid <id> --param targetUid=<id>` - ドラッグ操作（MCP: `drag`）
- `fill --uid <id> --value <value>` - 入力欄に値を設定（MCP: `fill`）
- `fill-form --param fields=...` - フォーム全体に値を設定（MCP: `fill_form`）
- `dialog --accept` / `dialog --dismiss` - ダイアログに応答（MCP: `handle_dialog`）
- `hover --uid <id>` - 要素にホバー（MCP: `hover`）
- `key --key <key>` - キー入力: Enter, Tab, Escape等（MCP: `press_key`）
- `upload --uid <id> --param paths=...` - ファイルアップロード（MCP: `upload_file`）

### Navigation（ナビゲーション）

- `navigate --url <URL>` - URLに移動（MCP: `navigate_page`）
- `new-page --url <URL>` - 新しいページを開く（MCP: `new_page`）
- `close` - 現在のページを閉じる（MCP: `close_page`）
- `pages` - 開いているページ一覧を取得（MCP: `list_pages`）
- `select-page --param index=<n>` - ページを切り替え（MCP: `select_page`）
- `wait --text <text>` - 指定テキストが表示されるまで待機（MCP: `wait_for`）

### Debugging（デバッグ）

- `snapshot` - DOMスナップショット取得: a11yツリー形式（MCP: `take_snapshot`）
- `screenshot --filename <file>` - スクリーンショット撮影（MCP: `take_screenshot`）
- `eval --expression <js>` - JavaScript実行（MCP: `evaluate_script`）
- `console-msg --param id=<id>` - コンソールメッセージ取得（MCP: `get_console_message`）
- `console` - コンソールメッセージ一覧（MCP: `list_console_messages`）

### Network（ネットワーク）

- `network-req --param reqid=<id>` - ネットワークリクエスト詳細（MCP: `get_network_request`）
- `network` - ネットワークリクエスト一覧（MCP: `list_network_requests`）

### Emulation（エミュレーション）

- `emulate --device <name>` - デバイスエミュレーション（MCP: `emulate`）
- `resize --width <w> --height <h>` - ビューポートサイズ変更（MCP: `resize_page`）

### Performance（パフォーマンス）

- `perf-start` - パフォーマンストレース開始（MCP: `performance_start_trace`）
- `perf-stop` - パフォーマンストレース停止（MCP: `performance_stop_trace`）
- `perf-analyze` - パフォーマンスインサイトの詳細分析（MCP: `performance_analyze_insight`）

## コマンドライン

```bash
# 基本形式
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py <command> [options] [--server <URL>]
```

全コマンドで `--server` オプションまたは環境変数 `CHROME_DEVTOOLS_SERVER_URL` でサーバーURLを指定。

## 共通オプション

| オプション | 説明 |
|---|---|
| `--uid <id>` | 要素の一意識別子（snapshotの出力で取得） |
| `--url <URL>` | URL |
| `--value <value>` | 設定する値 |
| `--key <key>` | キー名 |
| `--text <text>` | テキスト内容 |
| `--selector <css>` | CSSセレクタ |
| `--expression <js>` | JavaScript式 |
| `--filename <file>` | ファイル名 |
| `--device <name>` | デバイス名 |
| `--width <px>` | 幅（ピクセル） |
| `--height <px>` | 高さ（ピクセル） |
| `--timeout <ms>` | タイムアウト（ミリ秒） |
| `--accept` | ダイアログを承認 |
| `--dismiss` | ダイアログを却下 |
| `--param key=value` | 汎用パラメータ（複数指定可） |
| `--debug` | デバッグログ出力 |

## サーバー管理

```bash
# サーバー起動（JSON形式でポート情報を返す）
SERVER_INFO=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
echo $SERVER_INFO
# 出力例: {"port": 8941, "url": "http://localhost:8941/mcp", "status": "started"}

# サーバー停止
lsof -ti :8941 | xargs kill -9
```

**ポート探索**: 8941 → 8942 → 8943の順に空きポートを探す。全て使用中の場合は8941を停止して再利用。

**JSON出力フィールド**:
- `port`: 起動したポート番号
- `url`: MCP接続URL
- `status`: `started`（新規起動）または `reused`（再利用）

## ツール名の確認

MCPサーバーが実際に提供するツール名を確認:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py list-tools
```

CLIの短縮名とMCPツール名が異なる場合は、`list-tools` で確認した名前を直接指定できる。

## ログファイル

```bash
tail -f /tmp/chrome_devtools_8941.log
```
