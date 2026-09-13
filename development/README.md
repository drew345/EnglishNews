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

No credentials or production `.env` files were copied. Live generation setup
is deferred until the prototype needs it. Offline tests can run now.

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
