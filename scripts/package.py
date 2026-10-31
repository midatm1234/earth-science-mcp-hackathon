"""Package frozen contributions for review, peer testing and offline distribution.

    uv run python scripts/package.py contribution obs-model-starter
        -> dist/obs-model-starter-0.1.0.zip (+ .sha256), for peer testing and mentor upload

    uv run python scripts/package.py bundle
        -> dist/event-bundle-YYYYMMDD.zip with every catalog entry whose review is
           'accepted', the shared setup files, tutorials and a manifest of SHA-256 sums.
           Organizers publish this on a shared drive, USB stick or download page so
           participants need neither a GitHub account nor repository access.

    uv run python scripts/package.py verify dist/obs-model-starter-0.1.0.zip

The archive excludes caches, virtual environments, .env files and installed
skill copies. The SHA-256 printed here is the immutable reference recorded in
the catalog entry (source.ref) and in peer-test reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
DIST = REPO / "dist"
EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".venv", "venv", ".git", "dist", "verification", "wheelhouse",
                 ".claude", ".DS_Store"}
SHARED = ["README.md", "START_HERE.md", "CONTRIBUTING.md", "AGENTS.md", "CLAUDE.md", "pyproject.toml", "uv.lock",
          "requirements.txt", "requirements-dev.txt", ".python-version", ".mcp.json", ".codex/config.toml", ".env.example",
          ".gitignore",
          "LICENSE", "NOTICE", "docs", "tutorials", "templates", "scripts", "tests", "catalog", "examples",
          "submissions", "servers/README.md", "skills/README.md", ".github"]
FIXED_TIME = (2026, 1, 1, 0, 0, 0)  # deterministic archives: identical inputs give identical SHA-256


def _entry(entry_id: str) -> dict:
    path = REPO / "catalog" / "entries" / f"{entry_id}.yaml"
    if not path.exists():
        raise SystemExit(f"No catalog entry catalog/entries/{entry_id}.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _files(base: Path) -> list[Path]:
    candidates = [base] if base.is_file() else sorted(base.rglob("*"))
    out = []
    for p in candidates:
        if not p.is_file() or any(part in EXCLUDE_PARTS for part in p.relative_to(REPO).parts):
            continue
        if p.name.startswith(".env") and p.name != ".env.example":
            continue
        out.append(p)
    return out


def _write_zip(target: Path, files: list[Path], extra: dict[str, bytes]) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(set(files)):
            info = zipfile.ZipInfo(f.relative_to(REPO).as_posix(), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, f.read_bytes())
        for name, data in sorted(extra.items()):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(target.suffix + ".sha256").write_text(f"{digest}  {target.name}\n", encoding="utf-8")
    return digest


def _manifest(files: list[Path], meta: dict) -> bytes:
    return (json.dumps({**meta, "files": {f.relative_to(REPO).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
                                          for f in sorted(set(files))}}, indent=2) + "\n").encode()


def package_contribution(entry_id: str) -> tuple[Path, str]:
    e = _entry(entry_id)
    if e.get("origin") != "event":
        raise SystemExit(f"{entry_id} is external; nothing to package.")
    files = _files(REPO / e["source"]["path"]) + [REPO / "catalog" / "entries" / f"{entry_id}.yaml"]
    reports = [REPO / p["report"] for p in (e.get("status", {}).get("peer_testing") or []) if p.get("report")]
    files += [r for r in reports if r.exists()]
    target = DIST / f"{entry_id}-{e['version']}.zip"
    meta = {"artifact": entry_id, "type": e["type"], "version": e["version"], "source_ref": e["source"]["ref"]}
    digest = _write_zip(target, files, {f"{entry_id}-{e['version']}.MANIFEST.json": _manifest(files, meta)})
    return target, digest


def package_bundle() -> tuple[Path, str]:
    accepted = []
    for path in sorted((REPO / "catalog" / "entries").glob("*.yaml")):
        e = yaml.safe_load(path.read_text(encoding="utf-8"))
        if e.get("origin") == "event" and (e.get("status") or {}).get("review") == "accepted":
            accepted.append(e)
    files: list[Path] = []
    for item in SHARED:
        p = REPO / item
        if p.exists():
            files += _files(p)
    for e in accepted:
        files += _files(REPO / e["source"]["path"])
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    meta = {"bundle_created_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "accepted_artifacts": {e["id"]: {"version": e["version"], "source_ref": e["source"]["ref"]}
                                   for e in accepted}}
    target = DIST / f"event-bundle-{stamp}.zip"
    digest = _write_zip(target, files, {"BUNDLE_MANIFEST.json": _manifest(files, meta)})
    return target, digest


def verify(archive: Path) -> int:
    sidecar = archive.with_suffix(archive.suffix + ".sha256")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if sidecar.exists():
        expected = sidecar.read_text().split()[0]
        if expected != digest:
            print(f"MISMATCH: {archive.name} sha256 {digest} != {expected}")
            return 1
    with zipfile.ZipFile(archive) as zf:
        manifest_name = next(n for n in zf.namelist() if n.endswith("MANIFEST.json") and "/" not in n)
        manifest = json.loads(zf.read(manifest_name))
        for name, sha in manifest["files"].items():
            if hashlib.sha256(zf.read(name)).hexdigest() != sha:
                print(f"MISMATCH inside archive: {name}")
                return 1
    print(f"OK {archive.name} sha256 {digest} ({len(manifest['files'])} files)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("contribution")
    c.add_argument("id")
    sub.add_parser("bundle")
    v = sub.add_parser("verify")
    v.add_argument("archive", type=Path)
    args = p.parse_args(argv)
    if args.cmd == "contribution":
        target, digest = package_contribution(args.id)
    elif args.cmd == "bundle":
        target, digest = package_bundle()
    else:
        return verify(args.archive)
    print(f"wrote {target.relative_to(REPO)}\nsha256 {digest}")
    print("Record this sha256 as the frozen reference (catalog source.ref or peer-test report).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
