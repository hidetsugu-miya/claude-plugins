#!/bin/bash
# CocoIndex LiveUpdater をセッション終了時に停止する。
# 失敗してもセッション終了を妨げない（常に exit 0）。

PID_DIR="$HOME/.claude/tmp"

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
PROJECT_NAME=$(basename "$PROJECT_DIR")
SANITIZED=$(echo "$PROJECT_NAME" | sed 's/[^a-zA-Z0-9]/_/g')

PID_FILE="${PID_DIR}/.pid_${SANITIZED}"

# PIDファイルがなければ何もしない
if [[ ! -f "$PID_FILE" ]]; then
  exit 0
fi

PID=$(cat "$PID_FILE" 2>/dev/null || echo "")

# PIDが取得できなければクリーンアップのみ
if [[ -z "$PID" ]]; then
  rm -f "$PID_FILE"
  exit 0
fi

# プロセスが生きていれば SIGTERM 送信
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID" 2>/dev/null || true
fi

# PIDファイル削除
rm -f "$PID_FILE"

exit 0
