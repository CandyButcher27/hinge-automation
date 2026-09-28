# capture — hotkey screenshot to comment on clipboard

## Purpose
Press `Ctrl+Alt+H` while a profile is on screen. The tool grabs the emulator window, asks a vision model for an opening
comment aimed at one photo or prompt, puts the comment on the clipboard and saves it to SQLite.

## Location
`capture/hinge_capture.py` (tests: `capture/test_hinge_capture.py`). Started by `run-hinge.ps1 -Capture`.

## Interfaces
- `--window <title substring>`: grabs that window and tracks it as it moves. The launcher passes `Medium_Phone`.
- `--once`, `--image <png>`, `--region`, `--monitor`, `--hotkey`, `--delay`, `--list-windows`.
- Writes to `dating-assistant/data/assistant.db` (shared with the MCP server).

## Configuration
Provider auto-selects in this order: `ANTHROPIC_API_KEY`, then `OPENAI_API_KEY`, then the `claude` CLI. No key is set on this
machine, so it uses the `claude` CLI (~5-10s per capture).

## Important constraints
- It grabs pixels from the host window, so a black emulator render (see [[emulator]]) yields a black capture.
- The listener was started 2026-09-26 but no capture has actually been fired yet. Not verified end to end.
