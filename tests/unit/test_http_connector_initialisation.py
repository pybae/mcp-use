import pytest
import pytest_asyncio
import httpx
from mcp_use.connectors.http import HttpConnector

class DummyStream:
    def __init__(self):
        self._closed = False
    def close(self):
        self._closed = True

@pytest.mark.asyncio
async def test_http_connector_sse_fallback(monkeypatch):
    # Patch StreamableHttpConnectionManager to raise HTTPStatusError
    class DummyMgr:
        async def start(self):
            raise httpx.HTTPStatusError("405 error", request=None, response=type('resp', (), {'status_code':405})())
        async def close(self):
            return
    # Patch SseConnectionManager to return dummy streams
    class DummySseMgr:
        async def start(self_with):
            return DummyStream(), DummyStream()
        async def close(self_with):
            return
    monkeypatch.setattr("mcp_use.task_managers.StreamableHttpConnectionManager", DummyMgr)
    monkeypatch.setattr("mcp_use.task_managers.SseConnectionManager", DummySseMgr)
    # Patch ClientSession
    class DummyClientSession:
        async def __aenter__(self):
            return self
        async def initialize(self):
            class Capa:
                tools = True
                resources = True
                prompts = True
            class Result:
                capabilities = Capa()
            return Result()
        async def list_tools(self):
            class Tools:
                tools = []
            return Tools()
        async def list_resources(self):
            class Resources:
                resources = []
            return Resources()
        async def list_prompts(self):
            class Prompts:
                prompts = []
            return Prompts()
    monkeypatch.setattr("mcp_use.connectors.http.ClientSession", DummyClientSession)
    conn = HttpConnector(base_url="http://dummy")
    await conn.connect()
    assert conn._initialized is True
    assert isinstance(conn.tools, list)
    assert isinstance(conn.resources, list)
    assert isinstance(conn.prompts, list)
