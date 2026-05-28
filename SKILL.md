---
name: build-wiki
description: "Set up a self-feeding Karpathy-style LLM wiki in the current repo. Reads Karpathy's canonical gist, interviews the user to co-design their wiki schema, scaffolds raw/ and wiki/, installs git hooks, then builds context farmer subagents that feed the wiki from MCP sources. Schedules farmers on cloud, desktop, loop, or manual. Triggers: 'build wiki', 'karpathy wiki', 'set up a wiki', 'self-feeding wiki', 'context farming wiki'."
---

# Build Wiki

Scaffold a Karpathy-style LLM wiki and the farmers that feed it. One skill, one conversation, done.

The wiki half is interview-driven — Karpathy left the schema deliberately vague because the LLM is supposed to co-design it with the user. The farming half is scaffolded infrastructure, ported from the second-brain pattern.

## Constraints

- **Private repo only.** The wiki will contain personal context. Gate on `gh repo view --json visibility` before any file writes. Public or unknown → stop.
- **Farmer subagent names must end in `-farmer`.** Required for the `SubagentStop` hook to fire.
- **Farmers get read-only MCP tools only.** Never add write/send/delete tools to `settings.json` allowlist.
- **`raw/` is immutable.** Farmers append new files, never overwrite.
- **24-hour window.** Farmers only process sources from the last 24 hours per run.
- **Do not template `CLAUDE.md`.** It is written from the interview in Phase 3, not copied from a reference implementation.

## Arguments

Parse the ARGUMENTS line **before** state detection. If a recognized subcommand is present, skip the setup phases entirely and run the requested operation.

| Pattern | Action |
|---------|--------|
| `farm` | Run **all** farmers in `.claude/agents/*-farmer.md`, then ingest all new raw files per `CLAUDE.md` |
| `farm <source>` | Run `.claude/agents/<source>-farmer.md` only, then ingest new raw files per `CLAUDE.md` |
| `farm <source> seed <window>` | Seed run with explicit window (e.g., `seed last 30 days`), then ingest |
| `ingest` | Scan `raw/` for un-ingested files, ingest per `CLAUDE.md` |
| `lint` | Run wiki lint per `CLAUDE.md` |
| _(empty or unrecognized)_ | Current behavior — state detection → setup phases |

### Farm flow

When ARGUMENTS starts with `farm`:

1. **Resolve farmers.** If `<source>` is given, load `.claude/agents/<source>-farmer.md`. If bare `farm`, glob `.claude/agents/*-farmer.md` and run each.
2. **Invoke the farmer** via the `Agent` tool with subagent_type set to the farmer name. Pass the prompt from `references/farm-prompt.md` — normal or seed depending on args.
3. **If the farmer subagent fails or is rejected**, fall back to running the farmer's steps inline (read the farmer file and execute its process directly in the current session). This is what happened in the original conversation — the subagent wanted to rebase, the user rejected it, so the skill should just do the work itself.
4. **Ingest.** After farming completes, read `CLAUDE.md` and ingest every new file in `raw/` into `wiki/`. This is not optional — farming without ingesting leaves the wiki stale.
5. **Commit.** Stage raw files and wiki updates together. Commit message: `wiki: farm + ingest <source> (<N> new)`.

## Flow

Six phases, run sequentially. Skip any phase whose artifacts already exist.

| Phase | What | Mechanical or Interview |
|-------|------|-------------------------|
| 1 | Fetch gist + welcome + "how far" | Mechanical |
| 2 | Init vault (gating + folders + initial commit) | Mechanical (script) |
| 3 | Interview → write `CLAUDE.md` | Interview |
| 4 | Install farming infra (hooks + settings.json) | Mechanical (script) |
| 5 | Build first farmer | Interview |
| 6 | Schedule the farmer | Interview |

## State detection

At start, detect where to resume:

| State | Resume at |
|-------|-----------|
| No `raw/` directory | Phase 1 |
| `raw/` exists, no `CLAUDE.md` | Phase 3 |
| `CLAUDE.md` exists, no `.claude/hooks/subagent-push.sh` | Phase 4 |
| Hooks installed, no `.claude/agents/*-farmer.md` | Phase 5 |
| Farmers exist, none scheduled | Offer Phase 6 |
| Everything exists | Ask what they want to do (add farmer, schedule, ingest, query, lint) |

