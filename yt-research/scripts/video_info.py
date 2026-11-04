#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp>=2025.10.22", "youtube-transcript-api>=1.2.0"]
# ///
"""Get one YouTube video's metadata, chapters and plain-text transcript as JSON.

    video_info.py <video URL | ID> [--no-transcript] [--lang da,en] [--ai-transcript]

Metadata: YouTube Data API when YT_API_KEY is set, yt-dlp as the fallback.
Transcript: Supadata when SUPADATA_API_KEY is set, youtube-transcript-api as the fallback.
A missing transcript never fails the command: metadata is still returned.
"""
from __future__ import annotations

import re
import time

import _common as c

SUPADATA = "https://api.supadata.ai/v1/transcript"
POLL_SECONDS = 1     # Supadata recommends polling every second
POLL_ATTEMPTS = 300  # AI transcripts of long videos can take minutes

# youtube-transcript-api exception class names -> our codes (by name, so library versions don't matter).
TRANSCRIPT_ERRORS = {
    "TranscriptsDisabled": "NO_CAPTIONS",
    "NoTranscriptFound": "NO_CAPTIONS",
    "NoTranscriptAvailable": "NO_CAPTIONS",
    "VideoUnavailable": "PRIVATE_OR_UNAVAILABLE",
    "VideoUnplayable": "PRIVATE_OR_UNAVAILABLE",
    "AgeRestricted": "PRIVATE_OR_UNAVAILABLE",
    "InvalidVideoId": "BAD_INPUT",
    "RequestBlocked": "IP_BLOCKED",
    "IpBlocked": "IP_BLOCKED",
    "PoTokenRequired": "IP_BLOCKED",
    "TooManyRequests": "RATE_LIMITED",
    "ProxyError": "NETWORK_ERROR",
    "ConnectionError": "NETWORK_ERROR",
    "Timeout": "NETWORK_ERROR",
}

# "0:00 Intro", "1:30 - Arches", "[1:02:00] Outro"
CHAPTER_LINE = re.compile(r"^\s*[\[(]?((?:\d{1,2}:)?\d{1,2}:\d{2})[\])]?\s*[-–—:|.]?\s+(\S.*?)\s*$")


def parse_args(argv):
    parser = c.ArgParser(prog="video_info.py",
                         description="Get a video's metadata, chapters and plain-text transcript as JSON.")
    parser.add_argument("video", help="video URL or 11-character ID")
    parser.add_argument("--no-transcript", action="store_true", help="metadata only (faster, uses no credits)")
    parser.add_argument("--lang", default="en", metavar="da,en",
                        help="preferred transcript languages in order (default: en); then the original language")
    parser.add_argument("--ai-transcript", action="store_true",
                        help="let Supadata AI-generate a transcript when there are no captions (costs credits)")
    args = parser.parse_args(argv)
    args.langs = [lang.strip().lower() for lang in args.lang.split(",") if lang.strip()] or ["en"]
    return args


def main(argv):
    args = parse_args(argv)
    video_id = c.parse_video_id(args.video)

    attempts = []
    if c.env("YT_API_KEY"):
        attempts.append(("cloud", lambda: cloud_metadata(video_id)))
    attempts.append(("local", lambda: local_metadata(video_id)))
    source, out = c.first_success(attempts)
    out = {"source": source, **out}

    if not args.no_transcript:
        attempts = []
        if c.env("SUPADATA_API_KEY"):
            attempts.append(("supadata", lambda: supadata_transcript(video_id, args.langs, args.ai_transcript)))
        attempts.append(("youtube-transcript-api", lambda: local_transcript(video_id, args.langs)))
        try:
            transcript_source, transcript = c.first_success(attempts)
        except c.YTError as err:
            out.update(transcript=None, transcript_error=err.to_dict())
        else:
            out.update(transcript=transcript["text"], transcript_language=transcript["language"],
                       transcript_auto_generated=transcript["auto_generated"], transcript_source=transcript_source)
    return out


