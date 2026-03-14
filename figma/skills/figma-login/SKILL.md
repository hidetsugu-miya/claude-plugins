---
name: figma-login
description: Figma MCPへのOAuth認証手順。ブラウザでFigmaアカウントを認証し、トークンを保存する。
---

# Figma MCP ログイン

## 入力

$ARGUMENTS

## 手順

### 1. 認証URLを取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py login --url-only
```

初回はクライアント登録も自動で実行される。

### 2. ユーザーに認証を依頼

コマンドの出力（認証URL）を **省略せず全文** ユーザーに提示し、以下を依頼する:

1. このURLをブラウザで開いてFigmaアカウントで認証してください
2. 認証後、ブラウザのアドレスバーに `localhost:3119/callback?code=...&state=...` というURLが表示されます（ページ自体はエラーになります）
3. そのURLをコピーして貼り付けてください

**ユーザーからコールバックURLを受け取るまで次に進まないこと。**

### 3. コールバックURLでトークン取得

ユーザーから受け取ったURLを使って実行:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py login --code "<ユーザーが貼り付けたURL>"
```

### 4. ログイン確認

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py status
```

「Status: Authenticated」と表示されれば認証完了。

## 出力

認証結果を報告する:
- 認証状態（成功/失敗）
- スコープ情報
