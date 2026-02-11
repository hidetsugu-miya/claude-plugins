# claude-plugins

Custom Claude Code plugins by miya.

## Quick Start

マーケットプレイスを登録:

```text
/plugin marketplace add hidetsugu-miya/claude-plugins
```

使いたいプラグインをインストール:

```text
/plugin install cocoindex@hidetsugu-miya
/plugin install context7@hidetsugu-miya
/plugin install rollbar@hidetsugu-miya
/plugin install sentry@hidetsugu-miya
```

インストール後、Claude Codeを再起動してください。

## Plugins

### cocoindex

CocoIndex を使ったコードベースのベクトル検索プラグイン。自然言語クエリで関連コードのエントリーポイントを発見する。

初回セットアップは `/cocoindex-guide` を実行し、`references/setup.md` の手順に従ってください。

### context7

ライブラリの最新ドキュメントを取得するプラグイン。Context7 MCPサーバーを使ってパッケージ名からIDを解決し、バージョン固有のドキュメントを参照する。

使い方は `/context7` を実行してください。

### rollbar

Rollbarのエラートラッキングデータを取得・管理するプラグイン。@rollbar/mcp-serverを使ってアイテム詳細、デプロイ情報、トップエラーの確認・更新を行う。

環境変数 `ROLLBAR_ACCESS_TOKEN` の設定が必要です。使い方は `/rollbar` を実行してください。

### sentry

Sentryのエラートラッキングデータを取得・管理するプラグイン。@sentry/mcp-serverを使ってイシュー詳細、プロジェクト情報、エラー分析を行う。

環境変数 `SENTRY_ACCESS_TOKEN` の設定が必要です。使い方は `/sentry` を実行してください。
