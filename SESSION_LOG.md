# English News — session log

## 2026-09-14 — Korean country names included in English filter

- Added exact country-name matching on Korean vocabulary words as requested. Last source's text-only check now removes 태국 and 이재명 (31 → 29); 17 tests pass. No LLM calls or media generated. The other three proposed rules remain deferred; implementation and details are in the development worktree.

## 2026-09-14 — first two English vocabulary filters ready

- Development now filters whole-word “name” glosses and exact country-name/alias glosses before explanations/audio. 16 tests pass; offline September 14 check removes one entry (31 → 30). No LLM calls or media generation. Andrew requires text-only effectiveness checks.
- Deferred three rules: generic place descriptions, matching against actual English sentences, grammatical variants. Full details in development SESSION_LOG.md; next incoming media run uses the first two automatically.

## 2026-09-14 — manual upload; simplified English vocabulary filtering next

- Andrew reports uploading today's English video manually and will review it on YouTube. No URL/visibility supplied; automatic uploads remain disabled.
- Next task is improving the existing vocabulary inversion shortcut: preferably use software to require the English study word/phrase to occur in the actual English story, removing descriptive placeholders such as “a politician's name.” Reuse existing candidates and defer a complete independent English vocabulary selector. Detailed decisions/open matching questions are in development SESSION_LOG.md. Record only for now; do not remake the uploaded video.

## 2026-09-14 — full English video and repeatable local workflow

- Today's Korean run `20260914_105639_ba258775` now has a three-story English review video, `20260914_english_all_7bffe0766f` (~16m38s), with Korean upload materials. Continue in the development worktree; its development/README.md begins with the one-command runbook and checks for lighter-model handoff. No upload or automatic integration; Andrew reviews first.
- English channel description and enlarged icon v2 published. Korean channel renamed Learn Korean Through the News / @SteadyLanternKorean. Details and preserved assets/descriptions are in development assets/channel/. Production code and desktop workflow remain untouched.

## 2026-09-14 — English channel icon applied

- Uploaded and published the matching 영어 profile icon after Chrome file-URL access was enabled. Verified the icon and “All changes saved” in English channel Studio. This supersedes the earlier pending-upload note; public avatar propagation may lag. No video publication or Korean channel changes.

## 2026-09-14 — new channel created

- Verified new channel 뉴스로 배우는 영어, `@SteadyLanternEnglish`, ID `UCPvS_o6ypGR8-aA0P2pgtdA`, under the existing Steady Lantern account. Original Korean channel unchanged.
- Matching 영어 icon saved in development EnglishNews assets/channel/. Upload is pending Chrome extension file-URL permission; instructions were given to Andrew. Full details in development SESSION_LOG.md and assets/channel/README.md. Automatic video publication remains disabled.

## 2026-09-14 — feedback implemented; wait for next run

- Added Korean spoken section labels and compact colon-separated written vocabulary in the development worktrees; 307 tests pass. Details are in the development EnglishNews SESSION_LOG.md.
- Andrew clarified that all revisions must use the next incoming news run. Interrupted the in-progress old-video render and recorded the durable rule in both AGENTS.md files. Do not resume the partial old sample; wait for the new source run. No publication or production workflow changes.

## 2026-09-13 — prototype ready in development worktrees

- Andrew authorized the first frozen-story prototype and confirmed Alloy, English 0.88 and Korean sentences 1.07. Current review sample is `20260913_english_s1_e4644bf4a9` in the EnglishNews and Video Lab development output folders. It includes written lessons, assembled audio and a roughly 7m23s video; no upload or daily integration ran.
- Detailed implementation, audio repetition repair, QA and open review items are recorded in `C:/AI/Codex/Worktrees/english-news/EnglishNews/SESSION_LOG.md` and `development/README.md`. Continue there, not in this main planning checkout.
- 305 tests passed; eight Korean rendering/metadata artifacts remained byte-identical to the frozen baseline. Production Korean code, environments and desktop shortcut remain unchanged. Full user listening/review is next. Commits and generated media remain local.

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
