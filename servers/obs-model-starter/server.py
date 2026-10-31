"""obs-model-starter: a small, credential-free Earth science MCP server.

Tools
    list_datasets          - which sample datasets this server can read
    describe_dataset       - metadata, coverage, units, missing data, provenance
    compare_model_to_obs   - aligned monthly model-vs-observation bias and RMSE

All bundled data are SYNTHETIC teaching fixtures (see data/README.md).

Run
    uv run python servers/obs-model-starter/server.py                      # stdio (for Claude Code)
    uv run python servers/obs-model-starter/server.py --transport http     # http://127.0.0.1:8765/mcp

stdout is reserved for the MCP protocol when using stdio. All logs go to stderr.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Annotated, Any

import science
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

SERVER_NAME = "obs-model-starter"
SERVER_VERSION = "0.1.0"

logging.basicConfig(
    stream=sys.stderr,
    level=os.environ.get("OBS_MODEL_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(SERVER_NAME)

INSTRUCTIONS = (
    "Sample observation and model datasets (SYNTHETIC teaching fixtures). "
    "Call list_datasets first, then describe_dataset to check units, time convention, sites and "
    "missing data before calling compare_model_to_obs. Always report units, the number of valid "
    "pairs, excluded months, provenance and that the data are synthetic."
)

mcp = MCPServer(SERVER_NAME, version=SERVER_VERSION, instructions=INSTRUCTIONS)
READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)

_catalog: science.Catalog | None = None


def _get_catalog() -> science.Catalog:
    global _catalog
    if _catalog is None:
        _catalog = science.load_catalog()
    return _catalog


def _run(func, *args, **kwargs) -> Any:
    try:
        return func(_get_catalog(), *args, **kwargs)
    except science.DataError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(annotations=READ_ONLY)
def list_datasets() -> dict[str, Any]:
    """List the sample datasets this server can read.

    Returns one entry per dataset with dataset_id, kind ("observation" or "model"),
    variable, units, provenance_class ("synthetic" for every bundled fixture) and title.
    Use the dataset_id values as inputs to describe_dataset and compare_model_to_obs.
    """
    return {"datasets": _run(science.list_datasets)}


@mcp.tool(annotations=READ_ONLY)
def describe_dataset(
    dataset_id: Annotated[str, Field(description="Dataset id from list_datasets, e.g. 'syn-station-tas-monthly'.")],
) -> dict[str, Any]:
    """Summarize one dataset's metadata before using it.

    Returns variable, units, time resolution and time-stamp convention, time coverage,
    spatial support (point vs grid cell), coordinate convention, declared missing values,
    QC rules, per-site counts of valid/missing/QC-rejected values with mean/min/max,
    version, provenance, license and citation.
    Fails with a list of valid ids if dataset_id is unknown.
    """
    return _run(science.summarize_dataset, dataset_id)


@mcp.tool(annotations=READ_ONLY)
def compare_model_to_obs(
    obs_dataset_id: Annotated[str, Field(description="Observation dataset id, e.g. 'syn-station-tas-monthly'.")],
    model_dataset_id: Annotated[str, Field(description="Model dataset id, e.g. 'syn-model-a-tas-monthly'.")],
    site_id: Annotated[str, Field(description="Site id listed by describe_dataset, e.g. 'SYN-VALLEY'.")],
    start: Annotated[str | None, Field(description="First month to include, 'YYYY-MM'. Omit for no lower bound.")] = None,
    end: Annotated[str | None, Field(description="Last month to include, 'YYYY-MM' (inclusive). Omit for no upper bound.")] = None,
    include_suspect: Annotated[bool, Field(description="Use observations whose QC flag is not 'good'. Default false.")] = False,
) -> dict[str, Any]:
    """Compare monthly model values with observations at one site.

    Matches months on (site_id, YYYY-MM), converts model units to observation units,
    excludes missing values and non-good QC flags, then returns n_valid_pairs,
    matched_months, mean_bias = mean(model - observation), rmse, units, the months
    excluded and why, the alignment rule, warnings, and provenance of both inputs.
    Fails with an explanation if ids are wrong, variables or units are incompatible,
    the period is invalid, or no valid pairs remain.
    """
    log.info("compare_model_to_obs site=%s obs=%s model=%s", site_id, obs_dataset_id, model_dataset_id)
    return _run(science.compare_model_to_obs, obs_dataset_id, model_dataset_id, site_id, start, end, include_suspect)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="obs-model-starter MCP server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default=os.environ.get("OBS_MODEL_HOST", "127.0.0.1"),
                        help="HTTP bind address. Keep 127.0.0.1 on a laptop; containers use 0.0.0.0.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("OBS_MODEL_PORT", "8765")))
    args = parser.parse_args(argv)

    _get_catalog()  # fail fast if the fixtures are missing
    if args.transport == "stdio":
        log.info("starting %s %s on stdio", SERVER_NAME, SERVER_VERSION)
        mcp.run(transport="stdio")
    else:
        log.info("starting %s %s on http://%s:%d/mcp", SERVER_NAME, SERVER_VERSION, args.host, args.port)
        mcp.run(transport="streamable-http", host=args.host, port=args.port, stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
