#!/bin/bash
# CocoIndex ヘルスチェック: PostgreSQL接続 + 現プロジェクトのインデックス確認
#
# 使い方: bash check.sh
# 終了コード: 0=正常, 1=異常あり
#
# CLAUDE_PROJECT_DIR からプロジェクト名・テーブル名を自動計算する。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$PLUGIN_ROOT/templates"

CONFIG_DIR="$HOME/.config/cocoindex"
COMPOSE_DIR="$CONFIG_DIR"
CONTAINER_NAME="cocoindex"

# --- 0. Auto-provision config ---
mkdir -p "$CONFIG_DIR"
if [[ ! -f "$CONFIG_DIR/compose.yml" ]] && [[ -f "$TEMPLATES_DIR/compose.yml" ]]; then
  cp "$TEMPLATES_DIR/compose.yml" "$CONFIG_DIR/compose.yml"
  echo "INFO: compose.yml をテンプレートからコピーしました"
fi
if [[ ! -f "$CONFIG_DIR/.env" ]] && [[ -f "$TEMPLATES_DIR/.env.example" ]]; then
  cp "$TEMPLATES_DIR/.env.example" "$CONFIG_DIR/.env"
  echo "WARN: .env をテンプレートからコピーしました。VOYAGE_API_KEY を設定してください: $CONFIG_DIR/.env"
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
PROJECT_NAME=$(basename "$PROJECT_DIR")
# derive_flow_name と同じロジック: 英数字以外を _ に置換
SANITIZED=$(echo "$PROJECT_NAME" | sed 's/[^a-zA-Z0-9]/_/g')
TABLE_NAME="codeindex_${SANITIZED}__code_chunks"
TABLE_NAME=$(echo "$TABLE_NAME" | tr '[:upper:]' '[:lower:]')

HAS_ERROR=0

# --- 1. PostgreSQL接続確認（docker exec経由） ---
check_pg() {
  docker exec "$CONTAINER_NAME" pg_isready -U postgres >/dev/null 2>&1
}

if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$" && check_pg; then
  echo "OK: PostgreSQL is running (container: ${CONTAINER_NAME})"
else
  echo "NG: PostgreSQL is not reachable (container: ${CONTAINER_NAME})"
  # docker compose upを試みる
  if [[ -f "$COMPOSE_DIR/compose.yml" ]]; then
    echo "    Starting via docker compose..."
    (cd "$COMPOSE_DIR" && docker compose up -d) >/dev/null 2>&1 || true
    for i in $(seq 1 15); do
      if check_pg; then
        echo "OK: PostgreSQL started successfully"
        break
      fi
      sleep 1
    done
    if ! check_pg; then
      echo "NG: Failed to start PostgreSQL"
      HAS_ERROR=1
    fi
  else
    echo "    compose.yml not found at $COMPOSE_DIR"
    HAS_ERROR=1
  fi
fi

# --- 2. 現プロジェクトのインデックス確認 ---
if check_pg; then
  echo ""
  echo "Project: ${PROJECT_NAME}"
  echo "Table:   ${TABLE_NAME}"

  EXISTS=$(docker exec "$CONTAINER_NAME" psql -U postgres -t -A -c \
    "SELECT EXISTS(SELECT 1 FROM pg_tables WHERE tablename = '${TABLE_NAME}');" 2>/dev/null || echo "f")

  if [[ "$EXISTS" == "t" ]]; then
    COUNT=$(docker exec "$CONTAINER_NAME" psql -U postgres -t -A -c \
      "SELECT count(*) FROM \"${TABLE_NAME}\";" 2>/dev/null || echo "?")
    echo "Index:   OK ($COUNT chunks)"
  else
    echo "Index:   NOT FOUND (run setup to build)"
    HAS_ERROR=1
  fi
fi

exit $HAS_ERROR
