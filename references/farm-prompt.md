# Farm Prompt

Load on-demand — do NOT load at startup.

The reusable prompt that triggers a farmer subagent. Used by all scheduling modes (cloud, desktop, loop, manual). Paste this into whichever mode the user picks — no separate `/farm` skill needed.

## The normal (scheduled) prompt

```
Run the <source>-farmer subagent per its instructions in .claude/agents/<source>-farmer.md. Use the Task tool to invoke it with the prompt "Execute your farming instructions now." When it finishes, report what it captured: number of new files, titles, any issues.
```

Substitute `<source>` with the actual farmer name (e.g., `slack`, `fireflies`, `gmail`).

This is the prompt that goes into every scheduling mode (cloud, desktop, loop). **Never include seed instructions in a scheduled prompt** — seeding is a one-off human-triggered action.

## The seed (one-off backfill) prompt

Used only for the initial wiki backfill or when the user explicitly asks to pull older content. Not for schedules.

```
Run the <source>-farmer subagent per its instructions in .claude/agents/<source>-farmer.md. Use the Task tool to invoke it with the prompt "Execute your farming instructions now. SEED: <window spec>". When it finishes, report what it captured: number of new files, titles, any issues.
```

Window spec examples:
- `SEED: last 30 days`
- `SEED: last 100 items`
- `SEED: last 12 months`
- `SEED: all` — as far back as the source will give us

The farmer template instructs farmers to parse `SEED:` from the invoking prompt and use that window instead of the 24-hour default. Dedup against existing files in `raw/` still applies.

## Why this shape

- **Routes through the subagent, not inline.** The subagent gets its own context window (no parent-session bloat) and triggers the `SubagentStop` hook for auto-push.
- **Works in any mode.** Cloud scheduled tasks, desktop schedules, `/loop`, or manual — all of them accept a natural-language prompt. This is that prompt.
- **No skill wrapper needed.** Second-brain wraps this in a `/farm` slash command; this skill skips that layer because the prompt itself is portable.

## Running manually from a live session

If the user wants to farm right now without scheduling, they can:

1. Say "run the <source> farmer" — you launch the subagent via `Task`
2. Or paste the prompt above into a new Claude Code session

Both work. The subagent writes to `raw/`, commits, and the `SubagentStop` hook pushes.
