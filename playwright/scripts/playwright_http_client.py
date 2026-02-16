#!/usr/bin/env python3
"""
Playwright MCP HTTP Client

HTTPモードで起動したPlaywright MCPサーバーに接続
複数のスクリプトから同じブラウザセッションを共有可能
"""

import requests
import json
import os
import tempfile
from typing import Any, Dict, Optional


class PlaywrightHTTPError(Exception):
    """Playwright HTTP通信エラー"""
    pass


class PlaywrightHTTPClient:
    """Playwright MCP HTTPクライアント"""

    @staticmethod
    def _get_session_cache_path(base_url: str) -> str:
        """セッションキャッシュファイルのパスを取得"""
        # URLをファイル名として使える形式に変換
        safe_url = base_url.replace("://", "_").replace("/", "_").replace(":", "_")
        return os.path.join(tempfile.gettempdir(), f"playwright_session_{safe_url}.json")

    @staticmethod
    def _load_cached_session(base_url: str) -> Optional[str]:
        """キャッシュされたセッションIDを読み込み"""
        cache_path = PlaywrightHTTPClient._get_session_cache_path(base_url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    return data.get('session_id')
            except (json.JSONDecodeError, IOError):
                return None
        return None

    @staticmethod
    def _save_session(base_url: str, session_id: str):
        """セッションIDをキャッシュに保存"""
        cache_path = PlaywrightHTTPClient._get_session_cache_path(base_url)
        try:
            with open(cache_path, 'w') as f:
                json.dump({'session_id': session_id}, f)
        except IOError:
            pass  # キャッシュ保存に失敗しても続行

    def __init__(self, base_url: str = "http://localhost:8931/mcp", debug: bool = False, reuse_session: bool = True):
        """
        Playwrightクライアントを初期化

        Args:
            base_url: MCP ServerのURL
            debug: デバッグログを出力するか
            reuse_session: キャッシュされたセッションを再利用するか
        """
        self.base_url = base_url
        self.debug = debug
        self.request_id = 0
        self.session_id = None
        self.session = requests.Session()
        self.reuse_session = reuse_session

        # キャッシュされたセッションを試す
        if self.reuse_session:
            cached_session_id = self._load_cached_session(base_url)
            if cached_session_id:
                self.session_id = cached_session_id
                self._log(f"Reusing cached session: {self.session_id}")
                # セッションが有効か確認（軽量なリクエストで検証）
                try:
                    # ダミーリクエストでセッションの有効性を確認
                    test_request = self._send_request("ping", {})
                    return  # セッション再利用成功
                except Exception as e:
                    self._log(f"Cached session invalid ({e}), initializing new session")
                    self.session_id = None

        # MCPハンドシェイクを実行
        self._initialize()

    def __enter__(self):
        """コンテキストマネージャーのenter"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーのexit"""
        self.session.close()
        return False

    def _log(self, message: str):
        """デバッグログ出力"""
        if self.debug:
            print(f"[DEBUG] {message}")

    def _parse_sse(self, sse_text: str) -> Dict[str, Any]:
        """SSE形式のレスポンスをパース"""
        lines = sse_text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                data_json = line[6:]  # "data: " を除去
                return json.loads(data_json)
        raise PlaywrightHTTPError(f"Invalid SSE format: {sse_text}")

    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """JSON-RPCリクエストを送信"""
        self.request_id += 1
        request_data = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        self._log(f"Sending: {request_data}")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        # セッションIDがあればヘッダーに追加
        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        try:
            response = self.session.post(
                self.base_url,
                json=request_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise PlaywrightHTTPError(f"HTTP request failed: {e}") from e

        # セッションIDを保存
        if 'mcp-session-id' in response.headers:
            self.session_id = response.headers['mcp-session-id']
            self._log(f"Session ID: {self.session_id}")

        # SSE形式のレスポンスをパース
        if response.headers.get('content-type') == 'text/event-stream':
            response_data = self._parse_sse(response.text)
        else:
            response_data = response.json()

        self._log(f"Received: {response_data}")

        if "error" in response_data:
            error_info = response_data['error']
            raise PlaywrightHTTPError(
                f"Playwright Error [{error_info.get('code')}]: {error_info.get('message')}"
            )

        return response_data.get("result", {})

    def _initialize(self):
        """MCPハンドシェイク実行"""
        init_result = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "playwright-http-cli",
                "version": "1.0.0"
            }
        })

        server_info = init_result.get('serverInfo', {})
        self._log(f"Server initialized: {server_info.get('name')} v{server_info.get('version')}")

        # initialized通知を送信
        self._send_notification("notifications/initialized")

        # セッションIDをキャッシュに保存
        if self.reuse_session and self.session_id:
            self._save_session(self.base_url, self.session_id)

    def _send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """JSON-RPC通知を送信（レスポンスなし）"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

        self._log(f"Sending notification: {notification}")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        # セッションIDがあればヘッダーに追加
        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        try:
            self.session.post(
                self.base_url,
                json=notification,
                headers=headers,
                timeout=30
            )
        except requests.exceptions.RequestException:
            pass  # 通知はレスポンスを期待しない

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Playwrightツールを呼び出し

        Args:
            tool_name: ツール名
            arguments: ツール引数

        Returns:
            ツール実行結果
        """
        result = self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        return result.get("content", [])
