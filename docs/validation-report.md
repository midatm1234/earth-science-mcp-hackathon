# Validation report

Prepared 2026-10-30 (local time, UTC−7) during organizer preparation. Every row states what was actually run. Mock, fixture or documented-only checks are **not** reported as live integration tests.

## Environment

| Item | Value |
|---|---|
| Machine | macOS 27.0.1 (build 26A434), Apple silicon arm64 |
| uv | 0.13.6 |
| Python | 3.13.18, 3.11.18, 3.12.16, 3.14.10 (uv-managed); 3.13.12, 3.14.3 (Homebrew) |
| MCP SDK | `mcp==2.3.0` (lock: `uv.lock`, 39 packages) |
| Claude Code | 2.1.185, authenticated through an institutional API key helper (**not** a Claude subscription); its API gateway was unreachable from the test network |
| Network | Internet available; `cmr.earthdata.nasa.gov` reachable |

## Results

| # | Check | Command (from repository root unless noted) | Result |
|---|---|---|---|
| 1 | Full automated suite | `uv run python scripts/check_all.py` | **pass** – validation 0 errors; fixtures match generator; server tests 18 passed; tooling tests 13 passed |
| 2 | Lint | `uv run ruff check .` | **pass** |
| 3 | Lock reproducibility | `uv lock --check`; `uv export … \| diff requirements.txt` | **pass** |
| 4 | Clean environment (uv) | Event bundle unzipped to `/tmp/clean1`; `UV_CACHE_DIR` empty; `UV_PYTHON_PREFERENCE=only-managed`; `uv sync`; `first_call.py`; `check_all.py` | **pass** – Python 3.13.18 downloaded; `ALL CHECKS PASSED` |
| 5 | Other Python versions | same bundle; `uv sync --python 3.11/3.12/3.14`; `check_all.py` | **pass** on 3.11.18, 3.12.16, 3.14.10 |
| 6 | Clean environment (pip) | `/tmp/clean2`; Homebrew 3.14.3 `venv`; `pip install -r requirements.txt -r requirements-dev.txt`; `check_all.py` | **pass** |
| 7 | Offline wheelhouse | `/tmp/clean3`; organizer `uvx --python 3.13 pip download …` (35 wheels, 19 MB); participant `UV_OFFLINE=1 uv pip install --no-index --find-links wheelhouse …`; `uv run --no-sync python scripts/check_all.py` | **pass** after two fixes found by this test (pin the download Python; validator skips `wheelhouse/`) |
| 8 | Real MCP tool listing and invocation, in-process | `servers/obs-model-starter/tests/test_server.py` | **pass** – 3 tools listed with descriptions and output schemas; structured result; tool errors returned as `is_error` |
| 9 | stdio transport | pytest subprocess test; `uv run python scripts/first_call.py` | **pass** – 23 pairs, bias −1.054 °C, RMSE 1.212 °C for SYN-VALLEY / model A |
| 10 | stdout hygiene on stdio | `test_stdio_stdout_contains_only_protocol_messages` | **pass** – stdout only JSON-RPC; logs on stderr |
| 11 | Streamable HTTP transport | server `--transport http`; `first_call.py --http http://127.0.0.1:8765/mcp`; raw `curl` `initialize` and `tools/call` with `MCP-Protocol-Version: 2025-06-18` | **pass** – SYN-MOUNTAIN / model B: 23 pairs, bias −0.665 °C, RMSE 1.126 °C, `month_absent_from_obs: ["2020-12"]` |
| 12 | Independently checked science | `test_hand_computed_bias_and_rmse` (diffs +1, −1, +3 → bias 1.0, RMSE √(11/3)); `test_bundled_fixture_matches_independent_calculation` (separate raw-CSV recomputation, 3 sites × 2 models) | **pass** |
| 13 | Missing-data and alignment rules | tests for empty values, `-9999`, QC `suspect`, absent months, duplicate months, K→°C, period filter | **pass** |
| 14 | Skill package validity | `uvx --from skills-ref==0.1.1 agentskills validate skills/<name>`; `validate_repo.py --only skills` | **pass** for both skills |
| 15 | Skill installation | `install_skills.py`, `--check`, `--remove`, drift detection (tooling tests) | **pass** |
| 16 | Claude Code reads MCP config | `claude mcp list` → both project servers listed as *pending approval* (expected for `.mcp.json`) | **pass** |
| 17 | Claude Code connects MCP servers and discovers skills | `claude -p … --mcp-config <config> --output-format stream-json` session init, 4 consecutive sessions | **pass** – `obs-model-starter` and `earthdata` connected; `obs-model-comparison` and `earth-data-discovery` listed |
| 18 | Model-driven tool call, skill invocation (explicit, natural trigger, should-not-apply), combined workflow | `uv run python scripts/verify_claude_workflow.py` | **pending** – every run stopped at `API Error: Unable to connect to API (ConnectionRefused)`; the configured gateway is unreachable and is not a subscription. No model output was produced, so nothing is claimed. |
| 19 | Earthdata MCP live | `uv run python scripts/earthdata_probe.py --list-tools`; MERRA-2 M2TMNXSLV discovery | **pass** (live, 2026-10-31T04:18:59Z) – 7 tools; collection `C1276812859-GES_DISC`; 12 granules for 2020 in the polygon; `T2M` in K; Harmony/OPeNDAP services. Saved as a dated cached response. |
| 20 | Catalog validation | `validate_repo.py --only catalog --only index`; negative tests (fake hosted endpoint, bad peer result, unknown required tool) | **pass** |
| 21 | Relative documentation links and anchors | `validate_repo.py --only links` (all `.md` files) | **pass** – 0 broken links or anchors |
| 22 | Secrets, file sizes, dependency pins | validator + negative tests | **pass** |
| 23 | Tutorial 02 worked example | code blocks from the tutorial applied verbatim to a clean copy; tests added | **pass** – 20 tests; per-season bias returned |
| 24 | Submission and peer-testing flow | `/tmp/author`: scaffold → fill → `check_all` → `package.py contribution`; `/tmp/reviewer`: fresh bundle → `package.py verify` → unzip → `install_skills.py` → server tests → validator | **pass** after fixes found by this test (test-name collision; per-artifact manifest names) |
| 25 | Distribution bundle | `package.py bundle`; `package.py verify` | **pass** – 92 files, ~0.7 MB, deterministic archive with SHA-256 manifest |
| 26 | GitHub Actions | `.github/workflows/checks.yml` | **pending** – YAML parses and its commands pass locally; never run on GitHub (no remote) |

