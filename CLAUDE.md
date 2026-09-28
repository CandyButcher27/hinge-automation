# CLAUDE.md

Operating rules for Claude Code in this repo.

## What this is

Human-in-the-loop Hinge helper. Hinge runs in an Android emulator on a Windows host. Claude reads
profiles from screenshots, drafts comments, and sends likes with `tools/hinge.py` through the emulator
console, only after the user answers y for that profile. The `capture/` tool and `dating-assistant/`
MCP server share one SQLite DB. Out of scope: bulk or unattended liking, anything that spends money
without asking. See `docs/` for setup, architecture and the input model.

After any like is sent, make sure that person's `people/.../profile.md` and `people/likes.log` record it.

## Working rules

- Windows 11. Run adb binary-output commands (`exec-out screencap`) from Git Bash, not PowerShell.
- Python via uv (`uv sync`, `uv run ...`) for `capture/` and `tools/`. Node 22.5+ for `dating-assistant/`.
- Tests: `uv run pytest capture tools` and `cd dating-assistant; npm test`.
- Verify every Hinge tap with a screenshot before the next irreversible one.

## Confirm before acting

- Sending a like or message to anyone the user has not named in this session.
- Any Rose, Boost, HingeX, subscription or purchase screen — stop and ask.
- Committing anything under `people/` (it is gitignored; keep it that way).
