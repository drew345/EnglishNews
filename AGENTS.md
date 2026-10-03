# English News — agent context

Last updated: 2026-09-30

September 27: Andrew approved the NewsIntro v4 opening for both daily editions.
The shared Video Lab renderer calls Projects/NewsIntro for source dates from
20260927. Keep that sibling and its .venv installed. This project's media worker
carries chapter_title_en/ko from staged source stories and fingerprints the
external intro code/configuration. Video QA uses video-timeline.json for the
measured lesson onset, not a fixed one-second offset. Review intro-card frames
and lesson-start-frame.png, then upload the ordinary final lesson MP4. Offline
integration passed; the next incoming run is live validation. Daily job,
browser reservation and final Publish rules below remain authoritative.

September 28: Andrew prioritizes one-shot generation over exact scrolling
position. Aim for spoken text around 40% down the screen, but do not introduce
per-run manual timing adjustment or a render/check/remake cycle for cosmetic
position differences. Keep current scroll settings for the next incoming run;
ordinary technical/content QA still applies. Any later automatic alignment
improvement should calculate timing before the normal single final render.

## Purpose and boundaries

EnglishNews owns the **Learn English** edition for Korean speakers learning English: independent vocabulary, contextual explanations, deterministic speech repetitions and audience settings. The accepted implementation runs from Projects/EnglishNews on main with a verified local .venv and stable shared speech and renderer dependencies. The September 21/22 videos were accepted; no old media should be rebuilt.

Use **Learn English** (legacy key `english`) and **Learn Korean** (English speakers
learning Korean; legacy key `korean`) in progress updates and handoffs. Use
**Shared news** for common story selection. The naming convention is maintained
in sibling `korean-news/docs/daily-news-workflow.md`; repository names, saved keys,
paths and channel branding stay unchanged. State the edition explicitly, such as
“Learn English media is ready” or “Learn Korean is ready for your Publish click.”

## Single daily uploader — approved September 27

One permanent **Daily News Uploads** chat in korean-news now owns Learn English
preparation and both YouTube uploads. It prepares and checks Learn English media first,
then uploads Learn Korean, waits for Andrew's Publish and comment handoff, and uploads
Learn English only after Andrew explicitly says **Next video**. Both editions use the
same owned in-app browser tab. The desktop Korean News icon remains the entry
point. For the first live run, opening the permanent chat once before the icon is
a recommended reliability precaution, not a prerequisite for Learn Korean generation
or a requirement to watch continuously. It helps load the chat but does not
guarantee wake. Learn English preparation and uploads depend on that chat actually
starting; say Resume there if it remains idle.

The sole coordination procedure is sibling `korean-news/docs/daily-news-workflow.md`.
Its paired state and exact edition jobs preserve the current source, stage,
prepared media, video IDs and explicit Learn English gate across interruptions. Reload
the exact pair before acting on historical chat requests. The two former upload
chats are retired from daily routing. Never replay a published run, clear a draft
ID, or use an old dashboard-only request to abandon the active upload.

Andrew alone clicks Publish and posts comments. Select Public, leave Instant
Premiere off, retain the open wizard through Visibility, verify Publish once,
record ready_to_publish and immediately end the turn with the browser reserved.
On Published, verify that same video, perform the bounded comments handoff,
release the browser, then provide one comment: English for Learn Korean,
Korean for Learn English. After the Learn Korean comment handoff, wait for Next video;
browser release alone never authorizes Learn English. On Published, Andrew authorizes
liking the exact video once if it is not already liked, then opening comments.
Never toggle an already-liked video off; skip and report an ambiguous Like state.

Use the shared CLI reservation and one-submission guard for all YouTube work.
Use one supported CUA file chooser sequence and the registered owned tab; never
assume tab 1, use another chat's tab, or open Explorer. Keep correct saved fields.
Do not close the wizard to set Korean title/description language. If that separate
control is absent, record it pending; Published still goes directly to Like and
comments. Correct the separate field only on a later explicit request using
development/youtube-upload.md's bounded procedure. Actual Korean text, English video language
and other approved settings remain required before Publish. Google Account
settings are outside this procedure. A background Publish check does not prove
the visible tab was handed off; follow the shared runbook's visibility check.

