"""Repository validation for contributions. No network, no LLM, no credentials.

    uv run python scripts/validate_repo.py            # all checks
    uv run python scripts/validate_repo.py --only links --only skills

Checks
    catalog      catalog/entries/*.yaml fields, enums, ids, paths, status separation
    files        required files in every servers/<name>/ and skills/<name>/
    skills       SKILL.md frontmatter (Agent Skills spec) and required sections
    deps         requirements.txt pins use == and match uv.lock
    secrets      no committed .env files, no secret-looking literals
    sizes        file size limits
    links        relative Markdown links and #anchors resolve
    tooltests    each server has tests that make real MCP tool calls
    index        catalog/index.md is up to date (scripts/catalog.py index)

Secret patterns adapted from eve-esa/mcp-tool-registry scripts/validate_pr.py (Apache-2.0).
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections.abc import Callable, Iterable
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", "dist",
             "verification", ".claude", ".mypy_cache", "wheelhouse"}
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_DATA_FILE_BYTES = 1 * 1024 * 1024

ARTIFACT_TYPES = {"mcp-server", "agent-skill"}
ORIGINS = {"event", "external"}
REVIEW = {"draft", "submitted", "in-review", "changes-requested", "accepted", "withdrawn", "external"}
LOCAL_RESULTS = {"pass", "partial", "fail", "not-run"}
PEER_RESULTS = {"pass", "partial", "fail", "blocked"}
HOSTING = {"not-hosted", "planned", "hosted", "external", "not-applicable"}
DATA_CLASSES = {"synthetic", "cached live response", "recorded demonstration", "live call", "real public data",
                "user-supplied"}
TRANSPORTS = {"stdio", "streamable-http"}
REQUIRED_FIELDS = ["id", "type", "origin", "title", "scientific_purpose", "team", "authors", "version", "source",
                   "license", "attribution", "data", "credentials", "network", "dependencies",
                   "requires_mcp_tools", "tools", "transports", "install", "run", "runtime", "example", "tests",
                   "status"]
SKILL_SECTIONS = ["When to use", "When not to use", "Required tools", "Procedure", "Expected output",
                  "Assumptions", "Limitations", "Example tasks"]
SERVER_FILES = ["README.md", "server.py", "requirements.txt", "tests"]
ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

_SECRET_PATTERNS = [
    (re.compile(r"""(?:password|passwd|pwd)\s*[=:]\s*["'][^"'\s]{8,}["']""", re.I), "hardcoded password"),
    (re.compile(r"""(?:api_key|apikey|api_secret|client_secret)\s*[=:]\s*["'][^"'\s]{8,}["']""", re.I), "hardcoded API key"),
    (re.compile(r"""(?:secret_key|secret)\s*[=:]\s*["'][^"'\s]{16,}["']""", re.I), "hardcoded secret"),
    (re.compile(r"""(?:access_token|auth_token|bearer)\s*[=:]\s*["'][^"'\s]{16,}["']""", re.I), "hardcoded token"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"ghp_[0-9A-Za-z]{36}"), "GitHub token"),
    (re.compile(r"sk-(?:ant-)?[0-9A-Za-z\-_]{20,}"), "API secret key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private key"),
]
_PLACEHOLDER = re.compile(r"(?:\$\{[A-Z_]+\}|<[^>]+>|your[-_]|example|placeholder|changeme|xxx|TBD)", re.I)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def iter_files(root: Path, suffixes: Iterable[str] | None = None) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() and (suffixes is None or path.suffix in suffixes):
            yield path


def load_entries(root: Path) -> dict[str, tuple[Path, dict]]:
    entries = {}
    for path in sorted((root / "catalog" / "entries").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        entries[path.stem] = (path, data)
    return entries


# --------------------------------------------------------------------------- catalog


def check_catalog(root: Path, rep: Report) -> None:
    entries = load_entries(root)
    if not entries:
        rep.error("catalog/entries has no entries")
    server_tools: dict[str, set[str]] = {}
    for path, e in entries.values():
        if e.get("type") == "mcp-server":
            client_name = e.get("client_name")
            if not client_name or not re.match(r"^[a-z0-9-]+$", str(client_name)):
                rep.error(f"{rel(path, root)}: mcp-server entries need client_name (the name used in .mcp.json)")
                continue
            server_tools[str(client_name)] = set(e.get("tools") or [])
    for stem, (path, e) in entries.items():
        where = rel(path, root)
        missing = [f for f in REQUIRED_FIELDS if f not in e]
        if missing:
            rep.error(f"{where}: missing fields {missing}")
            continue
        if e["id"] != stem:
            rep.error(f"{where}: id '{e['id']}' must equal the file name '{stem}'")
        if not ID_RE.match(str(e["id"])) or len(str(e["id"])) > 64:
            rep.error(f"{where}: id must be lowercase letters/digits separated by single hyphens, max 64 chars")
        if e["type"] not in ARTIFACT_TYPES:
            rep.error(f"{where}: type must be one of {sorted(ARTIFACT_TYPES)}")
        if e["origin"] not in ORIGINS:
            rep.error(f"{where}: origin must be one of {sorted(ORIGINS)}")
        for key in ("path", "ref"):
            if not (e.get("source") or {}).get(key):
                rep.error(f"{where}: source.{key} is required (use TBD-at-freeze before the freeze)")
        if e["origin"] == "event":
            src = root / e["source"]["path"]
            if not src.exists():
                rep.error(f"{where}: source.path {e['source']['path']} does not exist")
            expected_parent = "servers" if e["type"] == "mcp-server" else "skills"
            if src.parent.name != expected_parent or src.name != e["id"]:
                rep.error(f"{where}: source.path must be {expected_parent}/{e['id']}")
        classes = set((e.get("data") or {}).get("classes") or [])
        if not classes or not classes <= DATA_CLASSES:
            rep.error(f"{where}: data.classes must be a non-empty subset of {sorted(DATA_CLASSES)}")
        if e["type"] == "mcp-server":
            if not e["tools"]:
                rep.error(f"{where}: an mcp-server entry must list its tools")
            if not set(e["transports"]) <= TRANSPORTS or not e["transports"]:
                rep.error(f"{where}: transports must be a non-empty subset of {sorted(TRANSPORTS)}")
        if e["type"] == "agent-skill":
            for tool in e["requires_mcp_tools"]:
                m = re.match(r"^mcp__([a-z0-9-]+)__([A-Za-z0-9_]+)$", tool)
                if not m:
                    rep.error(f"{where}: requires_mcp_tools entry '{tool}' must look like mcp__<server>__<tool>")
                    continue
                server, name = m.groups()
                known = server_tools.get(server)
                if known is None:
                    rep.error(f"{where}: requires tool from server '{server}', but no catalog entry has client_name '{server}'")
                elif name not in known:
                    rep.error(f"{where}: server '{server}' does not list tool '{name}'")
        status = e["status"] or {}
        for key in ("review", "local_verification", "peer_testing", "hosting"):
            if key not in status:
                rep.error(f"{where}: status.{key} is required (keep the four status fields separate)")
        if status.get("review") not in REVIEW:
            rep.error(f"{where}: status.review must be one of {sorted(REVIEW)}")
        lv = status.get("local_verification") or {}
        if lv.get("result") not in LOCAL_RESULTS:
            rep.error(f"{where}: status.local_verification.result must be one of {sorted(LOCAL_RESULTS)}")
        for item in status.get("peer_testing") or []:
            if item.get("result") not in PEER_RESULTS:
                rep.error(f"{where}: peer_testing result must be one of {sorted(PEER_RESULTS)}")
            report = item.get("report")
            if not report or not (root / report).exists():
                rep.error(f"{where}: peer_testing report file '{report}' not found")
        hosting = status.get("hosting") or {}
        if hosting.get("status") not in HOSTING:
            rep.error(f"{where}: status.hosting.status must be one of {sorted(HOSTING)}")
        if hosting.get("status") == "hosted" and str(hosting.get("endpoint", "TBD")).upper().startswith("TBD"):
            rep.error(f"{where}: hosting.status 'hosted' requires a real endpoint")
        if e["origin"] == "event" and status.get("review") == "accepted" and lv.get("result") in ("fail", "not-run"):
            rep.error(f"{where}: an accepted entry needs local_verification pass or partial")
    for kind, folder in (("mcp-server", "servers"), ("agent-skill", "skills")):
        for d in sorted((root / folder).iterdir()) if (root / folder).exists() else []:
            if d.is_dir() and not d.name.startswith((".", "_")) and d.name not in entries:
                rep.error(f"{folder}/{d.name}: no catalog entry catalog/entries/{d.name}.yaml ({kind})")


# --------------------------------------------------------------------------- files and skills


def check_files(root: Path, rep: Report) -> None:
    for d in sorted((root / "servers").iterdir()):
        if not d.is_dir() or d.name.startswith((".", "_")):
            continue
        for f in SERVER_FILES:
            if not (d / f).exists():
                rep.error(f"servers/{d.name}: missing {f}")
        if not ID_RE.match(d.name):
            rep.error(f"servers/{d.name}: folder name must be lowercase-hyphenated")
        if not list((d / "tests").glob("test_*.py")):
            rep.error(f"servers/{d.name}/tests: no test_*.py files")
        server_py = d / "server.py"
        if server_py.exists():
            text = server_py.read_text(encoding="utf-8")
            if "@mcp.tool" not in text:
                rep.error(f"servers/{d.name}/server.py: defines no @mcp.tool")
            if "--transport" not in text or "stdio" not in text:
                rep.error(f"servers/{d.name}/server.py: must accept --transport stdio|http")
            if re.search(r"^\s*print\(", text, re.M) and "file=sys.stderr" not in text:
                rep.error(f"servers/{d.name}/server.py: print() to stdout corrupts stdio; log to stderr")
        py_modules = [p for p in d.glob("*.py") if p.name != "server.py"]
        if not py_modules:
            rep.warn(f"servers/{d.name}: keep science functions in a module separate from server.py")
        if not (d / "data" / "README.md").exists() and (d / "data").exists():
            rep.error(f"servers/{d.name}/data: add README.md with provenance and redistribution terms")
    for d in sorted((root / "skills").iterdir()):
        if d.is_dir() and not d.name.startswith((".", "_")) and not (d / "SKILL.md").exists():
            rep.error(f"skills/{d.name}: missing SKILL.md")


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end < 0:
        return None, text
    try:
        meta = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return None, text
    return meta, text[end + 4:]


def validate_skill(skill_dir: Path) -> list[str]:
    errs = []
    path = skill_dir / "SKILL.md"
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    if meta is None:
        return ["SKILL.md must start with YAML frontmatter between --- lines"]
    name = meta.get("name")
    if not isinstance(name, str) or not (1 <= len(name) <= 64) or not ID_RE.match(name):
        errs.append("name must be 1-64 chars of lowercase letters, digits and single hyphens")
    elif name != skill_dir.name:
        errs.append(f"name '{name}' must match the folder name '{skill_dir.name}'")
    desc = meta.get("description")
    if not isinstance(desc, str) or not (1 <= len(desc) <= 1024):
        errs.append("description must be a non-empty string of at most 1024 characters")
    elif "use when" not in desc.lower():
        errs.append("description should say when to use the skill ('Use when ...')")
    comp = meta.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or len(comp) > 500):
        errs.append("compatibility must be a string of at most 500 characters")
    md = meta.get("metadata")
    if md is not None and (not isinstance(md, dict) or not all(isinstance(v, str) for v in md.values())):
        errs.append("metadata must map string keys to string values (quote versions: \"0.1.0\")")
    at = meta.get("allowed-tools")
    if at is not None and not isinstance(at, str):
        errs.append("allowed-tools must be a space-separated string")
    headings = {h.strip().lower() for h in re.findall(r"^#{2,3}\s+(.+)$", body, re.M)}
    for section in SKILL_SECTIONS:
        if section.lower() not in headings:
            errs.append(f"missing section '## {section}'")
    if len(body.splitlines()) > 500:
        errs.append("SKILL.md body exceeds 500 lines; move detail to references/")
    for link in re.findall(r"\]\(([^)#\s]+)", body):
        if not re.match(r"^[a-z]+://", link) and not (skill_dir / link).exists():
            errs.append(f"links to '{link}', which is not inside the skill folder")
    return errs


def check_skills(root: Path, rep: Report) -> None:
    for d in sorted((root / "skills").iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            for err in validate_skill(d):
                rep.error(f"skills/{d.name}/SKILL.md: {err}")


# --------------------------------------------------------------------------- deps, secrets, sizes


def check_deps(root: Path, rep: Report) -> None:
    lock_path = root / "uv.lock"
    locked: dict[str, str] = {}
    if lock_path.exists():
        lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))
        locked = {p["name"].lower().replace("_", "-"): p.get("version", "") for p in lock.get("package", [])}
    else:
        rep.error("uv.lock is missing; run `uv lock`")
    req_files = sorted((root / "servers").glob("*/requirements.txt"))
    if (root / "requirements.txt").exists():
        req_files.append(root / "requirements.txt")
    for req in req_files:
        for n, line in enumerate(req.read_text(encoding="utf-8").splitlines(), 1):
            line = line.split("#", 1)[0].strip()
            if not line or line.startswith(("-r ", "--")):
                continue
            if line.startswith(("-e", "file:", "git+", "http://", "https://")) or " @ " in line:
                rep.error(f"{rel(req, root)}:{n}: local, editable or URL installs are not allowed")
                continue
            m = re.match(r"^([A-Za-z0-9_.\-]+)(\[[^\]]+\])?==([^;\s]+)", line)
            if not m:
                rep.error(f"{rel(req, root)}:{n}: pin an exact version with == ('{line}')")
                continue
            name = m.group(1).lower().replace("_", "-")
            if name in locked and locked[name] != m.group(3):
                rep.error(f"{rel(req, root)}:{n}: {name}=={m.group(3)} differs from uv.lock ({locked[name]})")
            elif locked and name not in locked:
                rep.warn(f"{rel(req, root)}:{n}: {name} is not in uv.lock; add it to pyproject.toml or explain why")


def check_secrets(root: Path, rep: Report) -> None:
    for path in iter_files(root):
        name = path.name
        if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
            rep.error(f"{rel(path, root)}: environment files must not be committed (use .env.example)")
            continue
        if path.suffix in {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt", ".sh", ".ps1", ".example", ".cfg"} \
                or name == ".env.example":
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for n, line in enumerate(text.splitlines(), 1):
                for pattern, label in _SECRET_PATTERNS:
                    if pattern.search(line) and not _PLACEHOLDER.search(line) and "secret-scan: ignore" not in line:
                        rep.error(f"{rel(path, root)}:{n}: possible {label}")
            if name == ".env.example":
                for n, line in enumerate(text.splitlines(), 1):
                    if "=" in line and not line.lstrip().startswith("#"):
                        value = line.split("=", 1)[1].strip()
                        if value and not _PLACEHOLDER.search(value) and not re.match(r"^(https?://[^\s]+|\d+|[a-z0-9.\-]+|true|false)$", value, re.I):
                            rep.error(f".env.example:{n}: value looks like a real secret; use an empty value")


def check_sizes(root: Path, rep: Report) -> None:
    for path in iter_files(root):
        size = path.stat().st_size
        r = rel(path, root)
        if size > MAX_FILE_BYTES:
            rep.error(f"{r}: {size / 1e6:.1f} MB exceeds the 5 MB per-file limit")
        elif "/data/" in f"/{r}" and size > MAX_DATA_FILE_BYTES:
            rep.error(f"{r}: data fixtures must be under 1 MB; link to the source instead")


# --------------------------------------------------------------------------- links


def github_slug(heading: str) -> str:
    text = re.sub(r"`|\*\*|\*|_(?=\w)|\[|\]\([^)]*\)", "", heading.strip()).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_for(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    slugs: dict[str, int] = {}
    out = set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*$", text, re.M):
        slug = github_slug(heading)
        count = slugs.get(slug, 0)
        out.add(slug if count == 0 else f"{slug}-{count}")
        slugs[slug] = count + 1
    out |= set(re.findall(r'<a id="([^"]+)"', text))
    return out


def check_links(root: Path, rep: Report) -> None:
    link_re = re.compile(r"(?<!\!)\[[^\]]*\]\((<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\)")
    for md in iter_files(root, {".md"}):
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in link_re.findall(text):
            target = target.strip("<>")
            if re.match(r"^[a-z][a-z0-9+.\-]*:", target, re.I):
                continue
            file_part, _, anchor = target.partition("#")
            dest = md if not file_part else (md.parent / file_part).resolve()
            if file_part and not dest.exists():
                rep.error(f"{rel(md, root)}: broken link '{target}'")
                continue
            if anchor and dest.suffix == ".md" and anchor not in anchors_for(dest):
                rep.error(f"{rel(md, root)}: missing anchor '#{anchor}' in {rel(dest, root)}")


# --------------------------------------------------------------------------- tool tests and index


def check_tooltests(root: Path, rep: Report) -> None:
    for d in sorted((root / "servers").iterdir()):
        if not d.is_dir() or d.name.startswith((".", "_")):
            continue
        text = "\n".join(p.read_text(encoding="utf-8") for p in (d / "tests").glob("test_*.py"))
        if "call_tool(" not in text or "Client(" not in text:
            rep.error(f"servers/{d.name}/tests: add a test that calls a tool through an MCP Client (call_tool)")
        if "is_error" not in text:
            rep.error(f"servers/{d.name}/tests: add a test for an invalid-input case that checks is_error")


def check_index(root: Path, rep: Report) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import catalog as catalog_tool  # noqa: PLC0415

    current = (root / "catalog" / "index.md")
    expected = catalog_tool.render_index(root)
    if not current.exists() or current.read_text(encoding="utf-8") != expected:
        rep.error("catalog/index.md is out of date; run `uv run python scripts/catalog.py index`")


CHECKS: dict[str, Callable[[Path, Report], None]] = {
    "catalog": check_catalog,
    "files": check_files,
    "skills": check_skills,
    "deps": check_deps,
    "secrets": check_secrets,
    "sizes": check_sizes,
    "links": check_links,
    "tooltests": check_tooltests,
    "index": check_index,
}


def run(root: Path, only: list[str] | None = None) -> Report:
    rep = Report()
    for name, func in CHECKS.items():
        if only and name not in only:
            continue
        func(root, rep)
    return rep


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--only", action="append", choices=sorted(CHECKS))
    p.add_argument("--root", type=Path, default=REPO)
    args = p.parse_args(argv)
    rep = run(args.root.resolve(), args.only)
    for w in rep.warnings:
        print(f"WARNING {w}")
    for e in rep.errors:
        print(f"ERROR   {e}")
    checks = ", ".join(args.only or CHECKS)
    print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s) [{checks}]")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
