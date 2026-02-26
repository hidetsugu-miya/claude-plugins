---
name: code-search
description: コードベースのベクトル検索を実行する。ヘルスチェックから検索・インデックス構築までを一貫して行う。
context: fork
---

# CocoIndex ベクトル検索

## 入力

$ARGUMENTS

## ワークフロー

### 1. ヘルスチェック（PostgreSQL + インデックス確認）

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/check.sh
```

以下を一括確認する:
- PostgreSQL接続（停止中なら `docker compose up` を自動試行）
- 現プロジェクトのインデックステーブルの存在とチャンク数

### 2. 結果に応じて実行

#### 全てOK → 検索を実行

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python search.py "$ARGUMENTS" --project-dir "${CLAUDE_PROJECT_DIR:-$PWD}"
```

**検索オプション:**
- `--project-dir`: プロジェクトディレクトリ（`$CLAUDE_PROJECT_DIR` を優先、未設定時は `$PWD` にフォールバック）
- `--top`: 表示件数（デフォルト: 10）
- テーブル名はプロジェクトディレクトリのベースネームから自動計算される

#### Index: NOT FOUND → インデックス構築後に検索

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python main.py <source_path> [--patterns "**/*.rb,**/*.py"] [--exclude "**/tmp/**"] [--name <project_name>]
```

**構築オプション:**
- `source_path`: インデックス対象ディレクトリ（絶対パス）
- `--patterns`: 対象ファイルパターン（カンマ区切り、デフォルト: `**/*.rb`）
- `--exclude`: 除外パターン（カンマ区切り、デフォルト除外パターンに追加される）
- `--name`: プロジェクト名（省略時は `source_path` の親ディレクトリ名から自動推定）
- `--no-default-excludes`: デフォルト除外パターン（`.git`, `node_modules`, `.venv` 等）を無効化
- テーブル名: `codeindex_<project_name>__code_chunks`（実行後にも表示）

構築完了後、再度検索を実行する。

#### PostgreSQL接続NG → DB起動

```bash
cd ~/.config/cocoindex && docker compose up -d
```

起動後、ステップ1からやり直す。

**重要**: スクリプトは `uv run` 経由で実行すること。`python3` で直接実行すると依存パッケージが見つからずエラーになる。

## 出力

検索結果から関連ファイルのリストを構造化して報告する:
- 各ファイルのパスとスコア
- ファイルの概要（検索結果から読み取れる範囲で）
