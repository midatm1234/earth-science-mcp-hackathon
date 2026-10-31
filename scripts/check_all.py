"""Run every automated check. No network, no Claude, no credentials.

    uv run python scripts/check_all.py           # everything
    uv run python scripts/check_all.py --fast    # skip per-server test suites

Steps
    1. repository validation (scripts/validate_repo.py)
    2. synthetic fixtures match their generator
    3. each servers/<name>/tests suite, in its own process (contributions stay isolated)
    4. repository tooling tests (tests/)
    5. installed skill copies, if any, are up to date
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def step(title: str, cmd: list[str]) -> bool:
    print(f"\n=== {title}\n$ {' '.join(cmd)}", flush=True)
    ok = subprocess.run(cmd, cwd=REPO).returncode == 0
    print(f"--> {'PASS' if ok else 'FAIL'}: {title}", flush=True)
    return ok


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--fast", action="store_true")
    args = p.parse_args(argv)
    py = sys.executable
    results: dict[str, bool] = {}
    results["validate"] = step("repository validation", [py, "scripts/validate_repo.py"])
    results["fixtures"] = step("synthetic fixtures", [py, "scripts/generate_sample_data.py", "--check"])
    if not args.fast:
        for server in sorted((REPO / "servers").iterdir()):
            if (server / "tests").is_dir():
                results[f"server:{server.name}"] = step(
                    f"server tests: {server.name}",
                    [py, "-m", "pytest", "-p", "no:cacheprovider", "--rootdir", str(server), str(server / "tests")])
        results["tooling"] = step("tooling tests", [py, "-m", "pytest", "-p", "no:cacheprovider", "tests"])
    if (REPO / ".claude" / "skills").exists():
        results["skills-installed"] = step("installed skills current", [py, "scripts/install_skills.py", "--check"])

    print("\n=== Summary")
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in results.items() if not ok]
    print(f"\n{'ALL CHECKS PASSED' if not failed else 'FAILED: ' + ', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
