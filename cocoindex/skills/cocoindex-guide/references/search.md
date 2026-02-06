# インデックス検索

## 検索コマンド

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python search.py "<自然言語クエリ>" --project-dir "$OLDPWD" [--top N]
```

- `--project-dir`: プロジェクトディレクトリ（`$OLDPWD` で `cd` 前のディレクトリを自動取得）
- テーブル名はプロジェクトディレクトリのベースネームから自動計算される
- `--top`: 表示件数（デフォルト: 10）

## 検索後の深掘り

検索結果でファイルを特定した後の深掘り手法は `~/.claude/rules/tool-selection.md` を参照。
