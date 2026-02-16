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

## 手順

### 1. メモリを検索

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py search "<query>" --limit 10
```

### 2. タイムラインで前後関係を確認

```bash
# 検索結果のIDを使ってアンカー指定
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py timeline --anchor <ID>

# または直接クエリで検索
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py timeline --query "<query>"
```

### 3. 必要な観察の詳細を取得

```bash
# 単一
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py observation <ID>

# 複数バッチ
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/memory-search.py observations <ID1> <ID2> <ID3>
```

コマンドの詳細・オプションは `claude-mem-reference-reference` スキルを参照。
