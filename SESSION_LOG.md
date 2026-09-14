# English News — session log

## 2026-09-14 — English YouTube channel and matching icon

- Andrew selected 뉴스로 배우는 영어 and authorized channel creation, including the final Terms confirmation. Verified the created channel at `UCPvS_o6ypGR8-aA0P2pgtdA`, handle `@SteadyLanternEnglish`, managed by the same Steady Lantern account as Korean Listening Lessons. Existing channel name remains unchanged; the proposed Korean rename was only discussed.
- Created and saved a matching 영어 icon at `assets/channel/english-channel-icon-v1.png` using built-in ImageGen and the existing 한국어 channel avatar as reference. Prompt and channel details are in assets/channel/README.md.
- Icon upload is pending: Chrome fileChooser.setFiles returned Not allowed. Official troubleshooting requires user to enable Allow access to file URLs for the ChatGPT browser extension. English channel Studio Profile page is prepared; resume upload/crop/publish after that setting is enabled. No video publication or workflow integration occurred.

## 2026-09-14 — section labels, written formatting, and next-run-only rule

- Andrew watched the first sample and requested spoken Korean headline numbering, `어휘` before vocabulary, and `전체 요약` before the final English reading. Implemented separate native-speed label units and removed spoken “Full review.” Story numbering now also drives the written heading.
- Written blocks now follow the Korean source spacing: native sentence immediately followed by the vocabulary heading, one colon-separated logical line per vocabulary entry, then a blank line before the English sentence and between blocks. Removed em-dash separators. English video vocabulary rows use the existing 34px vocabulary style while sentence text stays 44px; long rows can wrap naturally.
- All 307 tests passed (9 EnglishNews, 270 Korean News, 28 Video Lab). Eight Korean deterministic baseline artifacts remain byte-identical. No production code or desktop workflow changed.
- Began rebuilding the old source before Andrew clarified that every revision must use the next incoming run. New labels/audio were generated locally, but the video render was interrupted immediately after that clarification; no matching rendering processes remain. The partial `20260913_english_s1_a50ff43638` is not a review deliverable. Do not resume it.
- Standing rule: never remake old videos unless explicitly asked. Keep these code changes ready and wait for the next news run. Frozen historical artifacts may still support offline regression checks. No upload took place.

## 2026-09-13 — first written/audio/video prototype

- Built the independent English-side historical importer, schema-v1 bundle/ready marker, cached batched explanation enrichment, written/speech plans and audio assembly. Used source story 1 from today's frozen run: 4 body sentences and 18 unchanged vocabulary entries. This imports the saved written format; live structured export and daily worker integration remain future work.
- Andrew confirmed Alloy with English 0.88 and Korean sentences 1.07 for this sample. Vocabulary and English review use 0.88. Existing API key was read explicitly in process; no credential file or production environment was changed.
- First sample `20260913_english_s1_e60a7d8774` exposed a missing fourth English vocabulary reading. Isolated audio/transcript diagnostics distinguished the missing reading from ASR repetition collapsing. Superseded by `20260913_english_s1_e4644bf4a9`, using individual glossary/native/explanation clips assembled `[0,0,1,2,0,0]`; English sentence pairs are also duplicated in software.
- Current sample: EnglishNews `output/runs/20260913_english_s1_e4644bf4a9/`; sibling Video Lab `outputs/20260913_english_s1_e4644bf4a9/20260913-english-news-lesson.mp4`. Audio 431.784 seconds; video about 442.67 seconds, 1920x1080/12 fps. Includes Korean thumbnail/title/description, reused story illustration, render status, beginning/middle/review/end QA frames. No YouTube chapters for this single-story sample.
- Video Lab now accepts explicit `audience=english`; defaults remain Korean. English uses Korean labels and metadata, explicit language-keyed headlines and narrower text wrapping to avoid the story card. Branding is provisional. Publication is disabled with no channel configured; no watcher or upload ran.
- Verification: 7 EnglishNews + 270 Korean News + 28 Video Lab tests passed (305). All eight rebuilt Korean deterministic artifacts matched the frozen output byte-for-byte, including cards, thumbnail, scrolling script and publication text. All 29 assembled speech units passed source-text, speed, repetition-order, duration and MP3-decode checks. Sample ASR confirmed headline/body/review content; whole-vocabulary ASR is unreliable at repetitions, so assembly evidence and isolated word transcription are used. Visual QA inspected middle, review and tail frames. Full human listening remains required.
- Preserved inherited glossary issues in the sample and flagged them in vocabulary-review.md: Baudeogi as a generic performer, “to occupy” for winning an award, and “souvenir” as a store name. Next: Andrew watches the sample and reviews pacing/word choices before live export, all-story processing or publication integration. Code is committed locally; branches and ignored media still need explicit transport before a device move.

## 2026-09-13 — ASUS isolated development setup

