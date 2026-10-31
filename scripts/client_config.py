"""Read and update the MCP client configurations shared by all supported assistants.

    .mcp.json            Claude Code, GitHub Copilot (VS Code Copilot harness, Copilot CLI), VS Code Claude harness
    .codex/config.toml   Codex CLI and the OpenAI Codex extension for VS Code

Both files must list the same servers with the same launch command. All
assistants start stdio servers from the repository root, so paths are relative
to it.

    uv run python scripts/client_config.py register <server-name>   # add servers/<name> for every assistant
    uv run python scripts/client_config.py check                    # both files agree
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

MCP_JSON = ".mcp.json"
CODEX_TOML = ".codex/config.toml"


def stdio_args(server: str) -> list[str]:
    return ["run", "--quiet", "python", f"servers/{server}/server.py", "--transport", "stdio"]


def load_mcp_json(root: Path) -> dict[str, dict]:
    path = root / MCP_JSON
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("mcpServers", {})


def load_codex(root: Path) -> dict[str, dict]:
    path = root / CODEX_TOML
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8")).get("mcp_servers", {})


def normalized(entry: dict) -> tuple:
    """Launch-relevant fields, comparable across the two formats."""
    if "url" in entry:
        return ("http", entry["url"])
    return ("stdio", entry.get("command"), tuple(entry.get("args", [])))


def differences(root: Path) -> list[str]:
    claude_copilot, codex = load_mcp_json(root), load_codex(root)
    problems = []
    for name in sorted(set(claude_copilot) | set(codex)):
        if name not in codex:
            problems.append(f"server '{name}' is in {MCP_JSON} but not in {CODEX_TOML}")
        elif name not in claude_copilot:
            problems.append(f"server '{name}' is in {CODEX_TOML} but not in {MCP_JSON}")
        elif normalized(claude_copilot[name]) != normalized(codex[name]):
            problems.append(f"server '{name}' is launched differently in {MCP_JSON} and {CODEX_TOML}")
    return problems


def register_stdio_server(root: Path, server: str) -> list[str]:
    """Add a local stdio server to both client configurations. Returns the files changed."""
    changed = []
    mcp_path = root / MCP_JSON
    data = json.loads(mcp_path.read_text(encoding="utf-8")) if mcp_path.exists() else {"mcpServers": {}}
    if server not in data.setdefault("mcpServers", {}):
        data["mcpServers"][server] = {"type": "stdio", "command": "uv", "args": stdio_args(server)}
        mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
        changed.append(MCP_JSON)
    toml_path = root / CODEX_TOML
    if server not in load_codex(root):
        toml_path.parent.mkdir(parents=True, exist_ok=True)
        args = ", ".join(json.dumps(a) for a in stdio_args(server))
        block = f'\n[mcp_servers.{server}]\ncommand = "uv"\nargs = [{args}]\nstartup_timeout_sec = 60\n'
        with toml_path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(block)
        changed.append(CODEX_TOML)
    return changed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Register MCP servers for Claude Code, Copilot and Codex.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("register")
    r.add_argument("server")
    sub.add_parser("check")
    args = p.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if args.cmd == "register":
        if not (root / "servers" / args.server / "server.py").exists():
            print(f"servers/{args.server}/server.py not found.", file=sys.stderr)
            return 1
        changed = register_stdio_server(root, args.server)
        print(f"registered {args.server} in: {', '.join(changed)}" if changed else f"{args.server} already registered")
        print("Start a new chat/session in your AI assistant so it starts the server.")
        return 0
    problems = differences(root)
    for problem in problems:
        print(f"ERROR {problem}")
    print("client configurations agree" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
