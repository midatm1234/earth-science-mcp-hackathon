"""Install, update, check or remove agent skills for Claude Code.

The canonical source of every skill is skills/<skill-name>/ in this repository.
Claude Code loads skills from .claude/skills/<skill-name>/ (project scope) or
~/.claude/skills/<skill-name>/ (personal scope). This script copies the
canonical folder there and writes a marker so later updates are safe.

    uv run python scripts/install_skills.py                      # install/update all, project scope
    uv run python scripts/install_skills.py obs-model-comparison # one skill
    uv run python scripts/install_skills.py --personal           # ~/.claude/skills instead
    uv run python scripts/install_skills.py --check              # report missing or outdated copies
    uv run python scripts/install_skills.py --remove NAME        # uninstall a copy

Never edit the installed copy: edit skills/<name>/ and re-run this script.
Copies (not symlinks) are used so the same command works on Windows.
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


def tree_hash(folder: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != MARKER):
        h.update(path.relative_to(folder).as_posix().encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def available() -> list[str]:
    return sorted(p.name for p in SOURCE.iterdir() if (p / "SKILL.md").is_file())


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("names", nargs="*", help="skill names (default: all in skills/)")
    p.add_argument("--personal", action="store_true", help="install to ~/.claude/skills")
    p.add_argument("--target", type=Path, help="explicit target skills folder (advanced)")
    p.add_argument("--check", action="store_true")
    p.add_argument("--remove", action="store_true")
    p.add_argument("--force", action="store_true", help="overwrite a folder not installed by this script")
    args = p.parse_args(argv)

    target_root = args.target or (Path.home() / ".claude" / "skills" if args.personal else REPO / ".claude" / "skills")
    names = args.names or available()
    unknown = [n for n in names if n not in available()]
    if unknown and not args.remove:
        print(f"Unknown skill(s): {', '.join(unknown)}. Available: {', '.join(available())}", file=sys.stderr)
        return 2

    problems = 0
    for name in names:
        src, dst = SOURCE / name, target_root / name
        marker = dst / MARKER
        if args.remove:
            if dst.exists() and (marker.exists() or args.force):
                shutil.rmtree(dst)
                print(f"removed  {dst}")
            elif dst.exists():
                print(f"skipped  {dst} (not installed by this script; use --force)")
            continue
        want = tree_hash(src)
        if args.check:
            if not dst.exists():
                print(f"MISSING  {name} -> {dst}")
                problems += 1
            elif not marker.exists() or marker.read_text().strip() != want or tree_hash(dst) != want:
                print(f"OUTDATED {name} -> {dst} (re-run without --check)")
                problems += 1
            else:
                print(f"ok       {name}")
            continue
        if dst.exists() and not marker.exists() and not args.force:
            print(f"skipped  {dst} exists and was not installed by this script; use --force", file=sys.stderr)
            problems += 1
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        marker.write_text(want + "\n")
        print(f"installed {name} -> {dst}")
    if not args.check and not args.remove and problems == 0:
        print("Restart Claude Code (or start a new session) so it loads the updated skills.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