- Andrew explicitly authorized worktrees after confirming that the desktop-icon workflow through video upload must be preserved. Verified the four relevant repositories were clean on main and their heads matched GitHub; EnglishNews is enrolled in CodexSync. No Start/End sync was run.
- Created `C:/AI/Codex/Worktrees/english-news/{EnglishNews,korean-news,KoreanLessonVideoLab}` on `codex/english-news-prototype`, with separate virtual environments. Original Korean News, Video Lab and core folders/environments/shortcuts remain untouched. No shared-core worktree was needed.
- Production core is editable at commit `1d3e870`; development installs that exact commit non-editably. Production package versions are captured in the development EnglishNews dependency locks. All three environments pass `pip check`.
- Preserved today's completed run `20260913_122823_97cda690`, staged input, and video output under the development EnglishNews `.local/baselines/` folder: 168 copied files, 108.1 MiB, SHA-256 verified. Earlier videos from September 3, September 2 and August 31 are also present. Frozen manifests retain original path strings and must be remapped in separate working fixtures before replay.
- Existing test suites pass in the new environments: Korean News 270, Video Lab 25 (295 total). Development API launcher path check passes; it selects port 8010 and excludes cleanup/staging/upload workers. No live generation, new render or upload was performed; no credentials copied.
- Next: continue in the EnglishNews development worktree, establish a remapped one-story fixture and implement the structured export/English prototype. Setup records are local; worktree folders, environments and frozen media do not travel through normal main-branch sync. Preserve development branches explicitly before another device move.

## 2026-09-13 — repository publication and sync enrollment

- On GRAM14-2023, Andrew supplied the empty drew345/EnglishNews GitHub repository and authorized initializing this folder, publishing the planning files, and adding it to routine sync.
- Initial branch: main. Track AGENTS.md, SESSION_LOG.md, FEASIBILITY.md and .gitignore; exclude the redundant local handoff ZIP, environments, secrets and generated output.
- Register routine coverage and a verified published commit in CodexSync; add a pointer-only entry to shared MindHub. This supersedes the earlier transport-gap note once remote verification succeeds.
- This is repository setup/coverage maintenance, not Start/End sync or coding takeover. No production Korean code or development worktrees changed. Next action remains inspecting a real output bundle on ASUS after the separately requested device sync.

## 2026-09-13 — feasibility and LG Gram 14 → ASUS preparation

- Investigated Korean News, Korean Learning Core, Video Lab and related dependency paths. Detailed findings are in FEASIBILITY.md. First cut is feasible with targeted extraction/configuration rather than a rewrite; preliminary operational estimate is 5–10 focused working days.
- User confirmed all current outputs including video, reuse of existing vocabulary selection, and a separate YouTube channel with Korean titles/descriptions. Added short English explanations to first-cut scope.
- Final corrected vocabulary sequence: English ×2 → Korean word → short English explanation → English ×2. Rechecked src/vocab_pass.py: word_pair is emitted before and after the definition fields. This supersedes the assistant's incorrect five-part proposal.
- Recommended explanation generation is one batched English-side enrichment request, preserving the original shared vocabulary prompt. Same-call generation is possible later with an optional field and compatible parser/model/retry changes.
- Existing-code validation from the study: 44 focused Korean News tests and all 25 Video Lab tests passed (69 total). No inversion code, live generation, full MP4 render or publication was performed.
- No production code, branches, worktrees or dependencies were changed. Korean News had pre-existing AGENTS.md and SESSION_LOG.md edits; left intact. Inspected heads were Korean News e22e38e and Korean core 1d3e870; recheck on ASUS after sync.
- User will perform End sync on LG Gram 14 and Start sync on ASUS. No sync ran in this task. EnglishNews currently lacks Git and CodexSync membership, so ordinary sync will not transfer it yet. Prepared local memory and a portable planning archive; transfer/enrollment remains to be verified.

### Exact restart on ASUS

1. Confirm this folder's three Markdown files arrived and read AGENTS.md plus this log. Verify the user's separately requested Start sync outcome; do not infer successful sync from these notes.
2. Inspect one actual completed Korean News run on ASUS, including written/TTS text, run.json, audio request metadata, and matching video artifacts if present. User expects outputs there; existence is not yet verified. Use these to confirm formatting, timing, and historical import feasibility.
3. Recheck repository instructions, branches, dirty state and actual installed core dependency. Successful Git sync checkpoints included source/memory, but ignored output, credentials, virtual environments and worktree folders are separate concerns.
4. When implementation begins, the agent can set up isolated development branches/worktrees/environments itself and explain which folders are stable versus experimental. Check sync handling of those branches before a subsequent device move.
5. Build a one-story written/audio/video prototype with the exact corrected vocabulary sequence, then review English explanations, pacing, video language labels and branding before automatic dual production.

Remaining product choices: English voice/speed, series name and destination channel identity. No need to reopen the settled vocabulary repetition question.
