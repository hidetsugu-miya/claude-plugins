---
name: claude-mem-reference-step
description: 永続メモリの検索・取得手順。検索からタイムライン・観察取得までのフローを提供。
---

# claude-mem 利用手順

## 概要

claude-memのWorker HTTP API（localhost:37777）を使用して永続メモリを検索・取得するスキル。過去のセッション情報、観察、タイムラインの参照に使用する。

## いつ使うか

- 過去のセッションで行った作業を確認したいとき
- 「以前どうやって解決したか」を調べたいとき
- 特定のトピックに関する過去の観察・決定を検索したいとき

## 3レイヤーワークフロー（必須）

コンテキスト消費を最小化するため、必ずこの順序で段階的に絞り込む。

### 1. 検索（インデックス取得）

IDとタイトルのみ返却される（1件あたり約50-100トークン）。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py search "<検索語>" --limit 10
```

パラメータ: `--limit`, `--project`, `--type`（observations/sessions/prompts）

### 2. タイムラインで前後関係を確認

検索結果のIDを使ってアンカー指定し、前後コンテキストを取得。

```bash
# アンカーID指定
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py timeline --anchor <ID>

# またはクエリで自動検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py timeline --query "<検索語>"
```

パラメータ: `--anchor`, `--query`, `--mode`（auto/observations/sessions）, `--before`, `--after`, `--project`

### 3. 必要な観察の詳細を取得

必要なIDだけを指定してフル詳細を取得。**フィルタリングなしに全件取得しないこと。**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py observation <ID>
```

## 追加の検索手段

```bash
# conceptタグで検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py by-concept "<concept>"

# ファイルパスで検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py by-file "<path>"

# 観察タイプで検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py by-type "<type>"
```

コマンドの詳細・オプションは `claude-mem-reference-reference` スキルを参照。
