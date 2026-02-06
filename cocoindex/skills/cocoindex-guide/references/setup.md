# セットアップ・インデックス構築

## 初回セットアップ

`~/.config/cocoindex/` が未作成の場合、テンプレートからコピーする:

```bash
mkdir -p ~/.config/cocoindex && cp ${CLAUDE_PLUGIN_ROOT}/templates/.env.example ~/.config/cocoindex/.env && cp ${CLAUDE_PLUGIN_ROOT}/templates/compose.yml ~/.config/cocoindex/compose.yml
```

コピー後、`~/.config/cocoindex/.env` を編集して `VOYAGE_API_KEY` を設定する。

## DB起動

```bash
cd ~/.config/cocoindex && docker compose up -d
```

## 構築コマンド

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python main.py <source_path> [--patterns "**/*.rb,**/*.py"] [--exclude "**/tmp/**"]
```

- `source_path`: インデックス対象ディレクトリ（絶対パス）
- `--patterns`: 対象ファイルパターン（カンマ区切り、デフォルト: `**/*.rb`）
- `--exclude`: 除外パターン（カンマ区切り）
- `--name`: プロジェクト名（省略時は `source_path` の親ディレクトリ名から自動推定）
- テーブル名: `codeindex_<project_name>__code_chunks`（実行後にも表示）

## 再構築

同じコマンドを再実行すればインデックスが更新される。
