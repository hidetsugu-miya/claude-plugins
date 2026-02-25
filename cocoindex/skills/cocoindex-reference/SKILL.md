---
name: cocoindex-reference
description: CocoIndexのセットアップ・構築・検索コマンドのリファレンス。環境構築からインデックス操作まで。
user-invocable: false
---

# CocoIndex リファレンス

## 共通情報

- **スクリプト**: `${CLAUDE_PLUGIN_ROOT}/scripts/`
- **ユーザー設定**: `~/.config/cocoindex/`（`.env`, `compose.yml`）
- **DB**: `cocoindex` コンテナ（ポート15432）

## セットアップ

### 初回セットアップ

`~/.config/cocoindex/` の設定ファイルは、セッション開始時およびヘルスチェック実行時にテンプレートから自動コピーされる。

手動セットアップが必要な場合:

```bash
mkdir -p ~/.config/cocoindex && cp ${CLAUDE_PLUGIN_ROOT}/templates/.env.example ~/.config/cocoindex/.env && cp ${CLAUDE_PLUGIN_ROOT}/templates/compose.yml ~/.config/cocoindex/compose.yml
```

自動・手動いずれの場合も、`~/.config/cocoindex/.env` の `VOYAGE_API_KEY` を設定すること。

### DB起動

```bash
cd ~/.config/cocoindex && docker compose up -d
```

## インデックス構築

### 構築コマンド

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python main.py <source_path> [--patterns "**/*.rb,**/*.py"] [--exclude "**/tmp/**"]
```

- `source_path`: インデックス対象ディレクトリ（絶対パス）
- `--patterns`: 対象ファイルパターン（カンマ区切り、デフォルト: `**/*.rb`）
- `--exclude`: 除外パターン（カンマ区切り）
- `--name`: プロジェクト名（省略時は `source_path` の親ディレクトリ名から自動推定）
- テーブル名: `codeindex_<project_name>__code_chunks`（実行後にも表示）

### 再構築

同じコマンドを再実行すればインデックスが更新される。

## 検索

### 検索コマンド

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python search.py "<自然言語クエリ>" --project-dir "$OLDPWD" [--top N]
```

- `--project-dir`: プロジェクトディレクトリ（`$OLDPWD` で `cd` 前のディレクトリを自動取得）
- テーブル名はプロジェクトディレクトリのベースネームから自動計算される
- `--top`: 表示件数（デフォルト: 10）

### 検索後の深掘り

検索結果でファイルを特定した後の深掘り手法は `~/.claude/rules/tool-selection.md` を参照。
