---
name: slack-reference
description: Slack MCPのコマンド詳細・ツール一覧・トークン管理のリファレンス。
---

# Slack MCP リファレンス

## サーバー

| サーバー | URL | 認証 |
|---|---|---|
| **Slack MCP** | `https://mcp.slack.com/mcp` | OAuth PKCE (user token) |

## CLIコマンド

### 認証・ワークスペース管理

```bash
# OAuth PKCEフローでログイン（ブラウザ認証）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py login

# ワークスペースのトークン削除
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py logout <workspace_key>

# 保存済みワークスペース一覧
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py workspaces

# デフォルトワークスペース変更
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py set-default <workspace_key>
```

### ツール操作

```bash
# 利用可能なツール一覧
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py tools

# ツール実行
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/slack_cli.py call <tool_name> --arg key=value [--arg key2=value2]
```

## 共通オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--workspace` | ワークスペースキー | デフォルトワークスペース |
| `--debug` | デバッグログを出力 | off |

## Slack MCPツール一覧

| ツール名 | 説明 | 主要引数 |
|---|---|---|
| `slack_send_message` | メッセージ送信 | `channel_id`*, `message`*, `thread_ts` |
| `slack_schedule_message` | メッセージ予約送信 | `channel_id`*, `message`*, `post_at`* |
| `slack_send_message_draft` | 下書き作成 | `channel_id`*, `message`*, `thread_ts` |
| `slack_search_public` | パブリックチャンネル検索 | `query`*, `limit`, `sort`, `sort_dir` |
| `slack_search_public_and_private` | 全チャンネル検索（DM含む） | `query`*, `channel_types`, `limit` |
| `slack_search_channels` | チャンネル名・説明で検索 | `query`*, `channel_types`, `limit` |
| `slack_search_users` | ユーザー検索 | `query`*, `limit` |
| `slack_read_channel` | チャンネルメッセージ読み取り | `channel_id`*, `limit`, `oldest`, `latest` |
| `slack_read_thread` | スレッド返信取得 | `channel_id`*, `message_ts`*, `limit` |
| `slack_read_canvas` | Canvas読み取り | `canvas_id`* |
| `slack_create_canvas` | Canvas作成 | `title`*, `content`* |
| `slack_read_user_profile` | ユーザープロフィール取得 | `user_id` |

**注意**: ツール一覧はサーバー側で変更される可能性があります。最新の一覧は `tools` コマンドで確認してください。

## トークン管理

- 保存先: `~/.config/slack-mcp/workspaces.json` (パーミッション 0600)
- トークン有効期限: 12時間
- 有効期限5分前に自動リフレッシュ
- リフレッシュに失敗した場合は `login` を再実行

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `No workspace configured` | `login` でワークスペースを追加 |
| `Token refresh failed` | `login` で再認証 |
| `HTTP request failed` | ネットワーク接続を確認。`--debug` で詳細ログを出力 |
| `MCP Error` | ツール名・引数を確認。`tools` で利用可能なツール一覧を確認 |
| ポート3118が使用中 | `login` 実行前に他のSlack MCP認証プロセスを終了 |
