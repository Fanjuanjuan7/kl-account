from typing import Any, Dict, Optional
import httpx


class BitBrowserClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self._client = httpx.Client(timeout=20)

    def post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        r = self._client.post(f"{self.base}{path}", json=json)
        r.raise_for_status()
        return r.json()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        r = self._client.get(f"{self.base}{path}", params=params)
        r.raise_for_status()
        return r.json()

    def health(self) -> Dict[str, Any]:
        return self.post("/health", {})

    def create_window(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.post("/browser/update", payload)

    def open_window(self, window_id: str) -> Dict[str, Any]:
        return self.post("/browser/open", {"id": window_id})

    def close_window(self, window_id: str) -> Dict[str, Any]:
        return self.post("/browser/close", {"id": window_id})

    def list_windows(self) -> Dict[str, Any]:
        return self.get("/browser/list")

    def switch_tab(self, window_id: str, tab_id: str) -> Dict[str, Any]:
        return self.post("/browser/switchTab", {"id": window_id, "tabId": tab_id})

    def get_window_tabs(self, window_id: str) -> Dict[str, Any]:
        return self.post("/browser/getTabs", {"id": window_id})

    def navigate_to(self, window_id: str, url: str) -> Dict[str, Any]:
        return self.post("/browser/navigate", {"id": window_id, "url": url})

    def close_tab(self, window_id: str, tab_id: str) -> Dict[str, Any]:
        """关闭指定标签页"""
        return self.post("/browser/closeTab", {"id": window_id, "tabId": tab_id})

    def open_tab(self, window_id: str, url: str) -> Dict[str, Any]:
        """在新标签页中打开URL"""
        return self.post("/browser/openTab", {"id": window_id, "url": url})

    def activate(self, window_id: str) -> Dict[str, Any]:
        """激活窗口"""
        return self.post("/browser/activate", {"id": window_id})

    def maximize(self, window_id: str) -> Dict[str, Any]:
        """最大化窗口"""
        return self.post("/browser/maximize", {"id": window_id})

    def devtools(self, window_id: str) -> Dict[str, Any]:
        """获取DevTools WebSocket地址"""
        return self.post("/browser/devtools", {"id": window_id})

