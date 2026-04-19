---
name: todoist-login
description: Todoist MCPへのOAuth 2.1認証手順。mcp-remote経由でブラウザ認証し、トークンを保存する。
---

# Todoist MCP ログイン

## 入力

$ARGUMENTS

## 手順

### 1. ログイン実行

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/todoist_cli.py login
```

mcp-remoteが自動でブラウザを開き、Todoistの認証画面に遷移する。

### 2. ユーザーへの案内

ユーザーに対しては **認証URLを提示せず**、以下のみを伝える:

- 「ブラウザが開きますので、Todoistアカウントで認証してください」

**禁止事項**:
- エージェントが認証URLをユーザーに貼り付けて「このURLをブラウザで開いてください」と依頼すること
- コールバックURLのコピー＆ペーストを依頼すること

mcp-remoteが OAuth 2.1 認証を処理し、認証完了後に自動でトークンを `~/.mcp-auth/` に保存する。

### 3. ログイン確認

ターミナルに「Login successful!」と表示されれば認証完了。

### トラブルシューティング

認証エラーが発生した場合:

```bash
# 認証キャッシュをクリアして再認証
rm -rf ~/.mcp-auth/
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/todoist_cli.py login
```

## 注意事項

- ヘッドレス環境（Dockerコンテナ・CI等）ではブラウザが自動起動しないため、デスクトップ環境で実行すること
- ヘッドレス環境で実行された場合も、エージェントは認証URLをユーザーに転送・提示しない

## 出力

認証結果を報告する:
- 認証状態（成功/失敗）
- サーバー情報
