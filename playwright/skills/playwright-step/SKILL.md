---
name: playwright-step
description: Webページのナビゲート、スナップショット取得、要素クリック。ブラウザ自動化やWebテストが必要な場合に使用。
---

# Playwright ブラウザ自動化 利用手順

## 概要

HTTPサーバーモードで動作するPlaywright MCPスキル。永続的なブラウザセッションで複数の操作を実行できる。

**特徴**:
- セッション再利用による高速化（2回目以降 約8-10倍高速）
- 自動セッション管理（セッションIDを自動キャッシュ・再利用）
- フォールバック機能（無効なセッションは自動的に新規作成）

## 手順

### 1. サーバー起動

```bash
SERVER_INFO=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
export PLAYWRIGHT_SERVER_URL=$(echo "$SERVER_INFO" | jq -r '.url')
```

**jqがない場合**:
```bash
SERVER_INFO=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
echo "$SERVER_INFO"  # ポート番号を確認
export PLAYWRIGHT_SERVER_URL="http://localhost:8931/mcp"  # 確認したポートを使用
```

### 2. ブラウザ操作を実行

環境変数を設定すれば `--server` オプションは不要。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py navigate --url "https://example.com"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py snapshot
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py click --element "ボタン" --ref "e1"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py type --element "入力欄" --ref "e2" --text "テキスト"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py press_key --key "Enter"
```

### 3. サーバー停止

作業終了後は必ずサーバーを停止:

```bash
lsof -ti :8931 | xargs kill -9
```

## 複数タスクの並行実行

最大3つのサーバーを同時に起動可能（`--server` オプションで明示的に指定）:

```bash
SERVER1=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
URL1=$(echo "$SERVER1" | jq -r '.url')
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py navigate --url "https://google.com" --server "$URL1" &

SERVER2=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
URL2=$(echo "$SERVER2" | jq -r '.url')
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/playwright.py navigate --url "https://yahoo.co.jp" --server "$URL2" &

wait
```

コマンドの詳細・オプションは `playwright-reference` スキルを参照。
