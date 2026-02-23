---
name: figma-reference
description: Figmaスキルのセットアップ・コマンド一覧・オプションのリファレンス。
---

# Figma リファレンス

## セットアップ

1. `pip3 install requests`
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py login` でOAuth認証（初回はクライアント登録も自動実行）

## コマンド一覧

```bash
# ログイン（OAuth PKCE認証）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py login

# ログアウト
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py logout

# 認証状態確認
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py status

# ツール一覧を表示
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py tools

# デザインコンテキスト取得（UIコード生成）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py call get_design_context --arg nodeId="<ID>"

# コード生成オプション付き
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py call get_design_context --arg nodeId="<ID>" --arg forceCodeGen=true --arg dirForAssetWrites="/tmp/figma_assets"

# スクリーンショットを生成
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py call get_screenshot --arg nodeId="<ID>"
```

## オプション

- `--debug` - デバッグログを有効化
- `--arg key=value` - ツール引数（複数指定可）

## 引数の型変換

`--arg` の値は自動的に型変換される:
- `true` / `false` → bool
- 数値文字列 → int / float
- JSON文字列 → パース結果
- その他 → 文字列

## 注意事項

- 初回利用時は `login` でOAuth認証が必要（ブラウザが開く）
- Figmaデスクトップアプリは不要（リモートMCPサーバーに接続）
- 生成されるReact+Tailwindコードは、プロジェクトの技術スタックに合わせて変換が必要
