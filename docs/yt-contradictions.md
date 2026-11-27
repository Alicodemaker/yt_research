# YT videos vs the guide: contradictions to research

Date: 2026-11-27. **Complete: all 195 New videos reviewed.** Compared against the guide (toggles 0–18 + changelog), the 📚 Docs rows and each other.

**Source check, 2026-11-27 (second pass).** I checked this doc against itself, opened the relevant 📚 Docs rows in Notion and read the official pages listed under each item. Each item now has a **Sources** line with a verdict:
- ✅ **settled**: an official source answers the question.
- ⚠️ **partly settled**: some of it is answered, and what's left is noted.
- ❓ **open**: not checked, or the source couldn't be reached.

Notion was not changed.

## 0. Contradictions inside this doc (fixed below)

| # | Where | Problem | Fix |
|---|---|---|---|
| 1 | Coverage | Said Docs rows were "mostly NOT opened". | 9 Docs rows were opened in this pass (listed under Coverage). |
| 2 | A2, A7 | Both cite "the Datatilsynet cookie row" for the May 2025 Datatilsynet + Digitaliseringsstyrelsen (DIGST) guidance. That guidance actually sits in the **"Datatilsynet: transfers to the US (DPF)"** row. The cookie row is shorter and doesn't cover embeds. | Both items now point to the right row. |
| 3 | A3 | Says "five videos" but lists four. | Changed to four. |
| 4 | A4 | Says "five videos" but lists six. | Changed to six. |
| 5 | A7 | Says "the Docs row wins… Cloudflare Web Analytics sets none" as if settled. The cookie row itself has a ⚠️: it doesn't say whether cookieless analytics needs consent. The US-transfer row says consent covers "cookies **and similar technologies**", and that IP addresses are personal data. | A7 downgraded to ⚠️. See A7. |
| 6 | A8 | Asks to "verify at the official EU page" whether the micro-enterprise exemption applies. The Docs row (Verified 2026-11-26) already quotes Art. 3 and Art. 4(5). | Marked ✅. What remains is a business check, not research. |
| 7 | A10 | Treats "OWASP Top 10 for LLM Apps" and "the Docs OWASP row" as one source. The Docs row is the **web** Top 10:2025, where supply chain is A03. The LLM Top 10 is a separate list. | Both are listed separately. |
| 8 | A11 | Puts WCAG 2.2.2 and 2.3.3 side by side. 2.2.2 is Level A, so it's required under the AA target. 2.3.3 is Level AAA, so it's best practice only. | Levels added. |
| 9 | A12 | Gives the guide's rule as "fresh session at about 50% (and by about 120k tokens)". On a 1M window, 50% is about 500k, so the two figures contradict each other. | Flagged for a guide fix: say which window size each figure is for. |
| 10 | A12 / B | Says the guide keeps `CLAUDE.md` under 100 lines and treats "Claude Pros: under 200" as the outlier. Anthropic's memory docs say **under 200**. | B row updated. 100 is a stricter house rule, not the official figure. |
| 11 | E | A3 is rated MEDIUM–HIGH but sits in step 4, after the MEDIUM items A4–A6. | Kept on purpose: it needs a real Lighthouse run first. The reason is now written in E. |

## Coverage and caveats
- **Reviewed: 195 of 195.** 63 videos produced 81 entries. The other 132 had nothing to flag.
- **Docs rows opened in this pass:** Danish cookie rules (Datatilsynet), Datatilsynet: transfers to the US (DPF), WCAG 2.2 + EU Accessibility Act, Google: SEO starter guide, Pages CMS: safe setup for client editing, OWASP: Top 10:2025 & HTTP headers, web.dev: Core Web Vitals. The full list of all 27 rows was also read. There is no Docs row for Claude Code, Anthropic prompting, Astro images, Google reviews or the EU AI Act. The official pages for those are linked under each item. Consider adding rows for them.
- One transcript (Matt Pocock, "How to Actually Code with AI") was covered partly by keyword search. About 12k characters were not read in full.
- Every video claim below is what a video says. The **Sources** lines are what the official sources say. Priorities are for Connectric: an Astro + Workers + Pages CMS lead-gen site with a frozen design system, under Danish law and GDPR.

## A. Research first (high/medium for Connectric)

1. **Stacking or re-running design skills vs the frozen design system** (HIGH)
   - "This Claude Skill Changed UI Design Forever": stack UI UX Pro Max, frontend-design, Impeccable, then audit and test skills in one build.
   - "Claude Skills for Designers (Ban AI Slop Forever)" and "Give Claude a Senior Designer's Taste": run Impeccable's pass commands (distill, layout, bolder, quieter, typeset, polish) on existing pages. Skip frontend-design if Impeccable is installed.
   - "Copying other website's Design.MD File": pull a famous brand's design.md into an existing project with npx, then swap fonts and colours.
   - Guide (toggles 2, 5, 8): invent-style skills only on new projects. Once the design system is frozen, use audit-only (`npx impeccable detect`) and fix by hand. Never change the design system after coding starts.
   - Research: which Impeccable commands only audit and which rewrite styles (`npx impeccable detect --help`, repo README). Test on a branch: one pass command, with before/after screenshots against the Connectric tokens. Suggested house rule: third-party design.md files only before the design system is frozen, never for Connectric.
   - **Sources:** ❓ open. This is third-party tooling with no official doc. It's a hands-on test, so a source wouldn't settle it.

