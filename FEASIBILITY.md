# English News feasibility study

Date: 2026-09-13. Scope: preliminary code and dependency assessment; no production implementation.

**Verdict: feasible, with targeted refactoring.** The existing pipeline already produces aligned English/Korean sentences and vocabulary definitions. Those can feed a second lesson without another news-selection, summarization, or vocabulary-selection pass. The updated first cut adds short English vocabulary explanations through an English-side enrichment call. Audio and video must be produced separately because the spoken content, duration, timing, and audience change.

Confirmed preferences: preserve all current output types, including video; reverse existing vocabulary first, adding a short English explanation in place of the Korean explanation; use a separate YouTube channel with Korean titles and descriptions. Independent English vocabulary selection rules and study tips are a later phase.

## What exists today

1. Korean News selects and freezes article sources, then generates 4–5 aligned sentence pairs, including a headline. The prompt targets intermediate Korean learners and approximately 80–100 English words.
2. Sentence 1 becomes the headline. The Korean core analyzes body Korean, selects difficult words, fetches bilingual definitions, and groups vocabulary with sentences. Definition counts are tracked across the run.
3. Korean News prepares written text and speech units. A duration preflight may remove the last story before synthesis.
4. The selected TTS provider produces audio chunks, per-story timing, a combined MP3, written lessons, and run metadata.
5. A desktop workflow exporter generates/caches story illustrations and stages completed runs into Video Lab.
6. Video Lab creates a scrolling lesson video with story cards, thumbnail, title/description sidecars, chapters, render status, and QA frames. The workflow opens an output folder and a prepared Codex upload task; publication remains supervised.

The strongest existing boundary is between structured lesson preparation and presentation. The main missing piece is a durable structured lesson export: prepared sentence/vocabulary objects currently remain in memory, while run.json stores artifact paths, titles, settings, and timings rather than the complete lesson structure.

## Dependency inventory

| Component | Actual relationship | Implication for English News |
|---|---|---|
| korean-news | Owns sources, bilingual generation, speech scripts/audio, run orchestration, image generation and staging | Keep as the initial content producer; add a structured export |
| korean-learning-core | Direct Python dependency; Korean analyzer, frequency data, ignores, loanwords, definitions, block assembly and written rendering | Reuse its output for inversion; do not put English difficulty rules into Korean lists |
| KoreanLessonVideoLab | Sibling project launched by the desktop supervisor; consumes staged files and creates video/publication artifacts | Reuse renderer with audience configuration and separate input/output namespaces |
| kor-bilingual-gen | Another consumer of the Korean core; confirmed shared imports | No direct News runtime dependency found; affected if shared interfaces/defaults change |
| loanwords | Maintains reviewed lists promoted into the Korean core | Indirect data dependency; its English-native assumptions should not govern future English selection |
| Google Drive Voice Inbox | A local cleanup watcher still references this folder | Legacy cleanup only; current News does not export new audio there |
| Codex and YouTube | Prepared upload-task link plus supervised browser upload workflow | Add an explicit English-series destination and Korean metadata; never inherit the Korean channel by default |
| OpenAI; optional Azure | Existing generation and audio integrations; default code path is OpenAI Speech | Reuse transport with a new audience-specific speech profile; Azure/Audio 1.5 need their own adaptations if offered |
| Pillow, ffmpeg, Windows fonts | Local image/video rendering dependencies | Reusable; rendering capacity and Korean-capable branding fonts need checking |
| MindHub / Unification notes | Referenced as planning/secret-management context in project documentation | No generation-time integration found in inspected News/Video Lab code |

No direct runtime ties to PlaylistPin, VoiceAdventure projects, or other sibling applications were found in the inspected source and workflow scripts. This inventory is based on local code and documentation, not an audit of external scheduler/account configuration.

The News requirements declare a GitHub dependency on Korean core without a pinned revision. Before cross-project refactoring, record the installed core version/revision and pin the tested dependency so machines use the same behavior.

