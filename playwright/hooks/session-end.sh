#!/bin/bash
# Playwright MCP Server をセッション終了時に停止する。
# プロジェクト単位でPIDを管理し、自プロジェクトのサーバーのみ停止する。
# npxが子プロセスとしてnodeを起動するため、子プロセスも含めて停止する。
# 失敗してもセッション終了を妨げない（常に exit 0）。

# hookのstdin JSONからcwdを取得（CLAUDE_PROJECT_DIRのフォールバック）
INPUT=$(cat)
CWD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null)
PROJECT_DIR="${CWD:-${CLAUDE_PROJECT_DIR:-}}"

if [[ -z "$PROJECT_DIR" ]]; then
  exit 0
fi

PID_DIR="${PROJECT_DIR}/tmp/playwright"
PID_FILE="${PID_DIR}/server.pid"
PORT_FILE="${PID_DIR}/server.port"

[[ -f "$PID_FILE" ]] || exit 0

PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
rm -f "$PID_FILE" "$PORT_FILE"

kill_tree() {
  local pid=$1
  # 子プロセスを先に停止
  for child in $(pgrep -P "$pid" 2>/dev/null); do
    kill_tree "$child"
  done
  kill "$pid" 2>/dev/null || true
}

if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
  kill_tree "$PID"
fi

exit 0
