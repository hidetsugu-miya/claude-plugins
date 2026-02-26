---
name: devin-step
description: DeepWiki CLIでGitHubリポジトリのドキュメント取得・質問応答、Devin Session APIでタスク委任を行う手順。
context: fork
---

# DeepWiki CLI / Devin Session API 利用手順

## 概要

DeepWiki CLIでGitHubリポジトリのドキュメント構造取得・内容取得・質問応答を行い、Devin Session APIでタスク委任を行うスキル。

## いつ使うか

- GitHubリポジトリのドキュメント・実装を調べたいとき
- リポジトリ（公開・プライベート問わず）の内容を確認したいとき
- Devinにタスクを委任したいとき（Session API）

## Wiki問い合わせ手順

### 1. ドキュメント構造を確認

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py structure <owner/repo>
```

### 2. 必要に応じてドキュメント内容を取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py read <owner/repo>
```

### 3. 質問で直接回答を得る

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py ask <owner/repo> "質問文"
```

## Session API手順（タスク委任）

### 1. セッション作成

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py run "タスク指示"
```

### 2. 状態確認

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py status <session_id>
```

### 3. メッセージ送信（必要に応じて）

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py message <session_id> "メッセージ"
```

コマンドの詳細・オプション・認証は `devin-reference` スキルを参照。
