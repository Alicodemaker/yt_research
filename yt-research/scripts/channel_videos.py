#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp>=2025.10.22"]
# ///
"""List a YouTube channel's latest and/or most popular videos as JSON.

    channel_videos.py <channel URL | @handle | UC... ID> [--latest N] [--popular N]
                      [--include shorts,live] [--exact-dates]

Uses the YouTube Data API when YT_API_KEY is set, with yt-dlp as the fallback.
"""
from __future__ import annotations

import _common as c

POPULAR_SCAN_LIMIT = 5000  # videos per upload type; a huge channel stays around 200 quota units
INCLUDE = {"shorts": "short", "live": "live"}
# Channel ID "UCxyz" has these upload playlists: regular videos, shorts and past live streams.
PLAYLIST_PREFIX = {"video": "UULF", "short": "UUSH", "live": "UULV"}
LOCAL_TABS = {"video": "/videos", "short": "/shorts", "live": "/streams"}


def parse_args(argv):
    parser = c.ArgParser(prog="channel_videos.py",
                         description="List a channel's latest and/or most popular videos as JSON.")
    parser.add_argument("channel", help="channel URL, @handle or UC... channel ID")
    parser.add_argument("--latest", type=int, metavar="N", help="N newest videos (default 50 if no other list asked)")
    parser.add_argument("--popular", type=int, metavar="N", help="N most viewed videos")
    parser.add_argument("--include", default="", metavar="shorts,live", help="also include shorts and/or live streams")
    parser.add_argument("--exact-dates", action="store_true",
                        help="local backend only: fetch each returned video for its exact date (slower)")
    args = parser.parse_args(argv)
    if args.latest is None and args.popular is None:
        args.latest = 50
    for name in ("latest", "popular"):
        if getattr(args, name) is not None and getattr(args, name) < 1:
            parser.error(f"--{name} must be 1 or more")
    extra = [x.strip() for x in args.include.split(",") if x.strip()]
    unknown = set(extra) - set(INCLUDE)
    if unknown:
        parser.error(f"--include accepts shorts and live, not: {', '.join(sorted(unknown))}")
    args.kinds = ["video"] + [INCLUDE[x] for x in extra]
    return args


def main(argv):
    args = parse_args(argv)
    kind, value = c.parse_channel(args.channel)
    attempts = []
    if c.env("YT_API_KEY"):
        attempts.append(("cloud", lambda: cloud(kind, value, args)))
    attempts.append(("local", lambda: local(kind, value, args)))
    source, result = c.first_success(attempts)
    return {"source": source, **result}


def make_video(video_id, title, date, approximate, views, seconds, kind, published):
    return {"id": video_id, "title": title, "url": c.video_url(video_id), "upload_date": date,
            "date_approximate": approximate, "views": views,
            "duration_seconds": int(seconds) if seconds else None, "duration": c.format_duration(seconds),
            "type": kind, "_published": published}


def select(channel, videos, args, complete):
    """Build the output lists. `_published` is a sort key only and is dropped here."""
    def public(video):
        return {k: v for k, v in video.items() if not k.startswith("_")}

    out = {"channel": channel}
    if args.latest:
        newest = sorted(videos, key=lambda v: v["_published"], reverse=True)
        out["latest"] = [public(v) for v in newest[:args.latest]]
    if args.popular:
        top = sorted(videos, key=lambda v: -1 if v["views"] is None else v["views"], reverse=True)
        out["popular"] = [public(v) for v in top[:args.popular]]
        out["popular_scanned"] = len(videos)
        out["popular_complete"] = complete
    return out


# ---------------------------------------------------------------- cloud: YouTube Data API

def cloud(kind, value, args):
    lookup = {"id": "id", "handle": "forHandle", "user": "forUsername", "custom": "forHandle"}[kind]
    body = c.youtube_api("channels", part="snippet", **{lookup: "@" + value if kind == "custom" else value})
    if not body.get("items"):
        raise c.YTError("NOT_FOUND", f"No YouTube channel found for {value}.")
    item = body["items"][0]
    channel_id = item["id"]
    channel = {"id": channel_id, "title": item["snippet"]["title"], "handle": item["snippet"].get("customUrl"),
               "url": c.channel_url("id", channel_id)}

    limit = POPULAR_SCAN_LIMIT if args.popular else args.latest
    videos, complete = [], True
    for kind_ in args.kinds:
        ids, more = playlist_ids(PLAYLIST_PREFIX[kind_] + channel_id[2:], limit)
        complete = complete and not more
        videos += [cloud_video(v, kind_) for v in video_details(ids)]
    return select(channel, videos, args, complete)