## Proposed first lesson format

| Element | Current spoken format | Proposed English-learning format |
|---|---|---|
| Headline | English once → Korean twice | Korean once → English twice |
| Body unit | English once → vocabulary → Korean twice | Korean once → inverted vocabulary → English twice |
| Vocabulary | Inspected code: Korean word twice → English definition → Korean definition → Korean word twice | English word/gloss twice → Korean word → short English explanation → English word/gloss twice |
| Full review | Korean headline and Korean body | English headline and English body |
| Written lesson | English first; vocab; Korean; Korean review | Korean first; inverted vocab; English; English review |
| Labels and publication copy | English learner-facing labels/copy | Korean learner-facing labels/copy |

The vocabulary sequence above is the user's final correction, confirmed against the original Korean renderer: repeat the target word twice at both ends. Example: “household → household → 가구 → A group of people who live together. → household → household.” This supersedes the earlier five-part sequence in the conversation. Written lessons should retain the existing convention of showing sentences once instead of duplicating every audio repetition. Hanja can remain in source data; it need not be displayed in the English lesson.

### Short English explanations: included in the first cut

Keep `en_def` as the existing short English equivalent/gloss and preserve `ko_def` for Korean News. Add a distinct `en_explanation` field to the English lesson data: one short, simple-English phrase or sentence explaining the selected meaning, ideally around 6–12 words where that suffices. Use both aligned sentences and the existing definitions as context; avoid circular explanations, unnecessarily difficult vocabulary, and unsupported facts.

The recommended first implementation makes one batched enrichment request for the selected vocabulary in a small run, splitting only if necessary. Match responses by stable entry IDs, not word spelling alone, so different senses in different stories stay separate. Cache validated explanations by source context and prompt/model identity. Missing or malformed explanations should produce a retryable English job issue without failing Korean News or silently reverting to Korean descriptions.

It is technically possible to request this field in the original vocabulary call. That would save an ordinary enrichment request but change the shared prompt, parser, VocabDef/VocabBlock models, block copying, and retry handling. Adding a field to an LLM request can also change its existing answers. Given the priority of protecting Korean News, defer this optimization: English-side enrichment isolates the new behavior and supports historical bundles. If combined generation is later adopted, make it opt-in, preserve the original prompt and defaults when disabled, and ensure retries retain the new field.

**Vocabulary inversion is mechanically valid but pedagogically approximate.** Entries contain `word`, `en_def`, `ko_def`, `slow_form`, and `hanja`. They do not contain a verified English target word aligned to a span of the English sentence. The test fixture for 한복, for example, uses “traditional Korean clothing” as its English definition. Proper-name definitions may be phrases such as “a politician's name.” Reversing existing entries therefore teaches some gloss phrases, and does not guarantee that the English being practiced occurs in the sentence.

For this first pass, retain the selected entries and their provenance; flag awkward/missing glosses for review rather than silently selecting new vocabulary. Later, select English words, phrases and collocations from the English text with English-specific difficulty rules and Korean explanations. The Korean-oriented simplification prompt can remain for the experiment, but it is not evidence that the English is calibrated to a particular learner level.

## Recommended architecture

Keep EnglishNews as a separate application/configuration boundary. Share lesson data and reusable media machinery, rather than copying the entire Korean News repository or importing its API application as a library.

**Common content preparation → immutable lesson bundle → two independent audience jobs → shared Video Lab with audience profiles.**

Export a versioned bundle after vocabulary preparation and the final story-lineup decision, before audio synthesis. Include source run ID and source references, retained story order, actual generated headlines, English/Korean sentence pairs, per-sentence vocabulary associations and definitions, chapter titles, and generation provenance. Preserve stable language field names: do not make `natural_ko` contain English just to fool the old renderer. Compute the English full review from the existing English sentences.

