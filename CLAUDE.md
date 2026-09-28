# CLAUDE.md

Operating rules for this repo. Global rules in `~/.claude/CLAUDE.md` still apply;
this file adds what is specific to this project.

## What this is

Personal Hinge helper. Hinge runs in an Android emulator on this laptop. Claude reads profiles from
screenshots, drafts comments, and sends likes with `tools/hinge.py` through the emulator console,
only after the user answers y for that profile. The `capture/` tool and `dating-assistant/` MCP server
share one SQLite DB. Out of scope: bulk or unattended liking, anything that spends money without asking.

Project memory lives in `mimi/` (loaded below). **Code is the source of truth.** Memory that disagrees
with the implementation gets corrected — never bend code to match a stale note. After any like is sent,
make sure that person's `people/.../profile.md` and `people/likes.log` record it.

## Workflow

- `/think` — for non-obvious design work, use it before committing to an approach
- `/debug` or the `debugger` agent — any bug, before proposing a fix
- `/mimi-close` — end of session

## External-facing content

Never mention `mimi/` or its filenames in commit messages, PR descriptions,
code comments, READMEs, or anything else written to be read outside this repo.

## Working rules

- Windows 11. Run adb binary-output commands (`exec-out screencap`) from Git Bash, not PowerShell.
- Python via `.venv` (`capture/`, `tools/`), Node 22.5+ (`dating-assistant/`).
- Tests: `cd dating-assistant; npm test` and `.\.venv\Scripts\python.exe -m pytest capture tools`.
- Verify every Hinge tap with a screenshot before the next irreversible one.

## Confirm before acting

- Sending a like or message to anyone the user has not named in this session.
- Any Rose, Boost, HingeX, subscription or purchase screen — stop and ask.
- Committing anything under `people/` (it is gitignored; keep it that way).

<!-- memory-layer:start -->
@mimi/MIMI.md
If mimi/MIMI.md is not already in your context, read it and mimi/STATE.md before starting any task.
<!-- memory-layer:end -->
