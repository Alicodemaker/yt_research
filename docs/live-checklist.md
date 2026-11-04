# Live checklist

The offline tests (`pytest -q`) use fakes. Run these against the real services after changing a backend, or when YouTube or Supadata change something. Run them from `yt-research/`.

## Cloud backend (keys set: `YT_API_KEY`, `SUPADATA_API_KEY`)

- [x] `uv run scripts/channel_videos.py @veritasium --latest 3` gives `"source": "cloud"`, three newest videos, and `date_approximate: false`.
- [x] `uv run scripts/channel_videos.py @veritasium --popular 3 --include shorts,live` gives the top 3 by views and `popular_complete: true`.
- [x] `uv run scripts/video_info.py <a recent video URL>` gives `"source": "cloud"`, chapters, and a `transcript` with `"transcript_source": "supadata"`.
- [x] `uv run scripts/video_info.py <video URL> --lang da,en` gives Danish if the video has it, otherwise English, otherwise the original language.
- [x] A wrong key (`YT_API_KEY=x uv run scripts/video_info.py <url> --no-transcript`) gives `BAD_API_KEY`, or falls back to `"source": "local"` when YouTube is reachable.

## Local backend (no keys)

- [x] `uv run scripts/channel_videos.py @veritasium --latest 3` gives `"source": "local"` and `date_approximate: true`.
- [x] Adding `--exact-dates` gives `date_approximate: false`.
- [x] `uv run scripts/video_info.py <url>` gives metadata and chapters. It gives a transcript on a home connection, or `IP_BLOCKED` in a cloud session.

## Error cases

- [x] A private or removed video gives `PRIVATE_OR_UNAVAILABLE` with exit code 1.
- [ ] A video with no captions keeps its metadata, and `transcript_error.code` is `NO_CAPTIONS`. (Not yet tried live; covered by offline tests.)
- [x] `channel_videos.py <a video URL>` gives `BAD_INPUT`, with a hint to use `video_info.py`.

## Results

**2026-11-04, Claude Code cloud session, no keys yet:**
- Local backend: `channel_videos.py` latest, popular (546 videos scanned in about 10 s), `--include shorts` and `--exact-dates` all work.
- `video_info.py` metadata and chapters work. The transcript gives `IP_BLOCKED`, as expected: YouTube blocks cloud IPs.
- Upload playlists checked on real channels: `UULF` (videos), `UUSH` (shorts) and `UULV` (live, only when the channel has streamed).
- The real YouTube Data API with a wrong key gives `BAD_API_KEY`.

**2026-11-04, same session, real keys:**
- `channel_videos.py` latest gives `source: cloud`, exact dates and exact views.
- Popular with `--include shorts,live`: all 546 videos scanned in about 7 s (about 23 quota units). The Data API accepts the `UULF` and `UUSH` playlists, and a channel without streams has no `UULV` playlist, which is treated as empty.
- `video_info.py`: metadata, 10 chapters and a Supadata transcript (33,569 characters) in about 2.4 s, with `transcript_source: supadata`.
- `--lang da,en` on a video without Danish gives English for 1 credit.
- A video that doesn't exist gives `PRIVATE_OR_UNAVAILABLE`. A video URL passed to `channel_videos.py` gives `BAD_INPUT`.
- Local estimated dates compared with exact cloud dates: within 2 days for videos under a month old, but often the wrong month for older ones (up to ±30 days at 1-12 months, ±1 year beyond). Accepted: the cloud backend gives exact dates.
