---
name: fstack-build
description: Execute an approved PLAN.md one step at a time. Use when the plan is approved and the user says to build.
---

# /fstack-build

Implement the approved plan in small steps. Verify each step before moving on. Pause at real choices.

## When to use

- An approved `PLAN.md` exists and the user says to build.
- `/fstack` routed here because the plan is approved and ready.

**Don't use for:** work with no approved `PLAN.md` (run `/fstack-plan`), or reviewing finished work (run `/fstack-check`). Logic that must be correct uses `tdd` inside the step.

## Steps

1. Take the first unfinished step from `PLAN.md`.
2. Implement it with the smallest change that works.
3. Verify it. Run it, run the test, load the page — whatever fits.
4. Report in 2–3 sentences: what changed, how you verified it.
5. Mark the step done in `PLAN.md`.
6. If the next step involves a real choice — library, API shape, naming that leaks into the public surface — **stop and ask** before proceeding.
7. Otherwise, continue to the next unfinished step. Repeat from step 1.

## Stop and ask

Pause when a step needs a decision that affects the rest of the work. Present the options in plain language. Say what you recommend and why. Wait for approval.

If you discover work that is not in the plan, propose the amendment and **stop and ask**. Add it to `PLAN.md` only after the user approves it.

## Output template

One report per step:

1. **Done**: what changed, in 1-2 sentences.
2. **Verified**: the command you ran and its result, for example `pytest: 48 passed`.
3. **Next**: "continuing to step N", or a choice with your recommendation and a question. Skip the choice when there's no real decision.

## Must NOT

- Do work that is not in the plan without asking first.
- Refactor surrounding code "while you're there".
- Batch multiple steps into one big change.
- Skip verification on any step.

## Example

> Agent: "Step 2 done: added the toggle component to the header and verified it renders. Step 3 needs a choice: store the preference in localStorage or a cookie? localStorage is simpler and this doesn't need server-side rendering of the theme. Recommend localStorage — ok?"
>
> User: "Yes, localStorage."
>
> Agent: *(marks step 2 done, implements step 3)*
