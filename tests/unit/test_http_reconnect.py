import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from mcp_use.connectors.http import HttpConnector
import httpx

@pytest.mark.asyncio
async def test_http_connector_auto_reconnect():
    connector = HttpConnector(
        base_url="http://localhost:1234",
        max_reconnect_attempts=2,
        reconnect_backoff_seconds=0.01,  # Speed up test
    )
    # Patch connect and session methods
    connector.connect = AsyncMock()
    connector._connected = False
    connector.client_session = AsyncMock()
    orig_call_tool = AsyncMock(side_effect=[httpx.TransportError("lost conn"), "tool_result"])
    with patch.object(connector, 'is_connected', side_effect=[False, False, True]):
        with patch.object(connector.client_session, 'call_tool', orig_call_tool):
            result = await connector.call_tool("mytool", {"x": 1})
            assert result == "tool_result"
            assert connector.connect.call_count == 2  # First for recovery, then for success
    # Test reconnect limit hit
    connector.connect.reset_mock()
    orig_call_tool = AsyncMock(side_effect=[httpx.TransportError("lost conn")]*3)
    with patch.object(connector, 'is_connected', return_value=False):
        with patch.object(connector.client_session, 'call_tool', orig_call_tool):
            with pytest.raises(RuntimeError, match='Max reconnect attempts exceeded'):
                await connector.call_tool("fail", {"fail": 1})
