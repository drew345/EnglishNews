# English News — agent context

Last updated: 2026-09-23

## Purpose and boundaries

EnglishNews owns the English edition: independent vocabulary, contextual explanations, deterministic speech repetitions and audience settings. The accepted implementation is being adopted into Projects/EnglishNews on main with stable shared speech and renderer dependencies. The September 21/22 videos were accepted; no old media should be rebuilt.

Andrew authorized main adoption and automatic generation/upload preparation on September 23. The desktop Korean News icon remains the entry point. Two ongoing dedicated Codex tasks consume exact jobs owned by sibling korean-news/docs/daily-news-workflow.md. English starts after the matching Korean render is complete, without waiting for Korean publication. Both tasks select Public, keep Instant Premiere off, and stop at Publish for Andrew. No Explorer folders, unsent prompts, or unattended publication.

Read this file and SESSION_LOG.md first when resuming. FEASIBILITY.md holds the detailed code inventory, architecture, risks and phased plan; do not duplicate it into additional plan files.

NewsHistory: the canonical preparation/media writers archive written lessons and English vocabulary audits via C:/AI/Codex/Projects/NewsHistory. Its AGENTS.md owns storage and retention; no automatic expiry. Monthly review uses combined history, not only this computer’s output folders.

## Current direction — 2026-09-20

- September 22 English run 20260922_english_all_9546311b74 is published at https://www.youtube.com/watch?v=caW7gBNv6Sg. Never duplicate it. New automatic jobs exclude pre-activation source runs and use only the next incoming Korean run.
- Routine text, definition and media checks are performed by the assistant. Ask only for material problems or new choices. Record preparation, media and YouTube draft IDs in the durable job before proceeding. Follow development/README.md and development/youtube-upload.md from Projects/EnglishNews.

- Andrew now wants independent vocabulary selection from the actual English lesson, including useful phrases, with a soft target of 8–12 items per story. Use English frequency data; the proposed Korean-rank mapping is superseded. The implementation uses wordfreq 3.1.1 top-6,000 surface-token ranks with configurable cutoff 3,500, taking the more common of surface/dictionary-resolved base rank. LemmInflect 0.2.3 dictionary-only round-trip checks resolve inflections; unknown or ambiguous inflected forms are omitted. Only expressions/patterns in phrase-reference.json are eligible, followed by contextual assessment.
- Carry over the Korean methodology's names, cities/geography, organizations, grammar, loanwords, normalization, overrides, repetition and contextual-definition stages with English-specific equivalents. Andrew explicitly wants familiar English loanwords used in Korean excluded even outside the frequency cutoff. The meaning-aware borrowing reference must not blindly invert the existing mixed-purpose Korean blocklist.
- The same three selected stories feed both audiences. Andrew permits independent wording with the same facts; preserve sentence-pair alignment within each lesson. Implemented stages and the later upstream fact-extraction option are in FEASIBILITY.md. The current optional export follows the unchanged bilingual summary and precedes Korean vocabulary; English composition can reword the shared facts independently.
- Lasting English-specific behavior after the content split belongs in EnglishNews. Avoid copied implementations requiring fixes in two places; genuinely shared speech/video machinery should have one maintained implementation and explicit interfaces. Do not accumulate worktrees or branches as permanent runtime dependencies. Reuse existing development worktrees and plan their retirement; no new repository is required merely for this phase.
- September 23 authorization supersedes the earlier worktree-only/main-merge deferral. Keep configurable cutoff 3,500. Adopt the reviewed code with regressions; validate the complete live workflow on the next incoming run before retiring worktrees.

## Settled first-cut requirements

