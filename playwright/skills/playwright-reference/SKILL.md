---
name: playwright-reference
description: Playwright MCPのコマンド詳細・オプションのリファレンス。
---

# Playwright リファレンス

## 主要コマンド

- `navigate --url <URL>` - URLに移動
- `snapshot` - ページスナップショット取得
- `screenshot --filename <file>` - スクリーンショット撮影
- `click --element <desc> --ref <ref>` - 要素をクリック
- `type --element <desc> --ref <ref> --text <text>` - テキスト入力
- `press_key --key <key>` - キー入力
- `hover --element <desc> --ref <ref>` - 要素にホバー
- `select_option --element <desc> --ref <ref> --values <val>` - オプション選択
- `wait_for --text <text>` または `--time <seconds>` - 待機
- `tabs --action <list|new|close|select>` - タブ操作
- `close` - ブラウザを閉じる
- `resize` - ブラウザのリサイズ
- `console` - コンソールメッセージ取得
- `network` - ネットワークリクエスト取得
- `evaluate` - JavaScriptを実行
- `drag` - ドラッグ操作
- `upload` - ファイルアップロード
- `back` - 前のページに戻る

## コマンドライン

```bash
# 基本形式
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py <command> [options] [--server <URL>]
```

全コマンドで `--server` オプションまたは環境変数 `PLAYWRIGHT_SERVER_URL` でサーバーURLを指定。

## サーバー管理

```bash
# サーバー起動（JSON形式でポート情報を返す）
SERVER_INFO=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
echo $SERVER_INFO
# 出力例: {"port": 8931, "url": "http://localhost:8931/mcp", "status": "started"}

# サーバー停止
lsof -ti :8931 | xargs kill -9
```

**ポート探索**: 8931 → 8932 → 8933の順に空きポートを探す。全て使用中の場合は8931を停止して再利用。

**JSON出力フィールド**:
- `port`: 起動したポート番号
- `url`: MCP接続URL
- `status`: `started`（新規起動）または `reused`（再利用）

## ログファイル

```bash
tail -f /tmp/playwright_8931.log
```

## オプション

その他のオプションは `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py --help` を参照。
