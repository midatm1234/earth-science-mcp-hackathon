"""Install, update, check or remove agent skills for Claude Code, GitHub Copilot and Codex.

The canonical source of every skill is skills/<skill-name>/ in this repository.
Each AI assistant looks for skills in its own folder:

    client    project folder (default)       personal folder (--personal)
    claude    .claude/skills/<name>/         ~/.claude/skills/<name>/
    codex     .agents/skills/<name>/         ~/.agents/skills/<name>/
    copilot   .agents/skills/<name>/         ~/.agents/skills/<name>/
              (VS Code Copilot also reads .claude/skills and .github/skills)

    uv run python scripts/install_skills.py                     # all clients (recommended)
    uv run python scripts/install_skills.py --client codex      # one client
    uv run python scripts/install_skills.py obs-model-comparison
    uv run python scripts/install_skills.py --personal
    uv run python scripts/install_skills.py --check             # report missing or outdated copies
    uv run python scripts/install_skills.py --remove NAME

Copilot shows a skill once even when it exists in both folders. Never edit an
installed copy: edit skills/<name>/ and re-run this script. Copies (not
symlinks) are used so the same command works on Windows.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "skills"
MARKER = ".installed-from-canonical"
CLIENT_DIRS = {"claude": ".claude", "codex": ".agents", "copilot": ".agents"}


def tree_hash(folder: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != MARKER):
        h.update(path.relative_to(folder).as_posix().encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def available() -> list[str]:
    return sorted(p.name for p in SOURCE.iterdir() if (p / "SKILL.md").is_file())


def target_roots(client: str, personal: bool, explicit: Path | None) -> list[Path]:
    if explicit:
        return [explicit]
    base = Path.home() if personal else REPO
    clients = list(CLIENT_DIRS) if client == "all" else [client]
    return sorted({base / CLIENT_DIRS[c] / "skills" for c in clients})


def process(name: str, target_root: Path, args: argparse.Namespace) -> int:
    src, dst = SOURCE / name, target_root / name
    marker = dst / MARKER
    if args.remove:
        if dst.exists() and (marker.exists() or args.force):
            shutil.rmtree(dst)
            print(f"removed   {dst}")
        elif dst.exists():
            print(f"skipped   {dst} (not installed by this script; use --force)")
        return 0
    want = tree_hash(src)
    if args.check:
        if not dst.exists():
            print(f"MISSING   {name} -> {dst}")
            return 1
        if not marker.exists() or marker.read_text().strip() != want or tree_hash(dst) != want:
            print(f"OUTDATED  {name} -> {dst} (re-run without --check)")
            return 1
        print(f"ok        {name} -> {dst}")
        return 0
    if dst.exists() and not marker.exists() and not args.force:
        print(f"skipped   {dst} exists and was not installed by this script; use --force", file=sys.stderr)
        return 1
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    marker.write_text(want + "\n")
    print(f"installed {name} -> {dst}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("names", nargs="*", help="skill names (default: all in skills/)")
    p.add_argument("--client", choices=["all", *CLIENT_DIRS], default="all",
                   help="which AI assistant to install for (default: all)")
    p.add_argument("--personal", action="store_true", help="install into your home folder instead of this project")
    p.add_argument("--target", type=Path, help="explicit target skills folder (advanced)")
    p.add_argument("--check", action="store_true")
    p.add_argument("--remove", action="store_true")
    p.add_argument("--force", action="store_true", help="overwrite a folder not installed by this script")
    args = p.parse_args(argv)

    names = args.names or available()
    unknown = [n for n in names if n not in available()]
    if unknown and not args.remove:
        print(f"Unknown skill(s): {', '.join(unknown)}. Available: {', '.join(available())}", file=sys.stderr)
        return 2

    problems = 0
    for root in target_roots(args.client, args.personal, args.target):
        for name in names:
            problems += process(name, root, args)
    if not args.check and not args.remove and problems == 0:
        print("Start a new chat or session in your AI assistant so it loads the updated skills.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
