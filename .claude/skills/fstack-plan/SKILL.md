---
name: fstack-plan
description: Write a short PLAN.md the user approves before building. Use after /fstack-nail confirms, or when the user asks for a plan and the idea is already clear.
---

# /fstack-plan

Turn confirmed understanding into a short written plan. The user approves it before any building starts.

## When to use

- After `/fstack-nail` confirms the summary.
- The user asks for a plan and the idea is already clear.
- `/fstack` routed here because there is no plan yet.

**Don't use for:** an unclear request (run `/fstack-nail` first), or a one-line fix that isn't a feature, like a typo or a doc wording change: just make it and push.

## Steps

1. If `/fstack-nail` produced a confirmed summary, use it as the basis for the plan. Do not reopen settled questions unless new evidence conflicts with it.
2. Write or update `PLAN.md` in the project root.
3. Use exactly four sections (see below). No other headings.
4. Show the plan to the user.
5. **Stop and ask** for approval. Do not implement until they approve.
6. If any step feels big, split it or cut it. Do not nest sub-steps.

## PLAN.md format

### What we're doing

2–4 sentences. Plain language. What and why.

### Steps

Numbered list. Max 7 steps. Each step small enough to finish and verify in one sitting.

### What we're NOT doing

Mandatory. Never leave this empty. List tempting extras that are out of scope.

### How we'll know it works

1–3 plain checks. Things you can actually try, like "toggle the switch, refresh, theme persists".

## Output template

- **PLAN.md**: the four sections above. None of them can be skipped. During the build, finished steps get a ✅ instead of being deleted.
- **Chat reply**: one line saying the plan is written, then "Approve?". Don't paste the whole plan into chat if it's already on screen.

## Must NOT

- Exceed one page. If longer, split the task into multiple plans.
- Add headings beyond the four sections.
- Start implementing. The plan ends at approval.

## Example "What we're NOT doing"

> **What we're NOT doing**
> - No theme customization beyond light/dark
> - No per-page theme overrides
> - No settings page — just the header toggle

## Example interaction

> Agent: *(writes PLAN.md, shows it)*
>
> "Here is the plan. Four sections: what we're doing, steps, what we're not doing, how we'll know it works. Approve this before I build?"
>
> User: "Approved."
>
> Agent: *(stops. User can invoke `/fstack-build` next.)*

## Worked example

**Starting context:** the project brief in AGENTS.md: research YouTube from an Android phone, 0 kr a month, cloud backend first with a local fallback.

**Result (excerpt from this repo's `PLAN.md`):**

> **What we're NOT doing**
> - No MCP server, web UI or database/cache.
> - No keyword search across YouTube (`search` costs 100 units).
> - No downloading of video or audio, no Whisper or local speech-to-text, no comments.
> - No AI-generated transcripts unless `--ai-transcript` is passed.
>
> **How we'll know it works**
> 1. From your Android phone, in a Claude Code cloud session with your PC switched off, ask: "What are @veritasium's 10 most popular videos about? Summarise the top one." Claude answers, and the JSON shows `"source": "cloud"`.

**Why it works:** the NOT list names the expensive temptations, which keeps the 0 kr budget. Every check is something you can actually do from the phone. Each of the 7 steps could be verified on its own and got a ✅.
