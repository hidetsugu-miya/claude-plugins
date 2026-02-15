---
name: rollbar-step
description: Rollbarエラートラッキングの調査手順。URL取得からアイテム詳細、トップエラー確認まで。
---

# Rollbar 利用手順

## 概要

`@rollbar/mcp-server`を使用してRollbarプロジェクトのエラートラッキングデータを取得・管理するスキル。

## 手順

### 1. URLからアイテム詳細を取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py url "<rollbar_url>"
```

### 2. アイテム番号から詳細を取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py item <item_number>
```

### 3. トップエラーを確認

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rollbar.py top [--env <environment>]
```

コマンドの詳細・オプションは `rollbar-reference` スキルを参照。