The export needs a content hash/schema version and atomic ready marker. The producer owns its bundle; English News owns its job status. A worker should consume the committed bundle, render the English lesson, synthesize audio, calculate new timings, and stage its own video inputs. Source run ID plus audience/profile version/content hash should define a repeatable job identity.

This allows both audience jobs to progress independently after common preparation. Failure of English audio/rendering should not fail Korean News. A restart should resume an incomplete English job without regenerating the source lesson or duplicating an upload.

Use separate state for output files, retries, voice rotation, video render status and publication receipts. The current exporter mutates the source run.json; a second consumer should not also perform unsynchronized read/modify/write updates there. Atomic file replacement alone does not prevent lost updates between writers.

Share each conceptual story image by explicit source asset identity. The current image prompt digest includes written context, so calling image generation again on inverted text may create a different cache identity. An image handoff should copy/reference the original cached image instead. Because images currently become available after Korean audio completes, either let English video staging wait for that asset, or later extract image generation into a common asset job. English text/audio need not wait. If the source image never becomes available, record an actionable staging failure and allow retry.

Start with one English worker and bounded media concurrency. Concurrent operation does not require running two ffmpeg encodes at once. A shared render queue can protect local responsiveness. English News does not need a second copy of the headline-selection UI or another server on port 8000 for the first pass.

## Required refactoring and concrete risks

| Area | Evidence and issue | Recommended change |
|---|---|---|
| Run orchestration | `src/api_app.py` is 1,516 lines; `_build_run` spans about 580 lines and combines preparation, preflight, synthesis, failure manifests and assembly | Extract preparation and bundle serialization first, keeping the current Korean output behavior stable |
| Speech presentation | `src/vocab_pass.py:424` explicitly emits English first, Korean repetitions and a Korean review | Add audience-driven presentation planning with native/target roles |
| Speech profile | `src/tts_profiles.py` explicitly requests a Korean learning script; English is 1.07 and learning units are 0.88 | Create a distinct English-learning profile, instructions and resume identity; choose speeds by role |
| Alternate audio providers | Audio 1.5 instructions and Azure SSML also embed Korean-learning assumptions | Validate OpenAI Speech first; do not expose unsupported inverted provider modes |
| Shared written rendering | Korean core's written renderer hardcodes English-first and Korean full review | Add an English app adapter initially, or a backward-compatible optional profile; preserve other consumers' defaults |
| Video headline parsing | `extract_lesson_headlines` treats first/second written lines as English/Korean; story cards prefer this parsed result | Read explicit language fields from the new bundle/manifest; retain legacy parsing only for old runs |
| Video identity | Filenames, titles, thumbnail wording/master, description copy and upload channel are hardcoded | Introduce a series/audience profile; output under distinct series namespaces |
| Duration and timing | Existing story timestamps and duration heuristic describe Korean audio | Measure English audio anew; recalculate chapter/card timing; assess the estimator with an English sample |
| Retention and recovery | Existing weekly cleanup understands Korean News and Video Lab's current directory/state layout | Extend recognition and ownership for English jobs; do not run two independent cleanups over shared assets |
| Compatibility code | `vocab_pass.py` retains many Korean helper definitions alongside shared-core forwarding | Audit callers before removing apparently redundant helpers; cleanup can follow the first working branch |

The 1,820-line headline module is large, but its selection logic does not need to change for inversion. A broad rewrite there would add risk without helping this feature. Likewise, a new universal “language-learning core” package is not a prerequisite. Extract small provider-neutral media interfaces only where real reuse warrants them, avoiding long-term imports through sibling projects' generic `src` modules.

Speech speed should be trialed, not blindly reversed. Native Korean can be natural paced; English repetitions should be comfortably understandable. Both English repetitions can use the same learning speed initially, matching today's default Speech behavior. A slow-then-natural pattern is a later choice. Slashed Korean syllable pacing has no useful direct English equivalent.