## Defects found and fixed during validation

| Found by | Defect | Fix |
|---|---|---|
| tooling test | `httpx>=…` misread as a URL install | URL check now requires `http://`/`https://` |
| tooling test | scaffold error path computed against the wrong root | `_refuse_existing` uses the target root |
| ruff | `# noqa: secret` marker conflicted with ruff syntax | marker renamed `# secret-scan: ignore` |
| offline test | wheelhouse downloaded for the wrong Python | `uvx --python 3.13 pip download` |
| offline test | size check scanned the git-ignored `wheelhouse/` | added to skip list |
| reviewer dry run | tooling test names could collide with real team names | test uses `zz-` names |
| reviewer dry run | `MANIFEST.json` from two packages overwrote each other at repo root | `<id>-<version>.MANIFEST.json`, git-ignored |
| Claude session debug log | intermittent `ImportError` in the server under Claude Code | cause: a globally exported `UV_PROJECT_ENVIRONMENT` was inherited by Claude Code's key helper, which synced a different project into the same venv. Test-setup artifact; documented in [troubleshooting](troubleshooting.md#mcp-server-not-connected) |

## Remaining manual checks (precise)

| # | Check | Who / how | Blocks |
|---|---|---|---|
| P1 | Claude **subscription** sign-in; `/status` shows the Claude account | organizer, rehearsal | participant path step 5 |
| P2 | `uv run python scripts/verify_claude_workflow.py` passes all five checks (MCP tool access, explicit, natural, negative, combined) with a subscription account; paste the printed summary here | organizer, rehearsal | skill catalog entries move from `partial` to `pass` |
| P3 | Windows 10/11 and Linux: START_HERE steps 1–5 and `check_all.py` | mentor laptops, or CI after push | compatibility rows |
| P4 | VS Code + Claude Code extension shows the same servers and skills | organizer | optional interface |
| P5 | GitHub Actions run green on all five matrix jobs | after the repository destination is decided | CI claim |
| P6 | MCP Inspector against the HTTP server | optional | – |
| P7 | Independent peer test of the starter by a non-author | mentor | catalog `peer_testing` (currently empty) |
| P8 | Shared server deployment | not planned until a host is authorized | `hosting` stays `not-hosted` |
| P9 | EVE Team 3 slides review | file not supplied | reference review |

## Readiness

| Area | Readiness |
|---|---|
| Laptop core path without AI (setup, first call, both transports, tests, scaffold, packaging) | **Ready** on macOS arm64; untested on Windows/Linux |
| Scientific starter and tests | **Ready** |
| Skills (format, install) | **Ready**; agent behaviour **unverified** (P2) |
| Claude Code integration | Client side **verified**; model-driven behaviour **pending** (P1, P2) |
| Discovery with Earthdata MCP | **Ready** (live verified; cached fallback) |
| Documentation and tutorials | **Complete**; links verified; worked examples executed |
| Submission, catalog, peer-testing workflow | **Ready** (dry run passed) |
| Remote repository, CI, hosting | **TBD** by organizer |
