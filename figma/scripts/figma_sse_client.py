#!/usr/bin/env python3
"""
Figma MCP SSE Client

SSEモードで起動したFigma MCPサーバーに接続
"""

import requests
import json
import os
import threading
import queue
from typing import Any, Dict, Optional
import sseclient


class FigmaSSEError(Exception):
    """Figma SSE通信エラー"""
    pass


class FigmaSSEClient:
    """Figma MCP SSEクライアント"""

    def __init__(self, base_url: str = "http://127.0.0.1:3845", debug: bool = False):
        """
        Figmaクライアントを初期化

        Args:
            base_url: MCPサーバーのベースURL
            debug: デバッグログを出力するか
        """
        self.base_url = base_url.rstrip('/')
        self.sse_url = f"{self.base_url}/sse"
        self.message_url = None
        self.debug = debug
        self.request_id = 0
        self.session = requests.Session()
        self.response_queue = queue.Queue()
        self.sse_thread = None
        self.sse_response = None
        self.running = False

        # SSE接続を開始してMCPハンドシェイクを実行
        self._start_sse()
        self._initialize()

    def __enter__(self):
        """コンテキストマネージャーのenter"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーのexit"""
        self._stop_sse()
        self.session.close()
        return False

    def _log(self, message: str):
        """デバッグログ出力"""
        if self.debug:
            import sys
            print(f"[DEBUG] {message}", file=sys.stderr)

    def _start_sse(self):
        """SSE接続を開始"""
        self.sse_response = self.session.get(self.sse_url, stream=True, timeout=30)
        self.running = True

        # SSEイベントを処理するスレッドを開始
        self.sse_thread = threading.Thread(target=self._sse_listener, daemon=True)
        self.sse_thread.start()

        # エンドポイントイベントを待つ
        try:
            event = self.response_queue.get(timeout=10)
            if event.get("type") == "endpoint":
                endpoint_path = event.get("data", "")
                self.message_url = f"{self.base_url}{endpoint_path}"
                self._log(f"Message URL: {self.message_url}")
        except queue.Empty:
            raise FigmaSSEError("Timeout waiting for endpoint event")

    def _stop_sse(self):
        """SSE接続を停止"""
        self.running = False
        if self.sse_response:
            self.sse_response.close()

    def _sse_listener(self):
        """SSEイベントをリッスン"""
        try:
            client = sseclient.SSEClient(self.sse_response)
            for event in client.events():
                if not self.running:
                    break

                self._log(f"SSE event: {event.event}, data: {event.data}")

                if event.event == "endpoint":
                    self.response_queue.put({"type": "endpoint", "data": event.data})
                elif event.event == "message":
                    try:
                        data = json.loads(event.data)
                        self.response_queue.put({"type": "message", "data": data})
                    except json.JSONDecodeError:
                        self._log(f"Failed to parse message: {event.data}")
        except Exception as e:
            self._log(f"SSE listener error: {e}")

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

        if not self.message_url:
            raise FigmaSSEError("Message URL not initialized")

        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = self.session.post(
                self.message_url,
                json=request_data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise FigmaSSEError(f"HTTP request failed: {e}") from e

        # SSEからレスポンスを待つ
        try:
            while True:
                event = self.response_queue.get(timeout=60)
                if event.get("type") == "message":
                    response_data = event.get("data", {})
                    self._log(f"Received: {response_data}")

                    # リクエストIDが一致するか確認
                    if response_data.get("id") == self.request_id:
                        if "error" in response_data:
                            error_info = response_data['error']
                            raise FigmaSSEError(
                                f"Figma Error [{error_info.get('code')}]: {error_info.get('message')}"
                            )
                        return response_data.get("result", {})
        except queue.Empty:
            raise FigmaSSEError("Timeout waiting for response")

    def _initialize(self):
        """MCPハンドシェイク実行"""
        init_result = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "figma-sse-cli",
                "version": "1.0.0"
            }
        })

        server_info = init_result.get('serverInfo', {})
        self._log(f"Server initialized: {server_info.get('name')} v{server_info.get('version')}")

        # initialized通知を送信
        self._send_notification("notifications/initialized")

    def _send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """JSON-RPC通知を送信（レスポンスなし）"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

        self._log(f"Sending notification: {notification}")

        if not self.message_url:
            return

        headers = {
            "Content-Type": "application/json",
        }

        try:
            self.session.post(
                self.message_url,
                json=notification,
                headers=headers,
                timeout=30
            )
        except requests.exceptions.RequestException:
            pass  # 通知はレスポンスを期待しない

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Figmaツールを呼び出し

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

    def list_tools(self) -> list:
        """利用可能なツール一覧を取得"""
        result = self._send_request("tools/list", {})
        return result.get("tools", [])
