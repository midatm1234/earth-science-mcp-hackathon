# Peer testing

Independent cross-team testing is a required part of the event, not an extra. A substantial, protected block at the end of the day is reserved for it. Presentations and unfinished development may not use this time. The mentor sets the pace and may adjust the schedule; the order of the steps stays the same.

Participant steps: [tutorial 05, part B](../tutorials/05-submit-and-test-a-peer.md#part-b--peer-testing). Report form: [templates/peer-test-report.md](../templates/peer-test-report.md).

## Structure of the block

| Step | Activity | Who |
|---|---|---|
| 1 | Handoff: assignments announced, merged work pulled, authors step away | mentors |
| 2 | Round 1: each team tests its first assigned contribution | reviewer teams |
| 3 | Round 2: each team tests its second assigned contribution | reviewer teams |
| 4 | Repair and retest: authors fix reported blockers (new frozen version); reviewers retest | authors + reviewers |
| 5 | Record outcomes: reports saved; catalog `peer_testing` updated | reviewers + mentors |

## Before the block: freeze check

Mentors confirm, for every contribution, before step 1:

- [ ] frozen version recorded (commit SHA, in the catalog entry and submission form);
- [ ] contribution merged to `main` so reviewers can fetch and pull it;
- [ ] tested setup command written in the README;
- [ ] required fixture included and ≤ 1 MB per file;
- [ ] documented example that runs on a prepared laptop.

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

- a clean checkout of `main` after the mentor merged the pull requests (fetch and pull in VS Code), already `uv sync`ed;
- a new chat/session of the reviewer's AI assistant (Copilot, Claude Code or Codex) in that folder;
- the contribution added only through its documented steps (fetch and pull, then install the skill and register the server).

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
