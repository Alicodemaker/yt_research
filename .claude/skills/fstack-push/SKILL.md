---
name: fstack-push
description: Commit the current task's changes and push them to the remote. Nothing else — no tests, no deploy.
---

# /fstack-push

Commit the current task's changes, then push to the remote. That is the whole job.

## When to use

- You want your current work committed and pushed, now.
- The user invokes `/fstack-push`.

**Don't use for:** "run the tests and push" (run `/fstack-check` first), or opening a pull request (only when the user asks for one).

## Steps

1. Check the working tree. Separate the current task's changes from unrelated work. If the scope is unclear, **stop and ask**.
2. Stage only the current task's changes and commit with a plain one-line message describing what changed. If the task is already committed, skip to the push.
3. Push the current branch to its remote.
4. Report what happened in one line: the commit (if any) and the push result.

## Output template

- **Line 1**: the commit (hash and message) and the push result (branch).
- **Line 2**: only if something was left out on purpose, such as unrelated changes or a file that looks like a secret.

## Must NOT

- Run tests or deploy. This skill only commits and pushes.
- Commit unrelated changes.
- Force-push, or push to a different branch than the current one.
- Skip hooks.
- Amend commits that are already on the remote.
- Commit files that look like secrets — `.env`, keys, credentials. Warn instead.

## Example

> User: `/fstack-push`
>
> Agent: "Committed 'Add export button to settings' and pushed to `main`. Done."

> User: `/fstack-push` *(nothing uncommitted)*
>
> Agent: "Nothing to commit. Pushed the 2 local commits to `main`."