- Produce the same output types as Korean News: written lessons, speech scripts, audio, video and publication sidecars.
- Headline/body sentences: Korean once, then English twice, with vocabulary in the appropriate body-unit position.
- Exact vocabulary sequence: English word/gloss twice → Korean word → short English explanation → English word/gloss twice.
- Example: household → household → 가구 → A group of people who live together. → household → household.
- The earlier five-part vocabulary sequence was an assistant error and is superseded. The original code repeats its Korean target word twice at each end; preserve that pattern with English as target.
- Select words/phrases directly from the English body sentences, with contextual Korean glosses and short English explanations. Historical Korean-gloss reuse is retired from the supported workflow; legacy modules remain for regression evidence.
- English full review; separate YouTube channel with Korean titles/descriptions. Voice Alloy. On September 20 Andrew requested English 2% faster: 0.8976 (0.88 × 1.02) for all English readings. Korean sentences/labels remain 1.07 and Korean vocabulary glosses 0.88, using explicit vocabulary clip speeds. Saved preparation profiles govern media; historical reviews retain their original rates. The channel identity is recorded below; English audience copy is owned by english_news/audience.json.
- English repetition is assembled from individual audio clips: sentence twice; vocabulary gloss twice, Korean word, English explanation, gloss twice. The first model-directed repetition sample omitted a final word, so v2 makes the repetition count deterministic. This does not change Korean News speech behavior.
- Independent English vocabulary selection is implemented; study tips remain deferred.
- English explanation policy v2 uses one dictionary-style phrase, normally 4–8 simple words (shorter allowed), with a software maximum of 10 and narrow circularity checks. Meaningful related-word reuse is allowed. Routine selection includes this guidance in its existing call; explicit `python -m english_news.definitions --prepared-run ...` revisions preserve selected vocabulary and Korean glosses. Andrew approved the shorter definitions and TTS format. The later audience-adjusted selection is output/text-review/20260920_english_text_69271a0759a5; Andrew authorized its current video build, now ready for spot-check at output/runs/20260920_english_all_2cea76ad88. That historical run has since been published; follow the latest session/job records.
- Selection uses spaCy tokenization/grammar/entities, dictionary-backed morphology, a controlled positive phrase reference, common-word and manual gates, then contextual usefulness, familiar same-meaning loanwords and definitions in the same request. Required context/learning-unit/learning-value judgments may veto entries, never override exclusions or write rule files. easy-overrides.json is a separate overlay containing user-approved tourism. The phrase reference excludes basic start over and numeric-maximum up to, preserving other senses. Target Korean adults with substantial existing English vocabulary; keep cutoff 3,500 and judge new learning separately from usefulness. Include overrides bypass frequency only; easy-list, morphology and phrase gates remain enforced. Exclude overrides block matching forms/lemmas. Names/grammar/entity/meaning checks still apply. Deduplicate within a story and allow up to three occurrences of a word/meaning across a run.
- Vocabulary effectiveness checks must be offline/text-only: no audio or video generation. Andrew explicitly reinforced this on 2026-09-14. Review the next incoming run's prepared written lesson before media. Never use old videos to trial a vocabulary revision.
- Routine preparation is `python -m english_news.prepare`; media uses `development/make-english-news.ps1 -PreparedRun ... -StagedRun ... -VideoLab ... -ReviewedText`. Read the runbook for complete commands and source rules. The old `-SourceRun` inversion path is removed. Require ready_for_review plus audio/video QA and upload-package.json before presenting media. Automatic upload preparation is authorized; Andrew alone clicks Publish.

## Development approach

- Always use the next incoming Korean News run for each new English sample or revision. Andrew explicitly said not to remake old videos (2026-09-14). Code changes and offline checks may proceed while waiting; do not synthesize or render an earlier run unless he specifically asks. Old frozen artifacts remain regression evidence only.
- Spoken/written headline labels are English `Headline N`, using the ordinary English speed. `어휘` before nonempty vocabulary sections and `전체 요약` before the full-story reading remain Korean. This September 20 review correction supersedes the all-Korean-label prototype. Written vocabulary uses a single logical line `- English gloss: Korean word: English explanation`; natural wrapping is allowed and video vocabulary must use the same 44px size as body text. English wrapping now matches the Korean renderer's budget to avoid the extra blank strip beside the card.

- Preserve the daily Korean News workflow. Recommended integration is a versioned structured lesson export feeding an independent English worker and audience-configurable Video Lab.
- English selection and contextual explanations share the English-side request. Optional composition has a separate grounding check. No English model request is added to Korean generation.
- September 18/19 outputs supplied offline diagnostics. Andrew approved the September 20 vocabulary and shortened definitions. Current TTS review: output/text-review/20260920_english_text_644487168a57/speech-script.txt, with the requested English speed increase and identical lesson content. Review the exact script before generating audio. Preserve the distinction between tests, model output and human acceptance.
- Use development branches in separate Git worktrees and separate virtual environments when edits begin. Existing production folders and shortcuts stay on stable main. These are development checkouts of the same repositories, not new independent copies of Korean News or Korean core.
- Andrew wants the agent to handle the technical setup and explain it plainly; do not require him to learn or manually perform Git worktree setup. On 2026-09-13 he authorized the isolated development setup; on September 23 he authorized adoption into main. Worktrees for EnglishNews, korean-news and KoreanLessonVideoLab now live under `C:/AI/Codex/Worktrees/english-news/`, each on `codex/english-news-prototype` with a separate `.venv`. Keep these until the next incoming end-to-end validation, then retire them after preserving needed ignored artifacts. Supported runtime paths are under Projects, not Worktrees. Setup instructions and dependency locks live in that EnglishNews worktree's `development/README.md` and directory.
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
