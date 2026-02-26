---
name: login
description: Slack MCPへのOAuth認証手順。ブラウザでSlackワークスペースを認証し、トークンを保存する。
---

# Slack MCP ログイン

## 入力

$ARGUMENTS

## 手順

### 1. ログイン実行

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py login
```

**ブラウザが開きます。ユーザーにSlackワークスペースの認証を依頼してください。**

スクリプトがブラウザを起動し、Slackの認証ページを表示します。ユーザーがワークスペースを選択して認証を完了すると、トークンが自動保存されます。

### 2. ログイン確認

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py workspaces
```

ワークスペース名とデフォルト設定が表示されれば認証完了。

### 3. 複数ワークスペース（オプション）

追加ワークスペースが必要な場合は `login` を再実行。デフォルトの切り替え:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py set-default <workspace_key>
```

### ワークスペース管理コマンド

```bash
# ワークスペースのトークン削除
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py logout <workspace_key>

# 保存済みワークスペース一覧
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py workspaces

# デフォルトワークスペース変更
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py set-default <workspace_key>
```

## トークン管理

- 保存先: `~/.config/slack-mcp/workspaces.json` (パーミッション 0600)
- トークン有効期限: 12時間
- 有効期限5分前に自動リフレッシュ
- リフレッシュに失敗した場合は `login` を再実行

## 出力

認証結果を報告する:
- ワークスペース名とID
- デフォルト設定の状態
