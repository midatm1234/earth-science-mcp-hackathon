"""Query the public NASA Earthdata MCP server (live) and optionally save a cached record.

This is a plain MCP client: it does not use Claude and needs no credentials. It
shows the Discover -> Verify -> Inspect sequence used in tutorials/01.

    uv run python scripts/earthdata_probe.py --list-tools
    uv run python scripts/earthdata_probe.py --short-name M2TMNXSLV \
        --wkt "POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33))" \
        --start 2020-01-01 --end 2020-12-31 --variable T2M
    ... --save examples/data/cached/earthdata_discovery_merra2_t2m.json

Metadata discovery only. Downloading granules requires a free Earthdata Login
account and is a separate step (see docs/discovery-first.md).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mcp import Client

DEFAULT_URL = os.environ.get("EARTHDATA_MCP_URL", "https://cmr.earthdata.nasa.gov/mcp/v1")


def _payload(result) -> Any:
    if result.structured_content is not None:
        return result.structured_content
    text = "".join(getattr(c, "text", "") for c in result.content)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _slim_collection(c: dict) -> dict:
    keep = ("concept_id", "short_name", "version", "entry_title", "doi", "time_start", "time_end",
            "bounding_box", "processing_level_id", "data_centers", "platforms")
    return {k: c.get(k) for k in keep if k in c}


def _slim_granule(g: dict) -> dict:
    keep = ("concept_id", "title", "granule_ur", "time_start", "time_end", "producer_granule_id")
    return {k: g.get(k) for k in keep if k in g}


async def run(args: argparse.Namespace) -> dict:
    record: dict[str, Any] = {
        "record_class": "cached live response",
        "warning": "Saved output of a live query; CMR contents change. Re-run the probe for current results.",
        "retrieved_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endpoint": args.url,
        "calls": [],
    }
    async with Client(args.url, read_timeout_seconds=90) as client:
        record["protocol_version"] = client.protocol_version
        if args.list_tools:
            tools = await client.list_tools()
            record["tools"] = [t.name for t in tools.tools]
            return record

        async def call(name: str, arguments: dict) -> Any:
            result = await client.call_tool(name, arguments)
            data = _payload(result)
            entry = {"tool": name, "arguments": arguments, "is_error": result.is_error}
            record["calls"].append(entry)
            if result.is_error:
                entry["error"] = data
                raise SystemExit(f"{name} failed: {data}")
            return data, entry

        coll_args = {"has_granules": True, "limit": 3}
        if args.short_name:
            coll_args["short_name"] = args.short_name
        if args.keyword:
            coll_args["keyword"] = args.keyword
        data, entry = await call("get_collections", coll_args)
        collections = data.get("collections", []) if isinstance(data, dict) else []
        entry["total_hits"] = data.get("total_hits") if isinstance(data, dict) else None
        entry["collections"] = [_slim_collection(c) for c in collections]
        if not collections:
            return record
        concept_id = collections[0]["concept_id"]

        gran_args = {"collection_concept_id": concept_id, "limit": args.granule_limit}
        if args.start:
            gran_args["temporal_start_date"] = f"{args.start}T00:00:00Z"
        if args.end:
            gran_args["temporal_end_date"] = f"{args.end}T23:59:59Z"
        if args.wkt:
            gran_args["spatial_wkt_geometry"] = args.wkt
        data, entry = await call("get_granules", gran_args)
        entry["total_hits"] = data.get("total_hits") if isinstance(data, dict) else None
        entry["granules"] = [_slim_granule(g) for g in (data.get("granules", []) if isinstance(data, dict) else [])]

        if args.variable:
            data, entry = await call("get_variables", {"collection_concept_id": concept_id,
                                                       "keyword": args.variable, "limit": 3})
            entry["variables"] = data.get("variables", data) if isinstance(data, dict) else data
        for extra in ("get_services", "get_citations"):
            data, entry = await call(extra, {"collection_concept_id": concept_id, "limit": 3})
            entry["total_hits"] = data.get("total_hits") if isinstance(data, dict) else None
            key = "services" if extra == "get_services" else "citations"
            items = data.get(key, []) if isinstance(data, dict) else []
            entry[key] = [{k: i.get(k) for k in ("concept_id", "name", "type", "url", "identifier", "long_name")
                           if k in i} for i in items]
    return record


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--list-tools", action="store_true")
    p.add_argument("--short-name")
    p.add_argument("--keyword")
    p.add_argument("--wkt", help="WKT geometry, LONGITUDE first, counter-clockwise ring")
    p.add_argument("--start", help="YYYY-MM-DD")
    p.add_argument("--end", help="YYYY-MM-DD")
    p.add_argument("--variable")
    p.add_argument("--granule-limit", type=int, default=3)
    p.add_argument("--save", type=Path, help="write the record as JSON (cached live response)")
    args = p.parse_args(argv)
    if not (args.list_tools or args.short_name or args.keyword):
        p.error("give --list-tools, --short-name or --keyword")
    try:
        record = asyncio.run(run(args))
    except OSError as exc:
        print(f"Could not reach {args.url}: {exc}. Check your network or use the cached example in "
              "examples/data/cached/.", file=sys.stderr)
        return 2
    text = json.dumps(record, indent=2)
    if args.save:
        args.save.write_text(text + "\n", encoding="utf-8")
        print(f"saved {args.save}", file=sys.stderr)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
