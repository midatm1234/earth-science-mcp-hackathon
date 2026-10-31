---
name: __SKILL_NAME__
description: REPLACE with what the skill does and the tools it uses. Use when REPLACE with the user requests that should trigger it (include the words scientists actually use).
license: Apache-2.0
compatibility: Requires the __SERVER_NAME__ MCP server connected to the client. Record the assistants you tested in submissions/<team>/submission.md.
allowed-tools: mcp____SERVER_NAME____summarize_values
metadata:
  version: "0.1.0"
  catalog-id: __SKILL_NAME__
---

# REPLACE skill title

One paragraph: the scientific workflow this skill guides and why a procedure is needed (what goes wrong without it).

## When to use

- REPLACE example request 1
- REPLACE example request 2

## When not to use

- REPLACE a nearby request that this skill should NOT handle, and what to use instead.

## Required tools

From the MCP server **`__SERVER_NAME__`**:

| Tool | Use |
|---|---|
| `summarize_values` | REPLACE |

Assistants add their own prefix (Claude Code `mcp____SERVER_NAME____summarize_values`, Copilot `__SERVER_NAME__-summarize_values`, Codex `mcp__<server name with _ for ->__summarize_values`). The `allowed-tools` header uses Claude Code names; other assistants ignore it.

If these tools are not available, stop and say which MCP server must be connected. Do not guess numbers.

## Procedure

1. **Select inputs.** REPLACE: how to map the user's words to tool arguments.
2. **Check metadata.** REPLACE: units, coordinates, time convention, missing data, version, provenance.
3. **Run the tools.** REPLACE: which tool, in which order, with which arguments.
4. **Check results.** REPLACE: sample size, warnings, errors and how to recover.
5. **Explain.** Use the output format below.

## Expected output

1. **Result** in one sentence with units.
2. **Table** of the key numbers.
3. **Method**: conversions, alignment, exclusions.
4. **Provenance**: dataset ids, versions, class (synthetic/cached/live), license.
5. **Limitations**.
6. **Tool trace**: tool names and arguments.

## Assumptions

- REPLACE

## Limitations

- REPLACE

## Example tasks

- `/__SKILL_NAME__` (Claude Code, Copilot) or `$__SKILL_NAME__` (Codex) REPLACE explicit invocation example
- "REPLACE natural-language request that should trigger the skill"
- Not applicable: "REPLACE request where the skill should not be used"
