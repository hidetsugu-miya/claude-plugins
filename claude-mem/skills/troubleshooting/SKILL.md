---
name: troubleshooting
description: claude-memのトラブルシューティング。Chromaサーバー接続エラーやGemini API問題の解決手順。
user-invocable: false
---

# claude-mem トラブルシューティング

## Chromaサーバー接続エラー

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

## Gemini API バージョンの既知の問題

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
