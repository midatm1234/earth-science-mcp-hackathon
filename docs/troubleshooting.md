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

**Symptom common to all assistants:** the assistant answers by running `scripts/first_call.py`, Python or `uv` in a terminal, or says the tool is unavailable. That is not an MCP tool call. Fix the connection first.

| Symptom | Fix |
|---|---|
| Nothing loads in any assistant | VS Code must have the `earth-science-mcp-hackathon` folder itself open (title bar), not a parent folder, and the workspace must be trusted (no "Restricted Mode" banner). Command Palette → **Workspaces: Manage Workspace Trust**. |
| Server fails to start; output says `uv` not found (`ENOENT`, "command not found") | VS Code was started before uv was installed. Quit VS Code completely and start it again. Still failing: put the full path of uv (`which uv` / `where uv`) as `command` in `.mcp.json` and `.codex/config.toml` for your laptop only. |
| Server starts in a terminal but fails in the assistant | Something prints to stdout. Run `uv run pytest servers/<name>/tests -k stdout`; replace `print()` with logging to stderr. |
| Server fails intermittently with an `ImportError` inside a package | Another uv project installs into the same environment. Do not export `UV_PROJECT_ENVIRONMENT` or `VIRTUAL_ENV` globally: assistants pass them to every process they start. Remove them from your shell profile, then `uv sync`. |
| Tools changed but the assistant shows old ones | Start a new chat/session. VS Code: **MCP: List Servers** → Restart; **MCP: Reset Cached Tools**. |

### GitHub Copilot

| Symptom | Fix |
|---|---|
| **MCP: List Servers** does not show the servers | Workspace not trusted, or wrong folder open. Copilot reads `.mcp.json` at the workspace root. |
| Servers listed but tools missing in chat | You are in a *Local* session: switch to the default **Copilot** session. Or the tools are disabled in the chat's tools picker. |
| A server shows an error | **MCP: List Servers** → server → **Show Output**. |
| Copilot features greyed out | Not signed in, Copilot not enabled for your account, or disabled by your organization. |
| Copilot CLI ignores `.mcp.json` | Prompt mode needs `--trust-folder`; interactive mode asks to trust the folder. |

### Claude Code

| Symptom | Fix |
|---|---|
| `/mcp` shows nothing | Start Claude Code in the repository folder (where `.mcp.json` is). |
| "Pending approval" | Project servers need approval. Restart the session and approve; in a terminal: `claude mcp reset-project-choices`, then `claude` to be asked again. |
| `obs-model-starter` failed | Check `uv --version` in the same environment; `claude --debug` shows the server's stderr. |
| Diagnostics | `claude mcp list`, `claude mcp get <name>`. |

### Codex

| Symptom | Fix |
|---|---|
| Codex lists no `obs-model-starter` / `earthdata` tools | The project is not trusted, so `.codex/config.toml` is ignored. Trust it ([setup](setup.md#codex)) and start a new Codex chat. `codex mcp list` (CLI) shows the servers once trusted. |
| Trusted, still nothing | The trust entry must use the folder's real full path (macOS `/tmp/...` is `/private/tmp/...`; Windows uses `C:\...`). |
| `startup timeout` for obs-model-starter | First `uv run` after `uv sync` can be slow on Windows; `startup_timeout_sec` is 60 in `.codex/config.toml`. Run `uv sync` first, then retry. |
| `codex exec`: "Not inside a trusted directory and --skip-git-repo-check was not specified" | The event ZIP is not a Git repository. Trust the folder (as above) and add `--skip-git-repo-check` to `codex exec`. Interactive Codex and the VS Code extension only need the trust. |
| Codex reads the skill with a shell command | Normal: Codex opens `.agents/skills/<name>/SKILL.md` with a read-only command before following it. |

## Skills

| Symptom | Fix |
|---|---|
| Skill missing in every assistant | `uv run python scripts/install_skills.py`, then start a new chat/session. `--check` reports missing or outdated copies. |
| Copilot: `/obs-model-comparison` unknown | Skills are read from `.claude/skills/`, `.agents/skills/` or `.github/skills/`; re-run the installer; new chat. |
| Claude Code: `/obs-model-comparison` unknown | Needs `.claude/skills/`: `install_skills.py --client claude`; restart the session in the repository folder. |
| Codex: `$obs-model-comparison` unknown | Needs `.agents/skills/`: `install_skills.py --client codex`; new Codex chat. |
| Skill never triggers by itself | Improve the `description` with the words users say, including "Use when …". |
| Skill loads but says tools are unavailable | The MCP server it needs is not connected – see above. |
| `install_skills.py` says "skipped … not installed by this script" | A same-named folder exists that you created by hand. Move it away or use `--force`. |
| Validator errors on SKILL.md | Read the message: name/folder mismatch, unquoted metadata values, missing sections. |

## Assistant sign-in and usage limits

| Symptom | Fix |
|---|---|
| Asked for an API key | All three assistants support personal account sign-in: Copilot with GitHub, Claude Code with a Claude account, Codex with ChatGPT. Remove `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` from your environment if an assistant picks them up. |
| Claude `/status` shows an API key or key helper | An environment variable or `~/.claude/settings.json` overrides subscription login; ask a mentor. |
| Browser login does not return to VS Code | Copy the code shown in the browser back into VS Code if prompted, or sign in again. |
| Usage limit reached (any assistant) | Continue with deterministic work: `first_call.py`, tests, `check_all.py`, writing the skill. Mark agent checks **blocked** and complete them later, or switch to another assistant you have. Shorter chats use less. |
| Organization blocks an assistant | Use another assistant or a personal laptop; the plain-client path still works. |

## Validation and submission

| Symptom | Fix |
|---|---|
| `catalog/index.md is out of date` | `uv run python scripts/catalog.py index` |
| `pin an exact version with ==` | Pin packages in `requirements.txt` and add them to `pyproject.toml` with `uv add pkg==X.Y.Z` |
| `differs from uv.lock` | Make `requirements.txt` match `uv.lock`, or re-run `uv lock` after changing `pyproject.toml` |
| `possible hardcoded API key` | Remove the secret; read it from an environment variable. If it is a false positive in a test, add `# secret-scan: ignore` and explain in the PR. |
| `broken link` / `missing anchor` | Fix the relative path or heading; anchors are lowercase with hyphens |
| `MISMATCH` from `package.py verify` | The archive changed after freezing; re-package and record the new SHA-256 |
