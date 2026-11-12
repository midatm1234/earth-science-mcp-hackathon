# Tutorial 03 – Create an agent skill

| | |
|---|---|
| **Scientific purpose** | Capture the expert procedure around a tool – which checks to run first, how to choose arguments, how to report results honestly – so any agent session follows it. |
| **Learning objective** | Describe the procedure to an AI assistant, let it write and install the skill, check what it wrote, and test it three ways: a direct request for the skill, a natural-language question, and a request where it should **not** apply. |
| **Starting state** | [Tutorial 02](02-build-an-mcp-tool.md) done: your team has an MCP server with its tools, listed in your assistant, and a folder `submissions/<team-name>/`. |
| **Credentials** | Your AI assistant's account. |

## What a skill is

A skill is a short instruction file (`SKILL.md`) that tells an AI assistant **when** to use your tool and **how** to report the result. The assistant sees only the skill's name and one-paragraph description until a question matches it, so the description must use the words people actually say.

You decide **what the procedure is** and **how to check it**. The assistant writes the file, installs it for all assistants and validates it. The repository's instructions ([AGENTS.md](../AGENTS.md), and `CLAUDE.md` for Claude Code) already tell the assistant where skills live and not to edit the installed copies, so you do not need to repeat that.

For a model of a good skill, ask your assistant to read and summarize [skills/obs-model-comparison/SKILL.md](../skills/obs-model-comparison/SKILL.md).

## Step 1 – Describe the procedure

Write down, in plain words:

- which question the skill is for, in the words a colleague would use;
- which tool the assistant must call first, and what to check in its result;
- when it should stop and ask, or say the tool is not connected;
- how the answer should look: a result sentence, a short table, the date checked, the source, limitations.

Also write down one request that looks similar but where the skill should **not** apply.

## Step 2 – Ask your assistant to write it

Start a **new** chat or session in your AI assistant (GitHub Copilot in Agent mode, Claude Code or Codex) and paste a prompt like this, with your own names:

```text
Create an agent skill named sst-latest-check for team <team-name>. It guides the MCP server my team
built in tutorial 02 (find it in catalog/entries/ with team: <team-name>); read its tools first and use
only those. Use it when someone asks how current the sea surface temperature data are.
Procedure: call the latest-granule tool and report what it returns; if the server is not connected, stop.
Install it, validate it, and follow AGENTS.md.
Tell me what you created and what you could not verify.
```

Read the assistant's plan before you approve it.

## Step 3 – Check what it wrote

Ask the assistant to show you `skills/<skill-name>/SKILL.md` and explain it, then check it against this list:

| Check | What to look for |
|---|---|
| Name | Lowercase words with hyphens, and the same as the skill's folder name. |
| Description | Says what the skill does and starts the trigger with "Use when…", in the words users say. |
| When to use / not to use | Both are there, and "not to use" includes your look-alike request. |
| Procedure | Numbered steps an agent can follow exactly: which tool first, what to check, when to stop. |
| Expected output | Names the parts of the answer, including provenance and limitations. |
| Honesty | The assistant says whether the skill was validated and installed, or only written. |

If something is missing, tell the assistant what to change and ask it to validate and reinstall. After every change, start a new chat or session: assistants read skills when a session begins.

## Step 4 – Test it three ways

Start a **new** chat or session for each test. Skills work with `/name` in Copilot and Claude Code and `$name` in Codex.

| Test | Prompt | Pass if |
|---|---|---|
| Direct request | `/sst-latest-check` (Codex: `$sst-latest-check`), then ask: `What is the latest sea surface temperature data available?` | The skill loads and the `get_latest_sst_granule` tool is called. |
| Natural question | `How up to date is the global sea surface temperature data from NASA?` | The assistant uses the skill by itself, without being told, and calls the tool. |
| Should not apply | `In one sentence, what does SST stand for?` | The skill is **not** used and no tool is called. |

Also check that the tool calls actually happen. If the assistant ran a shell command or Python script instead of calling the MCP tool, the test did not pass. If the server is disconnected, the skill should say so and stop.

Ask your assistant to record the assistant name and version, the prompts, the tools called and pass or fail for each test in `submissions/<team-name>/submission.md`. If your team uses more than one assistant, test each; skills behave slightly differently in each.

If the natural question fails, ask the assistant to improve the **description** by adding the words you used. If the skill is used when it should not be, ask for a more specific description.

## Example: a skill that runs a whole workflow

A skill can guide a **workflow** that needs several tools in a fixed order. In this example the workflow finds the newest sea surface temperature (SST) data, draws a Cartopy map, and makes a GIF animation of the map for the last 10 days.

