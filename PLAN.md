# PLAN: yt-research Agent Skill

## What we're doing

We're building an Agent Skill, `yt-research/`, that lets Claude Code and Cowork look up YouTube channels and videos, mainly from a cloud session started on an Android phone. It has two Python scripts, `channel_videos.py` and `video_info.py`, which print JSON, and a `SKILL.md` that tells Claude when and how to use them. The **cloud backend** is the main one: the official YouTube Data API (free key) for lists and metadata, and Supadata (free key, 100 transcripts/month) for transcripts. The **local backend** is the fallback: yt-dlp and youtube-transcript-api, used when the keys aren't set or a cloud call fails. Budget: 0 kr/month at up to 50 videos a month.

## Steps

1. **Turn the repo into a skill repo.** Remove the Vite/PWA files (`package*.json`, `vite.config.js`, `index.html`, `src/`, `public/`, the Pages deploy workflow). Rewrite the rules in AGENTS.md for a Python skill, point CI at `pytest`, and keep `.claude/skills/`.
2. **Write the shared helper `scripts/_common.py`.**
   - Input parsing: channel URL, `@handle` or ID; video URL or ID.
   - One JSON error shape: `{"error": {"code", "message", "hint"}}` with exit code 1 and no tracebacks.
   - Backend choice: use cloud when `YT_API_KEY` / `SUPADATA_API_KEY` are set, otherwise local, with fallback on cloud failure.
   - `YT_PROXY` passthrough for the local backend.
   - Every script declares its dependencies in a `uv` (PEP 723) header, with a `pip install` fallback.
3. **Build `channel_videos.py`** with `--latest N`, `--popular N`, `--include shorts,live` and `--exact-dates`.
   - Cloud: resolve the handle, read the uploads playlist (the videos-only, shorts or live variants), batch `videos.list` for views and duration, and sort by views for "popular". Dates are exact. It never uses the 100-unit `search` call.
   - Local: yt-dlp flat listing with approximate dates (`date_approximate: true`); `--exact-dates` fetches each video.
4. **Build `video_info.py`** with `--no-transcript`, `--lang da,en` (default `en`) and an opt-in `--ai-transcript`.
   - Metadata comes from `videos.list` (cloud) or yt-dlp (local). Chapters come from yt-dlp or from the timestamps in the description.
   - Transcript language order: the `--lang` languages, then the original language. Auto-generated captions are preferred over creator-made ones where the backend allows it.
   - The transcript is plain text. The output includes the language, whether it's auto-generated, and `source`.
   - Supadata is called with existing captions only, so a missing transcript never burns AI-generation credits unless `--ai-transcript` is passed.
5. **Map every failure to a clear error code:** `NO_CAPTIONS`, `PRIVATE_OR_UNAVAILABLE`, `NOT_FOUND`, `RATE_LIMITED`, `IP_BLOCKED`, `QUOTA_EXCEEDED`, `BAD_API_KEY`, `MISSING_DEPENDENCY`. Each message says what to do next.
6. **Write `SKILL.md` and `README.md`.**
   - SKILL.md: when to use each script, example workflows ("top 10 popular, then summarise #1"), how to read errors, and to keep transcripts out of chat unless asked.
   - README: one-time setup. Get the two keys, add them as cloud environment variables, allow `www.googleapis.com` and `api.supadata.ai`, and install for Cowork, for Claude Code on Windows, and for phone use.
7. **Tests.** Offline `pytest` with saved sample responses: input parsing, popular sorting, chapter parsing, language and auto-generated selection, error mapping, and backend fallback. Plus a short manual live checklist.

## What we're NOT doing

- No MCP server, web UI or database/cache.
- No official `captions.download`: it only works on videos you can edit, and needs OAuth.
- No keyword search across YouTube (`search` costs 100 units).
- No downloading of video or audio, no Whisper or local speech-to-text, no comments.
- No paid proxy setup. `YT_PROXY` is only passed through if you add one later.
- No AI-generated transcripts unless `--ai-transcript` is passed.

## How we'll know it works

1. From your Android phone, in a Claude Code cloud session with your PC switched off, ask: "What are @veritasium's 10 most popular videos about? Summarise the top one." Claude answers, and the JSON shows `"source": "cloud"`.
2. On your PC with no keys set, the same two commands work and show `"source": "local"`.
3. A private video, a video without captions and a wrong API key each return a clear JSON error with a hint, not a traceback, and `pytest` passes offline.
