"""__SERVER_NAME__: MCP server created from templates/mcp-server by team __TEAM__.

Run from the repository root:
    uv run python servers/__SERVER_NAME__/server.py                   # stdio
    uv run python servers/__SERVER_NAME__/server.py --transport http  # http://127.0.0.1:8766/mcp

Rules: keep science in science.py; keep this file a thin wrapper; never print to
stdout (it carries the MCP protocol on stdio); read secrets from environment
variables only.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

import science

SERVER_NAME = "__SERVER_NAME__"
SERVER_VERSION = "0.1.0"

logging.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(SERVER_NAME)

mcp = MCPServer(SERVER_NAME, version=SERVER_VERSION,
                instructions="Describe in two sentences what this server offers and the order to call its tools.")
READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


@mcp.tool(annotations=READ_ONLY)
def summarize_values(
    values: Annotated[list[float | None], Field(description="Numbers to summarize; use null for missing values.")],
    units: Annotated[str, Field(description="Units of the values, e.g. 'degC' or 'mm/day'.")],
    fill_value: Annotated[float | None, Field(description="Value that means missing, e.g. -9999. Optional.")] = None,
) -> dict[str, Any]:
    """Count valid and missing values and return their mean, minimum and maximum.

    Returns n_total, n_valid, n_missing, mean, min, max, units and the missing-data rule.
    Fails with an explanation if values is empty, units is empty, or every value is missing.
    """
    try:
        return science.summarize_values(values, units, fill_value)
    except science.DataError as exc:
        raise ToolError(str(exc)) from exc


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=f"{SERVER_NAME} MCP server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MCP_PORT", "8766")))
    args = parser.parse_args(argv)
    if args.transport == "stdio":
        log.info("starting %s on stdio", SERVER_NAME)
        mcp.run(transport="stdio")
    else:
        log.info("starting %s on http://%s:%d/mcp", SERVER_NAME, args.host, args.port)
        mcp.run(transport="streamable-http", host=args.host, port=args.port, stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
