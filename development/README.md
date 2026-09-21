# English News development runbook

Updated 2026-09-21. The implementation plan and ownership/merge sequence are in [FEASIBILITY.md](../FEASIBILITY.md). Work only in the existing development checkouts until review. No production setting, launcher, environment or main branch has been changed.

## Daily supervised procedure

Use this checklist when Andrew says the new Korean run is ready. Read AGENTS.md and the latest SESSION_LOG.md first. September 21 is the verified example; never reuse its IDs for a new day. Andrew wants the same procedure on the next incoming run and explicit instructions that a simpler model can eventually follow; no model change is requested yet.

1. **Identify inputs.** Confirm the new production Korean run is completed and its staged Video Lab images have the same source run ID. Check the session log and existing English run records for prior preparation/upload before starting. If source identity is ambiguous, ask; never mix dates or image runs.
2. **Prepare text.** Run the legacy-written command below while production export remains unavailable. Use the returned preparation ID, not a guessed latest folder. Keep agreed cutoff, voice and speed settings.
3. **Review text once.** Read all three stories, selected terms, Korean meanings, English definitions and selection reports. Confirm source wording is preserved in adapter mode; terms have the intended contextual meaning, phrases are natural and useful, and definitions are short and noncircular. Fewer than eight items is allowed. Stop for a material issue; otherwise record assistant review and proceed without another user checkpoint.
4. **Build media.** Run the media command below with that exact preparation and matching staged input. Resume valid cached work with the same command after an interruption; do not reselect vocabulary or rebuild published media as a recovery shortcut.
5. **Check results.** Require ready_for_review, passing audio/video QA, and upload-package.json. Compare the final speech script to the reviewed preparation and verify every upload-package hash. Inspect actual frames from all three stories, a story transition, and two times in the ending buffer; check readable wrapping, connected scrolling, and continued ending motion. Inspect the dated thumbnail and title/description/chapter sidecars. Failed QA blocks upload; do not waive it or claim full listening from decode checks.
6. **Prepare upload.** Follow [youtube-upload.md](youtube-upload.md) in the in-app browser. Verify the English channel, upload the checked MP4 and thumbnail, and apply saved choices. Record the YouTube video ID immediately. A temporary draft save is an internal step for setting Korean metadata language; continue to final Visibility. Do not publish. Leave Public unselected and Instant Premiere unchecked, visibly ready for Andrew.
7. **Finish after Andrew publishes.** Verify Studio Public, open the exact public video, pause playback and show Add a comment. Suggest a Korean comment if requested; do not post it without instruction. Save publication ID/URL/status in run records and SESSION_LOG.md. Next day starts from a new completed Korean run.

Escalate only new choices, material content concerns, missing/mismatched inputs, authentication obstacles, or failed checks that cannot be resolved within the saved procedure. Do not repeatedly ask about settled settings. No scheduled trigger, unattended publication, main merge, or production launcher change is part of this daily procedure.

## Prepare the next incoming lesson as text

English vocabulary is chosen from English sentence candidates. Korean vocabulary and its glosses are discarded. The selector uses wordfreq 3.1.1, spaCy 3.8.16/en_core_web_sm 3.8.0, cutoff 3,500, contextual borrowing/usefulness checks and a soft target of 8–12. See THIRD_PARTY.md for data provenance and limitations.

1. Use only the next incoming news run for a new lesson. Historical runs may be inspected with the offline diagnostic below, but must not be turned into new samples or media.
2. If the development Korean API produced a structured handoff, prepare independent English wording from the same facts:

   ```powershell
   .venv/Scripts/python.exe -X utf8 -m english_news.prepare --content-run output/content/NEW_SOURCE_RUN_ID --rewrite --allow-model --env-file C:/AI/Codex/Projects/korean-news/.env
   ```

   While production is unchanged and has no export hook, the next completed production run can supply its English sentence pairs without using its vocabulary:

   ```powershell
   .venv/Scripts/python.exe -X utf8 -m english_news.prepare --legacy-written C:/AI/Codex/Projects/korean-news/output/runs/NEW_SOURCE_RUN_ID/DATE-news-written.txt --source-run-id NEW_SOURCE_RUN_ID --allow-model --env-file C:/AI/Codex/Projects/korean-news/.env
   ```

   The legacy adapter retains existing English wording. It cannot independently rewrite without structured shared facts. Do not silently claim that this fallback exercises the new composition stage.
