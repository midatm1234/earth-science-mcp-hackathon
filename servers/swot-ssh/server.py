"""swot-ssh: MCP server created from templates/mcp-server by team test.

Run from the repository root:
    uv run python servers/swot-ssh/server.py                   # stdio
    uv run python servers/swot-ssh/server.py --transport http  # http://127.0.0.1:8766/mcp

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

import mapping
import science
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

SERVER_NAME = "swot-ssh"
SERVER_VERSION = "0.1.0"

logging.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(SERVER_NAME)

mcp = MCPServer(SERVER_NAME, version=SERVER_VERSION,
                instructions=("SWOT sea surface height (SWOT_L2_LR_SSH_D). Order: find_swot_passes (public metadata), then fetch_swot_pass "
                            "(downloads one pass; needs an Earthdata Login token in EARTHDATA_TOKEN), then draw_swot_map; "
                            "list_swot_output_files shows what was written."))
READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


South = Annotated[float, Field(description="Southern edge, degrees north (-90 to 90).")]
North = Annotated[float, Field(description="Northern edge, degrees north.")]
West = Annotated[float, Field(description="Western edge, degrees east (-180 to 180).")]
East = Annotated[float, Field(description="Eastern edge, degrees east.")]


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=True))
def find_swot_passes(
    south: South, north: North, west: West, east: East,
    days: Annotated[int, Field(description="How many days back to search, 1 to 30 (default 10).", ge=1, le=30)] = 10,
) -> dict[str, Any]:
    """List SWOT KaRIn sea surface height passes (Version D, Basic product) over a region in the last days.

    Uses NASA's public CMR catalog, so no login is needed. Returns pass names, start and end times (UTC),
    file sizes in MB (newest first), the date checked and the query. A pass is listed if its footprint
    overlaps the box, so it may touch only a corner. Fails with an explanation for a bad region or if CMR
    cannot be reached.
    """
    try:
        return science.find_passes(south, north, west, east, days)
    except science.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True, openWorldHint=True))
async def fetch_swot_pass(
    pass_name: Annotated[str, Field(description="A pass_name from find_swot_passes, e.g. 'SWOT_L2_LR_SSH_Basic_058_424_20261106T150521_20261106T155607_PID0_01'.")],
    south: South, north: North, west: West, east: East,
    variable: Annotated[str, Field(description="'ssh_karin' (sea surface height, m) or 'ssha_karin' (height anomaly, m).")] = "ssh_karin",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Download one SWOT pass (about 9 MB), cut out a region and save the valid points (metres).

    Needs an Earthdata Login: a user token in the environment variable EARTHDATA_TOKEN, or else a
    'machine urs.earthdata.nasa.gov' entry in ~/.netrc. Credentials are read from there only, sent only to
    NASA, and never passed through the chat or returned. If neither exists, this tool tries to open the
    Earthdata Login page through a sign-in prompt, then stops and says what to set. Drops fill values and points with any
    quality flag set, and reports how many were dropped. Returns the saved file's path and size, pass
    times, the point counts, min and max in metres, the rules, the source and the date checked, never the
    values. Fails with an explanation for a bad pass name or region, a rejected token, no valid points,
    or a network error.
    """
    token = science.get_token()
    basic = None if token else science.get_netrc_login()
    if not token and not basic:
        if ctx is not None:
            try:
                await ctx.elicit_url(
                    "Sign in to Earthdata Login, generate a user token on your profile page, set it as "
                    f"{science.TOKEN_VAR} in your terminal, then start a new session.",
                    science.LOGIN_URL, "earthdata-login",
                )
            except Exception as exc:  # noqa: BLE001 - the client may not support URL prompts; the message below still explains
                log.info("client did not show the sign-in prompt (%s: %s)", type(exc).__name__, exc)
        raise ToolError(science.NO_TOKEN_MESSAGE)
    try:
        return science.fetch_pass(pass_name, south, north, west, east, variable, token, basic=basic)
    except science.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True, openWorldHint=False))
def draw_swot_map(
    pass_name: Annotated[str, Field(description="A pass_name already fetched with fetch_swot_pass.")],
    variable: Annotated[str, Field(description="'ssh_karin' or 'ssha_karin' (must match what was fetched).")] = "ssh_karin",
) -> dict[str, Any]:
    """Draw a Cartopy map (PNG) of one fetched pass, as coloured points along the swath (not a regular grid).

    Returns the PNG's path and size, the number of points, the value range in metres, how it was drawn,
    the source and the date checked. Fails with an explanation if that pass has not been fetched.
    """
    try:
        return mapping.draw_map(pass_name, variable)
    except science.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=READ_ONLY)
def list_swot_output_files() -> dict[str, Any]:
    """List the files this server has written (saved subsets and PNG maps) with their sizes in bytes."""
    return mapping.list_output_files()


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
