# Facilitator guide

For the organizer (Hugo Kyo Lee) and mentors. Participants do not need this page.

## Roles

| Role | Responsibilities | Suggested ratio |
|---|---|---|
| Organizer | Decides TBD items, owns the repository and bundle, runs the clock, protects the peer-testing block | 1 |
| Mentor | Setup clinic, team support, discovery sign-off, freeze check, mentor-assisted submissions, independent review when needed | 1 per 2–3 teams |
| Setup-clinic lead | Runs the clinic table, tracks laptops that need a fallback | 1 (can be a mentor) |

Mentors must be able to: run every tutorial on their own laptop; read a stack trace; use `git` and `gh` (for mentor-assisted pull requests); explain units and time alignment.

## Decisions the organizer must make (TBD list)

| Item | Where it appears | Status |
|---|---|---|
| Event date, venue, duration, registration | README, agenda | TBD |
| Public repository destination (GitHub org/repo) | README, START_HERE, setup, tutorial 05, CODEOWNERS | TBD |
| Bundle distribution location (download page, shared drive, USB) | START_HERE, setup, tutorial 05 | TBD |
| Minimum Claude plan to recommend | setup | TBD – confirm against current Anthropic plan pages |
| Shared MCP server endpoint (future) | server-deployment-plan, .env.example | TBD – not needed for the event |
| Feedback form | agenda | TBD |
| Prizes/judging (if any) | not covered | TBD |

## Timeline before the event

| When | Task |
|---|---|
| T−6 weeks | Decide TBDs above. Create the public repository; push this repository; set branch protection (require the `checks` workflow). |
| T−4 weeks | Recruit mentors; give them this guide; each mentor completes all tutorials and one peer test of the starter. |
| T−3 weeks | Confirm Claude plan guidance; check [compatibility.md](compatibility.md) on Windows and Linux laptops (fill the "untested" rows). |
| T−2 weeks | Send participants [START_HERE.md](../START_HERE.md) and ask them to finish steps 1–4. Offer a remote setup clinic. |
| T−1 week | **Rehearsal** (checklist below). Freeze the starter version; build the bundle. |
| T−1 day | Rebuild the bundle if anything changed; copy bundle and wheelhouse to USB sticks; print the agenda and the peer-test report template. |

## Rehearsal checklist

Run on at least one macOS and one Windows laptop, ideally also Linux, from a clean user account or clean folder.

- [ ] `uv sync` from the bundle ZIP; `uv run python scripts/first_call.py` ends with `Success:`.
- [ ] `uv run python scripts/check_all.py` → `ALL CHECKS PASSED`.
- [ ] HTTP path: server with `--transport http`, client with `--http http://127.0.0.1:8765/mcp`.
- [ ] Claude Code sign-in with a **subscription** account; `/status` shows the Claude account.
- [ ] Project MCP approval prompt appears; `/mcp` shows `obs-model-starter` and `earthdata` connected.
- [ ] `uv run python scripts/install_skills.py`; `/obs-model-comparison` appears in the `/` menu.
- [ ] `uv run python scripts/verify_claude_workflow.py` → all five checks pass; paste the summary into [validation-report.md](validation-report.md).
- [ ] VS Code + Claude Code extension: same skill and MCP servers visible.
- [ ] Earthdata live check: `uv run python scripts/earthdata_probe.py --list-tools`.
- [ ] Scaffold a dummy team: `new_contribution.py --team rehearsal --server rehearsal-tools --skill rehearsal-check`; template tests pass; delete afterwards.
- [ ] Package and verify: `package.py contribution obs-model-starter` then `package.py verify ...`.
- [ ] Peer-test the starter with the report template in ≤ 25 minutes.
- [ ] Mentor-assisted route end to end: ZIP → mentor imports → branch → PR → CI green.
- [ ] Venue: Wi-Fi allows `astral.sh`, `pypi.org`, `files.pythonhosted.org`, `claude.ai`, `api.anthropic.com`, `cmr.earthdata.nasa.gov`; power strips; projector.
- [ ] Time the setup clinic: how long does a fresh laptop take? Adjust the agenda.

