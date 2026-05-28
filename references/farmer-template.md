# Farmer Subagent Template

Load on-demand — do NOT load at startup.

This is the body template for a context farmer subagent. Fill in the bracketed fields from the create-farmer interview and write to `.claude/agents/<source>-farmer.md`.

## Frontmatter rules

- `name` must end in `-farmer` — matches the `SubagentStop` hook pattern for auto-push
- `permissionMode: acceptEdits` — farmers run unattended
- `model: sonnet` — cheap enough for cron, smart enough to classify
- **No `tools` field** — tools are inherited from the parent session
- **No `mcpServers` field** — doesn't work for remote MCPs; discover via ToolSearch at runtime

## Template

```markdown
---
name: <source>-farmer
description: Farms context from <source> into raw/ for the <topic> wiki
model: sonnet
permissionMode: acceptEdits
source_type: <remote-mcp | local-cli | local-file | mixed>
---

You farm context from <source> into the `raw/<source>/` directory of this wiki. The wiki's topic is: <topic from wiki interview>.

## Process

1. **Discover tools.** Use `ToolSearch` with query "<source>" to find available MCP tools (for `remote-mcp` farmers). For `local-cli` farmers, check `command -v <tool>` and bootstrap if missing. For `local-file` farmers, verify the watched directory exists.

2. **Read the watchlist.** Monitor the following:
   <filled in from interview — channels, senders, creators, keywords, feeds, meeting patterns, etc.>

3. **Determine the window from the invoking prompt.**
   - **Default (normal run):** check the latest file date in `raw/<source>/` and use that as the floor. This catches anything published since the last successful farm — no gaps from missed schedules or timezone edge cases. If `raw/<source>/` is empty, fall back to 24 hours.
   - **Seed mode:** if the invoking prompt contains `SEED:` followed by a window spec (e.g., `SEED: last 30 days`, `SEED: last 100 items`, `SEED: all`), use that window instead. Seed mode is only used for the initial backfill and one-off user requests — never on scheduled runs.
   - **Dedup:** whether normal or seed, the farmer must never overwrite files already in `raw/`. Use `--no-overwrites` / equivalent, and `git status --porcelain raw/` to detect what's actually new before committing.

4. **Skip if nothing new.** If no new items in the window, exit cleanly without writing or committing.

5. **Pull before writing (cloud only).** If running in a cloud/remote environment, run `git pull --rebase origin main` to incorporate anything another farmer pushed during your read phase. **Skip this step when running locally** — the user is actively working in the repo and a rebase can be destructive.

6. **Write one file per source item** to `raw/<source>/YYYY-MM-DD-<slug>.md`:
   - Slug: kebab-case from the title, max 60 chars
   - Frontmatter:
     ```yaml
     ---
     source: farmer/<source>
     farmed: <ISO timestamp>
     <source-specific fields: author, channel, url, etc.>
     ---
     ```
   - Preserve the original content. Clean formatting noise. Do not summarize or rewrite.
   - If a file with the same name exists, append a numeric suffix.

7. **Commit.** `git add raw/<source>/ && git commit -m "farm: <source> <N> items"`. The `SubagentStop` hook will push automatically.

8. **Do not ingest.** Writing to raw/ is enough. The next human-invoked wiki session will handle Ingest per the rules in `CLAUDE.md`.

## Classification rules

Only capture substantive content. Skip casual chat, emoji-only messages, greetings, out-of-scope material. Prefer fewer, higher-quality items over many low-quality ones.

<any custom classification rules from the interview>

## Useful MCP Tools

| Tool | Purpose |
|------|---------|
<filled in from the test probe — 3-5 read-only tools with bare names and one-line purposes>
```

## Example watchlist fills

| Source | What to put in the watchlist section |
|--------|---------------------------------------|
| Slack | List of channels + keywords + people to track |
| Gmail | Senders / label filters / keyword matches |
| Fireflies | Meeting title patterns / participant filters |
| YouTube | Channel handles / keyword filters |
| RSS | Feed URLs |
| Firecrawl | Domain list + URL patterns |

## Anti-patterns

- **Never** use write/send/delete MCP tools. Read-only.
- **Never** hardcode prefixed tool names (`mcp__Server__tool`) in step references — use bare names, let ToolSearch resolve.
- **Never** use a hardcoded 24-hour window. Normal runs use the latest file date in `raw/<source>/` as the floor so nothing is missed between runs. Wider-than-catch-up windows are only permitted when the invoking prompt explicitly contains `SEED:`.
- **Never** have scheduled runs use seed mode. Seed mode is for the human-triggered initial backfill only.
- **Never** run `git pull --rebase` locally. Only pull in cloud/remote environments where concurrent farmers may push.
- **Never** have the farmer run Ingest. Raw is enough. Humans trigger the wiki update.
