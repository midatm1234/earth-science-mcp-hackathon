# Tutorial 04 – Combine tools and skills

| | |
|---|---|
| **Scientific purpose** | Answer a realistic question that needs several capabilities: find and verify real data (Earthdata MCP), run your own analysis (your server), and report it with a consistent procedure (your skill). |
| **Learning objective** | Plan a multi-tool workflow, run it in one session of your AI assistant, read the tool trace, and identify which part (tool, skill, data) is responsible for each statement in the answer. |
| **Estimated time** | 30 minutes |
| **Starting state** | Tutorials 01–03 done; your tool and skill installed; `earthdata` connected. |
| **Credentials** | Your AI assistant's account. No Earthdata Login (no downloads). |

## The pattern

```text
question
  └─ earth-data-discovery skill ──► Earthdata MCP: is real data available? which variable, units, period?
  └─ your skill ──────────────────► your MCP tools: compute on the fixture (or real data, if your tool reads it)
  └─ answer: result + provenance of each part + limitations + tool trace
```

The two halves must not be confused: discovery returns **metadata about real datasets**; the starter server computes on **synthetic fixtures**. A combined answer has to say which numbers come from where.

## Step 1 – Plan (5 minutes)

Write down, before prompting: the question; which tool answers which sub-question; what must be checked between steps (e.g. units of the real variable vs the fixture).

## Step 2 – Run (15 minutes)

Open a new chat in your assistant. Type `/` (Copilot, Claude Code) or `$` (Codex) before the skill name to invoke it explicitly. Example with the starter capabilities:

```text
We want to evaluate a model's monthly 2 m temperature against station data in central California for 2020.
1) Use the earth-data-discovery skill to check whether MERRA-2 monthly T2M (M2TMNXSLV) is available for POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33)) in 2020, and note its units.
2) Then use the obs-model-comparison procedure to show, with the synthetic sample data, how the comparison would be reported at SYN-VALLEY for 2020.
Clearly separate real-metadata results from synthetic-data results.
```

Expected: Earthdata calls (`get_collections`, `get_granules` → 12 granules, `get_variables` → T2M in K), then starter calls (`describe_dataset`, `compare_model_to_obs` with `start: 2020-01`, `end: 2020-12`). The answer should state that MERRA-2 T2M is in kelvin (like synthetic model A) and needs the same K→°C conversion, report the synthetic 2020 statistics, label them synthetic, and note that real station data and a download step would be needed for a real evaluation.

Replace this with your team's question, server and skill.

## Step 3 – Read the trace (10 minutes)

For each sentence in the answer, mark which tool result supports it. Anything unsupported is a hallucination risk: tighten the skill's procedure or output format.

| Statement in the answer | Source (tool + field) | Real / cached / synthetic |
|---|---|---|
| "12 monthly files exist for 2020" | `get_granules.total_hits` | real metadata, live |
| "bias −1.0 °C in 2020" | `compare_model_to_obs.mean_bias` | synthetic |

## Example prompt (team version)

```text
Using /<your-skill>, answer: <your scientific question>. First confirm data availability with Earthdata, then run our tool, then explain limitations.
```

## Expected output

An answer with two clearly separated parts (availability of real data; computed result), units consistent across parts, provenance per number, limitations, and a tool trace you can map line by line.

## Exercise

Ask a follow-up that should make the agent stop instead of guessing, e.g. "Now give me the real MERRA-2 bias at the station." Correct behaviour: explain that this requires downloading MERRA-2 (Earthdata Login) and real station observations, which the current tools do not provide. If the agent invents a number, add a rule to your skill.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| Synthetic numbers presented as real | Skill output format not strict | Require a provenance label per number |
| Units mixed (K and °C in one table) | No unit check step | Add "convert and state units" to the procedure |
| Agent tries to download data | Over-eager agent | Deny the tool call; add "do not download" to the skill |
| Earthdata unavailable | Network | Continue with your tools; mark discovery part **blocked** |
| Usage limit hit | Subscription limit | Continue with plain MCP client tests; mark combined workflow **blocked** |

Next: [Tutorial 05 – Submit and test a peer](05-submit-and-test-a-peer.md)
