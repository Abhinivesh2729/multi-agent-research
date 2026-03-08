"""MCP tool tests."""
import pytest
from mcp.tools.search import SEARCH_TOOL, handle_search
from mcp.tools.calculator import CALCULATOR_TOOL, handle_calculation


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


@pytest.mark.asyncio
async def test_calculator_valid_expression():
    """Test 4: calculator returns computed result for valid math."""
    result = await handle_calculation("2 + 3 * 4")

    assert result == "14"


@pytest.mark.asyncio
async def test_calculator_invalid_expression():
    """Test 5: calculator handles invalid expressions safely."""
    result = await handle_calculation("import os")

    assert "invalid expression" in result


def test_calculator_tool_schema():
    """Test 6: CALCULATOR_TOOL has required fields."""
    assert CALCULATOR_TOOL["name"] == "calculator"
    assert "expression" in CALCULATOR_TOOL["inputSchema"]["properties"]
    assert CALCULATOR_TOOL["inputSchema"]["properties"]["expression"]["type"] == "string"
