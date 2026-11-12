"""sst-latest: MCP server created from templates/mcp-server by team test.

Run from the repository root:
    uv run python servers/sst-latest/server.py                   # stdio
    uv run python servers/sst-latest/server.py --transport http  # http://127.0.0.1:8766/mcp

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
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

SERVER_NAME = "sst-latest"
SERVER_VERSION = "0.1.0"

logging.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(SERVER_NAME)

mcp = MCPServer(SERVER_NAME, version=SERVER_VERSION,
                instructions=("Sea surface temperature (SST) tools. get_latest_sst_granule reports the newest NASA CMR granule (metadata only). "
                            "For maps: get_newest_sst_dates, then fetch_sst_subset per day, then draw_sst_map and/or make_sst_gif; "
                            "list_sst_output_files shows what was written."))
READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


@mcp.tool(annotations=READ_ONLY)
def get_latest_sst_granule(
    collection_concept_id: Annotated[str, Field(description=(
        "NASA CMR collection concept id of a sea surface temperature product, e.g. "
        "'C1996881146-POCLOUD' (GHRSST MUR L4 global, the default)."))] = science.DEFAULT_COLLECTION,
) -> dict[str, Any]:
    """Find the newest sea surface temperature granule in a NASA CMR collection (metadata only).

    Returns the collection id, short name and title; the newest granule's name and its start and end
    times (UTC, ISO 8601); the granule's age in hours; the date checked; the rule used for "newest";
    and provenance. Does not download data and needs no credentials. Fails with an explanation if the
    id is malformed or unknown, the collection has no granules, or NASA CMR cannot be reached.
    """
    try:
        return science.latest_granule(collection_concept_id)
    except science.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=READ_ONLY)
def get_newest_sst_dates(
    days: Annotated[int, Field(description="How many of the newest daily analyses to list, 1 to 31 (default 10).", ge=1, le=31)] = 10,
) -> dict[str, Any]:
    """List the newest daily dates of the MUR sea surface temperature analysis (NOAA ERDDAP, no login).

    Returns the dates (YYYY-MM-DD, oldest first), the newest one, the date checked, the source and the
    query. Fails with an explanation if NOAA ERDDAP cannot be reached. Use these dates with fetch_sst_subset.
    """
    try:
        return mapping.newest_available_dates(days)
    except mapping.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True, openWorldHint=True))
def fetch_sst_subset(
    date: Annotated[str, Field(description="Day to fetch, YYYY-MM-DD, from get_newest_sst_dates.")],
    south: Annotated[float, Field(description="Southern edge, degrees north (-90 to 90).")],
    north: Annotated[float, Field(description="Northern edge, degrees north.")],
    west: Annotated[float, Field(description="Western edge, degrees east (-180 to 180).")],
    east: Annotated[float, Field(description="Eastern edge, degrees east.")],
) -> dict[str, Any]:
    """Fetch one day of MUR sea surface temperature (degC) for a small region and save it in sst_output/.

    The region may be at most 40 degrees on a side and is thinned to a coarse grid, so downloads stay
    small. Returns the saved file's path and size, number of points, grid step, min and max in degC, the
    source and the date checked, never the values. Fails with an explanation for bad dates or regions,
    a region with no data, or if NOAA ERDDAP cannot be reached.
    """
    try:
        return mapping.fetch_and_save(date, south, north, west, east)
    except mapping.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True, openWorldHint=False))
def draw_sst_map(
    date: Annotated[str, Field(description="Day to draw, YYYY-MM-DD; it must already be fetched with fetch_sst_subset.")],
) -> dict[str, Any]:
    """Draw a Cartopy map (PNG) of one fetched day, with land, coastlines and a degC colour bar.

    Returns the PNG's path and size, the date, the value range in degC, the source and the date checked.
    Fails with an explanation if that date has not been fetched.
    """
    try:
        return mapping.draw_saved_map(date)
    except mapping.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True, openWorldHint=False))
def make_sst_gif(
    dates: Annotated[list[str], Field(description="Fetched days to animate, YYYY-MM-DD, 2 to 31 of them, same region.")],
) -> dict[str, Any]:
    """Make an animated GIF of fetched days, one Cartopy map per day, with one shared colour scale.

    Returns the GIF's path and size, the number of frames, the dates in order, the colour scale in degC,
    the source and the date checked. Fails with an explanation if fewer than 2 dates are given, a date has
    not been fetched, or the dates cover different regions.
    """
    try:
        return mapping.make_saved_gif(dates)
    except mapping.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=READ_ONLY)
def list_sst_output_files() -> dict[str, Any]:
    """List the files this server has written (saved subsets, PNG maps, GIFs) with their sizes in bytes."""
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
