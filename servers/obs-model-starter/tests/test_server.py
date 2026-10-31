"""MCP-level tests: real protocol calls in-process, over stdio and over Streamable HTTP."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import server
from mcp import Client, StdioServerParameters

SERVER_PY = Path(__file__).resolve().parents[1] / "server.py"
EXPECTED_TOOLS = {"list_datasets", "describe_dataset", "compare_model_to_obs"}
COMPARE_ARGS = {
    "obs_dataset_id": "syn-station-tas-monthly",
    "model_dataset_id": "syn-model-a-tas-monthly",
    "site_id": "SYN-VALLEY",
}


async def _exercise(client: Client) -> dict:
    tools = await client.list_tools()
    names = {t.name for t in tools.tools}
    assert EXPECTED_TOOLS <= names
    for tool in tools.tools:
        assert tool.description and len(tool.description) > 40, f"{tool.name} needs a useful description"
    result = await client.call_tool("compare_model_to_obs", COMPARE_ARGS)
    assert not result.is_error
    return result.structured_content


def test_in_process_tools_and_structured_result():
    out = asyncio.run(_run_in_process())
    assert out["n_valid_pairs"] == 23
    assert out["units"] == "degC"
    assert out["excluded"]["obs_missing_value"] == ["2020-07"]
    assert "synthetic" in json.dumps(out["provenance"]).lower()


async def _run_in_process():
    async with Client(server.mcp) as client:
        return await _exercise(client)


def test_errors_are_tool_errors_not_crashes():
    async def go():
        async with Client(server.mcp) as client:
            bad = await client.call_tool("describe_dataset", {"dataset_id": "not-a-dataset"})
            assert bad.is_error
            assert "Available dataset ids" in bad.content[0].text
            bad = await client.call_tool("compare_model_to_obs", {**COMPARE_ARGS, "start": "2021-12", "end": "2020-01"})
            assert bad.is_error and "after end" in bad.content[0].text
            ok = await client.call_tool("list_datasets", {})
            assert len(ok.structured_content["datasets"]) == 3
    asyncio.run(go())


def test_stdio_transport_subprocess():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_PY), "--transport", "stdio"])

    async def go():
        async with Client(params) as client:
            return await _exercise(client)

    out = asyncio.run(go())
    assert out["n_valid_pairs"] == 23


def test_stdio_stdout_contains_only_protocol_messages():
    """Logs must go to stderr; anything else on stdout would corrupt the protocol."""
    proc = subprocess.Popen([sys.executable, str(SERVER_PY), "--transport", "stdio"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "stdout-check", "version": "0"}}}
    try:
        out, err = proc.communicate(json.dumps(init) + "\n", timeout=30)
    finally:
        proc.kill()
    lines = [line for line in out.splitlines() if line.strip()]
    assert lines, f"no stdout; stderr was: {err[-500:]}"
    for line in lines:
        assert json.loads(line)["jsonrpc"] == "2.0"
    assert "starting obs-model-starter" in err


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def http_server():
    port = _free_port()
    proc = subprocess.Popen([sys.executable, str(SERVER_PY), "--transport", "http", "--port", str(port)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={**os.environ})
    deadline = time.time() + 30
    while time.time() < deadline:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                break
        if proc.poll() is not None:
            raise RuntimeError(proc.stderr.read().decode())
        time.sleep(0.2)
    yield f"http://127.0.0.1:{port}/mcp"
    proc.terminate()
    proc.wait(timeout=10)


def test_streamable_http_transport_subprocess(http_server):
    async def go():
        async with Client(http_server) as client:
            return await _exercise(client)

    out = asyncio.run(go())
    assert out["n_valid_pairs"] == 23
