# English News — agent context

Last updated: 2026-09-13

## Purpose and boundaries

English News is a planned companion to Korean News for Korean-native speakers practicing English through the same news stories. This folder currently contains planning and memory only; implementation has not started.

Read this file and SESSION_LOG.md first when resuming. FEASIBILITY.md holds the detailed code inventory, architecture, risks and phased plan; do not duplicate it into additional plan files.

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

- Preserve the daily Korean News workflow. Recommended integration is a versioned structured lesson export feeding an independent English worker and audience-configurable Video Lab.
- Recommended first explanation implementation: a batched English-side enrichment request. Combining it into the original shared vocabulary call is possible but deferred to protect the existing prompt and other consumers.
- Before implementation, inspect real output on ASUS and verify the current repositories/dependencies. LG Gram 14 had no Korean News output/runs directory during the study.
- Use development branches in separate Git worktrees and separate virtual environments when edits begin. Existing production folders and shortcuts stay on stable main. These are development checkouts of the same repositories, not new independent copies of Korean News or Korean core.
- Andrew wants the agent to handle the technical setup and explain it plainly; do not require him to learn or manually perform Git worktree setup. Authorized preparation includes initializing/publishing this repository and registering it for sync; experimental implementation/worktrees have not started.
- Create a core worktree only if shared-core edits are necessary; prefer leaving it unchanged for the prototype. Shared-core changes require regression checks in both korean-news and kor-bilingual-gen.
- Separate development outputs, state and ports; prevent development cleanup/publication from touching production. Account for sibling-path discovery in the workflow supervisor.
- Use frozen content to compare Korean scripts/written output and render metadata, then complete listening/video review before adoption. Keep changes small and reversible.

## Related repositories

Resolve siblings relative to the local Projects directory: korean-news (source preparation/audio/workflow), korean-learning-core (shared Korean rules/vocabulary), KoreanLessonVideoLab (renderer), kor-bilingual-gen (other core consumer), loanwords (upstream reviewed list data). Read each repository's current instructions before editing it. English rules do not belong in shared Korean difficulty lists.

## Portability status

Repository: https://github.com/drew345/EnglishNews.git, branch main. Andrew authorized repository initialization/publication and routine-sync enrollment on 2026-09-13. CodexSync/github-sync.json is the authoritative membership list; MindHub keeps a pointer only. Verify published repository and coordination state when resuming. The local handoff ZIP is ignored by Git; the Markdown source files are the portable record.

The user plans End sync on LG Gram 14 and Start sync on ASUS separately. This memory-save request did not run either operation. Ordinary resumption or a device mention must not trigger sync automatically.
