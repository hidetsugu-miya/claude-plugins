---
name: claude-mem-reference-reference
description: claude-mem検索コマンドの詳細・オプションのリファレンス。
---

# claude-mem リファレンス

## 前提条件

claude-mem Worker（localhost:37777）が起動していること。

## 主要コマンド

- `search <query>` - メモリを検索
- `timeline --anchor <ID>` - 指定IDの前後タイムラインを取得
- `timeline --query <query>` - クエリから自動でアンカーを検索してタイムライン取得
- `observation <ID>` - 観察を単一取得
- `observations <ID>...` - 複数観察をバッチ取得
- `recent` - 最近のコンテキストを取得
- `session <ID>` - セッション情報を取得
- `prompt <ID>` - プロンプトを取得
- `help` - API仕様を表示

## コマンドライン

```bash
# 検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py search "<query>" [--limit N] [--project NAME] [--type TYPE]

# タイムライン（アンカーID指定）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py timeline --anchor <ID> [--before N] [--after N] [--project NAME]

# タイムライン（クエリ指定）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py timeline --query "<query>" [--before N] [--after N] [--project NAME]

# 観察取得（単一）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py observation <ID>

# 観察取得（バッチ）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py observations <ID1> <ID2> <ID3>

# 最近のコンテキスト
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py recent [--project NAME] [--limit N]

# セッション取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py session <ID>

# プロンプト取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py prompt <ID>
```

## オプション

### search

| オプション | 説明 | デフォルト |
|---|---|---|
| `--limit`, `-l` | 結果件数 | 20 |
| `--project`, `-p` | プロジェクト名フィルタ | なし |
| `--type`, `-t` | 検索タイプ（observations/sessions/prompts） | なし |

### timeline

| オプション | 説明 | デフォルト |
|---|---|---|
| `--anchor`, `-a` | アンカー観察ID | なし |
| `--query`, `-q` | アンカー自動検索クエリ | なし |
| `--before`, `-b` | アンカー前の深度 | 10 |
| `--after`, `-A` | アンカー後の深度 | 10 |
| `--project`, `-p` | プロジェクト名フィルタ | なし |

### recent

| オプション | 説明 | デフォルト |
|---|---|---|
| `--project`, `-p` | プロジェクト名 | なし |
| `--limit`, `-l` | セッション数 | 3 |

## その他

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py help
```
