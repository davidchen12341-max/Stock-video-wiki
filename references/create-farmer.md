# Create Farmer

Load on-demand — do NOT load at startup.

Interview flow for building a context farmer subagent. Adapted from `temp/second-brain/.claude/skills/create-farmer/SKILL.md`.

## Prerequisites

Before running this flow:
- `.claude/agents/` exists (created by `setup_farming.py`)
- `.claude/settings.json` has git permissions (created by `setup_farming.py`)
- `CLAUDE.md` exists (user has completed the wiki interview)

## Flow

### 1. Source

Ask:

> Where do you want context from? Give me one source at a time — Slack, YouTube, Gmail, Fireflies, a website, RSS, a local tool like `yt-dlp`, a watched folder — whatever.

### 2. Classify the source type

Based on the answer, classify the source into one of these buckets. You'll use this in Phase 6 to pick a scheduling mode.

| Type | Examples | Data lives where |
|------|----------|------------------|
| `remote-mcp` | Slack, Gmail, Fireflies, Notion, Google Calendar, Apify scrapers, Firecrawl | Claude.ai connectors — available in cloud |
| `local-cli` | `yt-dlp`, `gh` CLI, custom Python scripts, homebrew tools | On the user's machine only |
| `local-file` | Obsidian clipper output, watched folders, PDF drops | On the user's filesystem only |
| `mixed` | Combines the above | Treat as most restrictive |

Record the chosen type — it goes in the farmer's frontmatter `source_type:` field and drives Phase 6's scheduling recommendation.

### 3. Probe tool availability

- **`remote-mcp`**: Use `ToolSearch` with the service name as query. Report what you find.
  - **Tools returned:** "Found N tools for <source>. Testing one to confirm connectivity."
  - **No tools:** Stop and tell the user:
    > No MCP tools found for <source>. Connect one first via Claude Code `/mcp` or at claude.ai/settings/connectors, then re-run me and I'll continue.
- **`local-cli`**: Check the binary exists with `command -v <tool>` via Bash. If missing, tell the user how to install it (e.g., `brew install yt-dlp`) and pause.
- **`local-file`**: Ask for the absolute path of the folder the farmer should watch. Confirm it exists.

### 4. Test a read tool (or CLI)

For `remote-mcp`: pick one obvious read tool (e.g., `list channels`, `list recent messages`) and call it. Show the user what came back so they know the connection is live.

For `local-cli`: run the tool with a `--version` or `--help` flag via Bash to confirm it's invocable.

For `local-file`: `ls` the watched folder and show the user the count + a few filenames so they know the farmer will see the right material.

### 5. Watchlist interview

Ask what to watch. Tailor the question to the source:

| Source | Ask |
|--------|-----|
| Slack | "Which channels? Any keywords or people I should cross-reference?" |
| Gmail | "Which senders or labels? Any subject keywords?" |
| Fireflies | "Which meeting titles or participant patterns?" |
| YouTube | "Which channels or creators? Any keyword filters on titles?" |
| RSS | "Which feed URLs?" |
| Firecrawl | "Which domains or URL patterns?" |

Capture answers as a bulleted list — you'll paste them into the farmer body.

### 6. Write the subagent

Load `references/farmer-template.md`. Fill in:
- `<source>` — the service name (lowercase, kebab-case)
- `<topic>` — from `CLAUDE.md`
- `source_type:` frontmatter field — from step 2
- Watchlist section — from step 5
- Useful tools table — from the tools ToolSearch returned in step 3 (bare names, not prefixed) OR the CLI commands / file-read patterns if not `remote-mcp`

Write to `.claude/agents/<source>-farmer.md`.

### 7. Update settings.json permissions

Read `.claude/settings.json`. Add the specific read-only MCP tool names the farmer uses to `permissions.allow`. Use the **full prefixed names** here (e.g., `mcp__claude_ai_Slack__slack_read_channel`). Never add write/send/delete tools.

Example additions for a Slack farmer:
```json
"mcp__claude_ai_Slack__slack_read_channel",
"mcp__claude_ai_Slack__slack_read_thread",
"mcp__claude_ai_Slack__slack_search_public_and_private",
"mcp__claude_ai_Slack__slack_search_channels",
"mcp__claude_ai_Slack__slack_read_user_profile"
```

### 8. Test run

Ask:

> Want to run it now to test? I'll invoke the farmer in normal mode (last 24 hours) and show you what it pulls.

If yes: invoke the subagent via the `Task` tool with the farmer's name and prompt `"Run your farming process now per your instructions."` Show the user what the farmer captured — file count, first few titles, any issues.

Note: custom agents defined in `.claude/agents/` only load at session start, so if you just wrote the farmer file, you may need to run the farmer's steps inline (via Bash / MCP tools directly) for the first test. Warn the user and offer either option.

### 9. Offer seeding

Before moving to scheduling, ask:

> Want to seed the wiki with older content now? By default the farmer only looks at the last 24 hours. For the initial load, I can invoke it with a wider window — e.g., last 30 days, last 100 items, or as far back as the source will give us.

If yes:
- Decide on the seed parameters with the user (time window, item count, or both).
- Invoke the farmer with a seed-mode prompt — see `references/farm-prompt.md` for the exact shape. The farmer template specifies how farmers interpret seed instructions.
- After the seed run completes, show the user the result and offer to immediately ingest the seeded raw files into the wiki per `CLAUDE.md`, or wait until after scheduling.

If no: continue to scheduling.

### 10. Offer scheduling

Load `references/scheduling.md`. Ask:

> Want to schedule this to run automatically, or run it manually when you want fresh context?

If they schedule, walk them through the chosen mode. If they pick manual, tell them they can re-invoke the skill anytime and jump straight to the scheduling phase.

## Adding another farmer

Repeat this flow. Each farmer is independent. Multiple farmers should run on offset schedules (at least 30 minutes apart) to avoid merge conflicts from concurrent pushes.
