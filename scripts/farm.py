#!/usr/bin/env python3
"""
Fetches new videos from 5 stock investing YouTube channels
and writes raw markdown files to raw/youtube/
"""

import subprocess
import xml.etree.ElementTree as ET
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

CHANNELS = [
    {"name": "ZipTrader",          "handle": "@ZipTrader",          "id": "UC0BGhWsIbV7Dm-lsvhdlMbA", "slug": "zip-trader"},
    {"name": "Nolan Gouveia",      "handle": "@NolanGouveia",       "id": "UCr4XXQznhlgfzo4mwOgkF8w", "slug": "nolan-gouveia"},
    {"name": "Wallstreet Trapper", "handle": "@WallstreetTrapper",  "id": "UC0m2Iw1Ze_L1HIA7shg6vBA", "slug": "wallstreet-trapper"},
    {"name": "Tyler Hill Stocks",  "handle": "@TylerHillStocks",    "id": "UC-FwZq0rYfc2SzYkpoNBJGg", "slug": "tyler-hill-stocks"},
    {"name": "Felix Friends",      "handle": "@FelixFriends",       "id": "UCJtfma0mE_XrBAD9uakcjfA", "slug": "felix-friends"},
]

NS = {
    "atom":  "http://www.w3.org/2005/Atom",
    "yt":    "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}

RAW_DIR = Path("raw/youtube")


def get_floor_date():
    files = sorted(RAW_DIR.glob("*.md"), reverse=True)
    for f in files:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", f.name)
        if m:
            return m.group(1)
    return (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")


def slugify(text, max_len=50):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:max_len].rstrip("-")


def fetch_rss(channel_id):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    r = subprocess.run(["curl", "-sL", "--max-time", "15", url],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return []
    try:
        root = ET.fromstring(r.stdout)
    except ET.ParseError:
        return []

    entries = []
    for e in root.findall("atom:entry", NS):
        title_el     = e.find("atom:title", NS)
        video_id_el  = e.find("yt:videoId", NS)
        published_el = e.find("atom:published", NS)
        link_el      = e.find("atom:link", NS)
        desc_el      = e.find(".//media:description", NS)
        if not all([title_el, video_id_el, published_el, link_el]):
            continue
        entries.append({
            "title":       title_el.text,
            "video_id":    video_id_el.text,
            "published":   published_el.text[:10],
            "url":         link_el.get("href"),
            "description": (desc_el.text or "") if desc_el is not None else "",
        })
    return entries


def is_short(entry):
    t = entry["title"].lower()
    d = entry["description"].lower()
    return "#shorts" in t or d.startswith("#shorts")


def fetch_transcript(video_id):
    tmp_base = f"/tmp/{video_id}"
    srv3     = f"{tmp_base}.en.srv3"
    subprocess.run(
        ["python3", "-m", "yt_dlp",
         "--write-auto-subs", "--sub-lang", "en", "--skip-download",
         "--sub-format", "srv3",
         "--output", tmp_base,
         f"https://www.youtube.com/watch?v={video_id}"],
        capture_output=True, timeout=30,
    )
    if not os.path.exists(srv3):
        return None
    try:
        root  = ET.parse(srv3).getroot()
        lines = []
        for p in root.iter("p"):
            line = "".join(s.text or "" for s in p.iter("s")).strip()
            if line:
                lines.append(line)
        return " ".join(lines) or None
    except Exception:
        return None
    finally:
        for path in [srv3, f"{tmp_base}.en.vtt"]:
            if os.path.exists(path):
                os.remove(path)


def write_file(channel, entry, transcript):
    slug     = slugify(entry["title"])
    filename = f"{entry['published']}-{channel['slug']}-{slug}.md"
    path     = RAW_DIR / filename
    if path.exists():
        return None

    farmed_at      = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    has_transcript = transcript is not None

    content = (
        f"---\n"
        f"source: farmer/youtube\n"
        f"farmed: {farmed_at}\n"
        f"channel: {channel['name']}\n"
        f"channel_handle: {channel['handle']}\n"
        f"video_id: {entry['video_id']}\n"
        f"url: {entry['url']}\n"
        f"published: {entry['published']}\n"
        f"has_transcript: {'true' if has_transcript else 'false'}\n"
        f"---\n\n"
        f"# {entry['title']}\n\n"
        f"## Description\n\n"
        f"{entry['description']}\n"
    )
    if has_transcript:
        content += f"\n## Transcript\n\n{transcript}\n"

    path.write_text(content)
    return filename


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    floor = get_floor_date()
    print(f"Floor date: {floor}")

    new_files = []

    for channel in CHANNELS:
        print(f"\nFetching {channel['name']}...")
        entries = fetch_rss(channel["id"])
        if not entries:
            print("  fetch failed or empty feed")
            continue

        fresh = [e for e in entries if e["published"] >= floor and not is_short(e)]
        print(f"  {len(fresh)} new entries since {floor}")

        for entry in fresh:
            print(f"  → {entry['title']}")
            transcript = fetch_transcript(entry["video_id"])
            filename   = write_file(channel, entry, transcript)
            if filename:
                new_files.append((channel["name"], entry["title"], filename))
                print(f"    written: {filename}")
            else:
                print(f"    skipped (already exists)")

    print(f"\n{'='*40}")
    print(f"Total new files: {len(new_files)}")
    for ch, title, fname in new_files:
        print(f"  [{ch}] {title}")

    return len(new_files)


if __name__ == "__main__":
    sys.exit(0 if main() >= 0 else 1)
