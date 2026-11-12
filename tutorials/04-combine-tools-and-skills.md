# Tutorial 04 – Combine tools and skills

| | |
|---|---|
| **Scientific purpose** | Answer a realistic question that needs several capabilities: check real data with the Earthdata MCP, run your own tools, and report with a consistent procedure (your skill). |
| **Learning objective** | Plan a multi-tool workflow, let your AI assistant run it in one session, read the tool trace, and say which part (Earthdata, your tool, your skill) is responsible for each statement in the answer. |
| **Starting state** | [Tutorial 03](03-create-an-agent-skill.md) done: your MCP server and skill are listed in your assistant, and the `earthdata` server is connected. |
| **Credentials** | Your AI assistant's account. No Earthdata Login (no downloads). |

## What you do and what the assistant does

You decide **the question** and **which source answers which part**. The assistant chooses the tool calls and runs them in order. The answer must say which numbers came from where.

```text
question
  ├─ earthdata MCP ──► metadata about real data: what exists, how new, which variable and units
  ├─ your skill ─────► your MCP tools: the map, the animation, or your own calculation
  └─ answer: result + source of each part + limitations + tool trace
```

Keep the two halves apart. Earthdata returns **metadata** from NASA's catalog. Your server returns **its own results**, which may come from a different source (a sample file, or a service such as NOAA ERDDAP).

## Step 1 – Plan

Write down, in plain words:

- the question;
- which part each source answers, for example "Earthdata: is the data current? Our tools: the map";
- the dataset and region you will use;
- one thing the assistant must check between steps, for example that the newest dates from the two sources agree.

## Step 2 – Ask your assistant to run it

Start a **new** chat or session in your AI assistant (GitHub Copilot in Agent mode, Claude Code or Codex), so your server and skill are loaded. Pick the dataset your own tools work with. Examples:

| Dataset | Earthdata collection to look for | Your tools could |
|---|---|---|
| Sea surface temperature | GHRSST MUR L4 (`MUR-JPL-L4-GLOB-v4.1`) | map and animate the newest days |
| Sea surface height (SWOT) | SWOT L2 KaRIn Low Rate SSH, Version D (`SWOT_L2_LR_SSH_D`) | check which swaths cover your region and when; maps need swath handling and an Earthdata Login to download, so use it for the Earthdata half only unless your team has that set up |
| Precipitation | GPM IMERG Late daily (`GPM_3IMERGDL`) | map the last 7 days of rain |
| Soil moisture | SMAP L3 daily (`SPL3SMP`) | map the newest orbit-day composite |
| Your own data | search with the `earthdata` tools | whatever your tools do |

Paste a prompt like this, with your own dataset, region and skill name:

```text
I want <what your tools produce, e.g. a map and a 10-day animation> of <dataset> for <region>.

- First, with the earthdata MCP tools, find the collection for <dataset> and report the date of its
  newest granule.
- Then use /<your-skill> (Codex: $<your-skill>) to produce the result with our tools.
- Compare the newest date from Earthdata with the newest date our tools found, and say if they differ.
- Keep the parts separate: label each result as Earthdata metadata or as our tools' result, with its source.
- Do not download data and do not ask for Earthdata credentials.

Finish with the limitations and the tool trace.
```

The assistant may ask you to approve each tool call. Read what it asks to run.

Expected: Earthdata calls first (for example `get_collections`, `get_granules`), then your server's tools in order, then an answer that keeps the two sources apart.

If your tools cover a different dataset from the one you want to try, go back to [tutorial 02](02-build-an-mcp-tool.md) and ask the assistant to extend your server first. Your skill's tool list has to match.

## Step 3 – Read the trace

Ask the assistant for the tool trace, then check each sentence of the answer against a tool result. Anything without a matching result is a hallucination risk: ask the assistant to tighten the skill's procedure or output format.

| Statement in the answer | Source (tool and field) | Kind |
|---|---|---|
| "The newest <dataset> granule ends on <date>" | Earthdata `get_granules` | real metadata, live |
| "The result covers <dates>" | your tools' results | real data from your server's source |
| "The two newest dates agree" | both of the above | your check |

Also check:

| Check | What to look for |
|---|---|
| Separation | Each number is labelled with its source, and metadata is not presented as data values. |
| Units | Units are stated, and are the same everywhere a value is compared. |
| No downloads | No Earthdata file download, no login request. |
| Tools only | The assistant used the Earthdata tools and your server's tools, not shell commands or ad hoc scripts. |
| Honesty | The answer says what was not checked, for example fine-scale features on a thinned grid, or gaps in coverage. |

## Example: two datasets, two skills, one workflow

This optional example adds a second dataset, SWOT sea surface height (SSH), with its own tools and its own skill. The final workflow then uses **two skills**: `sst-map-workflow` for temperature and `swot-ssh-workflow` for sea surface height.

