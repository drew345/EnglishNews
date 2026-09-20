# English News — agent context

Last updated: 2026-09-20

## Purpose and boundaries

English News is a companion for Korean-native speakers practicing English through the same news stories. An explicit completed Korean run now produces all three English stories, speech/audio, video and Korean publication sidecars in isolated development worktrees. Routine command and lighter-model handoff instructions are at the top of development/README.md. Automatic daily triggering and upload are not enabled.

Read this file and SESSION_LOG.md first when resuming. FEASIBILITY.md holds the detailed code inventory, architecture, risks and phased plan; do not duplicate it into additional plan files.

## Current direction — 2026-09-20

- Andrew now wants independent vocabulary selection from the actual English lesson, including useful phrases, with a soft target of 8–12 items per story. Use English frequency data; the proposed Korean-rank mapping is superseded. `wordfreq` and an initial 3,500 cutoff are recommendations, not finalized implementation choices.
- Carry over the Korean methodology's names, cities/geography, organizations, grammar, loanwords, normalization, overrides, repetition and contextual-definition stages with English-specific equivalents. Andrew explicitly wants familiar English loanwords used in Korean excluded even outside the frequency cutoff. The proposed meaning-aware borrowing reference must not blindly invert the existing mixed-purpose Korean blocklist.
- The same three selected stories feed both audiences. Andrew permits independent wording with the same facts; preserve sentence-pair alignment within each lesson. Proposed stages and branching are in FEASIBILITY.md.
- Lasting English-specific behavior after the content split belongs in EnglishNews. Avoid copied implementations requiring fixes in two places; genuinely shared speech/video machinery should have one maintained implementation and explicit interfaces. Do not accumulate worktrees or branches as permanent runtime dependencies. Reuse existing development worktrees and plan their retirement; no new repository is required merely for this phase.
- This is design discussion, not completed implementation or merge authorization. Preserve the Korean desktop workflow. The prototype below still describes the running implementation; older deferrals of independent English vocabulary selection are superseded as planning constraints.

## Settled first-cut requirements

- Produce the same output types as Korean News: written lessons, speech scripts, audio, video and publication sidecars.
- Headline/body sentences: Korean once, then English twice, with vocabulary in the appropriate body-unit position.
- Exact vocabulary sequence: English word/gloss twice → Korean word → short English explanation → English word/gloss twice.
- Example: household → household → 가구 → A group of people who live together. → household → household.
- The earlier five-part vocabulary sequence was an assistant error and is superseded. The original code repeats its Korean target word twice at each end; preserve that pattern with English as target.
- Reuse selected vocabulary initially; English equivalents may be gloss phrases. Add a distinct short English explanation without overwriting the Korean definition.
- English full review; separate YouTube channel with Korean titles/descriptions. Andrew confirmed Alloy, English 0.88 and Korean sentences 1.07 for the initial sample; vocabulary blocks and review use 0.88. Channel identity and final branding remain open.
- English repetition is assembled from individual audio clips: sentence twice; vocabulary gloss twice, Korean word, English explanation, gloss twice. The first model-directed repetition sample omitted a final word, so v2 makes the repetition count deterministic. This does not change Korean News speech behavior.
- Independent English vocabulary selection rules and study tips come later.
- Vocabulary filters implemented: reject English glosses containing whole-word “name” (case-insensitive), and whole-gloss matches against the local country-name/alias list. Applied before explanations and speech; vocabulary-filter.json audits removals. No extra LLM calls. Deferred next: generic place descriptions, occurrence in the matching English sentence, and grammatical-variation matching. Full separate English selection/ranking remains deferred; preserve Korean production vocabulary rules.
- Vocabulary effectiveness checks must be offline/text-only: no audio or video generation. Andrew explicitly reinforced this on 2026-09-14.
- Country filtering also checks the Korean vocabulary word against a fixed Korean country-name/alias list (e.g. 태국, 한국, 호주). This catches generic English glosses attached to country names without implementing the deferred generic-description filter. Exact word only; no substring/particle matching.
- Routine builds use `development/make-english-news.ps1 -SourceRun <new Korean run ID>` in this worktree. Read the runbook first. Require ready_for_review plus audio/video QA and an upload-package.json; show the result for Andrew's review. Never upload automatically. Valid cached speech and completed renders support resuming an interrupted current run.

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
account as the existing Korean channel. See `assets/channel/README.md` for
identity and icon status. Creation does not enable automatic publication.

Repository: https://github.com/drew345/EnglishNews.git, branch main. Andrew authorized repository initialization/publication and routine-sync enrollment on 2026-09-13. CodexSync/github-sync.json is the authoritative membership list; MindHub keeps a pointer only. Verify published repository and coordination state when resuming. The local handoff ZIP is ignored by Git; the Markdown source files are the portable record.

The user plans End sync on LG Gram 14 and Start sync on ASUS separately. This memory-save request did not run either operation. Ordinary resumption or a device mention must not trigger sync automatically.
