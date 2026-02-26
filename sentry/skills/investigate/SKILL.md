---
name: investigate
description: Sentryエラートラッキングの調査を実行。URLやイシューIDからエラー詳細を取得し、検索やAI分析を行う。
context: fork
---

# Sentry 調査手順

委任メッセージまたはユーザーの指示から調査対象・目的を把握し、Sentry のエラートラッキングデータを取得する。

## 前提条件

- Node.js 20以上（推奨: Node 22）
- 環境変数 `SENTRY_ACCESS_TOKEN`（User Auth Token）が設定済みであること

Auth Token は Sentry > Settings > Account > API > Auth Tokens から取得。

## ワークフロー

1. **調査目的を判定**:
   - URL が指定されている → `url` コマンドでイシュー詳細を取得
   - イシュー検索が必要 → `search` コマンドで検索クエリを実行
   - 原因分析が必要 → `analyze` コマンドで AI 分析を実行
   - その他 → 下記コマンド一覧から適切なコマンドを選択
2. **コマンド実行**: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py <subcommand> [options]`
3. **結果の解析と報告**

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `url <sentry_url>` | Sentry の URL からイシュー詳細を取得 |
| `issue <issue_id>` | イシュー ID から詳細を取得 |
| `search <query>` | イシューを検索（`--org`, `--project` でフィルタ可） |
| `projects` | プロジェクト一覧を取得（`--org` でフィルタ可） |
| `orgs` | 組織一覧を取得 |
| `whoami` | 認証ユーザー情報を取得 |
| `update <id>` | イシューのステータス等を更新（resolved/unresolved/ignored） |
| `analyze <id>` | Seer AI でイシューを分析（根本原因の特定） |

## 使用例

```bash
# URL からイシュー詳細を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py url "https://myorg.sentry.io/issues/12345/"

# unresolved なイシューを検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py search "is:unresolved" --org myorg

# 特定プロジェクトのイシューを検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py search "is:unresolved" --org myorg --project my-project

# プロジェクト一覧を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py projects --org myorg

# イシューを resolved に更新
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py update MYPROJECT-123 --status resolved

# Seer AI でイシューを分析
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py analyze MYPROJECT-123
```

その他のオプションは `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py --help` を参照。

## 備考

- セルフホスト環境の URL の場合、`SENTRY_HOST` を自動算出する（手動設定は不要）
- `sentry.io` / `*.sentry.io` の URL はデフォルト扱い

## 出力形式

取得した情報を以下の形式で返す:

- 実行したコマンドと対象
- イシュー詳細または検索結果の要約
- AI 分析結果（analyze コマンド使用時）
- 対応が必要な場合の推奨アクション