2. **Google Maps embed + reviews slider + "80+ five-star" pill** (HIGH) — "Build $10,000 Websites using Claude Code" (also hotlinks Unsplash images)
   - Guide (toggle 18, the Datatilsynet rows, toggle 13): embeds load only after consent, no fake or unconfirmed ratings, sample photos flagged and blocked at launch.
   - Research: does an embedded Google Map need prior consent? Use a click-to-load or static map. Take review text only from the client's confirmed reviews, and check Google's terms for showing them.
   - **Sources:** ⚠️ partly settled.
     - **Map consent: ✅ yes.** The Docs row "Datatilsynet: transfers to the US (DPF)" quotes the joint guidance (Datatilsynet + DIGST, May 2025, [PDF](https://cdn.datatilsynet.dk/datatilsynet/Media/638829899950476628/F%C3%A6llesvejledning%20med%20DIGST%20-%20Cookie%20og%20lignende%20teknologier.pdf)). Consent also applies where third parties collect data on your site, and the guidance names "korttjenester" (map services). You must also name those third parties. The guide's click-to-load or static map stands.
     - **Ratings: ✅.** Showing "80+ five-star" needs real, checkable reviews. See A19 for Google's and Danish rules.
     - ❓ Still open: Google Maps Platform terms for showing Google review text on your own site.

3. **Hero design: video, parallax, layered photos, rotating images** (MEDIUM–HIGH) — four videos against one guide rule
   - "New way to prompt Fable 5": Osmo marquees, sliders, parallax and generated hero videos for a premium feel.
   - "Fable 5 VS Web Designer": the winning build has a full-background video hero, scroll parallax reveals and animated buttons.
   - "I Studied 10,000 AI Websites": layer a real photo behind the content, with cards overlapping the next section.
   - "The one thing vibe coding CAN'T fix": full-bleed image hero, scroll blur transitions, auto-rotating image tabs.
   - Guide (toggle 13, lead-gen rules): at most one subtle hero animation. No parallax or heavy background images.
   - Research: web.dev LCP/INP guidance, WCAG 2.2.2 for auto-rotating content, and a real Lighthouse mobile test of a hero photo on the preview. A light photo may be fine. Video and parallax are the risk. Several earlier videos already disagree with each other on this (see B).
   - **Sources:** ⚠️ partly settled.
     - Docs row "web.dev: Core Web Vitals" (Verified): good is LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, measured with Lighthouse before launch ([web.dev/articles/vitals](https://web.dev/articles/vitals)).
     - WCAG 2.2.2 Pause, Stop, Hide is **Level A**. Content that "starts automatically, lasts more than five seconds, and is presented in parallel with other content" needs a pause/stop/hide control ([Understanding 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide)). Auto-rotating tabs and a looping background video therefore need a pause button.
     - ❓ Still open: the Lighthouse test itself.

4. **Model, effort and switching** (MEDIUM) — six videos disagree with each other and with the guide
   - "Anthropic Engineer Explains: How to Stop Hitting Claude's Token Limit": switching model mid-session breaks the prompt cache. Pick a model at session start and stay on it. Hand cheap work to a subagent or a new session.
   - "Claude Pros Don't Pay for Max": medium is fine for site work. Avoid max unless needed. Don't switch model or effort mid-session.
   - "How to Actually Code with AI (Matt Pocock)": one strong model at medium effort for nearly everything. Fix the environment instead of switching models.
   - "My Fable 5.2 Workflow": never low or max, live in high/extra-high, Sonnet 5.5 is pointless, get the $200 plan. "New way to prompt Fable 5" runs extra effort. These two conflict with the Pocock and Pros videos.
   - "This AI Coding Workflow Is a GAME CHANGER": a strong model plans and reviews, a cheap model implements.
   - Guide (toggles 1, 14): `opusplan` (Opus plans, Sonnet builds), `/model opus` for merge/fix sessions then "switch back". Run `/doctor` when switching models. Max $100 first.
   - **Sources:** ⚠️ partly settled. Claude Code docs:
     - **Cache: ✅ the token-limit video is right.** "Each model has its own cache" and "Switching models recomputes the entire request even when the content is identical" ([prompt caching](https://code.claude.com/docs/en/prompt-caching)). `opusplan` is "Special mode that uses `opus` during plan mode, then switches to `sonnet` for execution" ([model config](https://code.claude.com/docs/en/model-config)). So every plan ↔ build switch in `opusplan`, and every manual `/model` change, starts a cold cache. The guide should state this cost.
     - **Effort: ✅ default is medium.** Fable 5.2, Opus 5.5, Sonnet 5.5 and Haiku 5.5 default to `medium`. Levels are low/medium/high/xhigh/max ([model config](https://code.claude.com/docs/en/model-config)). This supports Pocock and Claude Pros. The "never below high" advice is a personal preference.
     - **Fable 5.2: ✅ the "$200 plan" advice is misleading.** The docs say "No Fable model is the account-type default on any plan", and Fable usage "can bill to usage credits instead of drawing on your plan's included limits". It needs Claude Code v2.1.321+. A bigger plan doesn't simply buy more Fable. Add this to toggle 14.
     - ❓ Still open: the size of the cache cost in practice. Run one real PR Opus-only vs `opusplan` and compare usage and fix rounds.
   - Subagent models: the token-limit video and "How I Keep Up with AI" use Haiku for small jobs. The guide says Sonnet for subagents and Haiku only for trivial searches. Low relevance unless you build a scheduled agent.

5. **MCP context cost may be outdated** (MEDIUM) — "Claude Pros Don't Pay for Max" says MCP tool definitions now load only on demand. The guide says an MCP costs 13–20k tokens every session and prefers CLIs. Related: "Notion MCP wastes tokens" (GAME CHANGER video). Context7 MCP (software-factory video) vs cloning the library source into a git-ignored folder. The Context7 Search video offers a lighter HTTP API (free-tier figures unverified). "9 Free Repos" pushes a Firecrawl connector (check for an official CLI/skill).
   - Research: run `/context` in a fresh session with your MCPs on.
   - **Sources:** ✅ mostly settled: the video is right and the guide is stale.
     - Claude Code's MCP docs say tool search is on by default. Servers that connect late supply "deferred definitions that Claude loads on demand" ([MCP](https://code.claude.com/docs/en/mcp), [prompt caching](https://code.claude.com/docs/en/prompt-caching)).
     - It's controlled by `ENABLE_TOOL_SEARCH`, and is off when `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` is set or a non-first-party `ANTHROPIC_BASE_URL` is used ([tool search](https://code.claude.com/docs/en/agent-sdk/tool-search)).
     - Replace the "13–20k every session" figure with: "deferred by default; check with `/context`".
     - The CLI preference can stay for other reasons (scriptable, no server).

6. **Prompt format: no step lists** (MEDIUM) — "How to Get Dangerously Good With Claude": give the goal, done-when, validation, out-of-scope and guardrails, with no numbered steps (cites Anthropic's prompting guide). Guide toggle 4 and your project rule both use a "do (steps)" section.
   - **Sources:** ✅ settled: the video misreads Anthropic.
     - Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) say: "Provide instructions as sequential steps using numbered lists or bullet points when the order or completeness of steps matters."
     - Keep "do (steps)" for tasks where order matters. The video's goal / done-when / validation / out-of-scope fields are a good addition, not a replacement.
     - Not verified: a model-generated summary of the rest of the page mentioned "prefer general instructions over prescriptive steps" for *reasoning*. Read the full page before quoting that line.

7. **Cookie banner claim vs the Datatilsynet rows** (MEDIUM) — "My Best Claude Code Advice After 20 Years" says most countries need a cookie banner and the agent should add one by default. Guide toggle 18 and the Docs rows: consent only before non-technically-necessary cookies. Cloudflare Web Analytics sets none.
   - **Sources:** ⚠️ partly settled. The video is wrong as a default rule, but the guide's "no banner needed" isn't proven either.
     - Docs cookie row: consent is needed except for technically necessary purposes. ⚠️ The row says it doesn't state whether analytics without cookies needs consent.
     - Docs US-transfer row (joint guidance, May 2025): consent covers "cookies **og lignende teknologier**" (and similar technologies) used for visitor statistics. IP addresses are listed as personal data. An analytics vendor makes you responsible, usually with a data processing agreement.
     - Cloudflare says Web Analytics "does not use any client-side state, such as cookies or localStorage, to collect usage metrics" and does not fingerprint by IP or user agent ([blog](https://blog.cloudflare.com/privacy-first-web-analytics/), [product page](https://www.cloudflare.com/web-analytics/)). An older independent review found the beacon setting a cookie ([ctrl.blog](https://www.ctrl.blog/entry/review-cloudflare-analytics/)).
     - To do: load the preview with DevTools → Application and check that no cookies or localStorage are set by the beacon or any embed. If nothing is set and no other embeds load before consent, no banner is needed. Name Cloudflare in the privacy policy either way.

8. **"Code quality barely matters if the page converts" vs the launch gates** (MEDIUM) — "Web Design Workflow: Are You Ready for the Future?" against guide toggles 8 and 18 (accessibility, security, performance with proof). Related: "Awwward Winning Designs vs Practical Websites" shrugs off accessibility.
   - **Sources:** ✅ settled by the Docs row "WCAG 2.2 + EU Accessibility Act" (Verified 2026-11-26).
     - The EAA applies from 28 June 2025 only to listed consumer services: e-commerce, banking, e-books, electronic communications, audiovisual media, passenger transport.
     - Art. 4(5) exempts microenterprises providing services. Art. 3 defines a microenterprise as fewer than 10 staff and ≤ €2M turnover or balance sheet ([Directive 2019/882](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0882)).
     - A lead-gen info site is most likely not in scope, so WCAG 2.2 AA is the house standard, not a legal duty. The launch gates stay: they also cover security and performance, which the video ignores.
     - What remains is a business check: Connectric's headcount and turnover, and whether the site ever sells online.

9. **AI-generated photos of real people and premises** (MEDIUM, guide gap) — "Build a Website with AI For Beginners (Relume)" generates a character from a staff photo and an AI "scene" of the real cafe, and uses them on the site. Guide toggle 13 only covers flagged royalty-free sample photos. It has no rule for synthetic images of real people.
   - **Sources:** ⚠️ partly settled.
     - EU AI Act Art. 50 transparency duties have applied since **2 August 2026**. Law-firm alerts agree the Digital Omnibus did not postpone 50(4), the deep-fake disclosure duty for deployers. Only the 50(2) machine-readable marking duty got a short extension, reported as running to 2 Dec 2026 ([Goodwin](https://www.goodwinlaw.com/en/insights/publications/2026/08/alerts-technology-dpc-eu-ai-act-transparency-obligations-now-in-force), [Morgan Lewis](https://www.morganlewis.com/ru/blogs/sourcingatmorganlewis/2026/08/eu-ai-acts-transparency-rules-what-went-into-effect-on-2-august), [CSA note](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-article-50-transparency-20260729/)).
     - ❓ The Art. 50 text itself couldn't be fetched: artificialintelligenceact.eu is blocked from this session. Read it on EUR-Lex (Regulation (EU) 2024/1689).
     - ❓ Not checked: Forbrugerombudsmanden on misleading images.
     - The suggested rule stands: never use AI images as proof of real staff or premises; flagged samples only, and disclose if one is kept.

10. **Skill, MCP and package vetting before install** (MEDIUM, guide gap) — "10 cybersecurity terms": agents install hallucinated packages, tool/skill descriptions can hide instructions, pin MCP versions. "How To Use AI Skills Like A Senior Developer": install per project, check skills.sh security reports, read every file first. "Copying other website's Design.MD" runs an npx package that instructs the agent. Guide toggle 7/15 says give Claude a repo link and install the starter skills (symlinked globally), with no vetting or version-pinning step.
    - **Sources:** ⚠️ partly settled.
      - Claude Code [skills docs](https://code.claude.com/docs/en/skills): personal skills (`~/.claude/skills/`) load in "All your projects on this machine"; project skills (`.claude/skills/`) load only in that repo.
      - The same docs advise to "review the `allowed-tools` of skills checked into a repository before you run Claude Code there". You can set `"disableSkillShellExecution": true` and deny skills with rules such as `Skill(name *)`.
      - Docs row "OWASP: Top 10:2025" lists **A03 Software Supply Chain Failures** (web list).
      - ❓ Not opened: the separate [OWASP Top 10 for LLM Apps](https://genai.owasp.org/llm-top-10/), which has its own supply-chain entry.
      - Proposed guide addition: read SKILL.md and its scripts before installing; prefer project scope for third-party skills; pin versions; check that package names exist before `npm install`.

11. **Reduced motion is missing from the guide** (MEDIUM, gap) — "I Studied 10,000 AI Websites": respect `prefers-reduced-motion`, optionally add a motion toggle. Also relevant to smooth-scroll (Lenis) in "Using Claude Design 2.0" vs scroll-snap criticism in "Handy CSS layout patterns".
    - **Sources:** ✅ settled.
      - [2.2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide) is **Level A**, so it's required under the AA target: auto-moving content over 5 s needs a pause.
      - [2.3.3 Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions) is **Level AAA**, so it's best practice: "Motion animation triggered by interaction can be disabled".
      - Checklist line: pause control on any auto-motion over 5 s (required); honour `prefers-reduced-motion` (cheap best practice).

12. **Context threshold: 70% vs 50%** (LOW–MEDIUM) — "My Best Claude Code Advice" says quality degrades around 70% full on 1M windows. The guide says a fresh session at about 50% (and by about 120k tokens). The same video says memory files can run to hundreds of lines with @-imports. The guide keeps `CLAUDE.md` under 100 lines with pointers.
    - **Sources:** ✅ settled for memory. ❓ open for the threshold.
      - [Memory docs](https://code.claude.com/docs/en/memory): "Imported files are expanded and loaded into context alongside the CLAUDE.md that references them". So @-imports **don't save context**, and the video's "hundreds of lines with @-imports" costs the same as one long file.
      - The docs also say to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." The guide's 100 is a stricter house rule. Keep it, but label it as such.
      - Plain-text pointers (not `@`) are what keep context small.
      - ⚠️ Fix the guide: "50%" and "120k" conflict on a 1M window (see table row 9). No official figure was found for the threshold.

13. **Claude Code "code mode"** (MEDIUM, videos disagree)
    - "I Tested Claude Code's New Code Mode": about 35% fewer input tokens (about 17% by cost), terminal CLI only (2.1.323+), not in the VS Code panel or desktop app, switches off Claude in Chrome and computer use. Env var `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1`.
    - "Claude Code's New Code Mode Is a Game Changer for leadgen": the reviewer read it as terminal-only, experimental, for bulk API loops, not website work.
    - Guide: verify in Chrome via `claude --chrome` in the VS Code extension. No mention of code mode.
    - **Sources:** ✅ settled: skip it for Connectric.
      - [Code Mode docs](https://code.claude.com/docs/en/code-mode): "experimental and off by default. It may change or be removed in any release". It needs v2.1.323+.
      - "Code Mode doesn't work with the VS Code panel, the Desktop app, **or cloud sessions**", and with it on "you can't use Remote Control, Claude in Chrome, or computer use".
      - The docs give no token-saving figure, so the 35% / 17% figures are the video's own test.
      - It wouldn't run in your phone-started cloud sessions at all, and it removes the guide's Chrome check.

14. **Plan/progress files as JSON instead of Markdown** (MEDIUM) — "Everyone Ignore These Claude Concepts": the model rewrites or drops Markdown checklist items more than JSON items. Use JSON with a `passes` flag. Guide toggle 2 keeps `docs/ROADMAP.md` as a Markdown board that Claude edits.
    - **Sources:** ✅ the video quotes Anthropic correctly.
      - [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents): "we landed on using JSON for this, as the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files". Also: "edit this file only by changing the status of a passes field".
      - This setup is for long autonomous runs. For a human-read ROADMAP, a cheap middle way is to keep Markdown and add a check that no cards disappear between commits.

15. **Fewer pages vs many area/service pages** (MEDIUM) — "Brutally Honest Advice About Web Design": fewer, better pages. Guide toggle 13 generates service and area pages from CMS collections. "50 MORE Web Design Mistakes" says one-page sites are a mistake.
    - **Sources:** ✅ settled: the guide needs a guardrail.
      - Google's [spam policies](https://developers.google.com/search/docs/essentials/spam-policies): "Doorway abuse is when sites or pages are created to rank for specific, similar search queries". Examples include region/city pages that funnel users to one page, and "substantially similar pages".
      - Docs row "Google: SEO starter guide" (Verified): reduce duplicate content, one canonical URL, unique `<title>` per page.
      - Rule for toggle 13: only create an area page when it has real, unique local content (jobs done there, local photos, specific info). Otherwise use one service page that lists the areas.

16. **WordPress for CMS/forms, and on-page editing** (MEDIUM) — "Claude Just Changed Web Design Forever": a real CMS, e-commerce or complex forms means WordPress/Shopify/Squarespace. "The 5 Things Every Website Needs": every client site needs a flexible CMS with on-page client editing. "Breaking Down a Real Client Website Design": 99% of his client sites are WordPress + Elementor. Several Framer videos say Framer is best for client editing. Guide: Astro + Pages CMS (form-based, not on-page) beats WordPress.
    - **Sources:** ⚠️ partly settled.
      - Docs row "Pages CMS: safe setup for client editing" (Verified): clients are "invited by email", need no GitHub account, and can "edit content, edit media" scoped to one repo. Turn off `delete`/`rename` per collection, and set `commit.identity: user`.
      - It's form-based editing, not on-page. Forms aren't a CMS job: the quote form is Astro Actions + Turnstile (Docs rows "Astro: Actions & set:html", "Cloudflare: Turnstile…").
      - ❓ Still open: whether the lack of visual on-page editing is a sales problem. Ask the client; no source settles it.

17. **YouTube/video embeds for speed vs consent** (MEDIUM) — "How to Optimize Your Framer Website": use a YouTube/Vimeo embed instead of a self-hosted video. Guide toggle 18: video and maps load only after consent.
    - **Sources:** ✅ settled.
      - The joint guidance in the Docs US-transfer row names "videoafspillere" (video players) as third-party content needing consent, and says "det er dig, der ultimativt bestemmer, hvilket indhold der integreres" (you decide what is embedded, so consent is your job).
      - `youtube-nocookie.com` still loads Google's player and storage, so it is no exception. Use a click-to-load facade or a compressed self-hosted MP4.
      - Same logic for Unicorn Studio or any third-party effect: it needs consent if it loads from a third party. ❓ Not checked: Unicorn Studio's own privacy and DPF status (check the [DPF list](https://www.dataprivacyframework.gov/s/participant-search)).

18. **Dropdown nav: hover or click** (MEDIUM, videos disagree) — "Everything About Website Navigations": click-toggle submenus. "50 Website Design Mistakes": dropdowns should open on hover. Also "sticky menu on every site" vs hide on scroll down.
    - **Sources:** ✅ settled: hover-only is out.
      - [1.4.13 Content on Hover or Focus](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus) is Level AA: content must be dismissible, hoverable and persistent. Its notes: "Content which can be triggered via pointer hover should also be able to be triggered by keyboard focus. Refer to Success Criterion 2.1.1 Keyboard" (Level A).
      - Click/tap-to-open (keyboard-operable) satisfies both. For Connectric, a flat menu with no dropdown is still simplest.

19. **Seeding Google reviews** (MEDIUM) — "How I signed 5 web design clients last week": collect reviews from friends, family and demo sites first. Guide toggle 13: never fake reviews; real client reviews only.
    - **Sources:** ✅ settled: do not follow the video.
      - Google's [Maps user-contributed content policy](https://support.google.com/contributionpolicy/answer/7400114) bans "Content that is based on a conflict of interest", which includes "personal affiliations" and "familial relationships". It also bans content posted "due to an incentive offered by a business".
      - Denmark: the Forbrugerombudsmand's [guidelines on user reviews](https://forbrugerombudsmanden.dk/media/46465/2016-retningslinjer-om-offentliggoerelse-af-brugeranmeldelser.pdf) apply. In the Rekom case, 13 undeclared staff reviews led to a 400,000 kr fine ([DI](https://www.danskindustri.dk/brancher/di-handel/nyhedsarkiv/nyheder/2024/2/politianmeldt-for-vildledende-brugeranmeldelser-skrevet-af-ansatte/)).

20. **No image-optimisation rule in the guide** (MEDIUM, gap) — "Is This The Best FREE Image Optimizer? Squoosh": resize to 1200–1600 px, about 80% quality, WebP, banners under about 120 KB. "How to Optimize Your Framer Website" and "50 MORE Web Design Mistakes": right size/format, separate mobile images.
    - **Sources:** ⚠️ partly settled.
      - [Astro images](https://docs.astro.build/en/guides/images/): keep images "in `src/` when possible so that Astro can transform, optimize, and bundle them. Files in the `public/` directory are … copied … as-is, with no processing." Optimisation only happens via `<Image />`, `<Picture />` or Markdown images, not a plain `<img>`.
      - ❓ Still open: where Pages CMS uploads land. Check `media.input` in `.pages.yml` ([media config](https://pagescms.org/docs/configuration/media/)). If uploads go to `public/`, either point them at `src/assets/` or pre-optimise (the Squoosh numbers are a fair default).

21. **Design prompting: references and loops** (LOW–MEDIUM) — "Creator Of The Best Design Skill…": 9–12 reference images; give the agent hours with a self-scored 99.9% target; build with no animation first. Guide toggle 5: focused direction beats dumping references; open-ended "make it better" loops bloated a site in a 100-round test; prototype effects in a chat artifact first. "The one thing vibe coding CAN'T fix" praises "Frankensteining" sections from several sites, against the guide's "Frankenstein" warning (mostly wording: sections from several sites, one visual style).
    - Research: try both on one section. Cap rounds at 3–5, and use judge scores only with a budget.
    - **Sources:** ❓ open. This is a hands-on test; no official source applies.

22. **Handoff vs compact** (LOW–MEDIUM) — "Claude Pros Don't Pay for Max": `/compact` is expensive after the cache expires; write `handoff.md` then `/clear`; resume only chats under an hour old. Guide: new session at about 50% context, and a handoff report when a session compacts (changelog 2026-11-22). Related: "Every Claude Code Skill I Use" runs implementation in a brand-new conversation from the plan file, and says to review the validation strategy first and the file-level plan detail less. The guide says read the plan and switch to auto in the same session. Both fit the 50% rule. Consider "check the validation section first".
    - **Sources:** ⚠️ partly settled.
      - The cache logic is confirmed by Claude Code's [prompt caching](https://code.claude.com/docs/en/prompt-caching) page: the cache stays warm for one TTL window after the last request. After that, the next request (including `/compact`) re-reads the whole conversation.
      - ❓ The exact TTL on your plan isn't checked. It's 5 min or 1 h depending on setup.

## B. Videos that disagree with each other (cross-video)
- **Autonomy:** "I Built a Coding Agent That Builds Itself" (dark factory, auto-merge) vs "5 Types of AI Software Factories" (proofs of concept only) vs Matt Pocock (a daily scheduled agent opens PRs and he spot-checks about one in five). Guide step 8 and toggle 0 rule 6 (second reviewer on every PR) side with the cautious view. Not relevant until you consider automation.
- **Effort level:** high/extra-high (Fable 5 videos) vs medium is enough (Pocock, Claude Pros). **Docs: default is medium** (see A4).
- **Eyebrow text above headings:** an AI tell ("Claude Just Changed Web Design Forever", guide) vs good hierarchy ("The Only Web Design Video You Will Ever Need").
- **"Contact" CTA:** "avoid vague contact us" vs contact button top right is the convention. A named-action button in that slot fits both.
- **Hero video/photo:** video OK if silent vs minimal effects and no 3–5 s loaders vs guide. See A3: a looping video needs a pause control (WCAG 2.2.2, Level A).
- **CTA/accent colour:** "10,000 AI Websites" puts the accent on buttons and links (60-30-10). Guide toggle 13: one CTA colour used nowhere else. Check green-on-dark link contrast (WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color) / [1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)).
- **Fonts:** up to 3 fonts vs start with one typeface vs guide "one family". Connectric already uses two (Manrope + Inter), so the guide line may need "one or two". Self-host them (joint cookie guidance: third-party fonts are only exempt if not used for tracking).
- **Design inspiration:** avoid awards sites vs use Awwwards.
- **Stock photos:** fine as a placeholder (Brutally Honest; "What to Do When Your Client Sends Bad Content" fills gaps with Unsplash/Pexels and extra copy) vs always a mistake (50 MORE Mistakes, Most Underrated). The guide allows flagged sample photos in previews only and blocks launch. The bad-content video never mentions flagging or replacing. Check the [Unsplash](https://unsplash.com/license) and [Pexels](https://www.pexels.com/license/) licences for anything kept past launch.
- **How much layout AI should decide:** "5 SaaS UI/UX mistakes" (never let AI choose colours or layout) vs "Claude Fable 5 UI/UX One-Shots" (one-shot results better than the human version). The guide sits between: AI builds from your design system.
- **Subagents:** drop custom role agents (Claude Pros) vs restrict spawning ("11 More Tiny Coding Agent Fixes") vs "1000+ Hours" rating subagents A/S tier vs guide "one agent by default, subagent review always". One deliberate review agent per PR fits all. Check the token cost per PR.
- **CLAUDE.md size and need:** guide under 100 lines; Claude Pros under 200; "Top 5 Tips" 200–250 (Cowork); "Best Claude Code Advice" hundreds of lines with @-imports; "1000+ Hours" says you could skip it. **Docs: "target under 200 lines", and @-imports load at launch** ([memory](https://code.claude.com/docs/en/memory)). Claude Pros matches the docs. The guide's 100 is a stricter house rule.
- **Permissions:** bypass mode fine for personal tasks vs only throwaway test sites vs guide (never on client repos).
- **Parallel sessions:** "AI Makes Us WAY Faster but Fries Our Focus" vs guide toggle 7 (2–3 worktrees). Consider capping at 2.
- **Home repo vs repo per project:** "The Home Repo" runs every agent from one repo holding skills and rules; the guide uses a project-level `CLAUDE.md` and a worktree per feature. Connectric is one repo, so revisit only if client repos pass about 3.
- **Global vs project skills:** the "Senior Developer" skills video installs per project; the guide symlinks starter skills globally. Docs: personal skills load in every project, project skills only in their repo ([skills](https://code.claude.com/docs/en/skills)). Global is fine for your own vetted starter skills; third-party ones go per project (see A10).
- **Retainers:** $100/month hosting + maintenance vs prepaid hours, never free hours (earlier filed video: $800–1,500/month). Pick a model for the client contract.
- **CSS taste (low):** flex stacks (Three CSS patterns) vs margins replaced by grid gap ("most undervalued front-end skill"). Pick one spacing primitive in the design system. Scroll snap on sections is "scroll-jacking" (Handy CSS) vs Lenis smooth scroll (Claude Design 2.0). Either way, honour `prefers-reduced-motion` (A11).
- **Tailscale vs Headscale (not Connectric):** "Stop Using Tailscale" vs "What is Tailscale?".
- **Unverified SEO claims** (check against Google's docs before using): uppercase text and grammar affect SEO ("50 MORE Mistakes"); CTR and E-E-A-T as ranking factors, and footer links ("Footers"); a vague H1 hurts SEO ("50 Website Design Mistakes") vs Google says heading order doesn't matter for search ("Heading Hierarchy"). The Google SEO starter guide row (Verified) has no direct conflicts, and doesn't mention case, grammar or heading order. ❓ Not checked further.

## C. Guide may be outdated / missing something
- **Where Claude Design lives:** "AI Web Design Process: Claude to Webflow" says only claude.ai/design (research preview, not in the app). "Using Claude Design 2.0" opens it from the desktop app via a "design labs" entry. Guide toggle 5 and changelog 2026-11-05 say it's now in normal Claude chats and the separate site is closing.
  - **Sources:** ✅ the guide is right and the videos predate the change. Claude Design launched 17 Apr 2026 as an Anthropic Labs research preview ([announcement](https://www.anthropic.com/news/claude-design-anthropic-labs)). The [product page](https://claude.com/product/claude-design) and [Help Center](https://support.claude.com/en/articles/14604416) now describe it inside every Claude conversation. The standalone claude.ai/design closes on **14 Dec 2026**, so move any design systems before then. Enterprise orgs have it off by default.
- Fable 5.2 isn't mentioned in toggle 14. Add: not a default on any plan, bills to usage credits, needs v2.1.321+, default effort medium (see A4).
- Gaps: image optimisation (A20), code mode (A13: skip, doesn't run in cloud sessions), MCP loading (A5: now deferred by default), JSON status files (A14), reduced motion (A11), skill vetting (A10), AI-generated photos (A9).
- **Additions only, no conflict:**
  - Put pasted data first and the question last. ✅ Anthropic: "Place your long documents and inputs near the top of your prompt, above your query", which can improve quality "by up to 30 percent" ([best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)).
  - Use 3–5 examples in skills, and allow "I don't know" ("Everyone Ignore These Claude Concepts").
  - A "removal means gone" paragraph at the top of `CLAUDE.md`, and no "don't do X" leftovers ("Every AI model makes this mistake"). This partly goes against the guide's "add a rule when Claude repeats a mistake". Test on one project.
- **Claim to check, no conflict:** "Watch This If Your Coding Agent is Ignoring Your Rules (You Need Hooks)" says Anthropic cut Claude Code's system prompt by 80%. ❓ Not verified. The video otherwise agrees with the guide (hooks and deny rules are enforced; `CLAUDE.md` is a request).
- **Possible check:** "Give Me 7 Minutes & Your Web Design Skills Will Take Off" says to avoid ghost (outline-only) buttons. The guide is silent. Check Connectric's demo for outline secondary buttons against [1.4.11 Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast) (3:1 for the button border).
- **Gap:** "Fully Automated Email Marketing Using AI" runs a tag-triggered nurture sequence without explicit marketing consent or double opt-in. The guide's Danish/GDPR material doesn't cover email lists. Relevant only if Connectric adds a newsletter. ❓ Source to add then: Danish markedsføringsloven § 10 (consent for electronic marketing).

## D. Low relevance (listed for completeness)
- "How To Use Supabase With AI For Beginners" hands the project secret key to the agent. Guide: never paste secrets in chat; use `.env` plus a blocking hook. Connectric has no Supabase, but the rule applies to any form or email key (Docs rows "Astro: environment variables & secrets", "Cloudflare: Workers headers & secrets").
- "Claude Code Can't See These Bugs. Fiddler MCP Can" turns off header sanitising so the agent reads auth headers. It's a sponsored paid MCP. Use browser DevTools/Playwright traces instead.
- "I'm never going back" argues Svelte/SvelteKit is fine with AI. Connectric is Astro.
- "Build $10,000 Websites using Claude Code" deploys by Hostinger file upload with a PHP form. The guide decision is Simply.com for .dk and Workers for hosting.
- "How I Gave Claude a Second Brain" uses hosted RAG instead of Markdown memory. Sponsored, and far above Connectric's scale.
- "Make Any Website Look 10x Better" and the SuperGamingParties breakdown: Elementor templates.
- "How I Help Clients Repurpose Content…" adds a site-wide timed pop-up email form with only a privacy-policy link. Third-party marketing scripts need consent (Docs US-transfer row, joint guidance).
- "Build Recurring Revenue with WordPress Maintenance Plans" says EU clients must use an EU-located server. **Docs say otherwise (✅):** the Docs row "Datatilsynet: transfers to the US" allows US transfers to [DPF-certified](https://www.dataprivacyframework.gov/s/participant-search) companies, or with SCCs + a transfer impact assessment. EU hosting is the simplest choice, not a legal must.
- "The website that repositioned … $2M+ projects": horizontal scroll, parallax and heavy motion for a high-end portfolio.
- "Claude: Top 5 Tips for Productivity" and body text sizes (the video says min 12px and body 17–18px; Connectric uses 16): taste-level. WCAG sets no minimum font size, only [resize to 200%](https://www.w3.org/WAI/WCAG22/Understanding/resize-text) (1.4.4).
- Off-topic, nothing to flag: career, comedy, enterprise-agent, presentation and consumer-AI videos.

## E. Suggested research order
Items marked ✅ above only need a guide edit, not research.
1. A7 (cookie banner: one DevTools check) and A2 (only Google review-display terms left). A1 (design skills: a branch test). These can break launch rules.
2. Guide edits, now sourced: A8, A11, A13, A14, A15, A17, A18, A19, A5, A6, and C (Fable 5.2, Claude Design date).
3. A4: one Opus-only vs `opusplan` PR to measure the cache cost. A12: fix the 50%/120k wording.
4. A3 (hero) with one Lighthouse test on the preview. It's rated MEDIUM–HIGH but sits here because it needs the preview built first.
5. A9 (read Art. 50 on EUR-Lex), A10 (OWASP LLM list), A16 (ask the client), A20 (Pages CMS media path).
6. Everything else when the guide is next edited.

## F. Still to do
- ✅ Done 2026-11-27: added 14 📚 Docs rows. Ten are Verified: Claude Code model config & caching, memory, skills, Code Mode; Anthropic prompting and long-running harness; Astro images; Google spam policies; Google Maps UGC policy; WCAG motion & hover. The MCP tool search row is Partly verified. Three are Search-checked: EU AI Act Art. 50, Claude Design, Cloudflare Web Analytics. Before those three can move to Verified, read the AI Act text on EUR-Lex, open the Claude Design Help Center article, and check the site's cookies in DevTools.
- ✅ Done 2026-11-27: the Docs cookie row now has the Cloudflare Web Analytics quote and a pointer to the joint guidance (May 2025) in the US-transfer row. Its Status stays Partly verified until the DevTools check.
- Apart from the Docs rows above, nothing in Notion was changed. All 195 video rows are still Status = New, and no guide edits were made from this review. Decide per item whether to edit the guide, then set the videos to Filed with one changelog line.
