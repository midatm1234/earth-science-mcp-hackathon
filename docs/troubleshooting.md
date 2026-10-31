# Troubleshooting

Find your symptom, apply the fix, and re-run the check from [setup](setup.md#what-the-setup-clinic-checks). Ask a mentor if two fixes do not help.

## Installation

| Symptom | Fix |
|---|---|
| `uv: command not found` / `claude: command not found` | Close and reopen the terminal. macOS/Linux: check `~/.local/bin` is on PATH (`echo $PATH`); run `source ~/.zshrc` or `source ~/.bashrc`. Windows: sign out and in, or reopen PowerShell. |
| Windows: "running scripts is disabled on this system" | Use the exact uv command with `-ExecutionPolicy ByPass`. To activate a pip venv: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| macOS: "cannot be opened because the developer cannot be verified" | Use the curl installers (not a downloaded file), or allow it in System Settings → Privacy & Security. |
| `uv sync` fails downloading Python | Network/proxy (below), or use an installed Python: `uv sync --python 3.12` (any 3.11–3.14). |
| `uv sync` is very slow or files are locked | Repository is in a cloud-synced folder (OneDrive, iCloud, Google Drive, Dropbox). Move it to a normal local folder. |
| `error: No interpreter found for Python >=3.11` (pip route) | Install Python 3.13 from python.org; on Windows use `py -3.13`. |

## Network, proxy and certificates

| Symptom | Fix |
|---|---|
| `invalid peer certificate` / `CERTIFICATE_VERIFY_FAILED` | A corporate proxy re-signs TLS. Try `uv sync --native-tls` (uses the system certificate store) or set `UV_NATIVE_TLS=1`. |
| Behind an HTTP proxy | Set `HTTPS_PROXY=http://proxy:port` (and `HTTP_PROXY`) before running uv or claude. |
| Earthdata MCP unreachable | `uv run python scripts/earthdata_probe.py --list-tools` to test. Use the [cached example](../examples/data/cached/earthdata_discovery_merra2_t2m.json) to keep working and mark live checks **blocked**. |
| Venue Wi-Fi blocks downloads | Organizers provide the bundle and, if prepared, a wheelhouse on USB ([facilitator guide](facilitator-guide.md#offline-and-low-bandwidth-fallback)). |

## First tool call

| Symptom | Fix |
|---|---|
| `FAILED: ... No such file or directory` | Run from the repository root (the folder with `pyproject.toml`). |
| `FAILED: ConnectError` with `--http` | Start the server first in another terminal; URL must end in `/mcp`. |
| `[Errno 48] Address already in use` / `10048` | Another program uses port 8765. Start the server with `--port 8780` and use that port in the URL. |
| Results differ from the documented numbers | Fixtures changed: `uv run python scripts/generate_sample_data.py --check`. |
| `ModuleNotFoundError: No module named 'mcp'` | You ran `python` outside the project environment. Use `uv run python ...` (or activate `.venv` on the pip route). |

## MCP server not connected

| Symptom | Fix |
|---|---|
| `/mcp` shows nothing | Start `claude` **in the repository folder** (where `.mcp.json` is). |
| "Pending approval" | Project-scoped servers need your approval. Restart `claude` and approve; or `claude mcp reset-project-choices` and restart to be asked again. |
| `obs-model-starter` failed to start | Claude Code could not run `uv`. Check `uv --version` in the same terminal. If uv is installed but not found by Claude Code, add the server with an absolute path: `claude mcp add --scope local obs-model-starter -- /full/path/to/uv run --quiet python servers/obs-model-starter/server.py` (find the path with `which uv` or `where uv`). |
| Server starts in a terminal but fails in Claude | Something prints to stdout. Run `uv run pytest servers/<name>/tests -k stdout`; replace `print()` with logging to stderr. |
| Server fails intermittently with `ImportError` inside a package | Another uv project is installing into the same environment. Do not export `UV_PROJECT_ENVIRONMENT` (or `VIRTUAL_ENV`) globally: Claude Code passes it to every helper it starts. Remove it from your shell profile, then `uv sync`. |
| Tools changed but Claude shows old ones | Restart the Claude Code session; servers are started at session start. |
| Diagnostics | `claude mcp list`, `claude mcp get <name>`, or `claude --debug`. |

## Skills

| Symptom | Fix |
|---|---|
| `/obs-model-comparison` unknown | `uv run python scripts/install_skills.py` then restart `claude` in the repository folder. |
| Skill never triggers by itself | Improve the `description` with the words users say, including "Use when …". |
| Skill loads but says tools are unavailable | The MCP server it needs is not connected – see above. |
| `install_skills.py` says "skipped … not installed by this script" | A same-named folder exists that you created by hand. Move it away or use `--force`. |
| Validator errors on SKILL.md | Read the message: name/folder mismatch, unquoted metadata values, missing sections. |

## Claude sign-in and usage limits

| Symptom | Fix |
|---|---|
| Asked for an API key | Choose the Claude account (subscription) login. Remove `ANTHROPIC_API_KEY` from your environment (`unset ANTHROPIC_API_KEY`; Windows: `Remove-Item Env:ANTHROPIC_API_KEY`) and from shell profiles. |
| `/status` shows API key or key helper | An environment variable or settings file overrides subscription login; ask a mentor to check `~/.claude/settings.json`. |
| Browser login does not return to the terminal | Copy the code shown in the browser back into the terminal if prompted; or run `claude` again. |
| Usage limit reached | Continue with deterministic work: `first_call.py`, tests, `check_all.py`, writing the skill. Mark agent checks **blocked** and complete them later. Shorter sessions (`/clear`) use less. |
| Organization blocks Claude Code | Use a personal laptop or ask the organizer; the plain-client path still works. |

## Validation and submission

| Symptom | Fix |
|---|---|
| `catalog/index.md is out of date` | `uv run python scripts/catalog.py index` |
| `pin an exact version with ==` | Pin packages in `requirements.txt` and add them to `pyproject.toml` with `uv add pkg==X.Y.Z` |
| `differs from uv.lock` | Make `requirements.txt` match `uv.lock`, or re-run `uv lock` after changing `pyproject.toml` |
| `possible hardcoded API key` | Remove the secret; read it from an environment variable. If it is a false positive in a test, add `# secret-scan: ignore` and explain in the PR. |
| `broken link` / `missing anchor` | Fix the relative path or heading; anchors are lowercase with hyphens |
| `MISMATCH` from `package.py verify` | The archive changed after freezing; re-package and record the new SHA-256 |
