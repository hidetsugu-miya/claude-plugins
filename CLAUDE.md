# claude-plugins

Claude Code用のカスタムプラグインリポジトリ。

## プラグイン新設時

- README.mdにプラグインの説明とインストールコマンドを追加すること
- `.claude-plugin/plugin.json` にバージョン情報を含めること
- `.claude-plugin/marketplace.json` の `plugins` 配列にエントリを追加すること
- スクリプトを含むプラグインは、実際にコマンドを実行して動作確認すること（サーバー起動・主要コマンドの実行など）

## プラグイン変更時

- `.claude-plugin/plugin.json` のバージョンを更新すること（セマンティックバージョニングに従う）
- `.claude-plugin/marketplace.json` のバージョンも同期すること