## Building the bundle (distribution without GitHub)

```bash
uv run python scripts/check_all.py
uv run python scripts/package.py bundle
uv run python scripts/package.py verify dist/event-bundle-YYYYMMDD.zip
```

Publish the ZIP and its `.sha256` on the chosen location. Participants unzip and run `uv sync`. Reviewed team contributions are added after the event by setting `status.review: accepted` and re-running `package.py bundle`.

### Offline and low-bandwidth fallback

Prepare per platform (on a machine of that OS/architecture) a wheelhouse so `uv sync` works without PyPI:

```bash
# organizer, once per OS/architecture, from the repository root:
uv export --frozen --no-hashes --no-emit-project -o wheelhouse-requirements.txt
uvx --python 3.13 pip download -r wheelhouse-requirements.txt -d wheelhouse/   # wheels for the participants' Python
# participant, offline, from the repository root:
uv venv
uv pip install --no-index --find-links wheelhouse -r wheelhouse-requirements.txt
uv run --no-sync python scripts/first_call.py
```

With this route, use `uv run --no-sync` instead of `uv run` (so uv does not try to reach PyPI). The wheelhouse is about 19 MB and is platform-specific: build one per OS/architecture and Python version, and copy Python itself too (`uv python install 3.13` during the setup clinic, or copy uv's Python folder). Verification status of this fallback is recorded in [validation-report.md](validation-report.md).

## Day-of runbook

| Time | Facilitator action |
|---|---|
| Setup clinic | Tick each participant's six checks. Laptops that cannot run Claude Code: pair them with a teammate; they can still run all plain-client and test steps. |
| Discovery | Sign each discovery record. Reject "build" decisions without a stated gap; steer to "extend" where possible. Keep scope to one tool + one skill. |
| Build | Walk the room; insist on tests and on logging to stderr; watch for credentials in code. |
| Lunch | Each team runs `check_all.py --fast`; note teams at risk. |
| Freeze (14:20–14:40) | Teams package and record SHA-256. Mentors collect ZIPs from mentor-assisted teams. |
| Freeze check (14:40–14:55) | The five-item check from [peer-testing.md](peer-testing.md#before-the-block-freeze-check). Publish the assignment table. |
| Peer testing | Keep time with a visible timer. Enforce: no author help, no development except repair window. Collect reports. |
| Closing | Demos follow [templates/demo.md](../templates/demo.md); each states its peer-test result. |
| After | Merge PRs with `status.review` decided by organizers; record `peer_testing` from reports; leave `hosting: not-hosted` unless a server is actually deployed; rebuild the bundle. |

## Mentor-assisted submission procedure

1. Receive the team's ZIP(s); check `uv run python scripts/package.py verify <zip>`.
2. In a clean clone: `git checkout -b team/<team-slug>`; unzip at the repository root (paths inside start with `servers/`, `skills/`, `catalog/`).
3. `uv run python scripts/check_all.py`.
4. Commit with the team as co-authors if they consent (`Co-authored-by:` lines), push, open a PR using the template, and link the [mentor-assisted issue](../.github/ISSUE_TEMPLATE/mentor-assisted-submission.md) if used.

The required files and metadata are identical to the PR route.

## When things go wrong

| Situation | Response |
|---|---|
| Claude usage limits hit during the day | Continue deterministic work; mark agent checks blocked; resume later. Short sessions and `/clear` reduce usage. |
| Venue internet down | Starter, tests, skills authoring and packaging work offline (after `uv sync`). Earthdata checks become blocked; use the cached example for practice. |
| Earthdata MCP down | Same as above for discovery; continue with check B (catalog). |
| A team's laptop cannot install anything | Pair with another team member; mentor laptop for the final checks. |
| Only one team | A mentor who did not author the contribution performs the independent review. |
| Team wants to deploy their server | Not during the event. See [server-deployment-plan.md](server-deployment-plan.md). |
