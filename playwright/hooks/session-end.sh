#!/bin/bash
# Playwright MCP Server をセッション終了時に停止する。
# start_server.sh が記録したPIDファイルを参照して停止する。
# npxが子プロセスとしてnodeを起動するため、子プロセスも含めて停止する。
# 失敗してもセッション終了を妨げない（常に exit 0）。

PID_DIR="/tmp/playwright-mcp"
PORTS=(8931 8932 8933)

kill_tree() {
  local pid=$1
  # 子プロセスを先に停止
  for child in $(pgrep -P "$pid" 2>/dev/null); do
    kill_tree "$child"
  done
  kill "$pid" 2>/dev/null || true
}

for PORT in "${PORTS[@]}"; do
  PID_FILE="${PID_DIR}/playwright_${PORT}.pid"

  [[ -f "$PID_FILE" ]] || continue

  PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
  rm -f "$PID_FILE"

  if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
    kill_tree "$PID"
  fi
done

exit 0
