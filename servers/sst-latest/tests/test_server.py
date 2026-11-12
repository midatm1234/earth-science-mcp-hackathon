"""Protocol tests: real MCP calls in-process and over stdio. No network: errors are triggered before any request."""

import asyncio
import sys
from pathlib import Path

import server
from mcp import Client, StdioServerParameters

SERVER_PY = Path(__file__).resolve().parents[1] / "server.py"


def test_tool_listed_and_bad_id_gives_helpful_error():
    async def go():
        async with Client(server.mcp) as client:
            tools = (await client.list_tools()).tools
            assert {t.name for t in tools} == {
                "get_latest_sst_granule", "get_newest_sst_dates", "fetch_sst_subset",
                "draw_sst_map", "make_sst_gif", "list_sst_output_files"}
            bad = await client.call_tool("get_latest_sst_granule", {"collection_concept_id": "not-an-id"})
            assert bad.is_error and "concept id" in bad.content[0].text
            far = await client.call_tool(
                "fetch_sst_subset", {"date": "2026-11-10", "south": 0, "north": 60, "west": -170, "east": -120})
            assert far.is_error and "too large" in far.content[0].text
            unfetched = await client.call_tool("draw_sst_map", {"date": "1999-01-01"})
            assert unfetched.is_error and "Fetch that date first" in unfetched.content[0].text
    asyncio.run(go())


def test_stdio_transport_lists_tool_and_returns_error_text():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_PY), "--transport", "stdio"])

    async def go():
        async with Client(params) as client:
            assert "get_latest_sst_granule" in {t.name for t in (await client.list_tools()).tools}
            bad = await client.call_tool("get_latest_sst_granule", {"collection_concept_id": "x"})
            assert bad.is_error
    asyncio.run(go())
