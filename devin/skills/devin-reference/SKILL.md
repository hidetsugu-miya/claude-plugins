---
name: devin-reference
description: Devin MCP/DeepWikiのコマンド詳細・オプション・認証のリファレンス。
---

# Devin / DeepWiki リファレンス

## サーバー選択

| サーバー | URL | 認証 | プライベートリポ |
|---|---|---|---|
| **Devin MCP** | `https://mcp.devin.ai/mcp` | `DEVIN_API_KEY` (Bearer) | 対応 |
| **DeepWiki** | `https://mcp.deepwiki.com/mcp` (デフォルト) | 不要 | 非対応 |

## 主要コマンド

- `tools` - 利用可能なツール一覧を表示
- `structure <owner/repo>` - リポジトリのドキュメント構造を取得
- `read <owner/repo>` - リポジトリのドキュメント内容を取得
- `ask <owner/repo> "質問文"` - リポジトリについて質問

## コマンドライン

```bash
# ツール一覧
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py [--server URL] tools

# ドキュメント構造取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py [--server URL] structure <owner/repo>

# ドキュメント内容取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py [--server URL] read <owner/repo>

# 質問応答
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki_cli.py [--server URL] ask <owner/repo> "質問文"
```

## オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--server` | MCPサーバーURL | `https://mcp.deepwiki.com/mcp` |
| `--api-key` | Bearer認証用APIキー | 環境変数 `DEVIN_API_KEY` |
| `--debug` | デバッグログを出力 | off |

## 認証

Devin MCPの利用には `DEVIN_API_KEY` が必要。以下のいずれかで指定:

1. 環境変数 `DEVIN_API_KEY`（`.claude/settings.local.json` の `env` で設定済み）
2. `--api-key` オプション

### APIキーの種類に関する注意

**Personal API Key (`apk_user_` プレフィックス) を使用すること。**

| キー種別 | プレフィックス | `read_wiki_*` | `ask_question` |
|---|---|---|---|
| Personal API Key | `apk_user_` | OK | OK |
| Service User Credential | `cog_` | OK | 500エラー |

Service User Credential (`cog_`) はv3 Beta API専用で、`ask_question` が内部で呼ぶ `ada/query` エンドポイントがv3トークンに未対応のため500エラーになる。
