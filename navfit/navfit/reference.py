"""Collect what is *actually accessible* about a reference YouTube video.

Tries, in order, and records the outcome of each step honestly:
  1. oEmbed           -> title, channel, thumbnail (usually works)
  2. transcript       -> youtube-transcript-api (often blocked on cloud IPs)
  3. watch page       -> description / length (often blocked by bot checks)

Writes references/<exercise>-<video_id>.md. If the transcript is not available,
the report says so and asks for a transcript/summary instead of guessing.
The reference is used to *understand* the exercise; nothing is copied into the
video (no footage, audio or verbatim text).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request

from .compose import ROOT

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}


def video_id(url):
    u = urllib.parse.urlparse(url)
    if u.hostname and "youtu.be" in u.hostname:
        return u.path.strip("/")
    q = urllib.parse.parse_qs(u.query)
    if "v" in q:
        return q["v"][0]
    m = re.search(r"/(shorts|embed)/([\w-]{6,})", u.path)
    return m.group(2) if m else None


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def ingest(url, exercise):
    vid = video_id(url)
    if not vid:
        raise SystemExit("Could not read a YouTube video id from the URL")
    res = {"url": url, "id": vid, "fetched": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", "steps": {}}

    try:
        o = json.loads(_get("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(url, safe="")))
        res["title"], res["channel"], res["thumbnail"] = o.get("title"), o.get("author_name"), o.get("thumbnail_url")
        res["steps"]["oembed"] = "ok"
    except Exception as e:  # noqa: BLE001
        res["steps"]["oembed"] = f"failed: {e}"

    transcript = None
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        fetched = api.fetch(vid, languages=["ar", "en"])
        transcript = " ".join(s.text for s in fetched)
        res["steps"]["transcript"] = f"ok ({len(transcript.split())} words)"
    except Exception as e:  # noqa: BLE001
        res["steps"]["transcript"] = f"unavailable: {type(e).__name__}: {str(e).splitlines()[0][:160]}"

    try:
        html = _get(f"https://www.youtube.com/watch?v={vid}")
        m = re.search(r'"shortDescription":"(.*?)","isCrawlable', html)
        if m:
            res["description"] = json.loads('"' + m.group(1) + '"')
            res["steps"]["watch_page"] = "ok"
        else:
            res["steps"]["watch_page"] = "loaded but no description found (likely a consent/bot page)"
    except Exception as e:  # noqa: BLE001
        res["steps"]["watch_page"] = f"failed: {e}"

    os.makedirs(os.path.join(ROOT, "references"), exist_ok=True)
    path = os.path.join(ROOT, "references", f"{exercise}-{vid}.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"# Reference for `{exercise}`\n\n- URL: {url}\n- Fetched: {res['fetched']}\n")
        fh.write(f"- Title: {res.get('title', 'unknown')}\n- Channel: {res.get('channel', 'unknown')}\n\n")
        fh.write("## What could be accessed\n\n| step | result |\n|---|---|\n")
        for k, v in res["steps"].items():
            fh.write(f"| {k} | {v} |\n")
        if res.get("description"):
            fh.write("\n## Description (for understanding only — do not copy)\n\n" + res["description"] + "\n")
        if transcript:
            fh.write("\n## Transcript (for understanding only — do not copy)\n\n" + transcript + "\n")
        else:
            fh.write("\n## ⚠️ Transcript not available\n\nThe video content itself was **not** analysed. "
                     "To use it as a technique reference, add one of these to this file:\n"
                     "- the transcript (YouTube → ⋯ → Show transcript → copy), or\n"
                     "- a short summary of the cues it teaches, or\n"
                     "- a video file you have the rights to use.\n")
        fh.write("\n## Notes for content.yaml\n\n- Cues confirmed by this reference: _(fill in)_\n"
                 "- Cues that differ from our defaults: _(fill in)_\n")
    print(f"[ref] {path}")
    for k, v in res["steps"].items():
        print(f"  {k}: {v}")
    if not transcript:
        print("  -> transcript not accessible: please paste the transcript or a summary into the file above.")
    return res
