# English News — agent context

Last updated: 2026-09-20

## Purpose and boundaries

English News is a companion prototype for Korean-native speakers practicing English through the same news stories. A one-story written/audio/video sample is implemented in the isolated development worktrees; this main folder keeps the planning/handoff record. Continue in `C:/AI/Codex/Worktrees/english-news/EnglishNews` and read its current SESSION_LOG.md. Daily integration has not started.

Read this file and SESSION_LOG.md first when resuming. FEASIBILITY.md holds the detailed code inventory, architecture, risks and phased plan; do not duplicate it into additional plan files.

## Current direction — 2026-09-20

Andrew now wants independent English vocabulary selection from actual English lesson words/phrases, using English frequency data, with a soft 8–12 items per story and familiar-loanword exclusions. The same three stories share facts but may use independently natural wording. This supersedes earlier deferrals of independent selection; implementation has not started. Lasting English-specific behavior belongs in EnglishNews, with one maintained implementation for shared media machinery and no permanent dependency on experimental worktrees/branches. Continue in the existing development checkout; its AGENTS.md, FEASIBILITY.md and SESSION_LOG.md hold the detailed decisions, proposed stages and retirement criteria. Initial cutoff 3,500 remains a recommendation, not a confirmed setting.

## Settled first-cut requirements

- Produce the same output types as Korean News: written lessons, speech scripts, audio, video and publication sidecars.
- Headline/body sentences: Korean once, then English twice, with vocabulary in the appropriate body-unit position.
- Exact vocabulary sequence: English word/gloss twice → Korean word → short English explanation → English word/gloss twice.
- Example: household → household → 가구 → A group of people who live together. → household → household.
- The earlier five-part vocabulary sequence was an assistant error and is superseded. The original code repeats its Korean target word twice at each end; preserve that pattern with English as target.
- Reuse selected vocabulary initially; English equivalents may be gloss phrases. Add a distinct short English explanation without overwriting the Korean definition.
- English full review; separate YouTube channel with Korean titles/descriptions. Actual channel identity, series branding and speech speeds/voice remain open.
- Independent English vocabulary selection rules and study tips come later.

## Development approach

- Always use the next incoming Korean News run for each new English sample or revision. Andrew explicitly said not to remake old videos (2026-09-14). Code changes and offline checks may proceed while waiting; do not synthesize or render an earlier run unless he specifically asks. Old frozen artifacts remain regression evidence only.
- Spoken section labels are Korean: `헤드라인 N`, `어휘` before each nonempty vocabulary section, and `전체 요약` before the English full-story reading. Written vocabulary uses a single logical line `- English gloss: Korean word: English explanation`; match Korean lesson block spacing and use no em-dash separators.

- Preserve the daily Korean News workflow. Recommended integration is a versioned structured lesson export feeding an independent English worker and audience-configurable Video Lab.
- Recommended first explanation implementation: a batched English-side enrichment request. Combining it into the original shared vocabulary call is possible but deferred to protect the existing prompt and other consumers.
- Before implementation, inspect real output on ASUS and verify the current repositories/dependencies. LG Gram 14 had no Korean News output/runs directory during the study.
- Use development branches in separate Git worktrees and separate virtual environments when edits begin. Existing production folders and shortcuts stay on stable main. These are development checkouts of the same repositories, not new independent copies of Korean News or Korean core.
- Andrew wants the agent to handle the technical setup and explain it plainly; do not require him to learn or manually perform Git worktree setup. On 2026-09-13 he authorized the isolated development setup. Worktrees for EnglishNews, korean-news and KoreanLessonVideoLab now live under `C:/AI/Codex/Worktrees/english-news/`, each on `codex/english-news-prototype` with a separate `.venv`. Continue implementation there. Setup instructions and dependency locks live in that EnglishNews worktree's `development/README.md` and directory.
- The existing desktop icon and full Korean run-through-upload workflow must be preserved. Use the development-only `EnglishNews/development/start-api.ps1` (port 8010); do not run the production-style desktop launcher/supervisor from a worktree because it starts cleanup and publication handoff. No development workers are running after setup.
- Create a core worktree only if shared-core edits are necessary; prefer leaving it unchanged for the prototype. Shared-core changes require regression checks in both korean-news and kor-bilingual-gen.
- Separate development outputs, state and ports; prevent development cleanup/publication from touching production. Account for sibling-path discovery in the workflow supervisor.
- Use frozen content to compare Korean scripts/written output and render metadata, then complete listening/video review before adoption. Keep changes small and reversible.

## Related repositories

Resolve siblings relative to the local Projects directory: korean-news (source preparation/audio/workflow), korean-learning-core (shared Korean rules/vocabulary), KoreanLessonVideoLab (renderer), kor-bilingual-gen (other core consumer), loanwords (upstream reviewed list data). Read each repository's current instructions before editing it. English rules do not belong in shared Korean difficulty lists.

## Portability status

English YouTube channel created 2026-09-14: `뉴스로 배우는 영어`,
`@SteadyLanternEnglish`, ID `UCPvS_o6ypGR8-aA0P2pgtdA`. Same Steady Lantern
account as the existing Korean channel. Channel/icon records live in the
development EnglishNews `assets/channel/README.md`. Automatic publication
remains disabled.

Repository: https://github.com/drew345/EnglishNews.git, branch main. Andrew authorized repository initialization/publication and routine-sync enrollment on 2026-09-13. CodexSync/github-sync.json is the authoritative membership list; MindHub keeps a pointer only. Verify published repository and coordination state when resuming. The local handoff ZIP is ignored by Git; the Markdown source files are the portable record.

The user plans End sync on LG Gram 14 and Start sync on ASUS separately. This memory-save request did not run either operation. Ordinary resumption or a device mention must not trigger sync automatically.
