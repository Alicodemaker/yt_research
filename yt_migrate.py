"""One-time move: copy the videos in the "Build with AI" page's toggles into the 🎬 YT videos database.

    yt vids                          -> Status Filed (already in the guide)
    🆕 new yt vids                    -> Status New
    ⏳ new yt vids (no transcript)    -> New if a transcript was pasted in, otherwise No transcript

Double-click it (keep yt_notion.py next to it on the Desktop), or run:
    python "%USERPROFILE%\\Desktop\\yt_migrate.py"

It first lists what it found and asks before copying. Videos already in the database are
skipped, so running it again is safe. The old toggles are NOT deleted: check the database,
then delete them yourself in Notion. Needs NOTION_TOKEN, and the integration must be connected
to the Build with AI page as well as the database (⋯ → Connections).
"""
import os
import time

from yt_notion import DATABASE_ID, NotionError, api, code_blocks, video_id

PAGE_ID = "3e40409facda80eba1c8ed72632ddf8b"   # Build with AI
SECTIONS = {   # toggle text -> status (None: decided per video by whether it has a transcript)
    "yt vids": "Filed",
    "🆕 new yt vids": "New",
    "⏳ new yt vids (no transcript)": None,
}
OPENABLE = ("toggle", "heading_1", "heading_2", "heading_3", "column_list", "column", "callout")


def text_of(block):
    rich = block.get(block["type"], {}).get("rich_text", [])
    return "".join(r.get("plain_text", "") for r in rich).strip()


def children(block_id, call):
    """All child blocks, following Notion's pagination."""
    blocks, cursor = [], None
    while True:
        path = f"/blocks/{block_id}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
        reply = call("GET", path)
        blocks += reply["results"]
        if not reply.get("has_more"):
            return blocks
        cursor = reply["next_cursor"]


def find_sections(call, depth=3):
    """{section name: block id} for the three toggles, searching a few levels into the page."""
    found, level = {}, [PAGE_ID]
    for _ in range(depth):
        next_level = []
        for parent in level:
            for block in children(parent, call):
                name = text_of(block)
                if name in SECTIONS and block["has_children"]:
                    found[name] = block["id"]
                elif block["type"] in OPENABLE and block["has_children"]:
                    next_level.append(block["id"])
        if len(found) == len(SECTIONS) or not next_level:
            break
        level = next_level
    return found


def transcript_under(block_id, call):
    """Text of every code block under a video toggle (nested toggles included)."""
    parts = []
    for block in children(block_id, call):
        if block["type"] == "code":
            parts.append("".join(r.get("plain_text", "") for r in block["code"]["rich_text"]))
        elif block["type"] == "toggle" and block["has_children"]:
            parts.append(transcript_under(block["id"], call))
    return "\n".join(p for p in parts if p.strip()).strip()


def videos_in(section_id, call):
    """(title, canonical link, transcript) for each video toggle, and texts of toggles without a YouTube link."""
    videos, odd = [], []
    for block in children(section_id, call):
        if block["type"] != "toggle":
            continue
        rich = block["toggle"]["rich_text"]
        links = [r["href"] for r in rich if r.get("href") and video_id(r["href"])]
        if not links:
            odd.append(text_of(block))
            continue
        transcript = transcript_under(block["id"], call) if block["has_children"] else ""
        videos.append((text_of(block), f"https://www.youtube.com/watch?v={video_id(links[0])}", transcript))
    return videos, odd


def plan(call):
    """Everything to copy, as (title, link, transcript, status), plus toggles that were skipped."""
    sections = find_sections(call)
    missing = [name for name in SECTIONS if name not in sections]
    rows, odd = [], []
    for name, section_id in sections.items():
        videos, skipped = videos_in(section_id, call)
        odd += skipped
        for title, link, transcript in videos:
            status = SECTIONS[name] or ("New" if transcript else "No transcript")
            rows.append((title, link, transcript, status))
    return rows, odd, missing


def copy(row, call):
    """Create one database page. Returns False if the video is already there."""
    title, link, transcript, status = row
    if call("POST", f"/databases/{DATABASE_ID}/query",
            {"filter": {"property": "Link", "url": {"equals": link}}})["results"]:
        return False
    page = {"parent": {"database_id": DATABASE_ID},
            "properties": {"Name": {"title": [{"text": {"content": title[:2000]}}]},
                           "Link": {"url": link}, "Status": {"select": {"name": status}}}}
    if transcript:
        page["children"] = code_blocks(transcript)
    call("POST", "/pages", page)
    return True


def polite(method, path, body=None):
    """api() at Notion's pace (about 3 requests a second), retrying when it says slow down."""
    for attempt in range(5):
        time.sleep(0.35)
        try:
            return api(method, path, body)
        except NotionError as e:
            if "429" not in str(e) or attempt == 4:
                raise
            time.sleep(5)


def main():
    if not os.environ.get("NOTION_TOKEN"):
        print('NOTION_TOKEN is not set. Run: setx NOTION_TOKEN "your-secret" and open a new Command Prompt.')
        return
    print("Reading the Build with AI page (this takes a minute or two)...", flush=True)
    rows, odd, missing = plan(polite)
    counts = {}
    for row in rows:
        counts[row[3]] = counts.get(row[3], 0) + 1
    print(f"\nFound {len(rows)} videos: " + ", ".join(f"{n} {s}" for s, n in counts.items()))
    if missing:
        print("Toggles not found (left alone): " + ", ".join(missing))
    if odd:
        print(f"Skipped {len(odd)} toggles without a YouTube link, e.g.: " + "; ".join(odd[:3]))
    if not rows or input("\nCopy them into 🎬 YT videos? Type y and press Enter: ").strip().lower() != "y":
        print("Nothing copied.")
        return
    added = 0
    for n, row in enumerate(rows, 1):
        try:
            was_added = copy(row, polite)
        except NotionError as e:
            print(f"✗ [{n}/{len(rows)}] {row[0]}: {e}", flush=True)
            continue
        added += was_added
        print(f"{'✓' if was_added else '-'} [{n}/{len(rows)}] {row[0]}" + ("" if was_added else " (already there)"),
              flush=True)
    print(f"\nCopied {added} videos. The old toggles are untouched: check the database, then delete them in Notion.")


if __name__ == "__main__":
    try:
        main()
    except NotionError as e:
        print(f"\n✗ {e}\nIf it says not found: connect the integration to the Build with AI page too (⋯ → Connections).")
    except KeyboardInterrupt:
        print("\nStopped. Run it again to continue: videos already copied are skipped.")
    except Exception as e:   # show it, so a double-clicked window doesn't just vanish
        print(f"\nUnexpected error: {e!r}")
    input("\nPress Enter to close this window.")
