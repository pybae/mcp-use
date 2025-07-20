import pytest
import pytest_asyncio
from mcp_use.connectors.base import BaseConnector

class FakeSession:
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

class DummyConnector(BaseConnector):
    async def connect(self):
        self.client_session = FakeSession()
        self._connected = True  # Crucially not setting _initialized
    @property
    def public_identifier(self):
        return "dummy"

@pytest.mark.asyncio
async def test_base_connector_auto_initialize():
    c = DummyConnector()
    await c._ensure_connected()  # should call initialize()
    assert c._initialized is True
    assert isinstance(c.tools, list)
    assert isinstance(c.resources, list)
    assert isinstance(c.prompts, list)
