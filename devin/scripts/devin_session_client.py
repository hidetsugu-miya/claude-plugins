#!/usr/bin/env python3
"""
Devin Session API Client

Devin REST API経由でセッションの作成・状態取得・メッセージ送信を行う。
"""

import time
import requests
from typing import Any, Dict, List, Optional


class DevinSessionError(Exception):
    """Devin Session API エラー"""
    pass


class DevinSessionClient:
    """Devin Session API クライアント"""

    BASE_URL = "https://api.devin.ai"

    def __init__(self, api_key: str, debug: bool = False):
        """
        Args:
            api_key: Devin API Key (Bearer Token)
            debug: デバッグログを出力するか
        """
        if not api_key:
            raise DevinSessionError("API key is required. Set DEVIN_API_KEY environment variable.")
        self.api_key = api_key
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _log(self, message: str):
        if self.debug:
            print(f"[DEBUG] {message}")

    def _request(self, method: str, path: str, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """APIリクエストを送信"""
        url = f"{self.BASE_URL}{path}"
        self._log(f"{method} {url} {json_data}")

        try:
            response = self.session.request(method, url, json=json_data, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            body = ""
            try:
                body = e.response.json()
            except Exception:
                body = e.response.text
            raise DevinSessionError(f"HTTP {e.response.status_code}: {body}") from e
        except requests.exceptions.RequestException as e:
            raise DevinSessionError(f"Request failed: {e}") from e

        if not response.content:
            return {}

        result = response.json()
        self._log(f"Response: {result}")
        return result

    def create_session(
        self,
        prompt: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        idempotent: bool = False,
    ) -> Dict[str, Any]:
        """
        セッションを作成

        Args:
            prompt: タスク指示（必須）
            title: セッションタイトル
            tags: タグリスト
            idempotent: べき等モード

        Returns:
            {"session_id": str, "url": str, "is_new_session": bool}
        """
        body: Dict[str, Any] = {"prompt": prompt}
        if title:
            body["title"] = title
        if tags:
            body["tags"] = tags
        if idempotent:
            body["idempotent"] = True

        return self._request("POST", "/v1/sessions", body)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        セッション状態を取得

        Args:
            session_id: セッションID

        Returns:
            セッション詳細（status_enum, messages, pull_request等）
        """
        return self._request("GET", f"/v1/sessions/{session_id}")

    def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        セッションにメッセージを送信

        Args:
            session_id: セッションID
            message: メッセージ本文

        Returns:
            レスポンス
        """
        return self._request("POST", f"/v1/sessions/{session_id}/message", {"message": message})

    def wait_for_completion(
        self,
        session_id: str,
        interval: int = 15,
        timeout: int = 600,
    ) -> Dict[str, Any]:
        """
        ポーリングでセッション完了を待機

        Args:
            session_id: セッションID
            interval: ポーリング間隔秒数
            timeout: タイムアウト秒数

        Returns:
            最終セッション状態

        Raises:
            DevinSessionError: タイムアウト時
        """
        terminal_states = {"finished", "expired"}
        elapsed = 0

        while elapsed < timeout:
            result = self.get_session(session_id)
            status = result.get("status_enum", "")
            print(f"[{elapsed}s] Status: {status}")

            if status in terminal_states:
                return result

            time.sleep(interval)
            elapsed += interval

        raise DevinSessionError(f"Timeout after {timeout}s. Last status: {status}")
