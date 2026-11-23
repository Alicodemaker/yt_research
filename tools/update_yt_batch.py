"""Refresh the video list in yt_batch.py from the Notion "Build with AI" page.

Usage: python3 tools/update_yt_batch.py <saved Notion fetch>

The input is the Notion fetch result saved to a file (JSON with a "text" field, or the
page markdown itself). Only the videos in the "⏳ new yt vids (no transcript)" toggle are
used. Prints one line: the number of videos now in yt_batch.py.
"""
import json
import re
import sys
from pathlib import Path

TOGGLE = "⏳ new yt vids (no transcript)"
BATCH = Path(__file__).resolve().parent.parent / "yt_batch.py"
LINK = re.compile(r"\[(?:<b>)?(.*?)(?:</b>)?\]\(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})[^)]*\)")


def page_text(raw):
    try:
        return json.loads(raw)["text"]
    except (ValueError, KeyError, TypeError):
        return raw


def toggle_videos(text):
    """(video ID, title) for each video in the toggle, in page order, without duplicates."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.strip() == TOGGLE)
    videos, seen, depth = [], set(), 1
    for line in lines[start + 1:]:
        if line.strip().startswith("<toggle"):
            depth += 1
        elif line.strip() == "</toggle>":
            depth -= 1
            if depth == 0:
                break
        for title, vid in LINK.findall(line):
            if vid not in seen:
                seen.add(vid)
                videos.append((vid, re.sub(r"\\(.)", r"\1", title)))
    return videos


def with_videos(script, videos):
    body = "".join(f"    ({vid!r}, {title!r}),\n" for vid, title in videos)
    return re.sub(r"(?ms)^VIDEOS = \[\n.*?^\]\n", lambda _: f"VIDEOS = [\n{body}]\n", script, count=1)


if __name__ == "__main__":
    videos = toggle_videos(page_text(Path(sys.argv[1]).read_text(encoding="utf-8")))
    BATCH.write_text(with_videos(BATCH.read_text(encoding="utf-8"), videos), encoding="utf-8")
    print(f"{len(videos)} videos in yt_batch.py")