---

## Phase 1: Fetch gist + welcome

Use `curl` via Bash to get Karpathy's LLM wiki spec verbatim:

```bash
curl -sL https://gist.githubusercontent.com/karpathy/442a6bf555914893e9891c11519de94f/raw
```

Read the full content into your context. This is the source of truth for the pattern — you'll need it for the interview in Phase 3.

Do **not** use `WebFetch` for this — its post-processing model summarizes the gist instead of returning the raw markdown, which violates the "treat the source doc as canon" rule. `curl` returns the file unmodified.

If `curl` fails (no network, etc.), ask the user to paste the gist content directly.

### Welcome (first run only)

Detect first run by checking whether `raw/` exists. If it already exists, skip this welcome silently and jump to state detection.

On first run, display:

```
Welcome to the Karpathy wiki builder.

Karpathy dropped the idea: raw sources plus LLM-maintained wiki articles, and a schema you co-design together.

This skill fixes that:

  1. Co-design your wiki schema — I interview you, read Karpathy's gist together, and write your bespoke CLAUDE.md
  2. Install farming infrastructure — git hooks, auto-commit, auto-push
  3. Build context farmers — subagents that pull new material from any MCP source (Slack, YouTube, Gmail, Fireflies, RSS, whatever) into raw/
  4. Schedule them — cloud, desktop, loop, or manual

You pick the topic and the sources. I do the rest.
```

Then **immediately** call `AskUserQuestion`:

Question: `How far do you want to go right now?`

Options:
- `Full build — wiki + farmer + schedule (recommended)` — "Everything. Interviews you, scaffolds the wiki, walks you through your first farmer, schedules it. ~10 minutes."
- `Wiki + one farmer (manual runs)` — "Interview + wiki + one farmer you trigger yourself. Skip scheduling. ~5 minutes."
- `Just the wiki` — "Interview and scaffold only. No farmers yet — re-run me later to add them."

Store the choice:

| Choice | Phases |
|---|---|
| Full build | 2 → 3 → 4 → 5 → 6 |
| Wiki + one farmer | 2 → 3 → 4 → 5 |
| Just the wiki | 2 → 3 |

---

## Phase 2: Init vault

Run the init script:

```bash
python3 .claude/skills/build-wiki/scripts/init_vault.py
```

The script handles:
- `gh` CLI check
- Privacy check (blocks on public repos)
- Creates `raw/` and `wiki/` with `.gitkeep`
- Writes `.gitignore`
- `git init` if needed
- Initial commit and push

If the script exits with an error, read the error message to the user and stop. Common failures:
- `gh` not installed → tell them to `brew install gh` and run `gh auth login`
- Repo is public → tell them to run `gh repo edit --visibility private --accept-visibility-change-consequences`
- No remote → warn that cloud scheduling (Phase 6) won't work, continue

If the user needs to create a new private repo first, offer to run `gh repo create <name> --private --source=. --remote=origin --push` for them before re-running the script.

---

## Phase 3: Interview → CLAUDE.md

Before interviewing, check whether `CLAUDE.md` already exists in the repo root:
- **Missing:** proceed to the interview and write a new one.
- **Exists and appears to be a wiki schema** (mentions raw/, wiki/, ingest/query/lint, or references Karpathy): read it, summarize back to the user, and ask whether to skip Phase 3 or revise. Don't clobber silently.
- **Exists but is something else** (existing project CLAUDE.md for non-wiki instructions): stop and ask the user where they want the wiki schema. Options: (a) append a `# Wiki` section to the existing CLAUDE.md, (b) write to a different filename (e.g., `WIKI.md`) and update hooks + docs accordingly, (c) abort.

Load `references/wiki-interview.md` and run the interview it describes. Write `CLAUDE.md` from the user's actual answers, not from any template.

After writing, show them the file and ask: "Does this match what you had in mind? Anything to cut, add, or rewrite?" Revise before moving on.

---

## Phase 4: Install farming infrastructure

Run the setup script:

```bash
python3 .claude/skills/build-wiki/scripts/setup_farming.py
```

