# yt-research

An Agent Skill for Claude Code and Cowork that looks up YouTube channels and videos and returns JSON:

- **`channel_videos.py`**: a channel's latest and/or most popular videos (title, link, date, views, duration).
- **`video_info.py`**: one video's metadata, description, chapters and plain-text transcript.

Ask Claude things like *"What are @veritasium's 10 most popular videos about? Summarise the top one."* and it runs the scripts for you.

The skill lives in [`yt-research/`](yt-research/) (`SKILL.md` + `scripts/`). `.claude/skills/yt-research` is a shortcut to it, so Claude Code sessions on this repo find it automatically.

## How it fetches data

| What | Cloud backend (used first, needs keys) | Local fallback (no keys) |
|---|---|---|
| Channel lists and video metadata | YouTube Data API (`YT_API_KEY`) | yt-dlp |
| Transcripts | Supadata (`SUPADATA_API_KEY`) | youtube-transcript-api |

YouTube blocks transcript scraping from cloud servers, so **cloud sessions need `SUPADATA_API_KEY` for transcripts**. On a home connection everything also works without keys. The JSON says which backend answered (`source`, `transcript_source`).

**Cost: 0 kr** at normal research use (up to about 50 videos a month):
- The YouTube Data API is free for 10,000 units a day. A video lookup is 1 unit, and a channel list is about 1 unit per 50 videos.
- Supadata's free plan gives 100 transcripts a month. A video with no captions still uses 1 credit, and AI transcripts happen only with `--ai-transcript`.

## 1. Get the two free keys

**YouTube Data API key** (`YT_API_KEY`):
1. Sign in at https://console.cloud.google.com with a personal Google account. No billing or card is needed.
2. Click the project picker at the top → **New project** → `yt-research` → **Create**, and select it.
3. Open https://console.cloud.google.com/apis/library/youtube.googleapis.com → **Enable**.
4. Go to **APIs & Services → Credentials → Create credentials → API key**.
   - Under **API restrictions**, choose **YouTube Data API v3**.
   - Leave **Application restrictions** at **None**.
   - Click **Create** and copy the key (`AIza…`).

**Supadata key** (`SUPADATA_API_KEY`):
1. Sign up at https://supadata.ai on the **Free** plan.
2. Copy the key from the dashboard's **API Keys** page.

Never paste keys into a chat or commit them. If one leaks, delete it and create a new one.

## 2. Use it from your phone (Claude Code cloud session)

One-time setup: open the cloud environment's settings (environment menu in the session title bar → **Edit**).

- **Environment variables**: add `YT_API_KEY=…` and `SUPADATA_API_KEY=…`.
- **Network access → Allowed domains** (keep "Allow package managers" ticked): add `api.supadata.ai`. `www.googleapis.com` is usually allowed already. Add `youtube.com` and `*.youtube.com` too if you want the yt-dlp fallback to work in the cloud.

Then, any time: Claude app → **Code** → start a session on **this repo** (`yt_research`) → ask your question. Settings changes apply to new sessions only.

## 3. Use it in Cowork (Claude Desktop on Windows)

1. Zip the `yt-research` folder: right-click → **Send to → Compressed (zipped) folder**. The zip must contain `yt-research/SKILL.md`.
2. In Claude Desktop, open the skills settings (Settings → Capabilities → Skills, or Customize → Skills in newer versions) and upload the zip.
3. Ask a YouTube question in Cowork. Cowork runs on your PC's internet connection, so the local backend works without keys. Claude installs `yt-dlp` and `youtube-transcript-api` the first time.

If Cowork reports `NETWORK_ERROR`, allow `youtube.com` in Cowork's network settings.

## 4. Use it in Claude Code on Windows

1. Install `uv` once in PowerShell: `winget install --id=astral-sh.uv -e`
2. Copy the `yt-research` folder to `%USERPROFILE%\.claude\skills\yt-research`. Copy the real folder, not the `.claude/skills` shortcut.
3. Optional, for the cloud backend: `setx YT_API_KEY "AIza…"` and `setx SUPADATA_API_KEY "…"`, then open a new terminal.

**From your phone with the PC on:** run `claude remote-control` in any folder on the PC. That session then appears in the Claude app on your phone, and the scripts run on your home connection, so no keys are needed.

## Running the scripts yourself

```bash
cd yt-research
uv run scripts/channel_videos.py @veritasium --latest 10 --popular 10 --include shorts
uv run scripts/video_info.py https://youtu.be/dQw4w9WgXcQ --lang da,en
```

Without `uv`, run `pip install -U yt-dlp youtube-transcript-api` once, then use `python scripts/...`. All options and error codes are in [`yt-research/SKILL.md`](yt-research/SKILL.md).

## Development

- **Rules:** [AGENTS.md](AGENTS.md) is the single rules file. `CLAUDE.md` only points to it. The plan is in [PLAN.md](PLAN.md).
- **Tests:** `pip install pytest`, then `pytest -q`. They run offline with fakes of each service, and CI runs them on every pull request.
- **When YouTube changes something:** update yt-dlp first (`pip install -U yt-dlp`). `uv run` always gets a recent version.
