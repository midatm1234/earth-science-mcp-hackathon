# Tutorial 05 – Submit and test a peer

| | |
|---|---|
| **Scientific purpose** | A capability is only useful if someone else can reproduce it. Independent testing finds the gaps authors cannot see. |
| **Learning objective** | Freeze and submit your server and skill (pull request), then install another team's contribution in a clean session, run its example, invoke its skill, try new and invalid inputs, check units/provenance/limitations, and record a peer-test report with a retest. |
| **Starting state** | Tutorials 02–04 done; `submissions/<team>/submission.md` drafted. |
| **Credentials** | Your AI assistant's account. GitHub account only for the pull-request route. |

## Part A – Freeze and submit (before peer testing)

### 1. Pass the checks

Paste this prompt into your AI assistant:

```text
Regenerate the catalog index, then run all the repository checks (offline, no LLM). Show me the last line of the output and list every failure with the file it comes from. Do not fix anything yet; wait for my go-ahead.
```

Expected: the assistant reports `ALL CHECKS PASSED`. Then ask:

```text
Open my catalog entries for <server-name> and <skill-name> and my submissions/<team>/submission.md. Tell me which fields still contain REPLACE or are empty, and which checklist items are not ticked. Do not invent evidence: for anything I have not run, mark it pending.
```

Fill `catalog/entries/<server>.yaml` and `<skill>.yaml` (no `REPLACE` left), and the checklist in `submissions/<team>/submission.md`.

### 2. Freeze a version

```text
Commit my server <server-name>, my skill <skill-name>, my catalog entries and submissions/<team-name> on my team branch, then tell me the full commit SHA. Put that SHA into source.ref of both catalog entries and into the submission form, commit again, and show me what changed. Wait for my approval before you push.
```

Expected: a 40-character commit SHA recorded as `source.ref` in both catalog entries and in the submission form. After this, changes need a new version.

### 3. Submit by pull request

```text
Prepare a pull request for my team <team-name> against https://github.com/midatm1234/earth-science-mcp-hackathon. Use a new branch named for my team. Include only servers/<server-name>, skills/<skill-name>, catalog/entries and submissions/<team-name>. Show me the list of files and the proposed commit message and pull-request description, and wait for my approval before you commit or push anything. If I have not forked the repository, tell me and ask whether to fork it first.
```

After you approve, the assistant commits, pushes and opens the pull request, and you fill in the template. CI runs the same checks as `check_all.py` and never deploys anything.

**Once the mentor merges the pull requests**, everyone gets the merged contributions with Git in VS Code:

1. Open the repository folder in VS Code.
2. At the bottom left, click the branch name (for example `main`) and make sure it is `main`.
3. Click the circular **Sync Changes** arrow next to it, or open **Source Control** (left sidebar), click the `...` menu and choose **Fetch**, then **Pull**. This fetches and pulls the merged work from GitHub.
4. Confirm that `servers/<server-name>`, `skills/<skill-name>` and `catalog/entries` now contain the new contribution, then start a new chat/session in your AI assistant.

### 4. Mentor freeze check (before testing starts)

The mentor confirms for each contribution: frozen version recorded; contribution merged to `main` so reviewers can fetch and pull it; setup command tested; required fixture included; documented example runs on a prepared laptop. Contributions that fail this check are tested as-is and the failure is recorded – development does not continue into the testing block.

## Part B – Peer testing

Full procedure and rules: [docs/peer-testing.md](../docs/peer-testing.md). Copy [templates/peer-test-report.md](../templates/peer-test-report.md) to `catalog/peer-tests/<artifact-id>--<your-team>--1.md`.

| Step | Activity |
|---|---|
| 1 | Handoff: receive assignment; authors leave the table |
| 2 | Round 1: test your first assigned contribution |
| 3 | Round 2: test your second assigned contribution |
| 4 | Repair and retest: authors fix reported blockers (new version); reviewers retest |
| 5 | Record outcomes in reports and catalog entries |

The mentor sets the pace; the steps stay in this order.

### Clean session

Use the event's prepared environment (common dependencies already installed), and a **new chat/session** in your AI assistant (any of the three; record which). Get the other team's contribution after the mentor merges it: in VS Code, make sure the bottom-left branch is `main`, then click **Sync Changes** (or **Source Control** → `...` → **Fetch**, then **Pull**). Then paste:

```text
I am peer-testing another team's contribution: server <server-name> and skill <skill-name>. Check that servers/<server-name>, skills/<skill-name> and their catalog entries are present in this folder, and that the frozen commit SHA <sha> is in the git history. Then install the skill for all assistants and register the server in the client configuration files. Report each step and tell me when I need to start a new session.
```

Registering adds the server to `.mcp.json` (Copilot, Claude Code) and `.codex/config.toml` (Codex); then start a new session. For a hosted endpoint, add an `http` entry with its URL to both files instead (see the `earthdata` entries).

### Checks to run and record

1. Install or connect (note setup time).
2. Run the documented MCP example (tool, arguments, output).
3. Invoke the skill (`/<skill-name> ...`), and once with a natural request.
4. Try an additional scientific input of your choice (another site, period, variable).
5. Test an invalid input or boundary case (unknown id, empty period, wrong units).
6. Check units, provenance and limitations in the answer.
7. Report failures to authors immediately; after their fix, retest and record.

Statuses: **pass**, **partial**, **fail**, **blocked**. If assistant usage limits or the network interrupt you, continue checks 1, 2, 4 and 5 with a plain client (ask your assistant for a plain MCP call like the one in [first_call.py](../scripts/first_call.py), or use the MCP Inspector) and mark skill and combined-workflow checks **blocked**.

An author demonstrating their own work does not count as a peer test.

## Example prompt (reviewer)

```text
Use the <their-skill> skill to run its documented example: <their documented example>. Then repeat it with my additional input: <your additional input>. Report units and provenance, and show the tool trace.
```

Other useful prompts for the checks above:

```text
Call the documented example of the <server-name> server exactly as written in its README and show me the tool, the arguments and the output. Compare it with the README and tell me any difference.
```

```text
Try an invalid input on the <server-name> server (an unknown id, an empty period or the wrong units). Tell me whether the error message says what to fix, and whether any result was returned that should not have been.
```

```text
Write a peer-test report for <artifact-id> from the template in templates/peer-test-report.md, using only what we ran in this session. Mark any check we did not run as pending or blocked, and do not claim verification we did not do.
```

## Expected output

A completed peer-test report per artifact, with version/SHA, OS, assistant and its version, execution mode, setup time, expected vs actual, evidence, status, fixes, retest; and the author's catalog entry updated with `peer_testing: [{report: catalog/peer-tests/..., result: ...}]`.

## Exercise (practice before the day)

Peer-test the starter: treat `obs-model-starter` and `obs-model-comparison` as another team's work and fill in a report. Ask your assistant to use `SYN-COAST` with suspect observations included as your additional input, and a start month of 2023-01 as your boundary case.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| Contribution missing after pull | Not on `main`, or the PR is not merged yet | Check the bottom-left branch in VS Code, then fetch and pull again; record the commit SHA you tested |
| Server not found after registering | Session started before registering | Start a new chat/session |
| Two servers with the same name | Name collision with a user-level server | Ask your assistant to check the client configuration files for duplicate server names, then rename or remove one |
| Authors keep coding during testing | Not allowed | Mentor records the frozen result; fixes only in repair window |
| Only one team present | No independent reviewer | A mentor who did not author it performs the review |

Back to the [README](../README.md#learning-path).
