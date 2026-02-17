---
name: claude-mem-reference-reference
description: claude-mem検索コマンドの詳細・オプションのリファレンス。
---

# claude-mem リファレンス

## 前提条件

- claude-mem Worker（localhost:37777）が起動していること
- Chromaサーバー（localhost:8000）が起動していること（セマンティック検索に必要）

### Chromaサーバーのトラブルシューティング

検索で「Chroma connection failed」エラーが出る場合、Chromaサーバーが起動していない。

Workerは起動時にChromaを自動起動しようとするが、`chromadb` npmパッケージが未インストールの場合は失敗する。Python版chromadbの方が大容量DB（数百MB以上）で安定するため、こちらを推奨。

```bash
# Python版chromadbのインストール（推奨）
uv pip install --system chromadb

# Chromaサーバーの手動起動
chroma run --path ~/.claude-mem/vector-db --host 127.0.0.1 --port 8000

# 動作確認（v2 APIで200が返ればOK）
curl http://localhost:8000/api/v2/heartbeat
```

Node版chromadb（npmパッケージ）は大容量DBでハングすることがあるため非推奨。

## MCPツール

claude-memはMCPツールを提供しており、Claude Codeから直接使用できる。

### search

メモリを検索し、IDとタイトルのインデックスを返却する。

| パラメータ | 説明 | デフォルト |
|---|---|---|
| `query` | 検索クエリ（必須） | - |
| `limit` | 結果件数 | 20 |
| `project` | プロジェクト名フィルタ | なし |
| `type` | 検索タイプ | なし |
| `obs_type` | 観察タイプフィルタ | なし |
| `dateStart` | 開始日フィルタ | なし |
| `dateEnd` | 終了日フィルタ | なし |
| `offset` | 結果オフセット | 0 |
| `orderBy` | ソート順 | なし |

### timeline

指定ポイント周辺のタイムラインを取得する。

| パラメータ | 説明 | デフォルト |
|---|---|---|
| `anchor` | アンカーポイント（観察ID） | なし |
| `query` | 自動検索クエリ（anchor未指定時） | なし |
| `depth_before` | アンカー前の件数 | 10 |
| `depth_after` | アンカー後の件数 | 10 |
| `project` | プロジェクト名フィルタ | なし |

### get_observations

フィルタ済みIDの観察詳細を取得する。

| パラメータ | 説明 | デフォルト |
|---|---|---|
| `ids` | 観察IDの配列（必須） | - |
| `orderBy` | ソート順 | なし |
| `limit` | 件数制限 | なし |
| `project` | プロジェクト名フィルタ | なし |

### save_memory

手動でメモリを保存する。

| パラメータ | 説明 | デフォルト |
|---|---|---|
| `text` | 記憶内容（必須） | - |
| `title` | タイトル | 自動生成 |
| `project` | プロジェクト名 | claude-mem |

## CLIスクリプト（HTTP API）

Worker HTTP APIを直接操作するPythonスクリプト。デバッグや手動確認に使用。

### 主要コマンド

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
