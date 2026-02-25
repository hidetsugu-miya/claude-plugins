---
name: rollbar-reference
description: Rollbarスキルのセットアップ・コマンド一覧・使用例のリファレンス。
user-invocable: false
---

# Rollbar リファレンス

## セットアップ

### 必要条件

- Node.js 20以上（推奨: Node 22）
- 環境変数 `ROLLBAR_ACCESS_TOKEN`（Project Access Token、`read`スコープ）

```bash
export ROLLBAR_ACCESS_TOKEN=<your-project-token>
```

Project Access Tokenは Rollbar > Project Settings > Project Access Tokens から取得。

## 主要コマンド

- `url <rollbar_url>` - RollbarのURLからアイテム詳細を取得
- `item <number>` - アイテム番号から詳細を取得
- `top` - 過去24時間のトップエラーを取得
- `list` - アイテム一覧（`--status`, `--env`, `--query`でフィルタ可）
- `deploys` - デプロイ履歴を取得
- `version <version>` - バージョン詳細を取得（`--env`でフィルタ可）
- `update <number>` - アイテムのステータス等を更新（`write`スコープ必須）

## 使用例

```bash
# URLからアイテム詳細を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py url "https://app.rollbar.com/a/org/fix/item/project/4906"

# production環境のトップエラーを確認
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py top --env production

# activeなエラーを一覧表示
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py list --status active

# アイテム一覧を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py list [--status <status>] [--env <environment>]

# デプロイ一覧を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py deploys

# バージョン詳細を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py version <version> [--env <environment>]

# アイテムを更新
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py update <item_number> --status <status>
```

その他のオプションは `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py --help` を参照。
