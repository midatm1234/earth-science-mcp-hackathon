# Tutorial 05 – Submit and test a peer

| | |
|---|---|
| **Scientific purpose** | A capability is only useful if someone else can reproduce it. Independent testing finds the gaps authors cannot see. |
| **Learning objective** | Freeze and submit your server and skill (pull request or mentor-assisted), then install another team's contribution in a clean session, run its example, invoke its skill, try new and invalid inputs, check units/provenance/limitations, and record a peer-test report with a retest. |
| **Estimated time** | 20 minutes submission + the 90-minute peer-testing block |
| **Starting state** | Tutorials 02–04 done; `submissions/<team>/submission.md` drafted. |
| **Credentials** | Your AI assistant's account. GitHub account only for the pull-request route. |

## Part A – Freeze and submit (20 minutes, before the peer-testing block)

### 1. Pass the checks

```bash
uv run python scripts/catalog.py index
uv run python scripts/check_all.py
```

Expected last line: `ALL CHECKS PASSED`. Fill `catalog/entries/<server>.yaml` and `<skill>.yaml` (no `REPLACE` left), and the checklist in `submissions/<team>/submission.md`.

### 2. Freeze a version

```bash
uv run python scripts/package.py contribution <server-name>
uv run python scripts/package.py contribution <skill-name>
```

Expected: `wrote dist/<name>-0.1.0.zip` and `sha256 <64 hex characters>`. Record the SHA-256 (or, on the PR route, the commit SHA) as `source.ref` in both catalog entries and in the submission form. After this, changes need a new version.

### 3a. Pull-request route (if you use GitHub)

```bash
git checkout -b team/<team-slug>
git add servers/<server-name> skills/<skill-name> catalog/entries submissions/<team-slug>
git commit -m "Add <server-name> and <skill-name> (<team-slug>)"
git push -u origin team/<team-slug>
```

Then open a pull request on GitHub (repository URL **TBD**) and fill in the template. If you forked the repository first: `gh repo fork <URL TBD> --clone`, then the same commands. CI runs the same checks as `check_all.py` and never deploys anything.

### 3b. Mentor-assisted route (no GitHub needed)

Give the two ZIP files from step 2 to your mentor (USB stick or the shared folder announced by the organizer, **TBD**). The mentor checks the SHA-256, runs `check_all.py`, and opens the pull request on your behalf using the [mentor-assisted template](../.github/ISSUE_TEMPLATE/mentor-assisted-submission.md). Same files, same metadata, same review.

### 4. Mentor freeze check (before testing starts)

The mentor confirms for each contribution: frozen version recorded; package accessible to reviewers; setup command tested; required fixture included; documented example runs within five minutes. Contributions that fail this check are tested as-is and the failure is recorded – development does not continue into the testing block.

## Part B – Peer testing (the 90-minute block)

Full procedure and rules: [docs/peer-testing.md](../docs/peer-testing.md). Copy [templates/peer-test-report.md](../templates/peer-test-report.md) to `catalog/peer-tests/<artifact-id>--<your-team>--1.md`.

| Time | Activity |
|---|---|
| 10 min | Handoff: receive assignment and package; authors leave the table |
| 25 min | Round 1: test your first assigned contribution |
| 25 min | Round 2: test your second assigned contribution |
| 20 min | Repair and retest: authors fix reported blockers (new version); reviewers retest |
| 10 min | Record outcomes in reports and catalog entries |

### Clean session

Use the event's prepared environment (common dependencies already installed), a **new terminal** and a **new chat/session** in your AI assistant (any of the three; record which). Unzip the package into a fresh copy of the event bundle (or check out the frozen commit), then:

```bash
uv run python scripts/package.py verify <path>/<name>-0.1.0.zip
unzip -o <path>/<server-name>-0.1.0.zip      # Windows: Expand-Archive <path>\<server-name>-0.1.0.zip -DestinationPath . -Force
unzip -o <path>/<skill-name>-0.1.0.zip
uv run python scripts/install_skills.py <skill-name>
uv run python scripts/client_config.py register <server-name>
```

Unzip at the repository root: the archives contain `servers/…`, `skills/…` and `catalog/entries/…` paths, plus a `<name>-<version>.MANIFEST.json` checksum list (git-ignored).

`client_config.py register` adds the server to `.mcp.json` (Copilot, Claude Code) and `.codex/config.toml` (Codex); then start a new session. For a hosted endpoint, add an `http` entry with its URL to both files instead (see the `earthdata` entries).

### Checks to run and record

1. Install or connect (note setup time).
2. Run the documented MCP example (tool, arguments, output).
3. Invoke the skill (`/<skill-name> ...`), and once with a natural request.
4. Try an additional scientific input of your choice (another site, period, variable).
5. Test an invalid input or boundary case (unknown id, empty period, wrong units).
6. Check units, provenance and limitations in the answer.
7. Report failures to authors immediately; after their fix, retest and record.

Statuses: **pass**, **partial**, **fail**, **blocked**. If assistant usage limits or the network interrupt you, continue checks 1, 2, 4 and 5 with a plain client (pattern of [first_call.py](../scripts/first_call.py) or the MCP Inspector) and mark skill and combined-workflow checks **blocked**.

An author demonstrating their own work does not count as a peer test.

## Example prompt (reviewer)

```text
/<their-skill> <their documented example>, then: <your additional input>. Report units and provenance.
```

## Expected output

A completed peer-test report per artifact, with version/SHA, OS, assistant and its version, execution mode, setup time, expected vs actual, evidence, status, fixes, retest; and the author's catalog entry updated with `peer_testing: [{report: catalog/peer-tests/..., result: ...}]`.

## Exercise (practice before the day)

Peer-test the starter: treat `obs-model-starter` and `obs-model-comparison` as another team's work and fill a report in 15 minutes. Use `SYN-COAST` with `include_suspect` as your additional input and `start: 2023-01` as your boundary case.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| `MISMATCH` on verify | Corrupted or wrong file | Ask authors/mentor for the package again; record the SHA you tested |
| Server not found after registering | Session started before registering | Start a new chat/session |
| Two servers with the same name | Name collision with a user-level server | Rename or remove one; `uv run python scripts/client_config.py check` |
| Authors keep coding during testing | Not allowed | Mentor records the frozen result; fixes only in repair window |
| Only one team present | No independent reviewer | A mentor who did not author it performs the review |

Back to the [README](../README.md#learning-path).
