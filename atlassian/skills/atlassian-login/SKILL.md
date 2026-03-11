---
name: atlassian-login
description: Atlassian MCPへのOAuth 2.1認証手順。mcp-remote経由でブラウザ認証し、トークンを保存する。
---

# Atlassian MCP ログイン

## 入力

$ARGUMENTS

## 手順

### 1. ログイン実行

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/atlassian_cli.py login
```

**初回はブラウザが開きます。ユーザーにAtlassianアカウントの認証を依頼してください。**

mcp-remoteが自動でOAuth 2.1認証を処理します。ブラウザでAtlassianの認証ページが表示され、ユーザーが認証を完了するとトークンが `~/.mcp-auth/` に自動保存されます。

### 2. ログイン確認

「Login successful!」と表示されれば認証完了。

### トラブルシューティング

認証エラーが発生した場合:

```bash
# 認証キャッシュをクリアして再認証
rm -rf ~/.mcp-auth/
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/atlassian_cli.py login
```

## 出力

認証結果を報告する:
- 認証状態（成功/失敗）
- サーバー情報
