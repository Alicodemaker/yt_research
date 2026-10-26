# AGENTS.md

This is the only rules file for this repo. `CLAUDE.md` points here, and rules must not be added anywhere else.

## Project brief

_Not filled in yet. KICKOFF.md fills this in from BRIEF.md._

- **App:** _name and one-line description_
- **For:** _who uses it_
- **Main problem:** _what it solves_
- **Version 1 must:** _core features_
- **Version 1 must NOT:** _out of scope_
- **Look and feel:** _style in a few words_
- **Data:** _what it stores and where_

## General rules

- **Mobile-first.** Design for a ~390px wide phone screen first, then scale up. Tap targets are at least 44px. Respect safe areas.
- **PWA that works offline.** The app must be installable and must load and work without a network. Anything new has to be cached by the service worker (`vite-plugin-pwa` in `vite.config.js`). If a feature needs the network, it fails gracefully offline.
- **One theme file.** All colours, fonts and spacing live in `src/theme.css` as CSS variables. Components use only those variables and never hard-code values. If you need a new value, add it to the theme file first.
- **Small commits.** Make one logical change per commit, with a plain one-line message. Push often.
- **Keep it simple.** Add no dependency, abstraction or feature that the current plan doesn't need. When in doubt, leave it out.
- **Network hosts.** Production builds carry a strict Content-Security-Policy (`csp` in `vite.config.js`) that only lets the app talk to itself. Add every new network host (an API, fonts, images) to it, or its requests are silently blocked. The dev server has no policy, so test anything that uses the network on the production build.
- **Stack.** Use Vite and `vite-plugin-pwa`, with plain JS/CSS by default. Add a UI framework only if a plan explicitly calls for one.
- **Deploy.** Pushing to `main` deploys to GitHub Pages under `/<repo>/` (`.github/workflows/deploy.yml`). Never hard-code `/` as a root path: use relative paths or Vite's `import.meta.env.BASE_URL`.
- **Watch pull requests.** After opening a pull request, follow it through: fix failing CI (`.github/workflows/ci.yml` tests and builds every pull request) and address review comments, and push until CI is green. If you can't watch it here, check CI before you finish.

## When the app needs a backend (optional)

By default an app has no backend: data stays on the device. Add a backend only when a plan needs one (accounts, sync, payments, or data shared between people), and record the choice in an ADR. The app must still load and work offline.

When that happens, suggest the options below, or check them against whatever you were going to propose. Tell me the trade-offs and let me choose before you build.

- **Backend and database:** Convex (real-time and type-safe, with ready-made components for Stripe payments, WorkOS logins and PostHog analytics), or PlanetScale when plain Postgres fits better.
- **Hosting with server code:** Vercel, or Cloudflare (Workers, R2 storage, Durable Objects). If you pick Cloudflare, use its whole stack. GitHub Pages stays the host for apps without a backend.
- **Framework, if plain JS stops being enough:** SvelteKit (fast by default) or Next.js. This still needs a plan that explicitly calls for it (see **Stack**).
- **Backend service code:** Effect, for TypeScript with typed error handling.
- **Personal data:** check that the provider can keep data in the EU (GDPR).

## Skill map

The fstack loop is the backbone. Other skills plug in only at the points below. Never use two skills for the same job. If a skill mentions a skill that isn't on this map (for example, `tdd` mentions `code-review`), use the mapped skill for that job instead (`fstack-check` for review, `fstack-simplify` for cleanup).

| When | Use |
|---|---|
| Starting an app (once) | Follow `KICKOFF.md` |
| Each feature | `fstack-nail` (only if the request is unclear) → `fstack-plan` → `fstack-build` → `fstack-check` → `fstack-push` |
| Inside `fstack-build`, for logic that must be correct (calculations, scheduling, data rules) | `tdd` |
| Visual style | `frontend-design` once at kickoff to create the style. After that, only `fstack-design` to keep new screens consistent with `src/theme.css` |
| Before any pull request that changes the UI | `webapp-testing` at a mobile screen size (390×844) on the production build (`npm run build`, then `npx vite preview`), not the dev server. Save reusable test scripts in `tests/ui/` and commit them. Save a screenshot of each changed screen to `docs/screens/<screen>.png` (`<screen>-dark.png` for the dark theme), replacing the old one, so the PR shows before and after. Then `web-design-guidelines`. Fix real problems and list minor ones in the PR description. If browser tools can't run here, say so and continue |
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
