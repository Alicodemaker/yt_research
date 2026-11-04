"""Shared helpers for the yt-research scripts.

Input parsing, the one JSON error shape, the HTTP edge for the cloud backend,
lazy imports for the local backend, and cloud -> local fallback.
Standard library only, so the cloud backend needs nothing installed.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
CHANNEL_ID = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
HANDLE = re.compile(r"^@?[A-Za-z0-9._-]{3,30}$")
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}

# Errors that describe the video or channel itself. Another backend would say
# the same thing, so they are final and never trigger a fallback.
FINAL_CODES = {"BAD_INPUT", "NOT_FOUND", "PRIVATE_OR_UNAVAILABLE", "NO_CAPTIONS"}

HINTS = {
    "BAD_INPUT": "Pass a YouTube URL, an 11-character video ID, an @handle or a UC... channel ID.",
    "NOT_FOUND": "Check the spelling of the handle or ID, or open the URL in a browser.",
    "PRIVATE_OR_UNAVAILABLE": "The video is private, removed, members-only or region-locked. Nothing to retry.",
    "NO_CAPTIONS": "This video has no captions. Metadata is still available; summarise from the description.",
    "RATE_LIMITED": "YouTube is throttling requests. Wait a few minutes, then retry with fewer videos.",
    "IP_BLOCKED": "YouTube blocks this machine's IP (common on cloud servers). Set SUPADATA_API_KEY / YT_API_KEY, or YT_PROXY to a residential proxy.",
    "QUOTA_EXCEEDED": "The free daily or monthly quota is used up. YouTube resets at midnight Pacific time; Supadata resets monthly.",
    "BAD_API_KEY": "The API key was rejected. Check YT_API_KEY / SUPADATA_API_KEY.",
    "MISSING_DEPENDENCY": "Run with `uv run <script>`, or install once: pip install -U yt-dlp youtube-transcript-api",
    "NETWORK_ERROR": "Could not reach the host. In a cloud session, allow it in the environment's network settings.",
    "UNEXPECTED": "Unexpected failure. If it persists, update yt-dlp: pip install -U yt-dlp",
}


class YTError(Exception):
    """A failure Claude can act on: a stable code, a message and a next step."""

    def __init__(self, code: str, message: str, hint: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint or HINTS.get(code, "")

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "hint": self.hint}


# ---------------------------------------------------------------- input parsing


def _split_url(text: str):
    """Return (host, path parts, query) for a YouTube URL, or None if not a URL."""
    if "/" not in text:
        return None
    url = text if "://" in text else "https://" + text
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if host not in YOUTUBE_HOSTS:
        raise YTError("BAD_INPUT", f"Not a YouTube URL: {text}")
    return host, [p for p in parts.path.split("/") if p], urllib.parse.parse_qs(parts.query)


def parse_video_id(text: str) -> str:
    """Accept a video URL in any common form, or a bare 11-character ID."""
    text = (text or "").strip()
    if VIDEO_ID.match(text):
        return text
    split = _split_url(text)
    candidate = None
    if split:
        host, path, query = split
        if host == "youtu.be" and path:
            candidate = path[0]
        elif path[:1] == ["watch"]:
            candidate = (query.get("v") or [None])[0]
        elif len(path) >= 2 and path[0] in ("shorts", "live", "embed", "v"):
            candidate = path[1]
    if candidate and VIDEO_ID.match(candidate):
        return candidate
    raise YTError("BAD_INPUT", f"Could not find a YouTube video ID in: {text!r}")


def parse_channel(text: str) -> tuple[str, str]:
    """Return (kind, value): ("id", "UC..."), ("handle", "@name"), ("user", name) or ("custom", name)."""
    text = (text or "").strip()
    if CHANNEL_ID.match(text):
        return "id", text
    split = _split_url(text)
    if split is None:
        if HANDLE.match(text):
            return "handle", "@" + text.lstrip("@")
        raise YTError("BAD_INPUT", f"Not a channel URL, @handle or channel ID: {text!r}")
    host, path, _ = split
    if host == "youtu.be" or path[:1] in (["watch"], ["shorts"], ["live"], ["embed"]):
        raise YTError("BAD_INPUT", "That is a video URL, not a channel.",
                      "Use video_info.py for a single video; its output includes the channel.")
    if path and path[0].startswith("@"):
        return "handle", path[0]
    if len(path) >= 2 and path[0] == "channel" and CHANNEL_ID.match(path[1]):
        return "id", path[1]
    if len(path) >= 2 and path[0] == "user":
        return "user", path[1]
    if len(path) >= 2 and path[0] == "c":
        return "custom", path[1]
    raise YTError("BAD_INPUT", f"Could not find a channel in: {text!r}")


def channel_url(kind: str, value: str) -> str:
    prefix = {"id": "channel/", "handle": "", "user": "user/", "custom": "c/"}[kind]
    return f"https://www.youtube.com/{prefix}{value}"


def video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


# ---------------------------------------------------------------- output


def run(main) -> None:
    """Run a script's main(argv) -> dict: JSON on stdout, exit 1 on any failure, never a traceback."""
    try:
        result = main(sys.argv[1:])
    except YTError as err:
        print(json.dumps({"error": err.to_dict()}, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as err:  # noqa: BLE001 - the contract is "never a traceback"
        error = YTError("UNEXPECTED", f"{type(err).__name__}: {err}")
        print(json.dumps({"error": error.to_dict()}, ensure_ascii=False, indent=2))
        sys.exit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- environment


def env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def require(module: str):
    """Import a local-backend library, or fail with MISSING_DEPENDENCY."""
    try:
        return importlib.import_module(module)
    except ImportError:
        raise YTError("MISSING_DEPENDENCY", f"The Python package for '{module}' is not installed.") from None


# ---------------------------------------------------------------- HTTP edge (cloud backend)


def fetch_json(url: str, params: dict | None = None, headers: dict | None = None, timeout: int = 30):
    """GET a JSON API. Returns (status, body). Raises NETWORK_ERROR if the host can't be reached."""
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"Accept": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as err:
        try:
            body = json.loads(err.read() or b"{}")
        except ValueError:
            body = {}
        return err.code, body
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        host = urllib.parse.urlsplit(url).netloc
        reason = getattr(err, "reason", err)
        raise YTError("NETWORK_ERROR", f"Could not reach {host}: {reason}",
                      f"Allow {host} in the environment's network settings, or check the connection.") from None


# ---------------------------------------------------------------- backend fallback


def first_success(attempts):
    """Try (source, fn) pairs in order and return (source, result) from the first that works.

    A final error (about the video or channel itself) stops at once. Otherwise every
    attempt is tried; if all fail, the first error is raised with every attempt listed.
    """
    errors = []
    for source, fn in attempts:
        try:
            return source, fn()
        except YTError as err:
            errors.append((source, err))
            if err.code in FINAL_CODES:
                break
    final = next((e for _, e in errors if e.code in FINAL_CODES), errors[0][1])
    if len(errors) > 1:
        tried = "; ".join(f"{source}: {e.code} ({e.message})" for source, e in errors)
        final = YTError(final.code, f"{final.message} [tried {tried}]", final.hint)
    raise final


def proxy_url() -> str | None:
    """Optional proxy for the local backend (yt-dlp, youtube-transcript-api)."""
    return env("YT_PROXY")
