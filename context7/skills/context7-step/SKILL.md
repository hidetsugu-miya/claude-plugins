---
name: context7-step
description: ライブラリの最新ドキュメント取得手順。パッケージ名からIDを解決し、ドキュメントを参照する。
---

# Context7 利用手順

## 概要

最新のライブラリドキュメントを取得するスキル。`npx @upstash/context7-mcp@latest` を使用してJSON-RPCでMCPサーバーを呼び出し、npmパッケージやその他のライブラリの公式ドキュメントを直接参照できる。

## 手順

### 1. ライブラリIDを解決

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py resolve <library_name>
```

### 2. ドキュメントを取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py docs <library_id> [--topic <topic>] [--tokens <tokens>]
```

コマンドの詳細・オプションは `context7-reference` スキルを参照。

## サブエージェント

メインコンテキストの消費を抑えるため、`context7-runner` サブエージェントに委任して実行できる。
