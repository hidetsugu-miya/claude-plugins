---
name: claude-mem-reference
description: claude-mem検索コマンドの詳細・オプション・トラブルシューティングのリファレンス。
user-invocable: false
---

# claude-mem リファレンス

## 前提条件

- claude-mem Worker（localhost:37777）が起動していること
- Chromaサーバー（localhost:8000）が起動していること（セマンティック検索に必要）

### Chromaサーバーのトラブルシューティング

検索で「Chroma connection failed」エラーが出る場合、Chromaサーバーが起動していない。

Workerは起動時にChromaを自動起動しようとするが、`chromadb` npmパッケージが未インストールの場合は失敗する。

```bash
# chromadb npmパッケージのインストール（Worker自動起動に必要）
cd ~/.claude/plugins/cache/thedotmack/claude-mem/<VERSION>/
bun add chromadb

# 動作確認（v2 APIで200が返ればOK）
curl http://localhost:8000/api/v2/heartbeat
```

npmパッケージが大容量DB（数百MB以上）でハングする場合は、Python版chromadbで手動起動する:

```bash
# Python版chromadbのインストール
uv pip install --system chromadb

# Chromaサーバーの手動起動
chroma run --path ~/.claude-mem/vector-db --host 127.0.0.1 --port 8000
```

### Gemini API バージョンの既知の問題

Gemini 3系モデル（`gemini-3-flash`, `gemini-3-flash-preview`）を使用すると404エラーになる。

**原因**: `worker-service.cjs` のGemini APIエンドポイントが `v1` にハードコードされているが、Gemini 3系は `v1beta` でのみ利用可能。

**修正方法**: `worker-service.cjs` 内のエンドポイントを修正する:

```bash
# 修正（v1 → v1beta）
cd ~/.claude/plugins/cache/thedotmack/claude-mem/<VERSION>/scripts/
sed -i '' 's|generativelanguage.googleapis.com/v1/models|generativelanguage.googleapis.com/v1beta/models|' worker-service.cjs
```

修正後はworkerの再起動が必要。プラグインの更新で上書きされる点に注意。

参照: https://github.com/thedotmack/claude-mem/issues/1148

## 主要コマンド

- `search <query>` - メモリを検索（デフォルト: observations）
- `search <query> --type sessions` - セッション検索
- `search <query> --type prompts` - プロンプト検索
- `by-concept <concept>` - conceptタグで検索
- `by-file <path>` - ファイルパスで検索
- `by-type <type>` - 観察タイプで検索
- `timeline --anchor <ID>` - 指定IDの前後タイムラインを取得
- `timeline --query <query>` - クエリから自動でアンカーを検索してタイムライン取得
- `observation <ID>` - 観察を単一取得
- `recent` - 最近のコンテキストを取得
- `session <ID>` - セッション情報を取得
- `prompt <ID>` - プロンプトを取得
- `help` - API仕様を表示

### コマンドライン

```bash
SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py"

# 検索（observations）
python3 $SCRIPT search "<query>" [--limit N] [--project NAME]

# 検索（sessions/prompts）
python3 $SCRIPT search "<query>" --type sessions

# concept検索
python3 $SCRIPT by-concept "<concept>" [--limit N] [--project NAME]

# ファイルパス検索
python3 $SCRIPT by-file "<path>" [--limit N] [--project NAME]

# 観察タイプ検索
python3 $SCRIPT by-type "<type>" [--limit N] [--project NAME]

# タイムライン（アンカーID指定）
python3 $SCRIPT timeline --anchor <ID> [--before N] [--after N] [--project NAME]

# タイムライン（クエリ指定）
python3 $SCRIPT timeline --query "<query>" [--mode MODE] [--before N] [--after N] [--project NAME]

# 観察取得
python3 $SCRIPT observation <ID>

# 最近のコンテキスト
python3 $SCRIPT recent [--project NAME] [--limit N]

# セッション・プロンプト取得
python3 $SCRIPT session <ID>
python3 $SCRIPT prompt <ID>
```

### オプション詳細

#### search

| オプション | 説明 | デフォルト |
|---|---|---|
| `--limit`, `-l` | 結果件数 | 20 |
| `--project`, `-p` | プロジェクト名フィルタ | なし |
| `--type`, `-t` | 検索タイプ（observations/sessions/prompts） | observations |

#### by-concept / by-file / by-type

| オプション | 説明 | デフォルト |
|---|---|---|
| `--limit`, `-l` | 結果件数 | 10 |
| `--project`, `-p` | プロジェクト名フィルタ | なし |

#### timeline

| オプション | 説明 | デフォルト |
|---|---|---|
| `--anchor`, `-a` | アンカーポイント（観察ID, セッションID `S123`, ISO timestamp） | なし |
| `--query`, `-q` | アンカー自動検索クエリ | なし |
| `--mode`, `-m` | 検索モード（auto/observations/sessions） | auto |
| `--before`, `-b` | アンカー前の深度 | 10 |
| `--after`, `-A` | アンカー後の深度 | 10 |
| `--project`, `-p` | プロジェクト名フィルタ | なし |

#### recent

| オプション | 説明 | デフォルト |
|---|---|---|
| `--project`, `-p` | プロジェクト名 | なし |
| `--limit`, `-l` | セッション数 | 3 |

## HTTP API エンドポイント一覧

### 検索系

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/api/search/observations?query=...` | GET | observations検索 |
| `/api/search/sessions?query=...` | GET | sessions検索 |
| `/api/search/prompts?query=...` | GET | prompts検索 |
| `/api/search/by-concept?concept=...` | GET | conceptタグ検索 |
| `/api/search/by-file?filePath=...` | GET | ファイルパス検索 |
| `/api/search/by-type?type=...` | GET | 観察タイプ検索 |

### タイムライン系

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/api/context/timeline?anchor=...` | GET | アンカー指定タイムライン |
| `/api/timeline/by-query?query=...` | GET | クエリ指定タイムライン |

### 個別取得系

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/api/observation/{id}` | GET | 観察の単一取得 |
| `/api/session/{id}` | GET | セッション取得 |
| `/api/prompt/{id}` | GET | プロンプト取得 |

### コンテキスト系

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/api/context/recent` | GET | 最近のコンテキスト |
| `/api/search/help` | GET | API仕様 |
