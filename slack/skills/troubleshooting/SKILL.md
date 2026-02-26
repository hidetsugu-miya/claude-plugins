---
name: troubleshooting
description: Slack MCPの既知の問題と対処法のリファレンス。
user-invocable: false
---

# Slack MCP トラブルシューティング

| 症状 | 対処 |
|---|---|
| `No workspace configured` | `login` でワークスペースを追加 |
| `Token refresh failed` | `login` で再認証 |
| `HTTP request failed` | ネットワーク接続を確認。`--debug` で詳細ログを出力 |
| `MCP Error` | ツール名・引数を確認。`tools` で利用可能なツール一覧を確認 |
| ポート3118が使用中 | `login` 実行前に他のSlack MCP認証プロセスを終了 |
