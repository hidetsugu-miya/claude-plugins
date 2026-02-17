#!/bin/bash
# Playwright MCP Server を HTTPモードで起動
# 自動的に空きポートを探し、JSON形式でポート情報を返す

AVAILABLE_PORTS=(8931 8932 8933)
PID_DIR="/tmp/playwright-mcp"
mkdir -p "$PID_DIR"

# 空きポートを探す
SELECTED_PORT=""
for PORT in "${AVAILABLE_PORTS[@]}"; do
    if ! lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        SELECTED_PORT=$PORT
        break
    fi
done

# 全て使用中の場合は8931を停止して再利用
if [ -z "$SELECTED_PORT" ]; then
    PID=$(lsof -ti :8931)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
    SELECTED_PORT=8931
    STATUS="reused"
else
    STATUS="started"
fi

# ログファイルにリダイレクト
LOG_FILE="/tmp/playwright_${SELECTED_PORT}.log"
echo "Starting Playwright MCP Server on port $SELECTED_PORT..." > "$LOG_FILE"
echo "Press Ctrl+C to stop" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Server URL: http://localhost:$SELECTED_PORT/mcp" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# --shared-browser-context: HTTP MCPサーバーモードで複数クライアントからの接続を処理
# --isolated: 各サーバーインスタンスが独立したブラウザプロファイルを使用（複数サーバー起動時に必須）
npx @playwright/mcp@latest --port "$SELECTED_PORT" --shared-browser-context --isolated >> "$LOG_FILE" 2>&1 &
echo $! > "${PID_DIR}/playwright_${SELECTED_PORT}.pid"

# サーバーが起動するまで待機（ポートがリッスン状態になるまで）
for i in {1..10}; do
    if lsof -Pi :$SELECTED_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# JSON形式で情報を出力（stderr経由でログ、stdout経由でJSON）
echo "{\"port\": $SELECTED_PORT, \"url\": \"http://localhost:$SELECTED_PORT/mcp\", \"status\": \"$STATUS\"}"