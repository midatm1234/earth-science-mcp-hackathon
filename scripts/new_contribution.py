"""Create a team's contribution folders from the templates.

    uv run python scripts/new_contribution.py --team river-rats --server river-flow-tools --skill river-flow-check

Creates (and never overwrites):
    servers/<server>/                 from templates/mcp-server/ (runnable, tests pass)
    skills/<skill>/SKILL.md           from templates/agent-skill/
    catalog/entries/<server>.yaml     status: draft
    catalog/entries/<skill>.yaml      status: draft
    submissions/<team>/               discovery-record.md, submission.md, demo.md
and registers the new server in .mcp.json (Claude Code, Copilot) and
.codex/config.toml (Codex), so every supported assistant can start it.

Use --server only, or --skill only with --uses-server, to create one artifact.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import client_config

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / "templates"
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".txt", ".json", ".csv"}


def _check_name(kind: str, name: str) -> None:
    if not NAME_RE.match(name) or not 3 <= len(name) <= 40:
        raise SystemExit(f"{kind} name '{name}' must be 3-40 characters: lowercase letters and digits "
                         "separated by single hyphens, starting with a letter (e.g. 'river-flow-tools').")


def _fill(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace(key, value)
    return text


def _copy_tree(src: Path, dst: Path, values: dict[str, str], skip: set[str]) -> None:
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if rel.as_posix() in skip or "__pycache__" in rel.parts:
            continue
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.suffix in TEXT_SUFFIXES:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_fill(path.read_text(encoding="utf-8"), values), encoding="utf-8", newline="\n")
        else:
            shutil.copy2(path, target)


def _refuse_existing(root: Path, *paths: Path) -> None:
    existing = [p for p in paths if p.exists()]
    if existing:
        raise SystemExit("Already exists, not overwriting: " + ", ".join(str(p.relative_to(root)) for p in existing))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--team", required=True, help="team slug, e.g. river-rats")
    p.add_argument("--server", help="new MCP server name")
    p.add_argument("--skill", help="new agent skill name")
    p.add_argument("--uses-server", help="server the skill uses (defaults to --server)")
    p.add_argument("--root", type=Path, default=REPO, help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    root = args.root.resolve()

    _check_name("team", args.team)
    if not args.server and not args.skill:
        p.error("give --server, --skill, or both")
    server_for_skill = args.uses_server or args.server
    if args.skill and not server_for_skill:
        p.error("--skill needs --server or --uses-server")
    for kind, name in (("server", args.server), ("skill", args.skill)):
        if name:
            _check_name(kind, name)
    if args.server and args.skill and args.server == args.skill:
        p.error("server and skill need different names (e.g. 'river-flow-tools' and 'river-flow-check')")

    values = {"__SERVER_NAME__": server_for_skill or "", "__SKILL_NAME__": args.skill or "",
              "__TEAM__": args.team, "__DATE__": date.today().isoformat()}
    created: list[str] = []
    entries = root / "catalog" / "entries"

    if args.server:
        dst = root / "servers" / args.server
        _refuse_existing(root, dst, entries / f"{args.server}.yaml")
        _copy_tree(TEMPLATES / "mcp-server", dst, values, skip={"catalog-entry.yaml"})
        (entries / f"{args.server}.yaml").write_text(
            _fill((TEMPLATES / "mcp-server" / "catalog-entry.yaml").read_text(encoding="utf-8"), values),
            encoding="utf-8", newline="\n")
        created += [f"servers/{args.server}/", f"catalog/entries/{args.server}.yaml"]
        created += [f"{f} (registered {args.server})" for f in client_config.register_stdio_server(root, args.server)]

    if args.skill:
        dst = root / "skills" / args.skill
        _refuse_existing(root, dst, entries / f"{args.skill}.yaml")
        _copy_tree(TEMPLATES / "agent-skill", dst, values, skip={"catalog-entry.yaml"})
        (entries / f"{args.skill}.yaml").write_text(
            _fill((TEMPLATES / "agent-skill" / "catalog-entry.yaml").read_text(encoding="utf-8"), values),
            encoding="utf-8", newline="\n")
        created += [f"skills/{args.skill}/", f"catalog/entries/{args.skill}.yaml"]

    sub = root / "submissions" / args.team
    sub.mkdir(parents=True, exist_ok=True)
    for name in ("discovery-record.md", "submission.md", "demo.md"):
        target = sub / name
        if not target.exists():
            text = (TEMPLATES / name).read_text(encoding="utf-8")
            text = text.replace("](../", "](../../")  # templates/ is one level shallower than submissions/<team>/
            target.write_text(text, encoding="utf-8", newline="\n")
            created.append(f"submissions/{args.team}/{name}")

    print("Created:\n  " + "\n  ".join(created))
    print("\nNext steps:")
    if args.server:
        print(f"  uv run pytest servers/{args.server}/tests        # template tests should pass now")
    if args.skill:
        print(f"  uv run python scripts/install_skills.py {args.skill}")
    if args.server:
        print("  Start a new session in your AI assistant so it starts the new server")
    print("  uv run python scripts/catalog.py index")
    print("  uv run python scripts/check_all.py")
    print(f"  Fill in submissions/{args.team}/discovery-record.md before changing the code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