The skill may use **only your team's MCP tools**: no shell commands, no ad hoc Python scripts and no tools from other servers. So every action the workflow needs must exist as a tool first. Do it in two prompts, in two sessions.

### Part 1 – Ask your assistant to build the tools

Start a **new** chat or session and paste a prompt like this, with your own team name and region:

```text
Extend the sst-latest MCP server (team <team-name>) so it can pull the newest sea surface temperature
(SST) data, draw a Cartopy map, and make a GIF of the map for the last 10 days. Region: <region>.
First read the sst-latest README and tools, propose how many new tools are needed, then build them.

- Tools: one per step (newest date, fetch regional subset, draw map, make GIF, list files made);
  add more if a step needs them. The workflow must work using only the server's tools.
- Output: file paths, sizes, dates covered and date checked. Never images or data arrays.
  Write files only to one git-ignored output folder.
- Data: a small regional subset only. Prefer a source without login (e.g. NOAA CoastWatch ERDDAP).
  Any login credentials: environment variables only, never in files. Say which source you used.
- Dependencies: pin Cartopy and a GIF writer with uv add; explain them in the README.
- Tests: offline, with a small saved sample.

Follow AGENTS.md. Tell me what you built and what you could not verify.
```

Check the result with the Step 3 table, plus these questions for the assistant:

| Check | What to look for |
|---|---|
| Tool count | The assistant explained why it chose that many tools, and every step of the workflow has a tool. |
| Data | It named its source, the region size and why it did not download whole files. |
| Credentials | None in any file; any variable names are in the README. |
| Output | Tools return paths and dates, not pictures. |
| Honesty | It says which parts ran against the real service and which only against the saved sample. |

### Part 2 – Ask your assistant to write the skill

The new tools appear only in a new session. **Exit this session and start a new one**, confirm the new tools are listed, then paste:

```text
Write an agent skill named sst-map-workflow for team <team-name>. First list the tools of the
sst-latest MCP server in this session.

- Tools: use only those tools. List them in allowed-tools. Never fall back to shell commands,
  Python scripts or tools from other servers; if a tool is missing or fails, say so and stop.
- Procedure, in order: newest available date, fetch the last 10 days for the region, draw the map,
  make the GIF, list the files made.
- Answer: region, dates covered, source, date checked and files made; say an SST map shows a
  gridded analysis, not station measurements.
- Use it for: maps or animations of recent sea surface temperature. Not for: values at one place,
  or forecasts.
- Description: use the words people actually say.

Install it for all assistants, validate it, and follow AGENTS.md.
Tell me what you created and what you could not verify.
```

### Part 3 – Test it

Start a **new** session, then:

| Test | Prompt | Pass if |
|---|---|---|
| Direct request | `/sst-map-workflow` (Codex: `$sst-map-workflow`), then ask: `Make a map and a 10-day animation of sea surface temperature for <region>.` | Only your server's tools are called, in order, and a map and a GIF are created. |
| Only those tools | Ask: `Which tools did you call, and did you run any shell command or Python script?` | The answer lists only your server's tools and says no shell command or script was run. |
| Check the files | `How many frames does the GIF have, and which dates?` | 10 frames, and the dates are the 10 days ending at the newest available date. |
| Should not apply | `What was the sea surface temperature at Santa Monica pier yesterday?` | The skill is **not** used; the assistant explains that a gridded map is the wrong tool for a point value. |

## Exercise

Ask your assistant to add one more request that a user might plausibly confuse with your skill but that it should not handle, to the "When not to use" section. Reinstall, start a new session and check the skill stays out of the way.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| `/skill-name` or `$skill-name` not found | Skill not installed, or the session started before it was installed | Ask the assistant to install it; start a new session in the repository folder |
| Skill never triggers by itself | Description too generic | Ask the assistant to add "Use when…" with the words people use |
| Skill loads but the tools fail | MCP server not connected | Check the server list in your assistant ([troubleshooting](../docs/troubleshooting.md#mcp-server-not-connected)) |
| Works in one assistant, not another | Different skill folders or behaviour | Ask the assistant to check that all installed copies are current; test in each assistant |
| Your edits to an installed copy disappeared | Installed copies are overwritten | Always have the assistant edit the skill in `skills/<skill-name>/` and reinstall |
| The assistant says the skill is valid but you did not see it checked | Claim without evidence | Ask it to show the check and its output |

Next: [Tutorial 04 – Combine tools and skills](04-combine-tools-and-skills.md)
