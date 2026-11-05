---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to `docs/handoffs/YYYY-MM-DD-HHMM.md` in the repo, then commit and push it. Cloud sessions are thrown away when they end, so the OS temp folder would lose it.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

## When to use

- The session is long, or the user says they're stopping.

**Don't use for:** "summarise what we did" for the user. Reply in chat instead.

## Output template

- **Always**: Goal, and Next steps.
- **Only when they have content**: Done (with commit links), In progress, Open decisions, Gotchas (for example credits used or missing keys), Suggested skills.
