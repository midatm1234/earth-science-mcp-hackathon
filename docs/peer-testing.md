# Peer testing

Independent cross-team testing is a required part of the event, not an extra. In the provisional one-day format, the **final substantive 90-minute block** is reserved for it. Presentations and unfinished development may not use this time. If the organizer confirms a different event duration, adjust the allocation proportionally and record the change in the [agenda](agenda.md).

Participant steps: [tutorial 05, part B](../tutorials/05-submit-and-test-a-peer.md#part-b--peer-testing-the-90-minute-block). Report form: [templates/peer-test-report.md](../templates/peer-test-report.md).

## Structure of the 90 minutes

| Minutes | Activity | Who |
|---|---|---|
| 0–10 | Handoff: assignments announced, packages distributed, authors step away | mentors |
| 10–35 | Round 1: each team tests its first assigned contribution | reviewer teams |
| 35–60 | Round 2: each team tests its second assigned contribution | reviewer teams |
| 60–80 | Repair and retest: authors fix reported blockers (new frozen version); reviewers retest | authors + reviewers |
| 80–90 | Record outcomes: reports saved; catalog `peer_testing` updated | reviewers + mentors |

## Before the block: freeze check

Mentors confirm, for every contribution, before minute 0:

- [ ] frozen version recorded (commit SHA or archive SHA-256, in the catalog entry and submission form);
- [ ] accessible package (archive on the shared folder/USB, or commit reachable by reviewers);
- [ ] tested setup command written in the README;
- [ ] required fixture included and ≤ 1 MB per file;
- [ ] documented example that runs within five minutes on a prepared laptop.

Any unchecked item is recorded in the peer-test report as the starting state; it is not fixed by extending development into the block.

## Cross-assistant coverage

Where teams use different assistants, assign reviewers so each contribution is tested with at least one assistant its authors did **not** use. Record the assistant in the report. A skill that works in one assistant and fails in another is a *partial*, with the failing assistant named.

## Assignment

Number teams 1…N in random order. Team *i* reviews team *(i+1) mod N* in round 1 and team *(i+2) mod N* in round 2, so no team reviews itself and every contribution is reviewed twice (with N ≥ 3).

| Teams present | Rule |
|---|---|
| N ≥ 3 | Rotation above |
| N = 2 | Each team reviews the other in round 1; in round 2 a mentor who did not author either contribution reviews one of them |
| N = 1 | A mentor who did not author the contribution performs the independent review (both rounds) |

Authors may answer questions only through what is written in their README and submission; verbal help during a round is recorded in the report as a deviation.

## Clean session

Reviewers test in a **clean project or session** with the event's common dependencies already installed:

- a fresh copy of the event bundle (or a clean checkout of the frozen commit), already `uv sync`ed;
- a new terminal and a new chat/session of the reviewer's AI assistant (Copilot, Claude Code or Codex) in that folder;
- the contribution added only through its documented steps (unzip, `install_skills.py`, `client_config.py register`).

## What reviewers must do

1. Install or connect to the other team's contribution.
2. Run its documented MCP example.
3. Invoke its skill (explicitly, and with a natural request if time allows).
4. Try an additional scientific input.
5. Test an invalid-input or boundary case.
6. Check units, provenance and limitations.
7. Report failures and record a retest.

## What to record

Artifact version and frozen reference; author team and reviewer team; OS, AI assistant and its version, Python version; execution mode (stdio local, HTTP local, hosted); setup time; expected and actual results; evidence (tool names, arguments, output excerpts, error messages); status per check; fixes; retest outcome.

| Status | Meaning |
|---|---|
| pass | Works as documented |
| partial | Works with a documented deviation or minor defect |
| fail | Does not work as documented |
| blocked | Could not be attempted (state the reason, e.g. usage limit, network) |

An author demonstration does **not** count as independent reproduction.

## If assistant usage limits or connectivity interrupt testing

Continue the deterministic checks – install, documented MCP example, additional input, invalid input – with a plain MCP client (for example a copy of [first_call.py](../scripts/first_call.py) pointed at the server, or the MCP Inspector). Mark the skill invocation and any combined agent-workflow checks **blocked** until they can be completed, and complete them later if possible. Never mark a blocked check as pass.

## After the block

- Reports saved as `catalog/peer-tests/<artifact-id>--<reviewer-team>--<round>.md`.
- Each catalog entry's `status.peer_testing` lists the reports and results; `status.review`, `status.local_verification` and `status.hosting` are **not** changed by a peer test.
- Run `uv run python scripts/catalog.py index` and `scripts/check_all.py`.
- In the closing session, each team's demo states its independent peer-test result ([templates/demo.md](../templates/demo.md)).
