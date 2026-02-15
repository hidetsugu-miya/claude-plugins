---
name: figma-step
description: Figmaデザインファイルからコード生成する手順。ノードID特定からコマンド実行まで。
---

# Figma 利用手順

## 概要

Figmaデスクトップアプリと連携してデザインからコードを生成するスキル。SSEモードで常時接続。

## 手順

### 1. ノードIDを特定

FigmaのURLからノードIDを抽出:
- URL: `https://www.figma.com/design/.../...?node-id=21146-88120`
- ノードID: `21146:88120`（ハイフンをコロンに変換）

### 2. コマンドを実行

```bash
# UIコードを生成（推奨）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py get_design_context --node-id "<ID>"

# コード生成を強制 + アセット出力先を指定
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma.py get_design_context --node-id "<ID>" --force-code --dir-for-asset-writes "/tmp/figma_assets"
```

コマンドの詳細・オプションは `figma-reference` スキルを参照。
