# KICKOFF.md

Instructions for the first session of a new app built from this template. Follow them in order.

## How to run each step

- Invoke each skill yourself with the Skill tool. If a skill can't be invoked, read its `.claude/skills/<name>/SKILL.md` and follow it.
- When a skill raises a question, ask me and wait for my answer. Never answer for me.
- After each step, summarise it in 2–3 lines, then commit and push.
- Stop after step 6 and wait for my approval. Build nothing.

## Steps

1. **Set up the skills: `setup-matt-pocock-skills`.** Use sensible defaults for a solo project with no issue tracker (choose the local-markdown option). When it's done, check that `CLAUDE.md` still says only "Read AGENTS.md and follow it". If the skill added anything to `CLAUDE.md` (such as an `## Agent skills` block), move it into `AGENTS.md` and put `CLAUDE.md` back to that single line.

2. **Roast the idea: `fstack-roast`.** Run it on my app idea. Settle two things: is it worth building, and what is the smallest useful version 1?

3. **Settle the details: `grill-with-docs`.** Build on the roast's conclusions and don't repeat questions it already answered. Cover:
   - who it's for
   - the main problem
   - what version 1 must do
   - what it should NOT do
   - look and feel
   - what data it needs

   Record decisions in the docs (glossary and ADRs, as the skill does). Then write `BRIEF.md` (under one page) and fill in the **Project brief** section of `AGENTS.md`. Replace only that section. Before committing, diff `AGENTS.md` and check that every other section is unchanged.

4. **Create the style: `frontend-design`.** First ask me for 2–3 apps, sites or screenshots I like (for example from Mobbin) and what I like about each, and use them as the direction. Self-host any font in `src/fonts/`: the Content-Security-Policy blocks other hosts, and the app must work offline. Put the chosen colours, fonts and spacing into `src/theme.css` (the one theme file; keep its variable names where they fit), and build one sample screen, mobile-first, that uses only those variables. Update `theme_color` and `background_color` in `vite.config.js` and the `theme-color` meta tag in `index.html` to match.

5. **Audit the sample screen: `web-design-guidelines`.** Fix real problems and list minor ones in the summary.

6. **Plan version 1: `fstack-plan`.** Write `PLAN.md` for version 1, based on `BRIEF.md`.

**Stop here.** Show me the plan and wait for my approval.
