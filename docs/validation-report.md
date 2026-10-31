# Validation report

Prepared 2026-10-30 (local time, UTC−7) during organizer preparation. Every row states what was actually run. Mock, fixture or documented-only checks are **not** reported as live integration tests.

## Environment

| Item | Value |
|---|---|
| Machine | macOS 27.0.1 (build 26A434), Apple silicon arm64 |
| uv | 0.13.6 |
| Python | 3.13.18, 3.11.18, 3.12.16, 3.14.10 (uv-managed); 3.13.12, 3.14.3 (Homebrew) |
| MCP SDK | `mcp==2.3.0` (lock: `uv.lock`, 39 packages) |
| VS Code | 1.144.0, with Copilot Chat (built in), Claude Code extension 2.1.314, OpenAI Codex extension 26.51021.22027 |
| GitHub Copilot | Copilot CLI 1.0.105 (npm `@github/copilot`), GitHub sign-in; model claude-sonnet-5.5 routed by Copilot |
| Codex | codex-cli 0.164.0-alpha.11.1 bundled in the Codex VS Code extension, ChatGPT sign-in |
| Claude Code | CLI 2.1.185, authenticated through an institutional API key helper (**not** a Claude subscription); its API gateway was unreachable from the test network |
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
| 18a | **GitHub Copilot**: real MCP call, explicit skill, natural trigger, should-not-apply, combined Earthdata workflow | `uv run python scripts/verify_agent_workflow.py --client copilot` (clean clone `/tmp/esmh`) | **pass 5/5** – MCP calls `obs-model-starter/compare_model_to_obs` etc.; `skill` tool invoked for `obs-model-comparison`; negative case called no tools; combined called `earthdata/get_collections`, `get_granules`, `get_variables` |
| 18b | **Codex**: same five checks | `CODEX_HOME=<trusted> uv run python scripts/verify_agent_workflow.py --client codex` | **pass 5/5** (explicit first failed only because the answer said "July 2020" instead of "2020-07"; the check was widened and re-run: pass) |
| 18c | **Claude Code**: same checks | `uv run python scripts/verify_agent_workflow.py --client claude --only mcp --only explicit` | **blocked** – both MCP servers `connected`, skills listed; every request ended `API Error: Unable to connect to API (ConnectionRefused)`. Nothing claimed. |
| 18d | Copilot without folder trust | `copilot -p … --allow-all-tools` (no `--trust-folder`) | MCP servers **not** loaded; the model ran `scripts/first_call.py` via the shell and reported correct numbers. Documented as a failure mode: correct numbers are not proof of MCP use |
| 18e | Codex without project trust | `codex exec` with trust only as a `-c` override | `.codex/config.toml` **ignored**; trust must be recorded in `~/.codex/config.toml` (what Codex's trust prompt writes) |
| 18f | Team scaffold reaches every assistant | `new_contribution.py --server river-flow-tools …` then a `summarize_values` request via Copilot and Codex | **pass** – both made the MCP call (n_valid 2, mean 3 mm/day) with no manual configuration |
| 18h | Both engines from the **unzipped event bundle** (no `.git`), fresh `uv sync` | `verify_agent_workflow.py --client copilot` and `--client codex` in `/tmp/bundletest` | **pass 5/5 each**. Found: `codex exec` refuses non-Git folders unless `--skip-git-repo-check` (verifier fixed; troubleshooting updated). Untrusted non-Git folder: Codex loads skills but **not** MCP servers |
| 18g | Copilot skill de-duplication | skills in both `.claude/skills` and `.agents/skills` | **pass** – Copilot lists each skill once |
| 19 | Earthdata MCP live | `uv run python scripts/earthdata_probe.py --list-tools`; MERRA-2 M2TMNXSLV discovery | **pass** (live, 2026-10-31T04:18:59Z) – 7 tools; collection `C1276812859-GES_DISC`; 12 granules for 2020 in the polygon; `T2M` in K; Harmony/OPeNDAP services. Saved as a dated cached response. |
| 20 | Catalog validation | `validate_repo.py --only catalog --only index`; negative tests (fake hosted endpoint, bad peer result, unknown required tool) | **pass** |
| 21 | Relative documentation links and anchors | `validate_repo.py --only links` (all `.md` files) | **pass** – 0 broken links or anchors |
| 22 | Secrets, file sizes, dependency pins | validator + negative tests | **pass** |
| 23 | Tutorial 02 worked example | code blocks from the tutorial applied verbatim to a clean copy; tests added | **pass** – 20 tests; per-season bias returned |
| 24 | Submission and peer-testing flow | `/tmp/author`: scaffold → fill → `check_all` → `package.py contribution`; `/tmp/reviewer`: fresh bundle → `package.py verify` → unzip → `install_skills.py` → server tests → validator | **pass** after fixes found by this test (test-name collision; per-artifact manifest names) |
| 25 | Distribution bundle | `package.py bundle`; `package.py verify` | **pass** – 92 files, ~0.7 MB, deterministic archive with SHA-256 manifest |
| 27 | Client config consistency | `scripts/client_config.py check`; validator `clients`; negative tests (mismatched args, unregistered server) | **pass** |
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

## Defects found in the three-assistant review

| Found by | Defect | Fix |
|---|---|---|
| Copilot CLI run | Without folder trust, `.mcp.json` is ignored and the agent "succeeds" by running scripts in a shell | START_HERE, setup and troubleshooting say to open the folder itself and trust it; verifier denies the shell tool for Copilot and requires real MCP calls |
| Codex run | `.codex/config.toml` did not exist; Codex had no MCP servers | added `.codex/config.toml`, validated against `.mcp.json` |
| Codex run | Codex reads skills from `.agents/skills`, not `.claude/skills` | installer writes both folders (`--client` to choose) |
| Skill review | skills named tools by Claude-only prefixes and referred to `/mcp`, `Grep` | client-neutral wording; catalog uses `<server>/<tool>` |
| Scaffold review | new team servers were registered for no assistant | `new_contribution.py` and `client_config.py register` write both config files; validator requires it |

## Remaining manual checks (precise)

| # | Check | Who / how | Blocks |
|---|---|---|---|
| P1 | Claude Code with a **Claude subscription**: `/status`, then `uv run python scripts/verify_agent_workflow.py --client claude` (five checks) | organizer, rehearsal | Claude Code column of compatibility |
| P2 | **VS Code GUI** walk-through of START_HERE step 5 with each assistant (Copilot Chat view, Claude Code panel, Codex panel), including the Workspace Trust and Codex trust prompts | organizer, rehearsal | GUI claims (engines are tested) |
| P3 | Windows 10/11 and Linux: START_HERE steps 1–5 and `check_all.py` | mentor laptops, or CI after push | compatibility rows |
| P4 | Copilot **Free** and ChatGPT **Free** accounts complete the tutorials within their limits | organizer | plan guidance (TBD) |
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
| GitHub Copilot | **Engine verified** (5/5 checks, scaffolded server); VS Code GUI walk-through pending (P2) |
| Codex | **Engine verified** (5/5, binary from the VS Code extension); project-trust step must be done once per laptop; GUI walk-through pending (P2) |
| Claude Code | Client side verified (servers connect, skills listed); model-driven checks **pending** (P1) |
| Discovery with Earthdata MCP | **Ready** (live verified through Copilot and Codex; cached fallback) |
| Documentation and tutorials | **Complete** for all three assistants; links verified |
| Submission, catalog, peer-testing workflow | **Ready** (dry run passed) |
| Remote repository, CI, hosting | **TBD** by organizer |