Andrew wants the working browser tab selected while following the uploader,
and all other browser tabs in that uploader chat closed. Keep one owned tab,
show/select it before page work and handoff, and restore it after any popup.
For a new upload starting from a completed public watch page, first navigate
the same tab directly to Studio under the shared startup procedure, then
show/select it. Never switch channels on that old watch page: it can reload
and autoplay yesterday's video. Preserve unfinished wizards and saved drafts.
Use only supported in-app browser controls for this routine selection/cleanup.
Never start desktop Computer Use, enumerate windows, inspect the desktop tabstrip
or activate Codex to prove visibility, including when Andrew is using another app.
If browser controls cannot verify selection, preserve the wizard, identify the
owned tab in the handoff and end promptly; do not delay Publish for desktop checks.
Do not switch him away from unrelated chats/apps or close their tabs. Use the
shared upload-inputs command for exact verified paths and UTF-8 text. Fill title
and description directly; no file picker or clipboard is needed for text.
Intercept the chooser before any MP4/thumbnail button activation; never press
the button without a live listener, wait before pressing it, or mix browser
connections. Thumbnail capture and setFiles belong in one call. If a native
picker is positively evidenced, cancel only that identified blocking dialog
through the shared bounded recovery; this is the sole native-recovery exception.
A chooser timeout alone never authorizes desktop inspection or computer takeover.

The two five-minute recovery schedules stay paused. No recurring agent polling,
unrequested model changes, old media rebuilds or worktree retirement is part of this repair.
On September 30, Andrew selected GPT-6.1 Sol / Medium for Daily News Uploads,
replacing GPT-6 Sol / High. Keep GPT-6.1 Sol / Medium for subsequent daily runs
until he requests another change; do not change models automatically.
September 29's ASUS paired run completed through both publications and comment
handoffs, confirmed by Andrew and the saved jobs. The causes of earlier channel
and output-folder-focus incidents remain unproven. Main adoption was completed
September 23.

**Published is also an in-progress steering command.** If Andrew says it while
an upload turn is still active, stop remaining upload/settings checks and verify
the exact saved video immediately, even if ready_to_publish was not recorded.
Do not require the assistant's final message or another confirmation. Preserve
the video ID and move to the authorized Like/comments handoff after verification;
never restart the upload. Still end the normal upload turn promptly at Publish.

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
- Andrew wants the agent to handle the technical setup and explain it plainly; do not require him to learn or manually perform Git worktree setup. On 2026-09-13 he authorized the isolated development setup; on September 23 he authorized adoption into main. Worktrees for EnglishNews, korean-news and KoreanLessonVideoLab now live under `C:/AI/Codex/Worktrees/english-news/`, each on `codex/english-news-prototype` with a separate `.venv`. Keep these until the next incoming end-to-end validation, then retire them after preserving needed ignored artifacts. Supported runtime paths are under Projects, not Worktrees. Supported setup instructions and dependency locks live in Projects/EnglishNews/development.
- The existing desktop icon and full Korean run-through-upload workflow must be preserved. Use the development-only `EnglishNews/development/start-api.ps1` (port 8010); do not run the production-style desktop launcher/supervisor from a worktree because it starts cleanup and publication handoff. Do not start development workers for routine daily jobs.
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

## Historical research

Past TTS evaluations, English/Korean rendering-boundary research, and shared
capability extraction history are preserved together at
`C:\GoogleDrive\My Drive\AIDrive\z.retiredProjects\2026\Reference\LearningSystemsHistory\START-HERE.md`.
Consult that index when revisiting those decisions. The three source projects
are retired reference collections; their old plans and provider choices are
historical. Keep new work and memory in the active repository that owns it.