def metadata(video_id, title, channel, channel_id, channel_url, date, seconds, views, description, chapters):
    return {"id": video_id, "url": c.video_url(video_id), "title": title, "channel": channel,
            "channel_id": channel_id, "channel_url": channel_url, "upload_date": date,
            "duration_seconds": int(seconds) if seconds else None, "duration": c.format_duration(seconds),
            "views": views, "description": description, "chapters": chapters}


def chapter(seconds, title):
    return {"start": c.format_duration(seconds), "start_seconds": int(seconds), "title": title}


def chapters_from_description(description):
    """YouTube's own rule: chapters exist when the first timestamp is 0:00, there are 3+, and they ascend."""
    found = []
    for line in (description or "").splitlines():
        match = CHAPTER_LINE.match(line)
        if match:
            parts = [int(p) for p in match.group(1).split(":")]
            seconds = sum(p * 60 ** i for i, p in enumerate(reversed(parts)))
            found.append(chapter(seconds, match.group(2)))
    starts = [ch["start_seconds"] for ch in found]
    if len(found) < 3 or starts[0] != 0 or starts != sorted(set(starts)):
        return []
    return found


# ---------------------------------------------------------------- metadata

def cloud_metadata(video_id):
    body = c.youtube_api("videos", part="snippet,contentDetails,statistics", id=video_id)
    if not body.get("items"):
        raise c.YTError("PRIVATE_OR_UNAVAILABLE", f"Video {video_id} was not found: it is private, removed or never existed.")
    item = body["items"][0]
    snippet, stats = item["snippet"], item.get("statistics", {})
    return metadata(video_id, snippet["title"], snippet.get("channelTitle"), snippet.get("channelId"),
                    c.channel_url("id", snippet["channelId"]) if snippet.get("channelId") else None,
                    snippet["publishedAt"][:10], c.parse_iso_duration(item["contentDetails"].get("duration")),
                    int(stats["viewCount"]) if "viewCount" in stats else None, snippet.get("description", ""),
                    chapters_from_description(snippet.get("description")))


def local_metadata(video_id):
    yt_dlp = c.require("yt_dlp")
    try:
        with yt_dlp.YoutubeDL(c.ytdlp_options()) as ydl:
            info = ydl.extract_info(c.video_url(video_id), download=False)
    except Exception as err:  # DownloadError, or a plain network error
        raise c.ytdlp_error(err) from None
    chapters = [chapter(ch.get("start_time") or 0, ch.get("title")) for ch in info.get("chapters") or []]
    return metadata(video_id, info.get("title"), info.get("channel") or info.get("uploader"), info.get("channel_id"),
                    info.get("channel_url"), c.ymd(info.get("upload_date")), info.get("duration"),
                    info.get("view_count"), info.get("description") or "",
                    chapters or chapters_from_description(info.get("description")))


# ---------------------------------------------------------------- transcripts

def lang_matches(code, wanted):
    code, wanted = (code or "").lower(), wanted.lower()
    return code == wanted or code.startswith(wanted + "-")


def supadata_transcript(video_id, langs, allow_ai):
    """Ask for the first preferred language; Supadata falls back to what exists, so ask once more if needed."""
    answer = supadata_get(video_id, langs[0], allow_ai)
    for wanted in langs[1:]:
        if lang_matches(answer.get("lang"), langs[0]) or lang_matches(answer.get("lang"), wanted):
            break
        available = next((a for a in answer.get("availableLangs") or [] if lang_matches(a, wanted)), None)
        if available:
            answer = supadata_get(video_id, available, allow_ai)
            break
    content = answer.get("content")
    if isinstance(content, list):  # timestamped segments, if text=true was ignored
        content = " ".join(segment.get("text", "") for segment in content)
    return {"text": " ".join((content or "").split()), "language": answer.get("lang"), "auto_generated": None}


