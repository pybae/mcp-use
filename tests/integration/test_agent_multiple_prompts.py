import pytest
import pytest_asyncio
import asyncio
from mcp_use.agents.mcpagent import MCPAgent
from mcp_use.connectors.base import BaseConnector
from langchain.schema.language_model import BaseLanguageModel

class DummyLLM(BaseLanguageModel):
    async def agenerate(self, *a, **k):
        class Out:
            generations = [[type('X', (), {'text':"Dummy response"})()]]
            llm_output = {}
        return Out()
    @property
    def lc_aliases(self):
        return []
    @property
    def _identifying_params(self):
        return {}
    @property
    def _llm_type(self):
        return "dummy"

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
        self._connected = True
    @property
    def public_identifier(self):
        return "dummy"

@pytest.mark.asyncio
async def test_multi_prompt_runs():
    agent = MCPAgent(llm=DummyLLM(), connectors=[DummyConnector()])
    result1 = await agent.run("first message")
    result2 = await agent.run("second message")
    # Should not hit generic fallback error or crash
    assert "currently unable to retrieve the details" not in str(result2).lower()
    assert result2 is not None
