"""Your first MCP tool call, without any AI model.

This script is an MCP *client*. It starts the obs-model-starter *server*,
asks it which tools it offers (tools/list), then calls one tool (tools/call)
and prints the structured result. If this works, your Python setup is correct.

    uv run python scripts/first_call.py                 # start server over stdio (default)
    uv run python scripts/first_call.py --http http://127.0.0.1:8765/mcp
    uv run python scripts/first_call.py --site SYN-MOUNTAIN --model syn-model-b-tas-monthly
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

REPO = Path(__file__).resolve().parents[1]
SERVER = REPO / "servers" / "obs-model-starter" / "server.py"


async def run(args: argparse.Namespace) -> int:
    if args.http:
        target = args.http
        how = f"Streamable HTTP at {args.http}"
    else:
        target = StdioServerParameters(command=sys.executable, args=[str(SERVER), "--transport", "stdio"])
        how = "stdio (this script started the server as a subprocess)"
    print(f"Connecting to obs-model-starter over {how} ...")
    async with Client(target, read_timeout_seconds=60) as client:
        tools = await client.list_tools()
        print("\nStep 1 - tools/list returned:")
        for tool in tools.tools:
            first_line = (tool.description or "").strip().splitlines()[0]
            print(f"  - {tool.name}: {first_line}")

        arguments = {"obs_dataset_id": "syn-station-tas-monthly", "model_dataset_id": args.model,
                     "site_id": args.site}
        print(f"\nStep 2 - tools/call compare_model_to_obs {json.dumps(arguments)}")
        result = await client.call_tool("compare_model_to_obs", arguments)
        if result.is_error:
            print("The tool returned an error (this is a normal, readable MCP error):")
            print("  " + result.content[0].text)
            return 1
        out = result.structured_content
        print("\nStep 3 - key results:")
        print(f"  site            : {out['site_id']}")
        print(f"  valid pairs     : {out['n_valid_pairs']}")
        print(f"  units           : {out['units']} (model conversion: {out['unit_conversion']['model']})")
        print(f"  mean bias       : {out['mean_bias']} {out['units']}  ({out['bias_definition']})")
        print(f"  RMSE            : {out['rmse']} {out['units']}")
        excluded = {k: v for k, v in out["excluded"].items() if v}
        print(f"  excluded months : {excluded or 'none'}")
        for w in out["warnings"]:
            print(f"  warning         : {w}")
        if args.json:
            print(json.dumps(out, indent=2))
    print("\nSuccess: you listed tools and called one through the Model Context Protocol.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--http", help="URL of an already running server, e.g. http://127.0.0.1:8765/mcp")
    p.add_argument("--site", default="SYN-VALLEY")
    p.add_argument("--model", default="syn-model-a-tas-monthly")
    p.add_argument("--json", action="store_true", help="also print the full structured result")
    args = p.parse_args(argv)
    try:
        return asyncio.run(run(args))
    except Exception as exc:  # beginner-facing: print a hint instead of a traceback
        print(f"\nFAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("See docs/troubleshooting.md (section 'First tool call').", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
