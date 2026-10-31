# Peer-test report

Independent reproduction by a team (or mentor) that did **not** author the artifact. An author demonstration does not count. Save as `catalog/peer-tests/<artifact-id>--<reviewer-team>--<round>.md`. Procedure: [docs/peer-testing.md](../docs/peer-testing.md).

## 1. What was tested

| Field | Value |
|---|---|
| Artifact(s) | MCP server id: ______  Skill id: ______ |
| Artifact version and frozen reference | e.g. 0.1.0, sha256 `...` |
| Author team | |
| Reviewer team / mentor | |
| Round | 1 / 2 / retest |
| Date and start time | |
| OS and version | |
| Python version | `uv run python --version` |
| Claude Code version | `claude --version` |
| Execution mode | stdio local / Streamable HTTP local / hosted endpoint (URL) |
| Clean session? | new terminal + new Claude Code session, common dependencies preinstalled: yes / no |
| Setup time (minutes) | from receiving the package to first successful tool call |

## 2. Checks

Status: **pass** (works as documented), **partial** (works with a documented deviation), **fail** (does not work), **blocked** (could not be attempted; say why).

| # | Check | Expected (from author docs) | Actual | Status | Evidence |
|---|---|---|---|---|---|
| 1 | Install or connect | | | | command + output line |
| 2 | Documented MCP example | | | | tool name, arguments, key output |
| 3 | Invoke the skill | | | | prompt, tools called |
| 4 | Additional scientific input (reviewer's choice) | | | | |
| 5 | Invalid input or boundary case | readable error, no crash | | | error text |
| 6 | Units stated and correct | | | | |
| 7 | Provenance stated (source, version, synthetic/cached/live) | | | | |
| 8 | Limitations stated and sensible | | | | |

If Claude usage limits or network problems interrupt the session, continue checks 1, 2, 4, 5 with a plain MCP client (`scripts/first_call.py` pattern or MCP Inspector) and mark checks 3 and any agent-dependent part **blocked** until completed.

## 3. Failures reported to authors

| # | Description | Severity (blocker / major / minor) | Reported at (time) |
|---|---|---|---|

## 4. Fix and retest

| # | Fix made by authors (new reference) | Retest result | Evidence |
|---|---|---|---|

## 5. Overall result

| Field | Value |
|---|---|
| Overall status | pass / partial / fail / blocked |
| One-sentence summary | |
| Reviewer signature | |
| Mentor confirmation | |
