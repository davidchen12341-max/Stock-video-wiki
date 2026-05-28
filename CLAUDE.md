# Stock YouTuber Wiki

A persistent, LLM-maintained knowledge base tracking favorite stock/investing YouTube channels and their videos.

Pattern source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## Architecture

```
raw/          ← immutable source drops (JSON/text from the YouTube farmer)
wiki/
  channels/
    <channel-slug>/
      index.md    ← channel overview page
      videos/     ← one page per video from this channel
  index.md    ← catalog of every page with one-line summaries
  log.md      ← append-only ingest timeline
```

`raw/` is never modified after creation. The farmer appends new files; this schema governs what you do with them. `wiki/` is entirely LLM-owned — you create, update, and maintain all pages here.

**Auto-ingest rule:** Any new files in `raw/` that have not yet been ingested must be processed before the session ends.

---

## Page types

### Channel pages — `wiki/channels/<channel-slug>/<Display Name>.md`

Frontmatter:
```yaml
---
type: channel
name: <Full Channel Name>
handle: <@handle>
url: https://www.youtube.com/@handle
tags: [channel]
last_updated: <YYYY-MM-DD>
---
```

Body contains:
- Content style: what they cover, their typical format, their bias/approach
- Tickers they frequently mention (keep a running list, update on each ingest)
- Notable videos list: top videos worth revisiting, with `[[wikilinks]]` to their summary pages
- Last video date

### Video summaries — `wiki/channels/<channel-slug>/videos/<YYYY-MM-DD>-<short-title>.md`

Frontmatter:
```yaml
---
type: video
channel: <channel-slug>
title: <Full Video Title>
url: https://www.youtube.com/watch?v=<video_id>
published: <YYYY-MM-DD>
tickers: [NVDA, TSLA]   ← uppercase, all tickers mentioned
tags: [<channel-slug>, <ticker1>, <ticker2>]
---
```

Body contains:
- **Thesis:** one sentence — the main argument or call
- **Key takeaways:** 3-5 bullets
- **Tickers mentioned:** inline list for quick scanning
- **Notable calls:** any specific price targets, predictions, or strong opinions

---

## Operations

### Ingest

Triggered when new files appear in `raw/` (dropped by the YouTube farmer).

For each new raw file:
1. Read the file — it contains video metadata and transcript/description from the farmer
2. Create or update the video summary page in `wiki/channels/<channel-slug>/videos/`
3. Update the channel page at `wiki/channels/<channel-slug>/index.md` — add the video to notable list if it's high-quality, update last-seen date, update frequently-mentioned tickers
4. Update `wiki/index.md` — add the new video page entry
5. Append to `wiki/log.md`: `## [<date>] ingest | <channel> — <video title>`

When ingesting multiple videos at once, process them one at a time. Touch channel pages once per channel (batch updates), not once per video.

### Query

Answer questions by reading `wiki/index.md` first to find relevant pages, then drilling into them.

Example queries this wiki is built for:
- "What has everyone said about NVDA this week?"
- "Which channels covered earnings season?"
- "What's the bull case on TSLA across all creators?"

Good answers (comparisons, synthesis, stock roundups) should be filed back into `wiki/` as new pages so they compound over time.

---

## Conventions

- **File names:** lowercase, hyphens, no spaces. Channel slugs derived from channel name (e.g. `meet-kevin`, `the-plain-bagel`). Video files omit the channel slug since they're already inside the channel folder.
- **Dates:** ISO 8601 — `YYYY-MM-DD` everywhere.
- **Links:** use Obsidian wikilinks — `[[channels/zip-trader/index|ZipTrader]]` for channel pages, `[[channels/zip-trader/videos/2026-05-28-nvda-analysis|title]]` for videos.
- **Obsidian Bases:** the `type`, `channel`, `tickers`, and `published` frontmatter fields are queryable in Obsidian's Bases view. Use them to build filtered tables (e.g., all videos tagged `NVDA` sorted by date).
- **Tickers:** uppercase, no `$` prefix — `NVDA`, `TSLA`, `SPY`.
- **log.md entries start with:** `## [YYYY-MM-DD] ingest | <channel> — <title>` so they're grep-parseable.
