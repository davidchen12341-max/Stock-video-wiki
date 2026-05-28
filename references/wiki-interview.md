# Wiki Interview

Load on-demand — do NOT load at startup.

Karpathy left the wiki deliberately vague. The gist says: "share it with your LLM agent and work together to instantiate a version that fits your needs." This file is how you run that conversation.

Do not hand the user a fixed template. Interview them, then write their `CLAUDE.md` from the conversation.

## What you already have

The gist from Phase 1 is in your context. Re-read it before starting the interview — especially the "Architecture", "Operations", and "Indexing and logging" sections. You need them fresh to ask good follow-ups.

## The interview

Ask these questions one at a time. Do NOT dump them all at once. React to each answer before moving on.

### 1. Topic

> What do you want this wiki to know about? Give me a topic, a domain, or a use case. One or two sentences.

Examples to offer if they're stuck: "AI research papers", "my customers and deal pipeline", "a book I'm reading", "competitive analysis on OpenAI and Anthropic", "my own health and psychology", "a deep-dive on Roman history".

### 2. Scope

> Is this one focused topic, or a few related topics you'd want organized separately?

This determines whether `wiki/` is flat or has subdirectories. If they say "a few related topics", ask them to name 2-4 of them so you can seed subdirectories.

### 3. What goes in raw

> What kind of sources do you plan to feed this thing? Articles, PDFs, meeting transcripts, Slack messages, YouTube videos, tweets, your own notes?

The answer shapes the farmer conversation later. If they list things with obvious MCP connectors (Slack, Gmail, Fireflies), note them for Phase 5. If they list things without connectors (PDFs, pasted articles), note that raw/ will be partly hand-fed.

### 4. What kind of pages

> When you open the wiki, what do you want to see? Summaries of individual sources? Entity pages (one per person / company / concept)? Topic overviews that synthesize across sources? All of the above?

Karpathy's gist lists: summaries, entity pages, concept pages, comparisons, an overview, a synthesis. You don't need them all. Pick the 2-3 the user actually wants.

### 5. Operations they care about

> The wiki has three operations: **Ingest** (add a source, update the wiki), **Query** (ask it questions), **Lint** (health checks — contradictions, orphans, stale claims). Which of these do you care about? All three is fine, or you can start with just Ingest.

Write only the operations they picked into `CLAUDE.md`. Don't include lint prose if they're not going to use it.

### 6. Image handling (optional)

> Do your sources have images you care about, or is this text-only?

If text-only, skip image handling entirely. If images matter, mention the Obsidian clipper pattern from the gist.

### 7. Index and log

> Two navigation files: `index.md` (catalog of every page with a one-line summary) and `log.md` (append-only timeline of ingests and queries). Do you want both, just the index, or neither?

Default to both unless they opt out.

## Writing CLAUDE.md

After the interview, write `CLAUDE.md` at the repo root. Base the content on what they *actually said*, not on a template.

### Required sections

1. **Header** — title, one-line topic summary from Q1, link to the gist (`https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`) as the source of the pattern
2. **Architecture** — describe the raw/ + wiki/ layout *they* chose (flat or topic subdirs), state that raw/ is immutable and wiki/ is LLM-owned
3. **Operations** — one section per operation they picked in Q5. Write the rules in their language, not Karpathy's. Example: if their topic is "customer deals", the Ingest section should talk about deals, not "entities". Always include the auto-ingest rule: new files in `raw/` must be ingested before the session ends.
4. **Page types** — list the page types from Q4 with a sentence each on what they're for
5. **Conventions** — dates, file naming, link format, whatever's relevant to what they chose

### Anti-patterns

- **Do not** copy the Ingest/Query/Lint prose from `temp/karpathy-llm-wiki/SKILL.md`. That's one instantiation, not the canon.
- **Do not** include operations they said they don't want.
- **Do not** include image handling if they said text-only.
- **Do not** pad. Karpathy's gist is ~80 lines. Their `CLAUDE.md` should be shorter than that for a focused topic.
- **Do not** end with a "future work" section. That's bloat.

### After writing

Show the user the file. Ask: "Does this match what you had in mind? Anything to cut, add, or rewrite?" Revise before moving on. This is the schema the wiki will live under for months — worth 2 minutes to get right.
