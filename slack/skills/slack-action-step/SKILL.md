---
name: slack-action-step
description: Slack MCPツールの実行手順。メッセージ検索・送信・チャンネル読み取り等を実行する。
---

# Slack MCP アクション実行

## 入力

$ARGUMENTS

## 前提

slack-login-step でログイン済みであること。

## 手順

### 1. ツール実行

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py call <tool_name> --arg key=value
```

引数は `--arg` で複数指定可能:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py call slack_search_public --arg query="キーワード" --arg count=5
```

### 主要ツール例

| ツール | 用途 | 主要引数 |
|---|---|---|
| `slack_search_public` | パブリックチャンネル検索 | `query`, `limit` |
| `slack_search_public_and_private` | 全チャンネル検索（DM含む） | `query`, `limit` |
| `slack_send_message` | メッセージ送信 | `channel_id`, `message` |
| `slack_read_channel` | チャンネルメッセージ読み取り | `channel_id`, `limit` |
| `slack_read_thread` | スレッド返信取得 | `channel_id`, `message_ts` |
| `slack_search_channels` | チャンネル検索 | `query` |
| `slack_search_users` | ユーザー検索 | `query` |
| `slack_read_user_profile` | ユーザープロフィール | `user_id` |
| `slack_create_canvas` | Canvas作成 | `title`, `content` |

### ワークスペース指定（オプション）

デフォルト以外のワークスペースを使用:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py call <tool_name> --workspace <workspace_key> --arg key=value
```

## 出力

ツール実行結果を構造化して報告する。
