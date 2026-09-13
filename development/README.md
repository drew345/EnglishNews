# English News development setup

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

The current review sample is `20260913_english_s1_e4644bf4a9`: source story 1,
four body sentences, 18 existing vocabulary entries, and an English full review.
The EnglishNews `output/runs/<id>/` folder contains the structured historical
bundle, cached explanations, written lesson, speech plan/script, segment audio,
assembled MP3, run metadata and audio QA. The sibling Video Lab
`outputs/<id>/` contains the MP4, Korean title/description/thumbnail and QA frames.
One-story samples intentionally omit YouTube chapters (which need three entries).

From this EnglishNews worktree, using its `.venv/Scripts/python.exe`:

```powershell
.venv/Scripts/python.exe -X utf8 -m english_news.prototype --baseline .local/baselines/20260913_122823_97cda690 --env-file C:/AI/Codex/Projects/korean-news/.env --audio
.venv/Scripts/python.exe -X utf8 -m english_news.render output/runs/20260913_english_s1_e4644bf4a9
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

Alloy, English 0.88 and Korean sentences 1.07 were confirmed for this sample;
vocabulary blocks and the English review use 0.88. Branding is provisional.
The initial v1 diagnostic sample (`e60a7d8774`) is superseded: one checked
vocabulary clip omitted its last repetition. Use the v2 sample above.

Three inherited glossary entries are flagged in `vocabulary-review.md`:
Baudeogi as “traditional performer,” “to occupy” for winning a prize, and
“souvenir” as part of a store name. They are preserved for this agreed initial
inversion and need review before publication. No channel is configured and no
publication, watcher, production cleanup or daily workflow integration runs here.
