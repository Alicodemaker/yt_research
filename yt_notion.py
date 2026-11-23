"""File YouTube transcripts into the Notion "🎬 YT videos" database, straight from the clipboard.

Start it, copy videos with the "Copy YouTube Transcript" Chrome extension (it copies
"Title: ...", "URL: ...", a blank line, then the transcript), and each one is filed as a
database page with Status "New". Press Q (or close the window) to stop.

    python "%USERPROFILE%\\Desktop\\yt_notion.py"

Needs the NOTION_TOKEN environment variable (your Notion integration's secret), and the
database must be shared with that integration (database ⋯ → Connections). Windows only.
Uses only the Python standard library.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

DATABASE_ID = "4210409facda81eb8947d0eec51e254d"   # 🎬 YT videos, on the Build with AI page
NOTION = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
CHUNK = 2000       # Notion's limit for one piece of text
PER_BLOCK = 100    # pieces per code block


class NotionError(Exception):
    pass


# ---------- pure logic (tested offline) ----------

def video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([\w-]{11})", url)
    return m.group(1) if m else None


def parse(text):
    """(title, canonical url, transcript) from the extension's text, or None if it isn't one."""
    title = re.search(r"^\s*Title:[ \t]*(.+?)\s*$", text, re.M)
    url = re.search(r"^\s*URL:[ \t]*(\S+)", text, re.M)
    vid = video_id(url.group(1)) if url else None
    if not (title and vid):
        return None
    transcript = text[url.end():].strip()
    if not transcript:
        return None
    return re.sub(r"\s+", " ", title.group(1)), f"https://www.youtube.com/watch?v={vid}", transcript


def code_blocks(transcript):
    """The transcript as Notion code blocks, split to fit Notion's size limits."""
    pieces = [transcript[i:i + CHUNK] for i in range(0, len(transcript), CHUNK)]
    blocks = []
    for i in range(0, len(pieces), PER_BLOCK):
        rich = [{"type": "text", "text": {"content": p}} for p in pieces[i:i + PER_BLOCK]]
        blocks.append({"object": "block", "type": "code",
                       "code": {"language": "plain text", "rich_text": rich}})
    return blocks


def file_video(text, api):
    """File one copied video. Returns a message line, or None if the text isn't a transcript."""
    parsed = parse(text)
    if not parsed:
        return None
    title, url, transcript = parsed
    words = f"{len(transcript.split()):,} words"
    found = api("POST", f"/databases/{DATABASE_ID}/query",
                {"filter": {"property": "Link", "url": {"equals": url}}})["results"]
    if found:
        page = found[0]
        status = (page["properties"]["Status"]["select"] or {}).get("name")
        if status != "No transcript":
            return f"- Skipped, already in the database: {title}"
        api("PATCH", f"/blocks/{page['id']}/children", {"children": code_blocks(transcript)})
        api("PATCH", f"/pages/{page['id']}", {"properties": {"Status": {"select": {"name": "New"}}}})
        return f"✓ Transcript added: {title} ({words})"
    api("POST", "/pages", {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title[:CHUNK]}}]},
            "Link": {"url": url},
            "Status": {"select": {"name": "New"}},
        },
        "children": code_blocks(transcript),
    })
    return f"✓ Added: {title} ({words})"


# ---------- Notion API and Windows clipboard (run on the PC) ----------

def api(method, path, body=None):
    request = urllib.request.Request(
        NOTION + path, method=method, data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
                 "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise NotionError("Notion rejected NOTION_TOKEN. Copy the integration secret again.")
        if e.code == 404:
            raise NotionError("Database not found. On 🎬 YT videos: ⋯ → Connections → add your integration.")
        raise NotionError(f"Notion error {e.code}: {e.read().decode(errors='replace')[:300]}")


def clipboard():
    """Functions to read the clipboard text and its change counter (Windows only)."""
    import ctypes
    from ctypes import wintypes
    user32, kernel32 = ctypes.WinDLL("user32"), ctypes.WinDLL("kernel32")
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.GetClipboardData.argtypes = [wintypes.UINT]
    user32.GetClipboardData.restype = wintypes.HANDLE
    user32.GetClipboardSequenceNumber.restype = wintypes.DWORD
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = wintypes.LPVOID
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

    def read():
        for _ in range(5):   # another app may hold the clipboard for a moment
            if user32.OpenClipboard(None):
                break
            time.sleep(0.1)
        else:
            return None
        try:
            handle = user32.GetClipboardData(13)   # CF_UNICODETEXT
            pointer = kernel32.GlobalLock(handle) if handle else None
            if not pointer:
                return None
            try:
                return ctypes.wstring_at(pointer)
            finally:
                kernel32.GlobalUnlock(handle)
        finally:
            user32.CloseClipboard()

    return read, user32.GetClipboardSequenceNumber


def main():
    try:
        import msvcrt
    except ImportError:
        sys.exit("This script runs on Windows only.")
    if not os.environ.get("NOTION_TOKEN"):
        sys.exit("NOTION_TOKEN is not set. Run: setx NOTION_TOKEN \"your-secret\" and open a new Command Prompt.")
    read, sequence = clipboard()
    last = sequence()   # ignore whatever was copied before starting
    filed = 0
    print("Watching the clipboard. Copy videos with the extension. Press Q to stop.\n", flush=True)
    while True:
        if msvcrt.kbhit() and msvcrt.getwch().lower() == "q":
            break
        if sequence() != last:
            last = sequence()
            text = read()
            try:
                message = file_video(text, api) if text else None
            except NotionError as e:
                print(f"✗ {e}", flush=True)
                if "NOTION_TOKEN" in str(e) or "not found" in str(e):
                    break
                continue
            except OSError as e:   # network trouble: keep watching
                print(f"✗ Could not reach Notion ({e}). Copy that video again in a moment.", flush=True)
                continue
            if message:
                print(message, flush=True)
                filed += message.startswith("✓")
        time.sleep(0.3)
    print(f"\nFiled {filed} video{'s' if filed != 1 else ''}. Bye.")


if __name__ == "__main__":
    main()