3. Review `output/text-review/<ID>/written.txt`, `speech-script.txt`, `speech-plan.json`, and each `story-NN-selection.json`. The TTS script contains only spoken content with every repetition, rendered from the same plan the audio workflow consumes. The latter JSON records candidate forms, lemmas, ranks, names/grammar/common-word exclusions, contextual decisions, definitions and omissions. Fewer than eight suitable items is allowed. Check loanword meanings and phrase usefulness; neither frequency nor NER establishes learner value by itself.
4. Review text before media. On September 21 Andrew requested fewer manual steps for the next incoming run; the assistant may perform routine text/definition/plan checks and proceed with the agreed media settings when no material issue needs his judgment. Stop for substantive content problems or new decisions. Preserve his final Public/Publish handoff; production adoption and unattended publication remain separate. Edit a response replay or source input and prepare again to revise selection; manually editing written.txt does not update the structured lesson and will block media.

Text preparation makes paid requests only with `--allow-model`. Omit it for validated-cache reuse; use `--responses reviewed-responses.json` for offline replay. Response format is a dictionary keyed by story number, each containing `selection` and optionally `composition`/`grounding`; tests/test_prepare.py provides examples. `--candidates-only` needs no key and cannot produce a media-ready bundle. `--cutoff 4000` or `4500` changes the common-word gate. `--overrides overrides.json` accepts `include`/`exclude` arrays of words or lemmas: include bypasses the frequency gate, not entity or loanword review. Exclude blocks exact forms/lemmas, not every phrase containing a familiar component.

Validated response caches include complete input text, rules, model, frequency/NLP versions and overrides in their identity. Corruption fails visibly. Independent composition includes a separate grounding/translation review. A run ID/content checksum identifies the prepared lesson; all selected vocabulary has source offsets and contextual explanations. These are integrity checks on direct source selection, not the retired translated-gloss occurrence filter.

## Software eligibility safeguards (selection v4)

Single words use pinned LemmInflect 0.2.3 dictionary morphology. For inflected tokens, accept a base only if its dictionary inflection reproduces the source form for the grammatical tag. Unique verified bases drive frequency, borrowing hints, overrides and deduplication. Ambiguous or unknown inflected forms are omitted and audited, rather than guessed by an LLM. Noninflected/base tokens and intact compounds retain their literal form. spaCy still supplies grammatical tags and entities, which can be imperfect; dictionary evidence and the original spaCy lemma are recorded separately.

Only phrases recognized by `english_news/phrase-reference.json` reach the model. This initial, intentionally limited reference covers fixed expressions, inflected verb expressions, a short set of reflexive verbs and bounded cost/expense collocations. It does not admit arbitrary adjective+noun or verb+noun spans. Inflections preserve the exact original source text; canonical expression keys are only used for matching and deduplication. Prefer fewer items over unregistered combinations. Expand the reference through reviewed positive patterns when needed, not an accumulating blacklist of bad phrases.

`english_news/easy-overrides.json` contains optional `easy` and `rank_overrides` fields. The user-approved easy list contains `tourism`; rank overrides remain empty. The same fields are accepted by `--overrides`, alongside include/exclude. Include can bypass a frequency threshold, but cannot bypass an easy-list exclusion, uncertain morphology, phrase eligibility, names or semantic vetoes. Global and per-run rules are hashed into analysis/cache identity. The model has no operation that writes overrides or changes original ranks.

The audience is Korean adults with substantial existing English vocabulary; listening/speaking difficulty does not imply beginner vocabulary knowledge. The cutoff remains 3,500. `phrase-reference.json` marks confirmed basic senses: `start over` (including verified inflections) and `up to` before a numeric quantity, including spelled-out numbers. These receive the deterministic `basic_expression` exclusion, with sense evidence in the audit, even with an include override. The quantity pattern is conservative, not general semantic understanding; other uses such as `up to you` remain available for contextual assessment. No rule excludes a phrase simply because its component words are common.

The existing selection/definition call must return boolean `context_appropriate`, `learning_unit_appropriate` and `adds_learning_value` for each proposed item, alongside the borrowing assessment. False values are enforced as exclusions; lack of learning value yields `too_easy` even at usefulness 5. The prompt separates likely new vocabulary knowledge from usefulness or story relevance. No second review-model call is added. The request contains only eligible candidates; rejected spans remain in the local audit. Counts below eight remain valid. Software eligibility does not guarantee every surviving word is pedagogically useful; the same-call contextual review remains necessary. Old v3 review bundles remain readable, while new selections require the v4 response contract.

## Short English definitions

