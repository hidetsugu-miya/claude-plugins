---
name: context7-reference
description: Context7のコマンド詳細・オプションのリファレンス。
---

# Context7 リファレンス

## 主要コマンド

- `resolve <library_name>` - ライブラリ名からIDを解決
- `docs <library_id> [--topic <topic>] [--tokens <tokens>]` - ライブラリドキュメントを取得

## コマンドライン

```bash
# ライブラリIDを解決
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py resolve <library_name>

# ライブラリドキュメントを取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py docs <library_id> [--topic <topic>] [--tokens <tokens>]
```

## オプション

その他のオプションは `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py --help` を参照。
