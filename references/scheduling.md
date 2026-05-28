# Scheduling

Load on-demand — do NOT load at startup.

Four ways to run a farmer on a schedule. Ask the user which one they want, then walk them through that mode only.

## Source-type gating (read first)

Cloud mode runs in an Anthropic-hosted container that only has access to claude.ai MCP connectors and the cloned git repo. It **cannot** reach the user's local tools, local filesystem, or homebrew-installed binaries.

| Farmer source type | Cloud? | Why |
|--------------------|--------|-----|
| `remote-mcp` (Slack, Gmail, Fireflies, Notion, Apify, Firecrawl, etc.) | ✅ Recommended | MCP connectors follow the user into the cloud container |
| `local-cli` (`yt-dlp`, `gh`, custom scripts) | ❌ by default | Tool isn't installed in the container. Possible with a bootstrap step (`pip install`) but fragile — prefer desktop. |
| `local-file` (Obsidian clipper, watched folders, downloaded PDFs) | ❌ | Container can't see the user's filesystem |
| `mixed` | Treat as most restrictive component | |

If the user asks for cloud mode but the farmer isn't `remote-mcp`, stop and explain. Offer desktop or loop instead, or — if they insist on cloud — walk them through adding a runtime bootstrap.

## Mode comparison

| Mode | Runs when | Needs machine on | Needs GitHub remote | Works with local-cli / local-file? | Best for |
|------|-----------|------------------|---------------------|-------------------------------------|----------|
| **Cloud scheduled** | 24/7 on Anthropic infra | No | Yes | No (unless bootstrapped) | Remote-MCP farmers, set-and-forget |
| **Desktop scheduled** | On a cron, locally | Yes | No | Yes | Local-CLI / local-file farmers, long-running local automation |
| **Loop (session-scoped)** | While a Claude Code session is open | Yes | No | Yes | Quick polling during a work session |
| **Manual** | Only when user says so | Yes | No | Yes | Full control, no automation |

## Ask the user

> Four ways to run this on a schedule:
>
> 1. **Cloud** — runs 24/7 on Anthropic's infrastructure, no laptop needed, inherits your MCP connections automatically. Needs a private GitHub remote so the cloud runner can clone + push.
> 2. **Desktop** — runs locally on a cron from the Claude Code desktop app. Machine has to be on.
> 3. **Loop** — runs on a timer inside an active Claude Code session. Good for "poll every 30 minutes while I'm working."
> 4. **Manual** — I don't schedule anything. You run it when you want.
>
> Which one?

## Mode 1: Cloud scheduled

### Prerequisites

- Farmer source type is `remote-mcp` (see gating above). If not, stop and recommend desktop.
- Private GitHub remote (`git remote get-url origin` succeeds). If not, offer to run `gh repo create <name> --private --source=. --remote=origin --push` before continuing.
- User is signed in to Claude Code
- MCP connectors the farmer uses are connected in the user's Claude account (they inherit automatically into the scheduled task)

### Flow

Do **not** call `RemoteTrigger` or `CronCreate` directly — the cloud trigger API uses an undocumented v2 job-config shape that the built-in `schedule` skill already knows how to produce. Instead:

1. Ask: "What time should it run? Default: daily at 6am in your local timezone. I'll offset a few minutes off the hour to dodge the scheduler's :00/:30 pile-up."
2. If multiple farmers already exist, pick a time at least 30 minutes offset from existing schedules to avoid merge conflicts from concurrent pushes.
3. Load `references/farm-prompt.md` and build the farm prompt (substituting the farmer name).
4. Invoke the `schedule` skill via the `Skill` tool:

   ```
   Skill({
     skill: "schedule",
     args: "Create a new scheduled remote agent named \"<source>-farmer\" that runs <cron time in user's local timezone + TZ name> against the private GitHub repo <org>/<repo>, with the prompt: <farm prompt from references/farm-prompt.md>. Attach the MCP connectors the farmer uses: <list from farmer's Useful MCP Tools table>."
   })
   ```

5. The `schedule` skill handles: timezone → UTC conversion, environment selection, connector attachment, UUID generation, and the v2 job-config payload. Let it drive the actual `RemoteTrigger` call.

### Confirm

> Done. `<source>-farmer` runs at `<human time>` daily on Anthropic's cloud. You can see, edit, or run it now at claude.ai/code/scheduled. Close your laptop — it runs without you.

## Mode 2: Desktop scheduled

### Flow

Tell the user:

> Open the Claude Code desktop app → Schedule page → New local task. Set:
>
> | Field | Value |
> |-------|-------|
> | Name | `<source>-farmer` |
> | Schedule | `<user's preferred time>` |
> | Prompt | (paste the farm prompt below) |
> | Working directory | `<current repo path>` |

Load `references/farm-prompt.md` and give them the substituted prompt to paste.

### Caveats

- Runs only when the laptop is awake and Claude Code desktop is installed.
- No auto-push unless the farmer commits (it does — that's what the `SubagentStop` hook is for).

## Mode 3: Loop

### Flow

Tell the user they can run, from any active Claude Code session:

```
/loop 30m <paste farm prompt>
```

Load `references/farm-prompt.md` and substitute the farmer name. Default interval: 30 minutes. Stops when they close the session.

### Caveats

- Session-scoped. No persistence across restarts.
- Good for short bursts, not long-running automation.

## Mode 4: Manual

No setup. Tell them:

> To farm on demand, start a Claude Code session in this repo and say "run the <source> farmer" — I'll invoke it. You can also re-run this skill and jump straight to scheduling later.

## After any mode

Offer:

> Add another farmer for a different source, or are we done?

If another: go back to the create-farmer flow. Remember to offset the schedule time for the new farmer.
