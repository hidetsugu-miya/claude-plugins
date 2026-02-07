---
name: context7
description: ライブラリの最新ドキュメントを取得。パッケージ名からIDを解決し、バージョン固有のドキュメントを参照する際に使用。
---

# Context7 Documentation Skill

最新のライブラリドキュメントを取得するためのContext7スキル。`npx @upstash/context7-mcp@latest` を使用してJSON-RPCでMCPサーバーを呼び出し、npmパッケージやその他のライブラリの公式ドキュメントを直接参照できます。

## 使い方

### コマンドライン

```bash
# ライブラリIDを解決
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py resolve <library_name>

# ライブラリドキュメントを取得
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py docs <library_id> [--topic <topic>] [--tokens <tokens>]
```

## 主要コマンド

- `resolve <library_name>` - ライブラリ名からIDを解決
- `docs <library_id> [--topic <topic>] [--tokens <tokens>]` - ライブラリドキュメントを取得

その他のオプションは `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/context7.py --help` を参照。