For parallel editions of the same lesson, preserve the final Korean story lineup. English duration preflight can warn on excess length instead of silently dropping different stories; independent lineup policy can be added later if desired.

## Existing lessons versus future runs

Future runs can supply the structured bundle directly. Historical runs would need a separate importer from combined/per-story written lessons plus run metadata; vocabulary punctuation and older formats make that less reliable. Prefer written files over trying to reconstruct content from MP3 or repeated TTS scripts. Validate sentence/vocabulary associations and preserve original IDs before generating new media.

This local checkout has no `output/runs` directory. Historical format coverage and a real backfill cannot be verified here yet. This is a validation gap, not a blocker to designing the future handoff. Older manifests with absolute paths also need rebasing when moved between machines.

## Implementation sequence and effort

These are rough engineering estimates from code inspection, not a delivery commitment. They assume one developer, the current default Speech provider, and no redesign of the visual layout.

1. **Bundle boundary and regression baseline: 1–2 days.** Serialize final prepared content, preserve existing Korean artifacts, test complete/partial bundles and story lineup.
2. **Standalone inverted sample: 1–2 days.** Produce written text and new audio from one frozen lesson; review sentence order, vocabulary phrases, pauses and English full review.
3. **Video and separate-series configuration: 1–2 days.** Correct headline parsing, branding, thumbnail/fonts, timing and Korean metadata; produce MP4 and all sidecars.
4. **Parallel worker and operational hardening: 2–4 days.** Wire ready-bundle consumption, retries, restart recovery, namespace isolation, image reuse and retention; validate paired runs.

Planning range: **about 5–10 focused working days** for an operational first version including video, with listening review and channel setup potentially extending calendar time. A one-story prototype should be possible earlier. Historical migration and independent English vocabulary/study-tip generation are additional scope.

The revised scope adds a batched English-explanation call, but no new story generation or vocabulary selection. The other incremental work is new TTS, another video encode, and additional storage. Reusing illustrations avoids a second image-generation charge. Do not assume total cost or duration exactly doubles: the English edition has a different spoken length and can reuse source preparation. Measure one paired run before estimating daily usage; no live pricing or account limits were checked in this study. The explanation enrichment is a modest addition to the first-cut scope; the 5–10-day range remains preliminary rather than a firm estimate.

## Protecting the working Korean projects

Use development branches in separate Git worktrees for repositories that actually need edits. Leave the existing Korean News and Video Lab folders on their current stable main branches so daily shortcuts continue to use the known workflow. Do not switch the production folders onto feature branches. Korean core can remain untouched for the initial English-side explanation prototype; create a separate core worktree only if shared changes become necessary. No branch or worktree was created during this study.

Before implementation:

1. Record the starting commits and dependency identities. Inspected main heads are Korean News `e22e38e` and Korean core `1d3e870`. Korean News has pre-existing uncommitted changes in AGENTS.md and SESSION_LOG.md; preserve these separately from implementation. A branch or tag protects committed files, not uncommitted notes or ignored runtime artifacts. Checkpoint the exact current state without including secrets.
2. Use separate development virtual environments and explicit development project paths. Do not install an experimental core editably into the production environment. The supervisor normally discovers a sibling Video Lab, so set its development override deliberately. Give development API instances different ports if needed. Disable production upload-task launching and cleanup in the development workflow.
3. Capture representative frozen lesson fixtures with vocabulary, scripts, manifests and expected render metadata. Run the full relevant suites before editing. For deterministic preparation/rendering changes, compare Korean written text and TTS requests exactly; compare timestamps and generated IDs after normalization. Live LLM/audio calls are nondeterministic and require semantic/listening review rather than byte-for-byte comparison.
4. Introduce changes in small, independently reversible commits: bundle export, English enrichment/rendering, Video Lab series configuration, then worker integration. Preserve Korean defaults; a disabled English feature should not change existing prompts, vocabulary selection, spoken text or publication destination. Keep English failures isolated.
5. If Korean core changes, validate its suite plus both consumers, Korean News and kor-bilingual-gen, using the same candidate core revision in isolated environments. Passing News alone does not cover the other consumer.
6. Run one complete paired lesson in isolation, then a normal Korean-only regression run. Check all written/audio/video artifacts and perform full listening/visual review. Merge and enable only after the candidate passes those checks. Pin a compatible set of repository/dependency revisions and keep the prior set available for rollback.

