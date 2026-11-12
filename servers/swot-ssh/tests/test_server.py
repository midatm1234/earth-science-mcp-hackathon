"""Protocol tests: real MCP calls in-process and over stdio. No network, no token: errors fire before any request."""

import asyncio
import sys
from pathlib import Path

import server
from mcp import Client, StdioServerParameters

SERVER_PY = Path(__file__).resolve().parents[1] / "server.py"
PASS = "SWOT_L2_LR_SSH_Basic_058_424_20261106T150521_20261106T155607_PID0_01"
BOX = {"south": 33, "north": 39, "west": -126, "east": -124}


def test_tools_listed_and_errors_are_helpful(monkeypatch):
    monkeypatch.delenv("EARTHDATA_TOKEN", raising=False)

    async def go():
        async with Client(server.mcp) as client:
            names = {t.name for t in (await client.list_tools()).tools}
            assert names == {"find_swot_passes", "fetch_swot_pass", "draw_swot_map", "list_swot_output_files"}
            far = await client.call_tool("find_swot_passes", {"south": 0, "north": 60, "west": -170, "east": -120})
            assert far.is_error and "too large" in far.content[0].text
            no_token = await client.call_tool("fetch_swot_pass", {"pass_name": PASS, **BOX})
            assert no_token.is_error and "EARTHDATA_TOKEN" in no_token.content[0].text
            unfetched = await client.call_tool("draw_swot_map", {"pass_name": PASS})
            assert unfetched.is_error and "Fetch it first" in unfetched.content[0].text
    asyncio.run(go())


def test_stdio_transport_lists_tools():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_PY), "--transport", "stdio"])

    async def go():
        async with Client(params) as client:
            assert "fetch_swot_pass" in {t.name for t in (await client.list_tools()).tools}
    asyncio.run(go())
