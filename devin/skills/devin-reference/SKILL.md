---
name: devin-reference
description: Devin MCPのコマンド詳細・オプション・認証のリファレンス。
---

# Devin MCP リファレンス

## サーバー

| サーバー | URL | 認証 |
|---|---|---|
| **Devin MCP** (デフォルト) | `https://mcp.devin.ai/mcp` | `DEVIN_API_KEY` (Bearer) |

## Wiki問い合わせコマンド

- `tools` - 利用可能なツール一覧を表示
- `structure <owner/repo>` - リポジトリのドキュメント構造を取得
- `read <owner/repo>` - リポジトリのドキュメント内容を取得
- `ask <owner/repo> "質問文"` - リポジトリについて質問

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py tools
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py structure <owner/repo>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py read <owner/repo>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py ask <owner/repo> "質問文"
```

## Session APIコマンド

Devin Session API経由でタスクを委任・管理する。

- `run "タスク指示"` - セッション作成・タスク実行
- `status <session_id>` - セッション状態確認
- `message <session_id> "メッセージ"` - セッションにメッセージ送信

```bash
# セッション作成
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py run "タスク指示"

# 状態確認
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py status <session_id>

# メッセージ送信
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py message <session_id> "メッセージ"
```

### runオプション

| オプション | 説明 |
|---|---|
| `--title` | セッションタイトル |
| `--tags` | タグ（カンマ区切り） |
| `--idempotent` | べき等モード |
| `--wait` | 完了まで待機（ポーリング） |
| `--interval` | ポーリング間隔秒数（デフォルト: 15） |
| `--timeout` | ポーリングタイムアウト秒数（デフォルト: 600） |

### セッション状態

| status_enum | 説明 |
|---|---|
| `working` | 作業中 |
| `blocked` | ブロック中（ユーザー入力待ち等） |
| `finished` | 完了 |
| `expired` | 期限切れ |

### 運用ガイド

- `run` でセッション作成後、statusが `working` になったら **statusポーリングはバックグラウンドで実行** する。Devinの作業完了には数分かかるため、フォアグラウンドで待機するとその間他の作業がブロックされる。
- `--wait` オプションを使う場合も同様にバックグラウンド実行を推奨。
- `blocked` は Devin が追加指示を待っている状態。`message` で指示を送るか、結果が十分なら放置してよい。

## 共通オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--server` | MCPサーバーURL | `https://mcp.devin.ai/mcp` |
| `--api-key` | Bearer認証用APIキー | 環境変数 `DEVIN_API_KEY` |
| `--debug` | デバッグログを出力 | off |

## 認証

`DEVIN_API_KEY` が必要。以下のいずれかで指定:

1. 環境変数 `DEVIN_API_KEY`（`.claude/settings.local.json` の `env` で設定済み）
2. `--api-key` オプション

### APIキーの種類に関する注意

**Personal API Key (`apk_user_` プレフィックス) を使用すること。**

| キー種別 | プレフィックス | `read_wiki_*` | `ask_question` |
|---|---|---|---|
| Personal API Key | `apk_user_` | OK | OK |
| Service User Credential | `cog_` | OK | 500エラー |

Service User Credential (`cog_`) はv3 Beta API専用で、`ask_question` が内部で呼ぶ `ada/query` エンドポイントがv3トークンに未対応のため500エラーになる。
