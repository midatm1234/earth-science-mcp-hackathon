"""Acceptance checks for the starter MCP server and skills in Claude Code, GitHub Copilot or Codex.

Needs the chosen assistant installed and signed in, and network access. Each run
makes a few short model requests, which count toward that account's usage.
Nothing else in the repository needs an AI assistant.

    uv run python scripts/verify_agent_workflow.py --client claude
    uv run python scripts/verify_agent_workflow.py --client copilot
    uv run python scripts/verify_agent_workflow.py --client codex
    uv run python scripts/verify_agent_workflow.py --client codex --only mcp --only negative

Checks
    mcp       the model calls compare_model_to_obs through MCP and reports its numbers
    explicit  the obs-model-comparison skill invoked explicitly (/name or $name)
    natural   a natural-language request that should trigger obs-model-comparison
    negative  a request where the skill and the starter tools should NOT be used
    combined  earth-data-discovery skill + Earthdata MCP + starter server in one session

Which executable is used (override with --exe):
    claude    `claude` on PATH (Claude Code CLI; the VS Code extension uses the same engine)
    copilot   `copilot` on PATH (GitHub Copilot CLI; same agent runtime as VS Code's Copilot harness)
    codex     `codex` on PATH, else the CLI bundled in the OpenAI Codex VS Code extension

Prerequisites per client
    claude    approve the project MCP servers once (run `claude` in this folder)
    copilot   signed in (`copilot` then /login, or GH_TOKEN); the folder is trusted for the run (--trust-folder)
    codex     signed in (`codex login`); this folder trusted once (run `codex` here and accept)

Traces go to verification/<client>/ (git-ignored); the summary is printed and saved as summary.json.
Statuses: pass, fail, or blocked (assistant not installed, not signed in, or unreachable).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "servers" / "obs-model-starter"))
import science  # noqa: E402

STARTER = "obs-model-starter"
SKILL = "obs-model-comparison"
DISCOVERY = "earth-data-discovery"


def expected(model: str, site: str, start: str | None = None, end: str | None = None) -> dict:
    out = science.compare_model_to_obs(science.load_catalog(), "syn-station-tas-monthly", model, site, start, end)
    return {k: out[k] for k in ("n_valid_pairs", "mean_bias", "rmse")}


def number_variants(value: float) -> list[str]:
    a = abs(value)
    return sorted({f"{a:.3f}", f"{a:.2f}"})


def checks(invoke: str) -> dict[str, dict]:
    a_valley = expected("syn-model-a-tas-monthly", "SYN-VALLEY")
    b_mountain = expected("syn-model-b-tas-monthly", "SYN-MOUNTAIN", "2021-01", "2021-12")
    return {
        "mcp": {
            "prompt": "Use the obs-model-starter MCP tool compare_model_to_obs with obs_dataset_id "
                      "syn-station-tas-monthly, model_dataset_id syn-model-a-tas-monthly, site_id SYN-VALLEY. "
                      "Do not use a shell. Reply with only n_valid_pairs, mean_bias and rmse.",
            "expect_tools": [f"{STARTER}/compare_model_to_obs"],
            "expect_numbers": [a_valley["mean_bias"], a_valley["rmse"]],
            "expect_text": [str(a_valley["n_valid_pairs"])],
        },
        "explicit": {
            "prompt": f"{invoke}{SKILL} Compare model A with the station observations at SYN-VALLEY.",
            "expect_skill": SKILL,
            "expect_tools": [f"{STARTER}/describe_dataset", f"{STARTER}/compare_model_to_obs"],
            "expect_numbers": [a_valley["mean_bias"], a_valley["rmse"]],
            "expect_text": ["synthetic", ("2020-07", "july 2020", "jul 2020")],
        },
        "natural": {
            "prompt": "How well does model run B match the station observations at the mountain site in 2021? "
                      "Give bias and RMSE.",
            "expect_skill": SKILL,
            "expect_tools": [f"{STARTER}/compare_model_to_obs"],
            "expect_numbers": [b_mountain["mean_bias"], b_mountain["rmse"]],
            "expect_text": ["synthetic"],
        },
        "negative": {
            "prompt": "In one sentence, what does RMSE stand for? Do not use any tools.",
            "forbid_skill": SKILL,
            "forbid_tool_prefix": f"{STARTER}/",
            "expect_text": ["root"],
        },
        "combined": {
            "prompt": f"{invoke}{DISCOVERY} Is monthly 2 m air temperature from MERRA-2 (short name M2TMNXSLV) "
                      "available for POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33)) in 2020? Then name the "
                      "obs-model-starter tool that could compare such a model with station observations. "
                      "Keep the answer short.",
            "expect_skill": DISCOVERY,
            "expect_tools": ["earthdata/get_granules"],
            "expect_text": ["12", "compare_model_to_obs"],
        },
    }


@dataclass
class Run:
    returncode: int
    tools: list[str] = field(default_factory=list)       # "server/tool" for MCP, plain name otherwise
    skills: list[str] = field(default_factory=list)
    answer: str = ""
    info: dict = field(default_factory=dict)
    error: str = ""


# --------------------------------------------------------------------------- clients


def find_codex() -> str | None:
    if shutil.which("codex"):
        return shutil.which("codex")
    patterns = [
        "~/.vscode/extensions/openai.chatgpt-*/bin/*/codex",
        "~/.vscode/extensions/openai.chatgpt-*/bin/*/codex.exe",
    ]
    hits = sorted(h for p in patterns for h in glob.glob(os.path.expanduser(p)))
    return hits[-1] if hits else None


def run_claude(exe: str, prompt: str, trace: Path) -> Run:
    cmd = [exe, "-p", prompt, "--mcp-config", str(REPO / ".mcp.json"), "--strict-mcp-config",
           "--output-format", "stream-json", "--verbose", "--max-turns", "20",
           "--allowedTools", f"Skill,mcp__{STARTER}__*,mcp__earthdata__*,Read,Grep,Glob"]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=900)
    trace.write_text(proc.stdout, encoding="utf-8")
    run = Run(proc.returncode, error=proc.stderr[-300:])
    for line in proc.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "system" and msg.get("subtype") == "init":
            run.info = {"version": msg.get("claude_code_version"), "model": msg.get("model"),
                        "auth": msg.get("apiKeySource"), "mcp_servers": msg.get("mcp_servers")}
        elif msg.get("type") == "assistant":
            for block in msg["message"].get("content", []):
                if block.get("type") == "tool_use":
                    name = block["name"]
                    if name.startswith("mcp__"):
                        _, server, tool = name.split("__", 2)
                        name = f"{server}/{tool}"
                    run.tools.append(name)
                    if block["name"] == "Skill":
                        run.skills.append(str(block.get("input", {}).get("skill", "")))
        elif msg.get("type") == "result":
            run.answer = msg.get("result", "") or ""
    if prompt.startswith("/"):
        run.skills.append(prompt[1:].split()[0])  # slash commands expand the skill before the model runs
    return run


def run_copilot(exe: str, prompt: str, trace: Path) -> Run:
    cmd = [exe, "-p", prompt, "--trust-folder", "--output-format", "json", "--no-color",
           "--allow-all-tools", "--deny-tool", "shell", "--deny-tool", "write"]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=900)
    trace.write_text(proc.stdout, encoding="utf-8")
    run = Run(proc.returncode, error=proc.stderr[-300:])
    servers = {}
    for line in proc.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind, data = msg.get("type"), msg.get("data", {})
        if kind == "tool.execution_start":
            if data.get("mcpServerName"):
                run.tools.append(f"{data['mcpServerName']}/{data.get('mcpToolName')}")
            else:
                run.tools.append(data.get("toolName", ""))
                if data.get("toolName") == "skill":
                    run.skills.append(str((data.get("arguments") or {}).get("skill", "")))
        elif kind == "session.mcp_server_tools_loaded":
            servers[data.get("serverName")] = data.get("toolCount")
        elif kind == "assistant.message" and data.get("content"):
            run.answer = data["content"]
            run.info.setdefault("model", data.get("model"))
    run.info["mcp_servers_tool_counts"] = servers
    if prompt.startswith("/"):
        requested = prompt[1:].split()[0]
        if f'<skill-context name=\\"{requested}\\"' in proc.stdout or f'<skill-context name="{requested}"' in proc.stdout:
            run.skills.append(requested)  # slash command expanded the skill into the request
    version = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.strip().splitlines()
    run.info["version"] = version[0] if version else None
    return run


def run_codex(exe: str, prompt: str, trace: Path) -> Run:
    # --skip-git-repo-check: the event bundle (ZIP) is not a Git repository; project trust still applies.
    cmd = [exe, "exec", "--json", "--skip-git-repo-check", "-s", "read-only", "-c", 'model_reasoning_effort="low"', prompt]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    trace.write_text(proc.stdout, encoding="utf-8")
    run = Run(proc.returncode, error=proc.stderr[-300:])
    for line in proc.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = msg.get("item", {})
        if msg.get("type") == "item.completed":
            if item.get("type") == "mcp_tool_call":
                run.tools.append(f"{item.get('server')}/{item.get('tool')}")
            elif item.get("type") == "command_execution":
                command = item.get("command", "")
                run.tools.append("shell")
                for skill in (SKILL, DISCOVERY):
                    if f"skills/{skill}/SKILL.md" in command:
                        run.skills.append(skill)
            elif item.get("type") == "agent_message":
                run.answer = item.get("text", "")
        elif msg.get("type") in ("turn.failed", "error"):
            run.error = json.dumps(msg)[:300]
    if prompt.startswith("$"):
        run.skills.append(prompt[1:].split()[0])  # $name attaches the skill to the request
    version = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.strip()
    run.info["version"] = version
    return run


CLIENTS = {
    "claude": {"invoke": "/", "find": lambda: shutil.which("claude"), "run": run_claude},
    "copilot": {"invoke": "/", "find": lambda: shutil.which("copilot"), "run": run_copilot},
    "codex": {"invoke": "$", "find": find_codex, "run": run_codex},
}


# --------------------------------------------------------------------------- evaluation


def evaluate(name: str, spec: dict, run: Run) -> dict:
    failures: list[str] = []
    blocked = False
    low = run.answer.lower().replace("\u2212", "-")
    if run.returncode != 0 or "api error" in low or not run.answer:
        blocked = not run.tools
        failures.append(f"assistant exited {run.returncode}: {(run.answer or run.error)[:200]}")
    for tool in spec.get("expect_tools", []):
        if tool not in run.tools:
            failures.append(f"expected MCP tool {tool} was not called")
    if spec.get("expect_skill") and spec["expect_skill"] not in run.skills:
        failures.append(f"skill {spec['expect_skill']} not invoked (skills seen: {run.skills})")
    if spec.get("forbid_skill") and spec["forbid_skill"] in run.skills:
        failures.append(f"skill {spec['forbid_skill']} was used but should not apply")
    if spec.get("forbid_tool_prefix") and any(t.startswith(spec["forbid_tool_prefix"]) for t in run.tools):
        failures.append("starter MCP tools were called but should not have been")
    for value in spec.get("expect_numbers", []):
        if not any(v in low for v in number_variants(value)):
            failures.append(f"answer lacks {value} (accepted: {number_variants(value)})")
    for text in spec.get("expect_text", []):
        options = text if isinstance(text, tuple) else (text,)
        if not any(o.lower() in low for o in options):
            failures.append(f"answer lacks any of {options}")
    status = "pass" if not failures else ("blocked" if blocked else "fail")
    return {"check": name, "status": status, "failures": failures, "tools_called": run.tools,
            "skills_invoked": run.skills, "client_info": run.info, "answer_excerpt": run.answer[:500]}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--client", choices=sorted(CLIENTS), required=True)
    p.add_argument("--only", action="append", choices=["mcp", "explicit", "natural", "negative", "combined"])
    p.add_argument("--exe", help="path to the assistant's CLI executable")
    args = p.parse_args(argv)

    client = CLIENTS[args.client]
    exe = args.exe or client["find"]()
    if not exe:
        print(f"{args.client}: CLI not found. See docs/setup.md, or pass --exe.", file=sys.stderr)
        return 2
    if not shutil.which("uv"):
        print("uv is not on PATH; the MCP configuration starts the starter server with uv.", file=sys.stderr)
        return 2
    out_dir = REPO / "verification" / args.client
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = checks(client["invoke"])
    results = []
    for name in args.only or list(specs):
        print(f"running {args.client}/{name} ...", file=sys.stderr, flush=True)
        try:
            run = client["run"](exe, specs[name]["prompt"], out_dir / f"{name}.jsonl")
        except subprocess.TimeoutExpired:
            run = Run(124, error="timed out after 900 s")
        results.append(evaluate(name, specs[name], run))
    summary = {"client": args.client, "executable": exe, "run_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "platform": sys.platform, "results": results}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for r in results:
        print(f"{r['status'].upper():7} {args.client}/{r['check']:9} tools={r['tools_called']} skills={r['skills_invoked']}")
        for f in r["failures"]:
            print(f"        - {f}")
    print(f"\nTraces and summary: {out_dir.relative_to(REPO)}/")
    return 0 if all(r["status"] == "pass" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
