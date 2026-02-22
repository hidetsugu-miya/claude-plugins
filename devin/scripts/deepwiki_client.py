#!/usr/bin/env python3
"""
Devin MCP Streamable HTTP Client

Devin MCP サーバーに Streamable HTTP で接続し、
GitHubリポジトリのドキュメント構造取得・内容取得・質問応答を行う。
"""

import requests
import json
import os
import tempfile
from typing import Any, Dict, List, Optional


class DeepWikiMCPError(Exception):
    """DeepWiki MCP通信エラー"""
    pass


class DeepWikiMCPClient:
    """DeepWiki MCP Streamable HTTPクライアント"""

    DEFAULT_URL = "https://mcp.devin.ai/mcp"

    @staticmethod
    def _get_session_cache_path(base_url: str) -> str:
        safe_url = base_url.replace("://", "_").replace("/", "_").replace(":", "_")
        return os.path.join(tempfile.gettempdir(), f"deepwiki_session_{safe_url}.json")

    @staticmethod
    def _load_cached_session(base_url: str) -> Optional[str]:
        cache_path = DeepWikiMCPClient._get_session_cache_path(base_url)
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
        cache_path = DeepWikiMCPClient._get_session_cache_path(base_url)
        try:
            with open(cache_path, 'w') as f:
                json.dump({'session_id': session_id}, f)
        except IOError:
            pass

    def __init__(self, base_url: str = None, debug: bool = False, reuse_session: bool = True, timeout: int = 120, api_key: str = None):
        """
        DeepWiki MCPクライアントを初期化

        Args:
            base_url: MCP ServerのURL（デフォルト: https://mcp.devin.ai/mcp）
            debug: デバッグログを出力するか
            reuse_session: キャッシュされたセッションを再利用するか
            timeout: HTTPリクエストのタイムアウト秒数（デフォルト: 120）
            api_key: Bearer認証用APIキー（Devin MCP等で必要）
        """
        self.base_url = base_url or self.DEFAULT_URL
        self.debug = debug
        self.request_id = 0
        self.session_id = None
        self.session = requests.Session()
        self.reuse_session = reuse_session
        self.timeout = timeout
        self.api_key = api_key

        if self.reuse_session:
            cached_session_id = self._load_cached_session(self.base_url)
            if cached_session_id:
                self.session_id = cached_session_id
                self._log(f"Reusing cached session: {self.session_id}")
                try:
                    self._send_request("ping", {})
                    return
                except Exception as e:
                    self._log(f"Cached session invalid ({e}), initializing new session")
                    self.session_id = None

        self._initialize()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        return False

    def _log(self, message: str):
        if self.debug:
            print(f"[DEBUG] {message}")

    def _build_headers(self) -> Dict[str, str]:
        """共通HTTPヘッダーを構築"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        return headers

    def _parse_sse(self, sse_text: str) -> Dict[str, Any]:
        """SSE形式のレスポンスをパース"""
        lines = sse_text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                data_json = line[6:]
                return json.loads(data_json)
        raise DeepWikiMCPError(f"Invalid SSE format: {sse_text}")

    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """JSON-RPCリクエストを送信"""
        self.request_id += 1
        request_data = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        self._log(f"Sending: {method} {params}")

        headers = self._build_headers()

        try:
            response = self.session.post(
                self.base_url,
                json=request_data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise DeepWikiMCPError(f"HTTP request failed: {e}") from e

        if 'mcp-session-id' in response.headers:
            self.session_id = response.headers['mcp-session-id']
            self._log(f"Session ID: {self.session_id}")

        content_type = response.headers.get('content-type', '')
        if 'text/event-stream' in content_type:
            response_data = self._parse_sse(response.text)
        else:
            response_data = response.json()

        self._log(f"Received: {json.dumps(response_data, ensure_ascii=False)[:200]}")

        if "error" in response_data:
            error_info = response_data['error']
            raise DeepWikiMCPError(
                f"MCP Error [{error_info.get('code')}]: {error_info.get('message')}"
            )

        return response_data.get("result", {})

    def _initialize(self):
        """MCPハンドシェイク実行"""
        init_result = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "deepwiki-mcp-cli",
                "version": "1.0.0"
            }
        })

        server_info = init_result.get('serverInfo', {})
        self._log(f"Server: {server_info.get('name')} v{server_info.get('version')}")

        self._send_notification("notifications/initialized")

        if self.reuse_session and self.session_id:
            self._save_session(self.base_url, self.session_id)

    def _send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """JSON-RPC通知を送信"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

        headers = self._build_headers()

        try:
            self.session.post(
                self.base_url,
                json=notification,
                headers=headers,
                timeout=self.timeout
            )
        except requests.exceptions.RequestException:
            pass

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        MCPツールを呼び出し

        Args:
            tool_name: ツール名
            arguments: ツール引数

        Returns:
            ツール実行結果（contentリスト）
        """
        result = self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return result.get("content", [])

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        利用可能なツール一覧を取得

        Returns:
            ツール情報のリスト
        """
        result = self._send_request("tools/list")
        return result.get("tools", [])

    # --- DeepWiki特化メソッド ---

    def read_structure(self, repo: str) -> Any:
        """
        リポジトリのドキュメント目次を取得

        Args:
            repo: リポジトリ（owner/repo 形式、例: "anthropics/claude-code"）

        Returns:
            ドキュメント構造
        """
        return self.call_tool("read_wiki_structure", {
            "repoName": repo
        })

    def read_contents(self, repo: str) -> Any:
        """
        リポジトリのドキュメント全文を取得

        Args:
            repo: リポジトリ（owner/repo 形式）

        Returns:
            ドキュメント内容
        """
        return self.call_tool("read_wiki_contents", {
            "repoName": repo
        })

    def ask_question(self, repo: str, question: str) -> Any:
        """
        リポジトリについて自然言語で質問

        Args:
            repo: リポジトリ（owner/repo 形式）。リストで複数指定可（最大10）
            question: 質問文

        Returns:
            回答
        """
        return self.call_tool("ask_question", {
            "repoName": repo,
            "question": question
        })
