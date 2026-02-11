---
name: sentry
description: Sentryのエラートラッキングデータを取得・管理。イシュー詳細、プロジェクト情報、エラー分析に使用。
---

# Sentry Skill

`@sentry/mcp-server`を使用してSentryプロジェクトのエラートラッキングデータを取得・管理するスキル。

## 使い方

### コマンドライン

```bash
# URLからイシュー詳細を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py url "<sentry_url>"

# イシュー検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py search "is:unresolved" --org <organization>

# プロジェクト一覧を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py projects [--org <organization>]

# 組織一覧を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py orgs

# 認証ユーザー情報を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py whoami

# イシューを更新
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py update <issue_id> --status <status>

# Seer AIでイシューを分析
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py analyze <issue_id>
```

## セットアップ

### 必要条件

- Node.js 20以上（推奨: Node 22）
- 環境変数 `SENTRY_ACCESS_TOKEN`（User Auth Token）

```bash
export SENTRY_ACCESS_TOKEN=<your-auth-token>
```

Auth Tokenは Sentry > Settings > Account > API > Auth Tokens から取得。

## 主要コマンド

- `url <sentry_url>` - SentryのURLからイシュー詳細を取得
- `search <query>` - イシューを検索（`--org`, `--project`でフィルタ可）
- `projects` - プロジェクト一覧を取得
- `orgs` - 組織一覧を取得
- `whoami` - 認証ユーザー情報を取得
- `update <id>` - イシューのステータス等を更新（resolved/unresolved/ignored）
- `analyze <id>` - Seer AIでイシューを分析

## 使用例

```bash
# URLからイシュー詳細を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py url "https://myorg.sentry.io/issues/12345/"

# unresolvedなイシューを検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py search "is:unresolved" --org myorg

# 特定プロジェクトのイシューを検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py search "is:unresolved" --org myorg --project my-project

# イシューをresolvedに更新
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py update MYPROJECT-123 --status resolved

# Seer AIでイシューを分析（根本原因の特定）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py analyze MYPROJECT-123
```

その他のオプションは `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py --help` を参照。
