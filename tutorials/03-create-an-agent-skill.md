# Tutorial 03 – Create an agent skill

| | |
|---|---|
| **Scientific purpose** | Capture the expert procedure around a tool – which checks to run first, how to choose arguments, how to report results honestly – so any agent session follows it. |
| **Learning objective** | Write a valid `SKILL.md`, install it from its canonical folder for your AI assistant (Copilot, Claude Code or Codex), and test it three ways: explicit invocation, a natural-language trigger, and a request where it should **not** apply. Confirm it can reach its MCP tools. |
| **Estimated time** | 45 minutes |
| **Starting state** | Your tool works ([tutorial 02](02-build-an-mcp-tool.md)). `skills/<skill-name>/SKILL.md` exists from the scaffold (or copy [templates/agent-skill/SKILL.md](../templates/agent-skill/SKILL.md)). |
| **Credentials** | Your AI assistant's account. |

Read [skills/obs-model-comparison/SKILL.md](../skills/obs-model-comparison/SKILL.md) first: it is the model to imitate.

## Anatomy of SKILL.md

```markdown
---
name: seasonal-bias-check            # = folder name; lowercase, digits, single hyphens; ≤ 64 chars
description: Explains seasonal model bias at a site using the obs-model-starter seasonal_bias tool... Use when the user asks which season a model is too warm or too cold, or about seasonal bias.
license: Apache-2.0
compatibility: Requires the obs-model-starter MCP server.
allowed-tools: mcp__obs-model-starter__describe_dataset mcp__obs-model-starter__seasonal_bias
metadata:
  version: "0.1.0"                   # quote it: metadata values must be strings
---

# Title
## When to use
## When not to use
## Required tools
## Procedure
## Expected output
## Assumptions
## Limitations
## Example tasks
```

| Field | Why it matters |
|---|---|
| `name`, `description` | Required by the [Agent Skills spec](https://agentskills.io/specification). The assistant sees only these two until the skill is used, so the description must contain the words users actually say, and "Use when …". Max 1024 characters. |
| `allowed-tools` | Optional, experimental in the spec. Claude Code pre-approves the listed tools while the skill is active (MCP tools named `mcp__<server>__<tool>`); Copilot and Codex ignore it. In the body, name tools by server and tool (`obs-model-starter` → `compare_model_to_obs`), because each assistant adds a different prefix. |
| Body sections | Required by this hackathon's validator. Keep under 500 lines; put long reference material in `references/` and link it. |

Add `scripts/`, `references/` or `assets/` only if the procedure needs them.

## Step 1 – Write the skill (20 minutes)

Edit `skills/<skill-name>/SKILL.md`. Replace every `REPLACE`. In **Procedure**, write numbered steps an agent can follow exactly: which tool first, what to check in its result, when to stop and ask. In **Expected output**, specify the answer structure (result sentence, table, method, provenance, limitations, tool trace).

Validate:

```bash
uv run python scripts/validate_repo.py --only skills --only catalog
```

Expected: `0 error(s)`.

## Step 2 – Install from the canonical folder (2 minutes)

The canonical source is `skills/<skill-name>/`. Each assistant reads its own folder; one command copies the skill to all of them:

```bash
uv run python scripts/install_skills.py <skill-name>
```

Expected: `installed <skill-name> -> .../.claude/skills/<skill-name>` (Claude Code, also read by Copilot) and `-> .../.agents/skills/<skill-name>` (Codex, also read by Copilot). Copilot lists the skill once. Use `--client claude|copilot|codex` to install for one assistant only, and `--personal` to install into your home folder for all projects.

After every edit, re-run this command and start a new chat/session. Never edit the copies; `--check` reports outdated copies.

## Step 3 – Test three ways (20 minutes)

Run each prompt in a **new chat/session**. Invoke explicitly with `/name` in Copilot and Claude Code, `$name` in Codex.

| Test | Prompt (example for the starter skill) | Pass if |
|---|---|---|
| Explicit invocation | `/obs-model-comparison Compare model A with the station observations at SYN-VALLEY.` (Codex: `$obs-model-comparison …`) | Skill loads; `describe_dataset` and `compare_model_to_obs` are called; answer follows Expected output |
| Natural trigger | `How well does model run B match the station observations at the mountain site in 2021?` | The assistant loads the skill by itself (the transcript shows the skill being used or its `SKILL.md` being read) and calls the tools |
| Should not apply | `In one sentence, what does RMSE stand for?` | The skill is **not** loaded and no starter tool is called |
| Tool access | (any of the first two) | The MCP tool calls actually appear and return data; a shell running Python scripts does not count. If the server is disconnected the skill says so and stops |

Record the assistant and its version, the prompts, tools called and pass/fail in `submissions/<team>/submission.md`. If your team uses more than one assistant, test each; skills behave slightly differently in each.

If the natural trigger fails, improve the `description` (add the user's words) – not the body. If the skill triggers when it should not, make the description more specific.

Organizers can run the same checks non-interactively for the starter skills with any assistant's command-line tool (uses a few requests on that account):

```bash
uv run python scripts/verify_agent_workflow.py --client copilot   # or claude, codex
```

## Example prompt

```text
/seasonal-bias-check Which season is model A worst at SYN-MOUNTAIN, and is the sample big enough to say so?
```

## Expected output

A short answer with: result sentence; table of season, n pairs, bias (°C); note on pairing and excluded months; provenance (synthetic); limitations (≈6 pairs per season over two years is a small sample); tool trace.

## Exercise

Remove the "When not to use" section from your skill and run the validator. Read the error, restore the section, and add one more not-applicable example that a user might plausibly confuse with your skill.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| `/skill-name` or `$skill-name` not found | Not installed, or chat started before install | `install_skills.py <name>`; new chat in the repository folder |
| Validator: name must match folder | `name:` differs from folder | Make them identical |
| Validator: metadata must map … strings | `version: 0.1.0` unquoted | `version: "0.1.0"` |
| Skill loads but tools fail | MCP server not connected | Check the server list in your assistant ([troubleshooting](../docs/troubleshooting.md#mcp-server-not-connected)) |
| Skill never triggers naturally | Description too generic | Add "Use when …" with the user's words |
| Works in one assistant, not another | Different discovery folders or behaviour | `install_skills.py --check`; test in each assistant and record results |
| Edited `.claude/skills/...` or `.agents/skills/...` and lost changes | Installer overwrote the copy | Always edit `skills/<name>/` |

Next: [Tutorial 04 – Combine tools and skills](04-combine-tools-and-skills.md)
