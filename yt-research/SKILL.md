---
name: yt-research
description: Look up YouTube channels and videos and get structured data as JSON - a channel's latest or most popular videos (title, URL, date, views, duration), or one video's metadata, description, chapters and plain-text transcript. Use whenever the user mentions a YouTube channel, @handle or video link and wants to research, list, compare, rank, summarise, quote or analyse YouTube content, e.g. "what are @veritasium's most popular videos", "summarise this video", "what did they say about X in this talk".
---

# yt-research

Two scripts in `scripts/` print JSON to stdout. Exit code 0 means success, 1 means a JSON `error`.
Run them from this skill's folder. Prefer `uv run` (installs dependencies by itself):

```bash
uv run scripts/channel_videos.py <channel> [--latest N] [--popular N] [--include shorts,live] [--exact-dates]
uv run scripts/video_info.py <video> [--no-transcript] [--lang da,en] [--ai-transcript]
```

If `uv` is missing: `pip install -U yt-dlp youtube-transcript-api` once, then use `python3 scripts/...`.
(Use `python` instead of `python3` on Windows.)

## Which script

| The user wants | Run |
|---|---|
| A channel's recent uploads | `channel_videos.py @handle --latest 10` |
| A channel's biggest hits | `channel_videos.py @handle --popular 10` |
| Both at once (one scan) | `channel_videos.py @handle --latest 10 --popular 10` |
| Shorts or past live streams too | add `--include shorts,live` (excluded by default) |
| What one video is about, quotes, a summary | `video_info.py <url>` |
| Only facts about a video (date, views, chapters) | `video_info.py <url> --no-transcript` (faster, uses no transcript credits) |
| A transcript in another language | `video_info.py <url> --lang da,en` (tried in order, then the original language) |

Inputs can be anything the user pastes: `@handle`, a bare handle, a channel URL (`/@x`, `/channel/UC...`, `/user/x`, `/c/x`), a `UC...` ID, any video URL (`watch`, `youtu.be`, `shorts`, `live`, `embed`) or an 11-character video ID. No flags on `channel_videos.py` means `--latest 50`.

## Typical workflows

- **"Summarise @x's top 3 videos"**: `channel_videos.py @x --popular 3`, then `video_info.py <url>` for each, then summarise each transcript.
- **"What has @x been posting about lately?"**: `channel_videos.py @x --latest 20` and read the titles. Fetch transcripts only for the videos that matter.
- **"Find where they talk about X"**: `video_info.py <url>`, search the transcript, and use `chapters` to say roughly where in the video it is.

## Output

`channel_videos.py`:
- `channel` (`id`, `title`, `handle`, `url`), plus `latest` and/or `popular` lists.
- Each video has `id`, `title`, `url`, `upload_date` (YYYY-MM-DD), `date_approximate`, `views` (null if hidden), `duration_seconds`, `duration` ("10:05") and `type` (`video`, `short` or `live`).
- `popular_scanned` is how many videos were compared. `popular_complete: false` means the channel was too big to scan fully.

`video_info.py`:
- Metadata: `title`, `channel`, `channel_id`, `channel_url`, `upload_date`, `duration`, `views`, `description`, and `chapters` (list of `start`, `start_seconds`, `title`; empty if the video has none).
- Transcript: `transcript` (one plain-text string with no timestamps), plus `transcript_language`, `transcript_auto_generated` (null when unknown) and `transcript_source`.
- If the transcript can't be fetched, `transcript` is null and `transcript_error` explains why. The metadata is still valid, so use it.

`source` says which backend answered: `cloud` (YouTube Data API) or `local` (yt-dlp). In `channel_videos.py` the local backend's dates (`date_approximate: true`) can be off by days for recent videos and by months for old ones, and its views are rounded (7.4M → 7400000). Say "about" when quoting them, or pass `--exact-dates` (slower) for exact dates. `video_info.py` always returns exact numbers.

## Errors

Failures look like `{"error": {"code", "message", "hint"}}`. Follow the hint. Never retry in a loop.

| Code | What to do |
|---|---|
| `BAD_INPUT` | Fix the argument (for example, a video URL was passed to `channel_videos.py`). |
| `NOT_FOUND` / `PRIVATE_OR_UNAVAILABLE` | Tell the user. Retrying won't help. |
| `NO_CAPTIONS` | Work from the title, description and chapters, and say there was no transcript. Don't retry: even a "no captions" answer costs 1 Supadata credit. Only offer `--ai-transcript` if the user wants it: it uses 2 Supadata credits per minute of video. |
| `RATE_LIMITED` | Wait, then ask for fewer videos. |
| `IP_BLOCKED` | YouTube blocks this machine (common in cloud sessions). The user needs `YT_API_KEY` / `SUPADATA_API_KEY`, or `YT_PROXY`. |
| `QUOTA_EXCEEDED` | A free tier is used up (YouTube resets daily, Supadata monthly). Tell the user. |
| `BAD_API_KEY`, `NETWORK_ERROR`, `MISSING_DEPENDENCY` | A setup problem. Tell the user the hint. |

## Keys and limits (set by the user, never ask them to paste keys into chat)

- `YT_API_KEY`: YouTube Data API. Free 10,000 units/day. A channel list costs about 1 unit per 50 videos. The scripts never use the 100-unit search.
- `SUPADATA_API_KEY`: transcripts. Free 100/month. Each `video_info.py` call with a transcript costs 1 credit, and sometimes 2 when the first language isn't available. Use `--no-transcript` when the words aren't needed.
- `YT_PROXY`: an optional proxy URL for the local backend.
- With no keys, everything runs locally via yt-dlp and youtube-transcript-api. This works on a home connection, but is usually blocked from cloud servers.

## Good manners with output

Transcripts can be very long. Don't paste a full transcript into the chat unless asked: quote the relevant parts or summarise. When listing videos for the user, show title, date, views and link, not raw JSON.
