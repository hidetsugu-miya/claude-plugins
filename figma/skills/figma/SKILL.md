---
name: figma
description: Figmaデザインファイルの取得、ノード情報の参照、コンポーネント・スタイルの確認。デザインからコード実装が必要な場合に使用。
---

# Figma Dev Mode MCP

Figmaデスクトップアプリと連携してデザインからコードを生成するスキル。SSEモードで常時接続。

## セットアップ

- Figmaデスクトップアプリがインストール・起動済みであること
- `pip3 install sseclient-py requests`

## ノードIDの取得方法

FigmaのURLからノードIDを抽出：
- URL: `https://www.figma.com/design/.../...?node-id=21146-88120`
- ノードID: `21146:88120`（ハイフンをコロンに変換）

## コマンド

```bash
# ツール一覧を表示
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py list-tools

# UIコードを生成（推奨）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py get_design_context --node-id "<ID>"

# コード生成を強制 + アセット出力先を指定
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py get_design_context --node-id "<ID>" --force-code --dir-for-asset-writes "/tmp/figma_assets"

# スクリーンショットを生成
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py get_screenshot --node-id "<ID>"

# 変数定義を取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py get_variable_defs --node-id "<ID>"

# メタデータを取得（XML形式）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py get_metadata --node-id "<ID>"
```

### オプション

- `--server <URL>` - サーバーURL（デフォルト: `http://127.0.0.1:3845`）
- `--debug` - デバッグログを有効化
- `--force-code` - コード生成を強制
- `--dir-for-asset-writes <PATH>` - アセット出力ディレクトリ
- `--client-languages <LANGS>` - 使用言語（例: `typescript,javascript`）
- `--client-frameworks <FRAMEWORKS>` - 使用フレームワーク（例: `react,vue`）

## 注意事項

- 対象ファイルをFigmaデスクトップアプリのアクティブタブで開いている必要あり
- 生成されるReact+Tailwindコードは、プロジェクトの技術スタックに合わせて変換が必要
