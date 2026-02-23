#!/usr/bin/env python3
"""
Figma MCP Token Store

トークンの永続化・リフレッシュを管理する。
動的クライアント登録情報も保存。
保存先: ~/.config/figma-mcp/config.json (パーミッション 0600)
単一アカウントモデル（マルチワークスペース不要）。
"""

import json
import os
import time
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError


TOKEN_URL = "https://api.figma.com/v1/oauth/token"
CONFIG_DIR = os.path.expanduser("~/.config/figma-mcp")
STORE_PATH = os.path.join(CONFIG_DIR, "config.json")
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
            return {"client_credentials": None, "auth": None}
        try:
            with open(STORE_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"client_credentials": None, "auth": None}

    def _save(self):
        """ストアファイルに保存 (パーミッション 0600)"""
        os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
        with open(STORE_PATH, "w") as f:
            json.dump(self._data, f, indent=2)
        os.chmod(STORE_PATH, 0o600)

    # --- クライアント登録情報 ---

    def get_client_credentials(self) -> Optional[Dict[str, Any]]:
        """登録済みクライアント情報を取得"""
        return self._data.get("client_credentials")

    def save_client_credentials(self, client_id: str, client_secret: str):
        """動的クライアント登録結果を保存"""
        self._data["client_credentials"] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "registered_at": int(time.time()),
        }
        self._save()

    # --- 認証トークン ---

    def save_auth(self, access_token: str, refresh_token: str,
                  expires_in: int, scope: str):
        """認証トークンを保存"""
        self._data["auth"] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(time.time()) + expires_in,
            "scope": scope,
        }
        self._save()

    def remove_auth(self):
        """認証トークンを削除"""
        self._data["auth"] = None
        self._save()

    def is_authenticated(self) -> bool:
        """認証済みかどうか"""
        auth = self._data.get("auth")
        return auth is not None and bool(auth.get("access_token"))

    def get_auth(self) -> Optional[Dict[str, Any]]:
        """認証情報を取得"""
        return self._data.get("auth")

    def get_valid_token(self) -> str:
        """有効なアクセストークンを取得（必要なら自動リフレッシュ）"""
        auth = self._data.get("auth")
        if not auth or not auth.get("access_token"):
            raise TokenStoreError("Not authenticated. Run 'login' first.")

        expires_at = auth.get("expires_at", 0)
        if time.time() < expires_at - REFRESH_MARGIN_SECONDS:
            return auth["access_token"]

        # リフレッシュ実行
        return self._refresh_token()

    def _refresh_token(self) -> str:
        """トークンをリフレッシュ"""
        auth = self._data.get("auth")
        if not auth:
            raise TokenStoreError("Not authenticated. Run 'login' first.")

        refresh_token = auth.get("refresh_token")
        if not refresh_token:
            raise TokenStoreError("No refresh token. Run 'login' again.")

        creds = self.get_client_credentials()
        if not creds:
            raise TokenStoreError(
                "No client credentials. Run 'login' again."
            )

        data = urlencode({
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
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

        if "error" in result:
            error = result.get("error", "unknown")
            desc = result.get("error_description", "")
            raise TokenStoreError(
                f"Token refresh failed: {error} {desc}. Run 'login' again."
            )

        auth["access_token"] = result["access_token"]
        if "refresh_token" in result:
            auth["refresh_token"] = result["refresh_token"]
        auth["expires_at"] = int(time.time()) + result.get("expires_in", 3600)
        self._save()

        return auth["access_token"]