def supadata_get(video_id, lang, allow_ai):
    headers = {"x-api-key": c.env("SUPADATA_API_KEY")}
    params = {"url": c.video_url(video_id), "lang": lang, "text": "true", "mode": "auto" if allow_ai else "native"}
    status, body = c.fetch_json(SUPADATA, params, headers)
    if status == 202 and body.get("jobId"):
        return supadata_wait(body["jobId"], headers)
    if status == 200:
        return body
    raise supadata_error(status, body)


def supadata_wait(job_id, headers):
    for _ in range(POLL_ATTEMPTS):
        time.sleep(POLL_SECONDS)
        status, body = c.fetch_json(f"{SUPADATA}/{job_id}", headers=headers)
        if status != 200:
            raise supadata_error(status, body)
        if body.get("status") == "completed":
            return body
        if body.get("status") == "failed":
            raise supadata_error(200, body.get("error") or {"error": "transcript-unavailable"})
    raise c.YTError("UNEXPECTED", "Supadata did not finish the transcript in time.", "Try again in a minute.")


def supadata_error(status, body):
    """Map Supadata errors (docs.supadata.ai/errors) to our codes."""
    kind = str(body.get("error") or "")
    details = str(body.get("details") or "")
    message = f"Supadata: {details or body.get('message') or kind or f'HTTP {status}'}"
    if status == 206 or kind == "transcript-unavailable":
        return c.YTError("NO_CAPTIONS", message)
    if status in (403, 404) or kind in ("forbidden", "not-found"):
        return c.YTError("PRIVATE_OR_UNAVAILABLE", message)
    if status == 401 or kind == "unauthorized":
        return c.YTError("BAD_API_KEY", message, "SUPADATA_API_KEY was rejected. Copy it again from the Supadata dashboard.")
    if status == 429 or kind == "limit-exceeded":
        if "usage limit" in details.lower():
            return c.YTError("QUOTA_EXCEEDED", message, "This month's free Supadata credits are used up. They reset next billing cycle.")
        return c.YTError("RATE_LIMITED", message)
    if status == 402 or kind == "upgrade-required":
        return c.YTError("QUOTA_EXCEEDED", message, "This Supadata feature is not on the free plan.")
    return c.YTError("UNEXPECTED", f"{message} (HTTP {status})")


def local_transcript(video_id, langs):
    library = c.require("youtube_transcript_api")
    options = {}
    if c.proxy_url():
        proxies = c.require("youtube_transcript_api.proxies")
        options["proxy_config"] = proxies.GenericProxyConfig(http_url=c.proxy_url(), https_url=c.proxy_url())
    try:
        tracks = list(library.YouTubeTranscriptApi(**options).list(video_id))
        track = pick_track(tracks, langs)
        snippets = track.fetch().snippets
    except c.YTError:
        raise
    except Exception as err:
        raise transcript_error(err) from None
    text = " ".join(" ".join(s.text.split()) for s in snippets if s.text.strip())
    return {"text": text, "language": track.language_code, "auto_generated": bool(track.is_generated)}


def pick_track(tracks, langs):
    """Preferred languages in order, then the original spoken language. Auto-generated beats creator-made."""
    def best(candidates):
        return next((t for t in candidates if t.is_generated), None) or next(iter(candidates), None)

    for wanted in langs:
        track = best([t for t in tracks if lang_matches(t.language_code, wanted)])
        if track:
            return track
    track = best(tracks)  # the auto-generated track is in the language actually spoken
    if track is None:
        raise c.YTError("NO_CAPTIONS", "This video has no captions in any language.")
    return track


def transcript_error(err):
    names = [cls.__name__ for cls in type(err).__mro__]
    code = next((TRANSCRIPT_ERRORS[n] for n in names if n in TRANSCRIPT_ERRORS), "UNEXPECTED")
    text = str(err)
    if "most likely caused by:" in text:
        text = text.split("most likely caused by:", 1)[1].split("If you are sure", 1)[0]
    text = " ".join(text.split())
    if len(text) > 200:  # the library explains workarounds at length; keep the first sentence
        text = text[:text.find(". ", 20) + 1 or 200]
    return c.YTError(code, f"{type(err).__name__}: {text}")


if __name__ == "__main__":
    c.run(main)
