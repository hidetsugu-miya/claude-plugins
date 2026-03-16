#!/bin/bash
# CocoIndex LiveUpdater をセッション終了時に停止する。
# 失敗してもセッション終了を妨げない（常に exit 0）。

PID_DIR="$HOME/.claude/tmp"

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
PROJECT_NAME=$(basename "$PROJECT_DIR")
SANITIZED=$(echo "$PROJECT_NAME" | sed 's/[^a-zA-Z0-9]/_/g')

PID_FILE="${PID_DIR}/.pid_${SANITIZED}"

# --- ヘルパー: main.py プロセスか検証してから kill ---
safe_kill() {
  local pid="$1"
  if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
    return 1
  fi
  # PID再利用対策: 対象が実際に main.py であることを検証
  local cmdline
  cmdline=$(ps -p "$pid" -o args= 2>/dev/null || echo "")
  if [[ "$cmdline" == *"main.py"*"--name ${SANITIZED}"*"--live"* ]]; then
    kill "$pid" 2>/dev/null || true
    return 0
  fi
  return 1
}

# --- 1. PIDファイルベースの停止 ---
if [[ -f "$PID_FILE" ]]; then
  PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
  safe_kill "$PID"
  rm -f "$PID_FILE"
fi

# --- 2. pgrep フォールバック（PIDファイル欠損・異常終了対策） ---
REMAINING_PIDS=$(pgrep -f "main.py.*--name ${SANITIZED} --live" 2>/dev/null || true)
if [[ -n "$REMAINING_PIDS" ]]; then
  for pid in $REMAINING_PIDS; do
    safe_kill "$pid"
  done
fi

# --- VACUUM 実行（bloat 防止） ---
# LiveUpdater の UPSERT で蓄積した dead tuple を再利用可能にする
CONTAINER_NAME="cocoindex"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
  docker exec "$CONTAINER_NAME" psql -U postgres -d postgres -c "VACUUM;" 2>/dev/null || true
fi

exit 0