Rollback should restore the previous code and dependency versions without deleting newer lesson artifacts. Keep exported schemas backward-compatible and allow the English worker to be disabled independently. No approach guarantees zero regressions, but worktree/environment separation protects daily operation during development; regression fixtures and staged adoption protect it after integration.

## Validation and next decision

Executed against the existing code:

- Korean News: 34 focused tests for TTS vocabulary layout, summarization contracts, speech profiles and Video Lab export; all passed.
- Korean News: 10 additional OpenAI Speech transport/resume/operational tests; all passed.
- Video Lab: full existing suite of 25 tests; all passed.

**69 tests passed.** These establish a useful baseline; they do not validate an implemented inversion. No live generation, paid API calls, full MP4 render, upload or publication was performed. Production code was not changed. Korean News already had edits to AGENTS.md and SESSION_LOG.md before inspection; those were left intact.

Before release, verify: exact native-once/target-twice ordering; vocabulary attachment and review content; no regression in Korean output; separate profile/cache identity; correct English audio durations and chapters; correct card language labels; correct Korean series metadata; no run/path collisions; independent failure and resume; images surviving until both consumers finish; and an end-to-end full listen/watch.

The most useful next step is inspecting an actual Korean News output bundle on ASUS, then making one frozen lesson with vocabulary into inverted written/audio/video outputs for review. This tests the awkward-gloss issue and English pacing before investing in automatic dual production. Vocabulary cadence is settled above; remaining product decisions include English speed/voice, series name, and actual destination channel ID. None blocks the preliminary architecture. Read AGENTS.md and SESSION_LOG.md for the device handoff and transport gap.

## Source pointers

- [Sentence-pair model and prompt](C:/AI/Codex/Projects/korean-news/src/summarize.py)
- [Run preparation and assembly](C:/AI/Codex/Projects/korean-news/src/api_app.py)
- [Vocabulary bridge and TTS rendering](C:/AI/Codex/Projects/korean-news/src/vocab_pass.py)
- [Speech profiles](C:/AI/Codex/Projects/korean-news/src/tts_profiles.py) and [transport/resume](C:/AI/Codex/Projects/korean-news/src/openai_speech_tts.py)
- [Shared vocabulary definitions](C:/AI/Codex/Projects/korean-learning-core/src/korean_learning_core/vocab/definitions.py) and [written rendering](C:/AI/Codex/Projects/korean-learning-core/src/korean_learning_core/vocab/rendering.py)
- [Local workflow supervisor](C:/AI/Codex/Projects/korean-news/scripts/start_local_workflow.py), [exporter](C:/AI/Codex/Projects/korean-news/scripts/export_video_lab_inputs.py), [image generation](C:/AI/Codex/Projects/korean-news/scripts/generate_video_story_images.py), [cleanup](C:/AI/Codex/Projects/korean-news/scripts/cleanup_local_workflow.py)
- [Video renderer](C:/AI/Codex/Projects/KoreanLessonVideoLab/scripts/make_teleprompter_video.py), [watcher](C:/AI/Codex/Projects/KoreanLessonVideoLab/scripts/watch_korean_news_inputs.py), [thumbnail](C:/AI/Codex/Projects/KoreanLessonVideoLab/scripts/make_youtube_thumbnail.py), [current video policy](C:/AI/Codex/Projects/KoreanLessonVideoLab/PROJECT.md)

