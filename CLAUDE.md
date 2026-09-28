# CLAUDE.md

Operating rules for this repo. Global rules in `~/.claude/CLAUDE.md` still apply;
this file adds what is specific to this project.

## What this is

Personal Hinge helper. Hinge runs in an Android emulator on this laptop. Claude reads profiles from
screenshots, drafts comments, and — on the user's explicit per-profile instruction — scrolls and
sends likes through adb. The `capture/` tool and `dating-assistant/` MCP server share one SQLite DB.
Out of scope: bulk or unattended liking, anything that spends money without asking.

## Cold start order

1. This file — what the project is, and how to work in it
2. `memory/README.md` — pick the memory files this task actually needs
3. The relevant `memory/<component>.md` before touching that component

Then read the actual code. **Code is the source of truth.** Memory that
disagrees with the implementation gets corrected — never bend code to match a
stale note.

## Memory maintenance

After a **major change window** — a feature, a significant bug fix, an
architecture/API/pipeline/dependency change, a substantial refactor, a completed
debugging investigation — update memory in the same pass. Not after trivial
edits. After any like is sent, update that person's `people/.../profile.md` and the
state table in the people memory file.

Run `/wrapup` to do this properly. It refreshes the changed `memory/*.md` files
and `memory/README.md` if files were added, merged or removed.

- **Only what actually ran gets written as working.**
- **Correct stale claims in place.** Never leave a new fact beside a contradictory old one.

## Workflow

- `/think` — for non-obvious design work, use it before committing to an approach
- `/debug` or the `debugger` agent — any bug, before proposing a fix
- `/wrapup` — end of session

## External-facing content

Never mention `memory/` or its filenames in commit messages, PR descriptions,
code comments, READMEs, or anything else written to be read outside this repo.

## Working rules

- Windows 11. Run adb binary-output commands (`exec-out screencap`) from Git Bash, not PowerShell.
- Python via `.venv` (`capture/`), Node 22.5+ (`dating-assistant/`).
- Tests: `cd dating-assistant; npm test` and `.\.venv\Scripts\python.exe -m pytest capture`.
- Verify every Hinge tap with a screenshot before the next irreversible one.

## Confirm before acting

- Sending a like or message to anyone the user has not named in this session.
- Any Rose, Boost, HingeX, subscription or purchase screen — stop and ask.
- Committing anything under `people/` (it is gitignored; keep it that way).
