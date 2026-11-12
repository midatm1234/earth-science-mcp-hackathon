# Tutorial 02 – Build an MCP tool

| | |
|---|---|
| **Scientific purpose** | Turn a well-defined scientific calculation or data lookup into tools an agent can call reproducibly, with units, missing-data rules and provenance in the result. |
| **Learning objective** | Describe your scientific need to an AI assistant, let it build the MCP tools, check what it built, and try the tools in a new chat. |
| **Starting state** | [Tutorial 01](01-discover-existing-capabilities.md) done, and your team knows which calculation or data lookup it wants to turn into a tool. |
| **Credentials** | None for the core track. If your tool calls a service that needs a key, the key must come from an environment variable, never from a file. |

## What you do and what the assistant does

You decide **what the tool should answer** and **how to check it**. The AI assistant decides **how many tools to build** and writes the code, tests and catalog entry. The repository's instructions ([AGENTS.md](../AGENTS.md), and `CLAUDE.md` for Claude Code) already tell the assistant the project rules, so you do not need to repeat them.

## Step 1 – Describe the tool to your assistant

Write down, in plain words:

- the scientific question the tool should answer;
- the data it should use (what you found in tutorial 01);
- what a correct answer looks like, for example one number you can check by hand.

Do not say how many tools to build. Ask the assistant to propose that.

## Step 2 – Ask your assistant to build it

Open the repository folder in VS Code and start a **new** chat or session in your AI assistant (GitHub Copilot in Agent mode, Claude Code or Codex). Paste a prompt like the one below, with your own question, server name and team name.

```text
Build an MCP server named sst-latest for team <team-name> in this repository.
Question it should answer: what is the latest sea surface temperature data available?
First use the earthdata MCP tools to find a suitable global sea surface temperature collection
(for example GHRSST MUR L4) and look at its newest granule. Then propose how many tools are needed
and what each does, and build them. The tool should return the collection id, the time of the newest
granule and its name, with the date checked. Return metadata only: do not download data and do not
ask for Earthdata credentials. Tests must run offline, using a saved sample response.
Follow AGENTS.md. Tell me what you built and what you could not verify.
```

The assistant may ask you to approve the plan and each command it runs. Read the plan before you approve it: if you disagree with the proposed tools, say so and ask it to revise.

## Step 3 – Check what it built

Ask the assistant to explain the result, then check it against this list:

| Check | What to look for |
|---|---|
| Tools | Each tool does one clear thing and has a plain-language description. |
| Inputs | Each input says what it is and gives an example. |
| Output | Short and structured: numbers, units, ids. Not raw data files. |
| Rules in the result | Units, the date checked, what was excluded, and where the data come from. |
| Errors | A bad input gives a sentence that says what to change. |
| Tests | At least one expected value you can confirm by hand. |
| Honesty | The assistant says which checks it ran and which it did not. |

If something is missing, tell the assistant what to change and ask it to run the checks again.

## Step 4 – Try the tools with your AI assistant

The server is registered for all three assistants automatically. A newly added MCP server does not appear in the session where it was built. **Exit this session and start a new one** to see it. If your assistant asks you to approve the new server, approve it.

To confirm the server is connected, list the servers in the new session (Copilot: **MCP: List Servers**; Claude Code: `/mcp`; Codex: ask "Which MCP tools do you have?"). Then ask a question without naming the tool:

```text
What is the latest sea surface temperature data available?
```

Expected: the assistant asks permission to call your tool, then reports the collection, the time of the newest granule and the date checked. The newest granule should be only a day or two old for a daily product such as GHRSST MUR L4. To cross-check, ask the assistant to answer the same question with the `earthdata` tools alone (`get_granules` sorted newest first); the two answers should agree. This is a metadata answer: it tells you what exists, not the temperature values. If the assistant answers without calling your tool, say "use the sst-latest tools" and check the server is connected.

## Exercise

Ask your assistant a question your tool cannot answer, for example a collection name that does not exist. The tool should return a helpful error, not a crash. If it does not, ask the assistant to fix it and add a test for it.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| Assistant does not see the new tool | Session started before the server existed | Start a new chat or session; check the server list (see Step 4) |
| Server shows as failed | The server code has an error | Ask the assistant to run the server tests and fix the failure |
| Assistant answers from memory without calling a tool | It did not use MCP | Say "use the tools from the sst-latest server" |
| Tool returns a huge result | It returns raw data | Ask for counts, statistics, ids or links instead |
| The assistant says a check passed but you did not see it run | Claim without evidence | Ask it to show the command and its output |

Next: [Tutorial 03 – Create an agent skill](03-create-an-agent-skill.md)
