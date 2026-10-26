# AGENTS.md

This is the only rules file for this repo. `CLAUDE.md` points here, and rules must not be added anywhere else.

## Project brief

- **App:** `yt-research`, an Agent Skill that lets Claude Code and Cowork look up YouTube channels and videos and return JSON.
- **For:** one person doing research, mostly from a Claude Code cloud session started on an Android phone, with a Windows PC as fallback.
- **Main problem:** getting channel video lists, video metadata and plain-text transcripts into Claude without manual copying.
- **Version 1 must:** provide `channel_videos.py` (latest / popular videos) and `video_info.py` (metadata, chapters, transcript). Cloud backend first (YouTube Data API + Supadata), local backend as fallback (yt-dlp + youtube-transcript-api). Clear JSON errors.
- **Version 1 must NOT:** see "What we're NOT doing" in `PLAN.md`.
- **Budget:** 0 kr/month at up to 50 videos a month (free tiers only).
- **Data:** nothing is stored. Keys come from environment variables.

## General rules

- **Layout.** The skill lives in `yt-research/` (`SKILL.md` + `scripts/`). Tests live in `tests/`. The `yt-research/` folder must stay self-contained so it can be zipped and uploaded as a skill.
- **Python 3.10+, standard library first.** The cloud backend uses only the standard library (`urllib`). `yt-dlp` and `youtube-transcript-api` are imported lazily, only by the local backend, so a missing package becomes a `MISSING_DEPENDENCY` error, not a crash.
- **Self-installing scripts.** Each script declares its dependencies in a PEP 723 header so `uv run` works with no setup. `pip install -U yt-dlp youtube-transcript-api` is the documented fallback.
- **JSON only on stdout.** Success prints JSON and exits 0. Failure prints `{"error": {"code", "message", "hint"}}` and exits 1. Never print a traceback.
- **Stay inside the free tiers.** Never call the YouTube `search` endpoint (100 units). Never let Supadata AI-generate a transcript unless `--ai-transcript` is passed.
- **Secrets.** Never commit API keys. They come from `YT_API_KEY`, `SUPADATA_API_KEY` and optionally `YT_PROXY`.
- **Tests run offline.** `pytest` uses saved sample responses and never touches the network.
- **Small commits.** Make one logical change per commit, with a plain one-line message. Push often.
- **Keep it simple.** Add no dependency, abstraction or feature that the current plan doesn't need. When in doubt, leave it out.
- **Watch pull requests.** After opening a pull request, follow it through: fix failing CI (`.github/workflows/ci.yml` runs `pytest` on every pull request) and address review comments, and push until CI is green.

## Skill map

The fstack loop is the backbone. Other skills plug in only at the points below. Never use two skills for the same job. If a skill mentions a skill that isn't on this map (for example, `tdd` mentions `code-review`), use the mapped skill for that job instead (`fstack-check` for review, `fstack-simplify` for cleanup).

| When | Use |
|---|---|
| Each feature | `fstack-nail` (only if the request is unclear) → `fstack-plan` → `fstack-build` → `fstack-check` → `fstack-push` |
| Inside `fstack-build`, for logic that must be correct (parsing, sorting, language selection, error mapping) | `tdd` |
| Writing or changing code that calls Claude or another AI model | `claude-api` (built into Claude Code), loaded before touching that code |
| Bug found by `fstack-check` or testing, with a cause that isn't obvious | `diagnosing-bugs` |
| Trying an idea | `prototype` on a separate throwaway branch (`prototype/<name>`). Never merge it. If it works, plan it properly with `fstack-plan` |
| Understanding the code | `zoom-out` (read-only, changes nothing) |
| Cleaning up | `fstack-simplify` first. Use `improve-codebase-architecture` only when asked, or when simplify isn't enough. Its changes go through `fstack-plan` before any code changes |
| Ending a session | When a session is long or the user says they're stopping, run `handoff` |
| Starting a session | Read the latest handoff in `docs/handoffs/` if one exists |

Helper skills: `grilling`, `domain-modeling` and `codebase-design` are installed only because `grill-with-docs`, `tdd` and `improve-codebase-architecture` load them. Don't invoke them on their own.

### Project overrides for skills

- **handoff:** cloud sessions are thrown away when they end, so save handoffs to `docs/handoffs/YYYY-MM-DD-HHMM.md` in the repo, not the OS temp folder, and commit and push them.
- **prototype:** there is no issue tracker. Record the prototype branch name and the verdict in `PLAN.md` or a commit message.
- **Asking questions:** when a skill asks the user something, ask and wait. Never answer for the user.