The script:
- Copies `auto-commit.sh`, `session-sync.sh`, `subagent-push.sh` into `.claude/hooks/`
- Wires the hooks into `.claude/settings.json`
- Adds base git permissions to `permissions.allow`
- Creates `.claude/agents/` for farmer subagents

Idempotent — safe to re-run.

---

## Phase 5: Build first farmer

Load `references/create-farmer.md` and run the flow it describes. The farmer subagent goes in `.claude/agents/<source>-farmer.md` using the template in `references/farmer-template.md`.

After writing the farmer, update `.claude/settings.json` with the specific read-only MCP tools the farmer uses (create-farmer.md step 6). Never add write/send/delete tools.

**Record the source type** — you'll need this for Phase 6's scheduling recommendation:
- **`remote-mcp`** — farmer uses claude.ai connectors (Slack, Gmail, Fireflies, Notion, Apify, Firecrawl, etc.). Cloud scheduling works because those connectors are available in the remote environment.
- **`local-cli`** — farmer shells out to a tool installed on the user's machine (`yt-dlp`, custom scripts, homebrew binaries). Cloud scheduling will fail unless the farmer bootstraps the tool — prefer desktop/loop.
- **`local-file`** — farmer reads from a directory the user curates on their machine (Obsidian clipper output, downloaded PDFs). Cloud cannot see it — desktop/loop/manual only.
- **`mixed`** — combines the above. Treat as the most restrictive.

Commit: `farmer: add <source>-farmer`

### 5a. Optional: seed the wiki

After the farmer is written, offer a seed run:

> Want to seed the wiki with older content before the first scheduled run? I can invoke the farmer once with a wider lookback window (e.g., last 30 days, last 100 items, or "everything the source will give us") so you start with real material instead of an empty `raw/`.

If yes: invoke the farmer via the `Task` tool (or run the steps inline if custom agents can't load mid-session) with a seed-mode prompt — see `references/farm-prompt.md`. The farmer-template.md specifies how farmers handle seed mode.

After seeding, offer to ingest the new raw files into the wiki immediately per `CLAUDE.md`, or defer ingestion until after scheduling.

Then offer: run a normal 24h test, schedule it (Phase 6), or add another farmer (repeat Phase 5).

---

## Phase 6: Schedule

Load `references/scheduling.md` for the mode-comparison table and the source-type gating rules. The decision looks like this:

| Source type | Recommended mode | Why |
|-------------|------------------|-----|
| `remote-mcp` | **Cloud** | Connectors follow the user; runs 24/7 without the laptop |
| `local-cli` | **Desktop cron** (or loop for short bursts) | Tool only exists on the user's machine |
| `local-file` | **Desktop cron** or **Manual** | Cloud can't see the filesystem |
| `mixed` | **Desktop cron** | Same reason as the most restrictive component |

**Gate:** if the user asks for cloud mode but the farmer's source type is anything other than `remote-mcp`, stop and explain why. Offer the appropriate alternative or a bootstrap workaround (e.g., `pip install` the tool at runtime) if they really want cloud.

If cloud is the chosen mode **and** Phase 2 warned about no remote, stop and tell the user to push to a private GitHub repo first (offer to run `gh repo create` for them).

**To actually create the schedule, invoke the built-in `schedule` skill via the `Skill` tool** — do NOT hand-roll `RemoteTrigger` / `CronCreate` calls. The skill handles the undocumented v2 job-config shape, environment IDs, MCP connector attachment, and UUID generation. Pass a natural-language prompt that includes: farmer name, cron time in user's local timezone (let the skill convert), repo URL, and the farm prompt from `references/farm-prompt.md`.

For desktop and loop modes, `scheduling.md` gives the user-facing instructions — those don't use the `schedule` skill.

After scheduling, offer: "Add another farmer, or are we done?"

---

## After setup

Remind the user of the loop:

1. Farmers run on their schedule, drop new files into `raw/`, auto-commit and auto-push via hooks
2. When the user opens the repo in Claude Code, the session pulls (via `session-sync.sh`), sees new raw files, and can Ingest them into `wiki/` per the rules in `CLAUDE.md`
3. To add another source, re-run this skill — it detects state and jumps to Phase 5
