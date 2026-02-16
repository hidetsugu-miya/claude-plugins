---
name: devin-step
description: Devin MCP/DeepWiki経由でGitHubリポジトリのドキュメント取得・質問応答の手順。
---

# Devin / DeepWiki 利用手順

## 概要

MCP Streamable HTTPでDevin MCP またはDeepWikiに接続し、GitHubリポジトリのドキュメント構造取得・内容取得・質問応答を行うスキル。

## いつ使うか

- GitHubリポジトリのドキュメント・実装を調べたいとき
- プライベートリポジトリの内容を確認したいとき（Devin MCP）
- OSSライブラリの仕組みについて質問したいとき（DeepWiki）

## 手順

### 1. ドキュメント構造を確認

```bash
# 公開リポジトリ（DeepWiki）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py structure <owner/repo>

# プライベートリポジトリ（Devin MCP）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py --server https://mcp.devin.ai/mcp structure <owner/repo>
```

### 2. 必要に応じてドキュメント内容を取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py [--server https://mcp.devin.ai/mcp] read <owner/repo>
```

### 3. 質問で直接回答を得る

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py [--server https://mcp.devin.ai/mcp] ask <owner/repo> "質問文"
```

## サーバー選択の判断

- **公開リポジトリ** → `--server` 指定不要（DeepWikiがデフォルト）
- **プライベートリポジトリ** → `--server https://mcp.devin.ai/mcp` を指定（`DEVIN_API_KEY` 環境変数が必要）

コマンドの詳細・オプション・認証は `devin-reference` スキルを参照。
