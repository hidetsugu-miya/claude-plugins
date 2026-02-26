---
name: setup
description: CocoIndexの環境セットアップ手順。初回設定・DB起動・設定ファイルの管理方法。
user-invocable: false
---

# CocoIndex セットアップ

## 共通情報

- **スクリプト**: `${CLAUDE_PLUGIN_ROOT}/scripts/`
- **ユーザー設定**: `~/.config/cocoindex/`（`.env`, `compose.yml`）
- **DB**: `cocoindex` コンテナ（ポート15432）

## 初回セットアップ

`~/.config/cocoindex/` の設定ファイルは、セッション開始時およびヘルスチェック実行時にテンプレートから自動コピーされる。

手動セットアップが必要な場合:

```bash
mkdir -p ~/.config/cocoindex && cp ${CLAUDE_PLUGIN_ROOT}/templates/.env.example ~/.config/cocoindex/.env && cp ${CLAUDE_PLUGIN_ROOT}/templates/compose.yml ~/.config/cocoindex/compose.yml
```

自動・手動いずれの場合も、`~/.config/cocoindex/.env` の `VOYAGE_API_KEY` を設定すること。

## DB起動

```bash
cd ~/.config/cocoindex && docker compose up -d
```

## インデックス再構築

同じ構築コマンドを再実行すればインデックスが更新される。