`english_news/definitions.py` owns the shared English definition prompt and validator. Routine selection uses these instructions within its existing request: one dictionary-style phrase, normally 4–8 simple words, shorter when sufficient, maximum 10. Explain the contextual sense in general terms without retelling the story, listing alternatives, or losing essential meaning. Avoid circular headword reuse, but allow meaningful compounds/related forms. Software enforces the length ceiling and narrow exact-headword/headword-plus-generic-label checks; it does not claim to establish semantic accuracy. Invalid responses use the existing single corrective retry, never mechanical truncation. Prompt contents participate in cache identity; new preparations record definition policy v2. Historical bundles remain readable under their original policy.

To revise definitions in an already selected lesson without reselecting vocabulary (only when a same-run text revision is authorized):

```powershell
.venv/Scripts/python.exe -X utf8 -m english_news.definitions --prepared-run output/text-review/EXISTING_ID --allow-model --env-file C:/AI/Codex/Projects/korean-news/.env
```

This explicit revision batches only the English explanations into one request, with one corrective retry if needed. It rejects missing/duplicate/unknown IDs and attempts to return other fields. It creates a new review bundle, retaining source sentences, Korean glosses, vocabulary selections and original selection audits exactly. Parent checksum, model, prompt checksum and actual response are saved in the preparation. It makes no audio/video. `--responses FILE` permits offline replay; without `--allow-model`, only a validated cache or replay can be used. Routine generation does not gain an extra definition request.

## Optional development content handoff

The Korean hook runs after the existing bilingual summary and before Korean vocabulary. The original English publisher summary/article and selected bilingual facts are exported; English composition can reword those facts and provide its own Korean translations. The Korean summary prompt is unchanged. Moving shared fact extraction ahead of both audience prose generators remains a later architectural step, not something this implementation claims to have done.

Set `NEWS_CONTENT_EXPORT_DIR` only in the development process, to this EnglishNews checkout's `output/content`, then use `development/start-api.ps1` (port 8010). Its `-Check` mode checks paths without starting a server. Export is disabled by default. The API launcher never starts cleanup, renderer watchers, staging or publication. Never run a production desktop launcher from a worktree.

A complete `news-content-v1` handoff contains `story-01.content.json` through the declared count, atomically published with SHA-256 envelopes. The English consumer rejects missing/changed/mixed stories. Retries are idempotent. Export errors are logged and leave Korean generation running. This initial hook supports up to three selected stories, which Korean duration preflight never trims; larger runs are skipped to avoid divergent lineups. No automatic English watcher or daily trigger is enabled.

## Media after text review

For the next incoming run, when Andrew has authorized media, use the exact reviewed preparation and matching original story images:

```powershell
./development/make-english-news.ps1 -PreparedRun output/text-review/NEW_ENGLISH_TEXT_ID -StagedRun C:/AI/Codex/Projects/KoreanLessonVideoLab/inputs/korean-news/NEW_SOURCE_RUN_ID -VideoLab C:/AI/Codex/Worktrees/english-news/KoreanLessonVideoLab -EnvFile C:/AI/Codex/Projects/korean-news/.env -ReviewedText
```

The explicit review flag records the operator's review decision; it does not solicit a second confirmation after authorization. The wrapper has no SourceRun mode that can reuse Korean vocabulary. It synthesizes the selected words/phrases with the existing cadence: English twice, Korean gloss, English explanation, English twice. Voice Alloy; English 0.8976 (a 2% increase from 0.88), Korean sentences/section labels 1.07, Korean vocabulary glosses 0.88. Unique vocabulary clips carry individual speeds. Body English is repeated twice and the full review is English. Vocabulary stays attached to its own body sentence.

Call boundaries differ from production Korean News: English generates three unique clips per vocabulary item (English term, Korean meaning, English explanation) and assembles the order 0,0,1,2,0,0. Production Korean's current OpenAI Speech path sends all vocabulary for a sentence plus the twice-read Korean sentence as one learning block. English's separate calls preserve repetition counts and independent rates, at the cost of more requests.

Before assembly, each English clip must pass the offline audio-signal guard, including cached clips. A near-silent response retries only that segment, at most twice, under separate cached filenames; persistent failure blocks the build and records signal-qa.json. Normal clips need no additional model request. Final audio QA checks the assembly sources again. This catches silent responses such as September 21 hands-on, but cannot prove spoken-word correctness or detect every partial omission.

The scroll-only heading comes from audience.json scroll_title (currently the user-requested Korean News Lesson) followed by the run date as YYYY-MM-DD. It occupies space above the existing Headline 1 starting position; it is not in the spoken plan. Existing row positions, story timing, channel title and publication metadata remain unchanged.

