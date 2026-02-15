---
name: sentry-step
description: Sentryエラートラッキングの調査手順。URL取得からイシュー検索、AI分析まで。
---

# Sentry 利用手順

## 概要

`@sentry/mcp-server`を使用してSentryプロジェクトのエラートラッキングデータを取得・管理するスキル。

## 手順

### 1. URLからイシュー詳細を取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py url "<sentry_url>"
```

### 2. イシューを検索

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py search "is:unresolved" --org <organization>
```

### 3. AI分析を実行

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sentry.py analyze <issue_id>
```

コマンドの詳細・オプションは `sentry-reference` スキルを参照。
