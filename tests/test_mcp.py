"""MCP tool tests."""
import pytest
from mcp.tools.search import SEARCH_TOOL, handle_search


@pytest.mark.asyncio
async def test_search_known_topic():
    """Test 1: handle_search returns string for known topic."""
    result = await handle_search("capital france")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "Paris" in result or "France" in result


@pytest.mark.asyncio
async def test_search_unknown_topic():
    """Test 2: handle_search returns string for unknown topic."""
    result = await handle_search("xyzzy unknown topic 12345")

    assert isinstance(result, str)
    assert len(result) > 0


def test_search_tool_schema():
    """Test 3: SEARCH_TOOL has required fields."""
    assert SEARCH_TOOL["name"] == "web_search"
    assert "query" in SEARCH_TOOL["inputSchema"]["properties"]
    assert SEARCH_TOOL["inputSchema"]["properties"]["query"]["type"] == "string"
