---
name: figma-login
description: Figma MCPへのOAuth認証手順。ブラウザでFigmaアカウントを認証し、トークンを保存する。
---

# Figma MCP ログイン

## 入力

$ARGUMENTS

## 手順

### 1. ログイン実行

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py login
```

初回はクライアント登録も自動で実行される。

実行するとブラウザが自動で開き、`localhost:3119/callback` でコールバックを受信してトークンを保存する。ユーザーには以下を依頼する:

1. 開いたブラウザでFigmaアカウントにログインして認証を許可してください
2. 認証完了後、自動でトークンが保存されます

**「Login successful!」が表示されるまで待機すること。**

### 2. ヘッドレス環境フォールバック

ブラウザが開けない環境（SSH・コンテナ等）では自動でコールバックURL手動入力モードに切り替わる。その場合は表示された認証URLをユーザーに提示し、コールバックURL（`localhost:3119/callback?code=...&state=...`）の貼り付けを依頼する。

ポートフォワード（`-p 3119:3119`）が設定済みであれば、コールバックサーバーが自動で受信する。

### 3. ログイン確認

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py status
```

「Status: Authenticated」と表示されれば認証完了。

## 出力

認証結果を報告する:
- 認証状態（成功/失敗）
- スコープ情報
