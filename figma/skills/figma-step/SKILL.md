---
name: figma-step
description: Figmaデザインファイルからコード生成する手順。ノードID特定からコマンド実行まで。
---

# Figma 利用手順

## 概要

Figma MCPサーバーと連携してデザインからコードを生成するスキル。OAuth認証でリモートサーバーに接続。

## 前提

Figma MCPへのログインが必要。未認証の場合は `figma-login-step` スキルを実行。

## 手順

### 1. ノードIDを特定

FigmaのURLからノードIDを抽出:
- URL: `https://www.figma.com/design/.../...?node-id=21146-88120`
- ノードID: `21146:88120`（ハイフンをコロンに変換）

### 2. コマンドを実行

```bash
# UIコードを生成（推奨）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py call get_design_context --arg nodeId="<ID>"

# コード生成オプション付き
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/figma_cli.py call get_design_context --arg nodeId="<ID>" --arg forceCodeGen=true --arg dirForAssetWrites="/tmp/figma_assets"
```

コマンドの詳細・オプションは `figma-reference` スキルを参照。