> **Needs an Earthdata Login token.** SWOT files are not on a login-free service that I found, so this example downloads data. Do it only if your organizers allow it. You need a free [Earthdata Login](https://urs.earthdata.nasa.gov) account and a user token:
>
> 1. Sign in at <https://urs.earthdata.nasa.gov> and open your profile.
> 2. Click **Generate Token**, then the **Generate Token** button. The token is hidden until you click **Show Token**.
> 3. Set it as the environment variable `EARTHDATA_TOKEN` on your own machine, then start a new session. Do not paste it into the chat, a file in the repository or a tool argument.
>
> A token is valid for 60 days, and you can hold at most two. If it expires or is rejected, generate a new one (see NASA's [user token guide](https://urs.earthdata.nasa.gov/documentation/for_users/user_token)). If it may have been exposed, delete it on the same page.
>
> **How the tool uses it.** The tool reads `EARTHDATA_TOKEN` and sends it only to NASA, in the header `Authorization: Bearer <token>`, as the user token guide describes. If the token is missing, the tool pauses and asks you to sign in through a pop-up in your assistant. The pop-up opens the Earthdata Login page in your browser, so your password never goes through the chat, the model or any log. After you generate the token and set the variable, run the request again. If it still fails, see NASA's [Python data access guide](https://urs.earthdata.nasa.gov/documentation/for_users/data_access/python) for how the data server redirects through Earthdata Login.

### Part 1 – Build the SWOT tools

Start a **new** chat or session and paste a prompt like this, with your own team name and region:

```text
Create a new MCP server named swot-ssh for team <team-name> that finds and maps SWOT sea surface height.
Data: SWOT L2 KaRIn Low Rate SSH, Version D (SWOT_L2_LR_SSH_D), variable ssh_karin in metres.
First read the sst-latest README as a model, use the earthdata MCP tools to confirm the collection,
propose how many tools are needed, then build them. Region: <region>.

- Tools: one per step (passes over the region in the last 10 days, fetch a region subset of one pass,
  draw one Cartopy map, list files made); add more if a step needs them.
- Swath data: SWOT is irregular swaths, not a grid; draw it as points or a swath mesh, and say so.
- Quality: apply the product's quality flags, drop fill values, and report how many points were dropped.
- Output: file paths, sizes, pass times, units (m) and date checked. Never data arrays.
  Write files only to the git-ignored output folder.
- Login: use the Earthdata user token .
- Dependencies: pin any new package with uv add. Tests: offline, with a small saved sample.

Follow AGENTS.md. Tell me what you built and what you could not verify.
```

Check the result with the Step 3 table in [tutorial 03](03-create-an-agent-skill.md), plus:

| Check | What to look for |
|---|---|
| Credentials | The token is read only from `EARTHDATA_TOKEN`, sent only to NASA, and appears in no file, log or tool result; the variable name is in the README; a missing or rejected token gives a clear message, not a crash. |
| Quality | The result says which flags were applied and how many points were dropped. |
| Swath | The assistant explained how it draws irregular swaths. |
| Honesty | It says what ran against the real service and what only against the saved sample. |

### Part 2 – Write the second skill

**Exit this session and start a new one** so the new tools load. Then paste:

```text
Write an agent skill named swot-ssh-workflow for team <team-name>. First list the tools of the
swot-ssh MCP server in this session.

- Tools: use only those tools. List them in allowed-tools. Never fall back to shell commands,
  Python scripts or tools from other servers; if a tool is missing or fails, say so and stop.
- Procedure, in order: passes over the region in the last 10 days, fetch the newest pass,
  draw the map, list the files made.
- Answer: region, pass times, units (m), quality flags applied, source, date checked and files made;
  say SWOT is a swath measurement of sea surface height, not a daily gridded field.
- Use it for: maps of recent sea surface height or ocean eddies. Not for: temperature, or
  values at one place.
- Description: use the words people actually say.

Install it for all assistants, validate it, and follow AGENTS.md.
Tell me what you created and what you could not verify.
```

### Part 3 – Run the workflow with both skills

Start a **new** session, then paste:

```text
For <region>, use /sst-map-workflow to map the newest sea surface temperature, then use
/swot-ssh-workflow to map the newest SWOT sea surface height pass over the same region.

- Report the date of the SST map and the time of the SWOT pass, and say how far apart they are.
- Say what each shows: SST is a daily gridded analysis; SWOT is a swath with quality flags.
- Keep the parts separate and label each result with its source.
- Do not draw conclusions about eddies or fronts that the two maps do not show.

Finish with the limitations and the tool trace.
```

Pass if:

- the trace shows `sst-latest` tools for the first map and `swot-ssh` tools for the second, in that order;
- no shell command or ad hoc script was used;
- the answer states the time gap between the two maps and does not claim they are simultaneous;
- with `EARTHDATA_TOKEN` unset, the tool paused with a sign-in pop-up (or a clear message) and made no download;
- with the token set, the download worked;
- no password or token appears anywhere in the conversation, the tool results or the files.

## Exercise

Ask a follow-up that should make the assistant stop instead of guessing:

```text
Now download today's full global file for this dataset and give me the exact value at one named location.
```

Pass if the assistant explains that downloading needs an Earthdata Login (not part of this workshop) and that your tools make regional results, not point values, and does not invent a number. If it invents a number, ask it to add a rule to your skill and run the exercise again in a new session.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| Your tools or skill are not found | Session started before they were installed | Exit and start a new session; check the server list in your assistant |
| Metadata presented as data values | Skill output format not strict | Ask the assistant to require a source label per number |
| The two sources show different newest dates | Different update schedules, or the question compares different things | Report both; do not hide the difference |
| Assistant tries to download data | Over-eager assistant | Decline the call; ask it to add "do not download" to the skill |
| Earthdata unavailable | Network | Continue with your own tools and mark the discovery part **blocked** |
| Usage limit message | Account limit reached | Stop here and mark the combined workflow **blocked** |

Next: [Tutorial 05 – Submit and test a peer](05-submit-and-test-a-peer.md)
