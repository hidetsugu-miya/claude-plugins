---
name: claude-mem-reference-step
description: 永続メモリの検索・取得手順。検索からタイムライン・観察取得までのフローを提供。
---

# claude-mem 利用手順

## 概要

claude-memの永続メモリを検索・取得するスキル。MCPツールを使用して過去のセッション情報、観察、タイムラインを参照する。

## いつ使うか

- 過去のセッションで行った作業を確認したいとき
- 「以前どうやって解決したか」を調べたいとき
- 特定のトピックに関する過去の観察・決定を検索したいとき

## 3レイヤーワークフロー（必須）

コンテキスト消費を最小化するため、必ずこの順序で段階的に絞り込む。

### 1. 検索（インデックス取得）

IDとタイトルのみ返却される（1件あたり約50-100トークン）。

```text
mcp__plugin_claude-mem_mcp-search__search(query="<検索語>", limit=10)
```

パラメータ: `query`(必須), `limit`, `project`, `type`, `obs_type`, `dateStart`, `dateEnd`, `offset`, `orderBy`

### 2. タイムライン（前後関係の確認）

検索結果から気になるIDの前後コンテキストを取得。

```text
mcp__plugin_claude-mem_mcp-search__timeline(anchor=<ID>)
```

パラメータ: `anchor`(ID) または `query`(自動検索), `depth_before`, `depth_after`, `project`

### 3. 観察の詳細取得（フィルタ済みIDのみ）

必要なIDだけを指定してフル詳細を取得。**フィルタリングなしに全件取得しないこと。**

```text
mcp__plugin_claude-mem_mcp-search__get_observations(ids=[<ID1>, <ID2>])
```

パラメータ: `ids`(必須), `orderBy`, `limit`, `project`

## メモリの保存

重要な情報を記憶させたいときに使用。

```text
mcp__plugin_claude-mem_mcp-search__save_memory(text="<記憶内容>", title="<タイトル>", project="<プロジェクト名>")
```

コマンドの詳細・CLIオプションは `claude-mem-reference-reference` スキルを参照。
