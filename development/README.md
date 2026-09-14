# English News development setup

## Routine three-story run (Windows ASUS)

Vocabulary update: the command now removes English glosses containing whole-word
“name” or exactly matching the checked-in country-name/alias list before
explanation/speech generation. See vocabulary-filter.json in each new output.
Generic place descriptions, sentence-occurrence checks and grammatical variants
are saved for next time. Effectiveness checks for these rules are text-only:
do not run this media-building command merely to test a vocabulary change.

Work in `C:/AI/Codex/Worktrees/english-news/EnglishNews`. Andrew runs the original
Korean News desktop icon first, then tells the assistant the new run is ready.
Use only that next incoming run. Do not regenerate an earlier reviewed video
unless he specifically asks. No GPT model needs to reconstruct the pipeline.

1. Find the new run ID in `C:/AI/Codex/Projects/korean-news/output/runs/`.
   Read its `run.json`: require `status=completed` and three stories. Confirm
   the same ID has three images in the production Video Lab
   `inputs/korean-news/<ID>/` folder. If multiple new runs are plausible, ask
   Andrew which one; never silently use an older run.
2. Execute one command from this worktree:

   ```powershell
   ./development/make-english-news.ps1 -SourceRun NEW_RUN_ID
   ```

3. Wait for exit code 0 and `READY FOR REVIEW`. Read
   `output/runs/<English ID>/workflow-status.json` (`ready_for_review`),
   `audio-qa.json`, `video-qa.json`, `vocabulary-review.md`, and
   `upload-package.json`. The package lists exact video, Korean title,
   description, thumbnail and chapters paths with checksums. Open the MP4
   for Andrew, inspect the start, transition and end frames, and mention
   outstanding vocabulary concerns. Automated checks do not replace listening.
4. Stop at local review. Do not upload, start a watcher, create an upload task,
   or change production. The intended channel is 뉴스로 배우는 영어 /
   @SteadyLanternEnglish (`UCPvS_o6ypGR8-aA0P2pgtdA`). Upload requires Andrew's
   subsequent request after reviewing this video.

The command snapshots and verifies source text/metadata/images, prepares all
three lessons using Alloy (English 0.88, Korean 1.07), generates or resumes
cached speech, concatenates story audio, checks exact repetition assembly,
renders story-timed scrolling, validates the complete media and sidecars,
and leaves publication disabled. Source folders are read-only inputs.
An OS lock prevents simultaneous builds and releases on process exit.

On failure, read the error and workflow status. Repeating the **same command
for the in-progress run** resumes valid speech/explanations. Completed renders
are reused only when code, input and video checksums match. A failed render
restarts rendering; it does not need another speech synthesis. Do not delete
caches, alter source snapshots, or run the Korean desktop launcher from these
worktrees. Input corruption, missing keys, malformed lesson text or missing
staged images should be reported and resolved explicitly.

The wrapper uses the existing Korean News `.env` without copying it. Its ASUS
Projects root is explicit in the script; review that path after a device move.
The enrichment model is already `gpt-5.6-luna`. Running the procedure with a
lighter Codex model is the next operational handoff test, not yet demonstrated.

Current review: `20260914_english_all_7bffe0766f`, based on source
`20260914_105639_ba258775`. Three stories, 31 vocabulary entries, 80 speech units.
The MP4 is in sibling Video Lab `outputs/<English ID>/` (about 16m38s).
This supersedes the one-story commands below for routine work.

Created on ASUS, 2026-09-13. All three repositories use branch
`codex/english-news-prototype` in linked worktrees under
`C:/AI/Codex/Worktrees/english-news/`:

- `EnglishNews`: English worker development and these setup records.
- `korean-news`: future lesson-export changes.
- `KoreanLessonVideoLab`: future audience-aware rendering changes.

Each worktree has its own `.venv`. The original folders under
`C:/AI/Codex/Projects/` remain on `main`, with the existing desktop shortcut,
production environments and complete run-to-upload workflow intact.
A branch is the line of development; a worktree gives that branch its own
folder so production and development can stay checked out simultaneously.

## Running development

Use `development/start-api.ps1` from this worktree to start the development
Korean News API on port 8010. `-Check` validates paths without starting it.
This launcher disables API cleanup and does not start the desktop supervisor,
staging, Voice Inbox cleanup, render watchers or upload handoff. Do not use
the copied production desktop launchers or `start_local_workflow.py` to run
development: they retain production cleanup/publication behavior.

