---
name: chrome-devtools-step
description: Chrome DevToolsでブラウザ操作・デバッグ。DOM操作、スクリーンショット、コンソールログ、ネットワーク監視、パフォーマンス分析に使用。
---

# Chrome DevTools ブラウザ自動化・デバッグ 利用手順

## 概要

mcp-proxy経由でHTTPサーバーモードで動作するChrome DevTools MCPスキル。永続的なブラウザセッションで操作・デバッグを実行できる。

**特徴**:
- セッション再利用による高速化（2回目以降は初期化をスキップ）
- 自動セッション管理（セッションIDを自動キャッシュ・再利用）
- 26種類のツール（入力・ナビゲーション・デバッグ・ネットワーク・エミュレーション・パフォーマンス）

## 手順

### 1. サーバー起動

```bash
SERVER_INFO=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
export CHROME_DEVTOOLS_SERVER_URL=$(echo "$SERVER_INFO" | jq -r '.url')
```

**jqがない場合**:
```bash
SERVER_INFO=$(bash ${CLAUDE_PLUGIN_ROOT}/scripts/start_server.sh)
echo "$SERVER_INFO"  # ポート番号を確認
export CHROME_DEVTOOLS_SERVER_URL="http://localhost:8941/mcp"  # 確認したポートを使用
```

### 2. ブラウザ操作を実行

環境変数を設定すれば `--server` オプションは不要。

```bash
# ページに移動
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py navigate --url "https://example.com"

# DOMスナップショット取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py snapshot

# スクリーンショット撮影
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py screenshot

# 要素クリック
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py click --uid "e1"

# テキスト入力
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py fill --uid "e2" --value "テキスト"

# キー入力
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py key --key "Enter"

# JavaScript実行
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py eval --expression "document.title"

# コンソールログ取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py console

# ネットワークログ取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py network
```

### 3. 利用可能ツールの確認

MCPサーバーが提供する実際のツール一覧を取得:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py list-tools
```

### 4. サーバー停止

セッション終了時にhookで自動停止されるため、手動停止は通常不要。
手動で停止する場合:

```bash
lsof -ti :8941 | xargs kill -9
```

## 汎用引数

定義済み引数にないパラメータは `--param key=value` で渡せる:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chrome_devtools.py click --param uid=e1 --param button=right
```

コマンドの詳細・オプションは `chrome-devtools-reference` スキルを参照。
