"""Run the Claude Code acceptance checks for the starter MCP server and skills.

This needs an authenticated Claude Code (subscription sign-in for the event
workflow) and network access. It makes a few short model requests, which
count toward your Claude usage. Nothing else in the repository needs Claude.

    uv run python scripts/verify_claude_workflow.py            # all checks
    uv run python scripts/verify_claude_workflow.py --only mcp # just tool access

Each check runs `claude -p` with this repository's .mcp.json loaded explicitly
and records a JSON-lines trace under verification/claude/ (git-ignored). The
summary printed at the end is what goes into docs/validation-report.md.

Checks
    mcp       MCP tool access: the model calls compare_model_to_obs and reports its numbers
    explicit  /obs-model-comparison invoked explicitly
    natural   a natural-language request that should trigger obs-model-comparison
    negative  a request where obs-model-comparison should NOT be used
    combined  discovery skill + Earthdata MCP + starter server in one session
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "verification" / "claude"
STARTER = "mcp__obs-model-starter__"

CHECKS = {
    "mcp": {
        "prompt": "Use the obs-model-starter MCP tool compare_model_to_obs with obs_dataset_id "
                  "syn-station-tas-monthly, model_dataset_id syn-model-a-tas-monthly, site_id SYN-VALLEY. "
                  "Reply with only n_valid_pairs, mean_bias and rmse.",
        "allowed": [f"{STARTER}compare_model_to_obs"],
        "expect_tools": [f"{STARTER}compare_model_to_obs"],
        "expect_text": ["23", "-1.054", "1.212"],
    },
    "explicit": {
        "prompt": "/obs-model-comparison Compare model A with the station observations at SYN-VALLEY.",
        "allowed": [f"{STARTER}*"],
        "expect_skill": "obs-model-comparison",
        "expect_tools": [f"{STARTER}describe_dataset", f"{STARTER}compare_model_to_obs"],
        "expect_text": ["-1.05", "1.21", "synthetic"],
    },
    "natural": {
        "prompt": "How well does model run B match the station observations at the mountain site in 2021? "
                  "Give bias and RMSE.",
        "allowed": [f"{STARTER}*"],
        "expect_skill": "obs-model-comparison",
        "expect_tools": [f"{STARTER}compare_model_to_obs"],
        "expect_text": ["2021"],
    },
    "negative": {
        "prompt": "In one sentence, what does RMSE stand for? Do not use any tools.",
        "allowed": [f"{STARTER}*"],
        "forbid_skill": "obs-model-comparison",
        "forbid_tools_prefix": STARTER,
        "expect_text": ["root"],
    },
    "combined": {
        "prompt": "/earth-data-discovery Is monthly 2 m air temperature from MERRA-2 (short name M2TMNXSLV) "
                  "available for POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33)) in 2020? Then list which "
                  "tools in this repository's obs-model-starter server could compare such a model with station "
                  "observations. Keep the answer short.",
        "allowed": ["mcp__earthdata__*", f"{STARTER}*", "Read", "Grep", "Glob"],
        "expect_skill": "earth-data-discovery",
        "expect_tools": ["mcp__earthdata__get_granules"],
        "expect_text": ["12"],
    },
}


def run_check(name: str, spec: dict, model: str | None) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    trace = OUT / f"{name}.jsonl"
    cmd = ["claude", "-p", spec["prompt"], "--mcp-config", str(REPO / ".mcp.json"), "--strict-mcp-config",
           "--output-format", "stream-json", "--verbose", "--max-turns", "20",
           "--allowedTools", ",".join(["Skill", *spec["allowed"]])]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)
    trace.write_text(proc.stdout, encoding="utf-8")
    tools, skills, final, init = [], [], "", {}
    for line in proc.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "system" and msg.get("subtype") == "init":
            init = msg
        if msg.get("type") == "assistant":
            for block in msg["message"].get("content", []):
                if block.get("type") == "tool_use":
                    tools.append(block["name"])
                    if block["name"] == "Skill":
                        skills.append(str(block.get("input", {}).get("skill", "")))
        if msg.get("type") == "result":
            final = msg.get("result", "") or ""
    text_lower = final.lower()
    explicit_slash = spec["prompt"].startswith("/")
    failures = []
    if "API Error" in final or proc.returncode not in (0,):
        failures.append(f"claude exited {proc.returncode}: {final[:200] or proc.stderr[-200:]}")
    for t in spec.get("expect_tools", []):
        if t not in tools:
            failures.append(f"expected tool {t} not called")
    if spec.get("expect_skill") and not explicit_slash and spec["expect_skill"] not in " ".join(skills):
        failures.append(f"skill {spec['expect_skill']} not invoked (Skill calls: {skills})")
    if spec.get("forbid_skill") and spec["forbid_skill"] in " ".join(skills):
        failures.append(f"skill {spec['forbid_skill']} invoked but should not apply")
    if spec.get("forbid_tools_prefix") and any(t.startswith(spec["forbid_tools_prefix"]) for t in tools):
        failures.append("starter MCP tools were called but should not have been")
    for snippet in spec.get("expect_text", []):
        if snippet.lower() not in text_lower:
            failures.append(f"final answer lacks '{snippet}'")
    return {
        "check": name,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "tools_called": tools,
        "skills_invoked": skills,
        "mcp_servers": init.get("mcp_servers"),
        "claude_code_version": init.get("claude_code_version"),
        "model": init.get("model"),
        "auth_source": init.get("apiKeySource"),
        "trace": str(trace.relative_to(REPO)),
        "answer_excerpt": final[:400],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--only", choices=sorted(CHECKS), action="append")
    p.add_argument("--model", help="optional model alias, e.g. sonnet")
    args = p.parse_args(argv)
    if not shutil.which("claude"):
        print("claude is not on PATH. Install Claude Code first (docs/setup.md).", file=sys.stderr)
        return 2
    if not shutil.which("uv"):
        print("uv is not on PATH; .mcp.json starts the starter server with uv.", file=sys.stderr)
        return 2
    results = []
    for name in args.only or list(CHECKS):
        print(f"running {name} ...", file=sys.stderr)
        results.append(run_check(name, CHECKS[name], args.model))
    summary = {"run_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "results": results}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for r in results:
        print(f"{r['status'].upper():5} {r['check']:9} tools={r['tools_called']} skills={r['skills_invoked']}")
        for f in r["failures"]:
            print(f"      - {f}")
    print(f"\nTraces and summary: {OUT.relative_to(REPO)}/")
    return 0 if all(r["status"] == "pass" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
