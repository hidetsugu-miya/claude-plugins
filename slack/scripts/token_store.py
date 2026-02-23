#!/usr/bin/env python3
"""
Slack MCP Token Store

トークンの永続化・リフレッシュを管理する。
保存先: ~/.config/slack-mcp/workspaces.json (パーミッション 0600)
複数ワークスペース対応: {team_name}-{team_id} をキーに管理
"""

import json
import os
import time
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError


CLIENT_ID = "1601185624273.8899143856786"
TOKEN_URL = "https://slack.com/api/oauth.v2.user.access"
CONFIG_DIR = os.path.expanduser("~/.config/slack-mcp")
STORE_PATH = os.path.join(CONFIG_DIR, "workspaces.json")
REFRESH_MARGIN_SECONDS = 300  # 有効期限5分前にリフレッシュ


class TokenStoreError(Exception):
    """トークンストアエラー"""
    pass


class TokenStore:
    """トークン永続化・リフレッシュ管理"""

    def __init__(self):
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        """ストアファイルを読み込み"""
        if not os.path.exists(STORE_PATH):
            return {"workspaces": {}, "default_workspace": None}
        try:
            with open(STORE_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"workspaces": {}, "default_workspace": None}

    def _save(self):
        """ストアファイルに保存 (パーミッション 0600)"""
        os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
        with open(STORE_PATH, "w") as f:
            json.dump(self._data, f, indent=2)
        os.chmod(STORE_PATH, 0o600)

    @staticmethod
    def make_workspace_key(team_name: str, team_id: str) -> str:
        """ワークスペースキーを生成"""
        safe_name = team_name.lower().replace(" ", "-")
        return f"{safe_name}-{team_id}"

    def save_workspace(self, team_id: str, team_name: str,
                       access_token: str, refresh_token: str,
                       expires_in: int, scope: str):
        """ワークスペースのトークン情報を保存"""
        key = self.make_workspace_key(team_name, team_id)
        self._data["workspaces"][key] = {
            "team_id": team_id,
            "team_name": team_name,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(time.time()) + expires_in,
            "scope": scope,
        }
        # デフォルトが未設定なら設定
        if not self._data.get("default_workspace"):
            self._data["default_workspace"] = key
        self._save()
        return key

    def remove_workspace(self, workspace_key: str) -> bool:
        """ワークスペースのトークンを削除"""
        if workspace_key not in self._data["workspaces"]:
            return False
        del self._data["workspaces"][workspace_key]
        if self._data.get("default_workspace") == workspace_key:
            keys = list(self._data["workspaces"].keys())
            self._data["default_workspace"] = keys[0] if keys else None
        self._save()
        return True

    def set_default(self, workspace_key: str) -> bool:
        """デフォルトワークスペースを設定"""
        if workspace_key not in self._data["workspaces"]:
            return False
        self._data["default_workspace"] = workspace_key
        self._save()
        return True

    def list_workspaces(self) -> Dict[str, Dict[str, Any]]:
        """保存済みワークスペース一覧"""
        return self._data.get("workspaces", {})

    def get_default_key(self) -> Optional[str]:
        """デフォルトワークスペースキーを取得"""
        return self._data.get("default_workspace")

    def resolve_workspace_key(self, workspace: Optional[str] = None) -> str:
        """ワークスペースキーを解決（指定なしならデフォルト）"""
        if workspace:
            if workspace in self._data["workspaces"]:
                return workspace
            # 部分一致検索
            for key in self._data["workspaces"]:
                if workspace.lower() in key.lower():
                    return key
            raise TokenStoreError(f"Workspace not found: {workspace}")
        default = self.get_default_key()
        if not default or default not in self._data["workspaces"]:
            raise TokenStoreError("No workspace configured. Run 'login' first.")
        return default

    def get_valid_token(self, workspace: Optional[str] = None) -> str:
        """有効なアクセストークンを取得（必要なら自動リフレッシュ）"""
        key = self.resolve_workspace_key(workspace)
        ws = self._data["workspaces"][key]

        expires_at = ws.get("expires_at", 0)
        if time.time() < expires_at - REFRESH_MARGIN_SECONDS:
            return ws["access_token"]

        # リフレッシュ実行
        return self._refresh_token(key)

    def _refresh_token(self, workspace_key: str) -> str:
        """トークンをリフレッシュ"""
        ws = self._data["workspaces"][workspace_key]
        refresh_token = ws.get("refresh_token")
        if not refresh_token:
            raise TokenStoreError(
                f"No refresh token for {workspace_key}. Run 'login' again."
            )

        data = urlencode({
            "client_id": CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }).encode()

        req = Request(TOKEN_URL, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
        except (URLError, HTTPError) as e:
            raise TokenStoreError(f"Token refresh failed: {e}") from e

        if not result.get("ok"):
            error = result.get("error", "unknown")
            raise TokenStoreError(
                f"Token refresh failed: {error}. Run 'login' again."
            )

        ws["access_token"] = result["access_token"]
        ws["refresh_token"] = result["refresh_token"]
        ws["expires_at"] = int(time.time()) + result.get("expires_in", 43200)
        self._save()

        return ws["access_token"]
