"""MCP Server for research tools."""
import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server.models import InitializationOptions
from .tools.search import SEARCH_TOOL, handle_search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("research-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name=SEARCH_TOOL["name"],
            description=SEARCH_TOOL["description"],
            inputSchema=SEARCH_TOOL["inputSchema"]
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "web_search":
        query = arguments.get("query", "")
        result = await handle_search(query)
        return [TextContent(type="text", text=result)]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    logger.info("Starting research MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="research-mcp",
                server_version="1.0.0"
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
