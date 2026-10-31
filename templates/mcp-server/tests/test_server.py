"""Protocol tests: real MCP calls in-process and over stdio. Keep at least one success and one error case."""

import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

import server

SERVER_PY = Path(__file__).resolve().parents[1] / "server.py"


def test_tool_listed_and_called_in_process():
    async def go():
        async with Client(server.mcp) as client:
            names = {t.name for t in (await client.list_tools()).tools}
            assert "summarize_values" in names
            ok = await client.call_tool("summarize_values", {"values": [1, 2, None], "units": "degC"})
            assert not ok.is_error
            assert ok.structured_content["n_valid"] == 2
            bad = await client.call_tool("summarize_values", {"values": [], "units": "degC"})
            assert bad.is_error and "empty" in bad.content[0].text
    asyncio.run(go())


def test_stdio_transport():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_PY), "--transport", "stdio"])

    async def go():
        async with Client(params) as client:
            result = await client.call_tool("summarize_values", {"values": [2, 4], "units": "mm/day"})
            assert result.structured_content["mean"] == 3
    asyncio.run(go())
