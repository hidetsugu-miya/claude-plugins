# claude-plugins

Claude Code用のカスタムプラグインリポジトリ。

## プラグイン新設時

- README.mdにプラグインの説明とインストールコマンドを追加すること
- `.claude-plugin/plugin.json` にバージョン情報を含めること
- `.claude-plugin/marketplace.json` の `plugins` 配列にエントリを追加すること
- スクリプトを含むプラグインは、実際にコマンドを実行して動作確認すること（サーバー起動・主要コマンドの実行など）

## 必須: `{plugin}/` 配下を変更したらバージョン更新

`{plugin}/` 配下のファイルを追加・変更・削除する作業には、以下のバージョン更新が含まれる。ファイル変更とバージョン更新は一体であり、バージョン更新なしにプラグインの変更は完了しない。

1. `{plugin}/.claude-plugin/plugin.json` の `version` を更新
2. `.claude-plugin/marketplace.json` の同プラグインの `version` を同期

バージョン判断: 機能追加→マイナー、修正→パッチ、破壊的変更→メジャー