Speech settings are saved in the preparation profile and consumed unchanged by media. Older preparations without explicit settings remain at their original rates. To apply current settings to approved text without a model/audio call, run `.venv/Scripts/python.exe -m english_news.speech_review --prepared-run output/text-review/EXISTING_ID`; it creates a separate review bundle and exact `speech-script.txt`, preserving all lesson content. The loader rejects script/plan edits that disagree with the saved preparation.

Current profiles also save `headline_label: Headline`: written and spoken labels use English and the ordinary English speed. The headline label and Korean headline are separate calls; no special rate is needed. Older profiles without that setting retain Korean labels for reproducibility. Applying the current profile can change presentation labels while preserving sentence/vocabulary content. Video vocabulary uses full body size (44px), natural wrapping, and the same wrapping allowance as the established Korean scroll.

Audio and video outputs now remain under EnglishNews `output/runs/<ID>/`; video and publication sidecars are in its `video/` subfolder. Images are copied and checked by hash. Video Lab runs through its CLI with explicit paths, without cross-project sys.path imports or a requirement that .git be a worktree file. It never runs a publication watcher. `english_news/audience.json` owns English labels and description/thumbnail copy; the renderer preserves defaults for older manifests.

Require workflow-status.json `ready_for_review`, audio-qa.json, video-qa.json and upload-package.json, inspect QA frames and listen before adoption. Publication stays disabled; the channel is 뉴스로 배우는 영어 / @SteadyLanternEnglish, ID UCPvS_o6ypGR8-aA0P2pgtdA. Repeat the same media command to resume valid cached speech/render work. Do not rebuild old videos merely to test selection. The historical prototype.py and vocabulary.py remain only for old regression fixtures, not routine generation.

## Install and test

Each development checkout has its own .venv. EnglishNews no longer needs an editable Korean core or sibling src imports. From this checkout:

```powershell
.venv/Scripts/python.exe -m pip install --no-deps ../korean-news
.venv/Scripts/python.exe -m pip install -e .
.venv/Scripts/python.exe -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m unittest discover -s tests
```

The first command builds `korean-news-media==0.1.0` from the reviewed development checkout. It packages the existing speech source under `korean_news_media`; it does not copy implementations into EnglishNews. Public speech modules are tts_common, openai_speech_tts and tts_transcription. Reinstall after shared source changes. Before adoption, pin the reviewed Korean commit/wheel; do not install the current unchanged production checkout, which lacks this package. The English optional `media` extra describes the version requirement. Media imports work from an ordinary checkout, so development folders can be retired after merging. `ENGLISH_NEWS_HOME` may explicitly select the EnglishNews checkout; source/editable installs default to their own checkout. Renderer dependencies stay in Video Lab's environment.

`english-news-requirements.lock.txt` captures the validated English development environment. The older Korean/Video Lab locks record the initial September 13 setup. Offline tests use mocks/replays; they do not synthesize or render real media. Run both sibling suites with their own .venv when changing a shared interface.

Offline diagnostic example (historical text is permitted here):

```powershell
.venv/Scripts/python.exe -X utf8 -m english_news.diagnostics --legacy-written PATH_TO_WRITTEN --source-run-id SOURCE_RUN_ID --output .local/diagnostics/SOURCE_RUN_ID
```

This compares 3,500/4,000/4,500 candidate pools. It does not make semantic selections or a new lesson. Frequency data is queried in memory, not copied into a standalone list.

## Checkouts, adoption and portability

Use the existing three `codex/english-news-prototype` worktrees under C:/AI/Codex/Worktrees/english-news. No new branches or worktrees are needed. Production remains under C:/AI/Codex/Projects on main. Shared Korean core and loanword repositories are unchanged.

After text and next-run media review: reconcile each development branch with its own main; merge the small Korean export/package change and compatible Video Lab interface; pin those reviewed dependencies in EnglishNews and merge its application; test ordinary checkout paths; then retire the three worktrees after preserving needed ignored outputs. English logic remains in EnglishNews and shared media fixes have one owner. Never fold independent copies of Korean code into EnglishNews.

Worktrees, environments and generated media do not travel with normal main-branch sync. Commit/push development branches separately before a device move; transport wanted ignored artifacts separately. Keep keys outside Git. No credential has been copied or provisioned by this change. Historical setup/sample details remain in SESSION_LOG.md and Git history; they are not current run instructions.
