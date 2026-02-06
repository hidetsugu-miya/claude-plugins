---
name: cocoindex-guide
description: コードベースのベクトル検索利用ガイド。インデックスの構築・検索フローを提供。自然言語クエリで関連コードのエントリーポイントを発見する。
---

# CocoIndex 利用ガイド

## 概要

コードベースのベクトルインデックスを構築・検索するツール。
自然言語クエリで関連ファイルの**エントリーポイント**を発見する。

プロジェクト名・テーブル名は自動計算される。
しょ
## いつ使うか

- シンボル名もファイル名も不明で、grepキーワードすら推測できない場合
- ドメイン固有の概念（日本語含む）でコードを探したい場合
- 「〇〇の機能はあるか？」という存在確認の初手として

## いつ使わないか

- シンボル名やキーワードが推測できる場合（他のツールの方が効率的）
- 具体的なツール選択は `~/.claude/rules/tool-selection.md` を参照

## 共通情報

- **スクリプト**: `${CLAUDE_PLUGIN_ROOT}/scripts/`
- **ユーザー設定**: `~/.config/cocoindex/`（`.env`, `compose.yml`）
- **DB**: `cocoindex` コンテナ（ポート15432）

## 利用判断

### 1. ヘルスチェック（PostgreSQL + インデックス確認）

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/check.sh
```

以下を一括確認する:
- PostgreSQL接続（停止中なら `docker compose up` を自動試行）
- 現プロジェクトのインデックステーブルの存在とチャンク数

**結果の判断**:
- 全てOK → **必ず `references/search.md` を読んでから**検索を実行する
- Index: NOT FOUND → **必ず `references/setup.md` を読んでから**構築を実行する
- PostgreSQL接続NG → **必ず `references/setup.md` を読んでから**セットアップを実行する

**重要**: スクリプトは `uv run` 経由で実行すること。`python3` で直接実行すると依存パッケージが見つからずエラーになる。

## リファレンス

- **`references/setup.md`** — 初回セットアップ・DB起動・インデックス構築
- **`references/search.md`** — 検索コマンド・結果の判断基準