Output and runtime state resolve inside the development worktrees. Video Lab
is explicitly selected by the development launcher and also retains the
expected sibling folder name. Render commands must use development input and
output paths. No server or worker is started by setup.

No credentials or production `.env` files were copied. The prototype can read
the existing key using an explicit `--env-file` argument; it keeps the key in
process memory. Offline tests need no credentials.

## Dependencies and baseline

The two lock files capture the production package versions at setup.
EnglishNews provisionally uses the Korean News lock for prototype work.
Production Korean News uses editable Korean core from the sibling repository;
development installs its clean commit `1d3e870ace54b31d87c93d8c15a43d9dd394acd0`
as a non-editable package. No core worktree or shared-core edits are needed.

Today's frozen source run, staged input, and rendered output are copied under
`.local/baselines/20260913_122823_97cda690/` in this EnglishNews worktree.
`manifest.json` records SHA-256 checksums and original paths. These copies
are outside production cleanup locations and excluded from Git. Original
manifests retain production path strings for evidence; never pass them to
tools that write through those paths. Create a separate working fixture and
remap paths before replaying anything.

The baseline contains written lessons, speech inputs/request metadata, audio,
story illustrations, the MP4 and publication/QA sidecars. This is a preserved
comparison baseline, not an English prototype or a completed listening review.

## Portability

Worktree directories, `.venv` folders and frozen media are local. Existing
routine sync covers the main repository folders; it must not be assumed to
carry development branches or these ignored artifacts. Before a device move,
commit/push development changes and recreate the worktrees/environments on the
other device. Baseline media needs separate transport if it is needed there.
Do not add worktrees as independent repositories to routine sync.

## One-story prototype

The previously reviewed sample is `20260913_english_s1_e4644bf4a9`: source story 1,
four body sentences, 18 existing vocabulary entries, and an English full review.
The EnglishNews `output/runs/<id>/` folder contains the structured historical
bundle, cached explanations, written lesson, speech plan/script, segment audio,
assembled MP3, run metadata and audio QA. The sibling Video Lab
`outputs/<id>/` contains the MP4, Korean title/description/thumbnail and QA frames.
One-story samples intentionally omit YouTube chapters (which need three entries).

From this EnglishNews worktree, using its `.venv/Scripts/python.exe`:

```powershell
.venv/Scripts/python.exe -X utf8 -m english_news.prototype --baseline .local/baselines/NEW_RUN_ID --env-file C:/AI/Codex/Projects/korean-news/.env --audio
.venv/Scripts/python.exe -X utf8 -m english_news.render output/runs/NEW_ENGLISH_RUN_ID
.venv/Scripts/python.exe -X utf8 -m unittest discover tests
.venv/Scripts/python.exe -X utf8 development/check_korean_baseline.py
.venv/Scripts/python.exe -X utf8 development/check_sample.py output/runs/20260913_english_s1_e4644bf4a9
```

This is an explicit local historical importer, not a live export hook or daily
worker integration. It rejects mismatched Korean review content before making
API requests. New runs use content/profile identities and cache explanations;
speech transport resumes validated segment requests. Each vocabulary entry
synthesizes its English gloss, Korean word and English explanation separately,
then assembles indices `[0, 0, 1, 2, 0, 0]`. English sentence audio is duplicated
in software too. This avoids model omissions of repeated speech.

As of September 14, always use the next incoming run for new samples. Replace
the NEW_RUN_ID placeholders above only after receiving that run. Do not rerender
old samples unless Andrew explicitly requests it. The interrupted old-run v3
render `20260913_english_s1_a50ff43638` is not a review deliverable.

Alloy, English 0.88 and Korean sentences 1.07 were confirmed for this sample;
vocabulary blocks and the English review use 0.88. Branding is provisional.
The initial v1 diagnostic sample (`e60a7d8774`) is superseded: one checked
vocabulary clip omitted its last repetition. Use the v2 sample above.

Three inherited glossary entries are flagged in `vocabulary-review.md`:
Baudeogi as “traditional performer,” “to occupy” for winning a prize, and
“souvenir” as part of a store name. They are preserved for this agreed initial
inversion and need review before publication. No channel is configured and no
publication, watcher, production cleanup or daily workflow integration runs here.