def playlist_ids(playlist_id, limit):
    """Return (up to `limit` video IDs newest first, whether more exist). A missing playlist is empty."""
    ids, token = [], None
    while len(ids) < limit:
        try:
            body = c.youtube_api("playlistItems", part="contentDetails", playlistId=playlist_id,
                                 maxResults=50, pageToken=token)
        except c.YTError as err:
            if err.code == "NOT_FOUND":  # e.g. a channel with no shorts has no shorts playlist
                return [], False
            raise
        ids += [item["contentDetails"]["videoId"] for item in body.get("items", [])]
        token = body.get("nextPageToken")
        if not token:
            break
    return ids[:limit], bool(token) or len(ids) > limit


def video_details(ids):
    items = []
    for start in range(0, len(ids), 50):
        body = c.youtube_api("videos", part="snippet,contentDetails,statistics", id=",".join(ids[start:start + 50]))
        items += body.get("items", [])
    return items


def cloud_video(item, kind):
    snippet, stats = item["snippet"], item.get("statistics", {})
    views = int(stats["viewCount"]) if "viewCount" in stats else None
    return make_video(item["id"], snippet["title"], snippet["publishedAt"][:10], False, views,
                      c.parse_iso_duration(item["contentDetails"].get("duration")), kind, snippet["publishedAt"])


# ---------------------------------------------------------------- local: yt-dlp

def local(kind, value, args):
    yt_dlp = c.require("yt_dlp")
    base = c.channel_url(kind, value)
    options = {"quiet": True, "no_warnings": True, "logger": c.QuietLogger(), "skip_download": True,
               "extract_flat": "in_playlist",
               "extractor_args": {"youtubetab": {"approximate_date": [""]}}}
    if c.proxy_url():
        options["proxy"] = c.proxy_url()
    if not args.popular:
        options["playlistend"] = args.latest

    channel, videos = None, []
    for kind_ in args.kinds:
        info = extract(yt_dlp, base + LOCAL_TABS[kind_], options, missing_ok=True)
        if info is None:
            continue
        channel = channel or local_channel(info)
        videos += [local_video(e, kind_) for e in info.get("entries") or [] if e and e.get("id")]
    if channel is None:
        raise c.YTError("NOT_FOUND", f"{base} has no videos, shorts or live tabs.")
    out = select(channel, videos, args, True)
    if args.exact_dates:
        exact_dates(yt_dlp, out, {k: v for k, v in options.items() if k not in ("extract_flat", "playlistend")})
    return out


def extract(yt_dlp, url, options, missing_ok=False):
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as err:  # yt-dlp raises DownloadError, and sometimes plain network errors
        if missing_ok and "does not have a" in str(err).lower():  # "...does not have a shorts tab"
            return None
        raise c.ytdlp_error(err) from None


def local_channel(info):
    handle = info.get("uploader_id")
    return {"id": info.get("channel_id") or info.get("id"),
            "title": info.get("channel") or info.get("uploader") or info.get("title"),
            "handle": handle if handle and handle.startswith("@") else None,
            "url": info.get("channel_url")}


def local_video(entry, kind):
    date = c.ymd(entry.get("upload_date")) or c.date_from_timestamp(entry.get("timestamp"))
    return make_video(entry["id"], entry.get("title"), date, True, entry.get("view_count"),
                      entry.get("duration"), kind, entry.get("timestamp") or 0)


def exact_dates(yt_dlp, out, options):
    """Replace approximate dates with exact ones, one request per returned video."""
    found = {}
    for video in out.get("latest", []) + out.get("popular", []):
        if video["id"] not in found:
            try:
                found[video["id"]] = c.ymd(extract(yt_dlp, video["url"], options).get("upload_date"))
            except c.YTError:
                found[video["id"]] = None  # keep the approximate date
        if found[video["id"]]:
            video["upload_date"], video["date_approximate"] = found[video["id"]], False


if __name__ == "__main__":
    c.run(main)
