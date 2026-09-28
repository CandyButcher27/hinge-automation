# hinge automation

Two halves that share one local SQLite database.

```
capture/            hotkey → screenshot → Claude vision → comment on your clipboard
dating-assistant/   MCP server → Claude Desktop / Claude Code tools over the same data
                    └── data/assistant.db   ← shared
```

- **`capture/`** — the fast loop. Profile on screen, press `Ctrl+Alt+H`, paste the comment. See `capture/README.md`.
- **`dating-assistant/`** — the thinking loop. Set preferences, review profiles, paste conversations, draft replies, all from Claude. See `dating-assistant/README.md`.

## What this does not do

No part of this touches Hinge or any other dating service: no API calls, no
reverse-engineered endpoints, no login automation, no scraping, no browser
automation, no network inspection, no stored credentials or cookies.

Data reaches the database two ways only — you type or paste it in through Claude,
or it is read from pixels on your own screen. Sending is always manual: the tools
produce text, you paste it and tap send.

## Quick start

```powershell
cd "C:\Users\sriva\Desktop\Me\hinge automation"

# MCP server
cd dating-assistant
npm install
npm run build
claude mcp add dating-assistant -- node "C:\Users\sriva\Desktop\Me\hinge automation\dating-assistant\dist\index.js"

# capture tool — on the laptop, no phone needed
#   Hinge runs inside the Android emulator; this boots it and wires the capture to it.
.\run-hinge.ps1 -Install    # first time only: sign into Play Store once, tap Install
.\run-hinge.ps1 -Capture    # Ctrl+Alt+H -> comment on clipboard, target = emulator window

# (alternative) mirror a real phone instead
# cd ..
# python -m venv .venv
# .\.venv\Scripts\python.exe -m pip install anthropic mss pynput pytest pillow
# $env:ANTHROPIC_API_KEY = "sk-ant-..."
# .\.venv\Scripts\python.exe "capture\hinge_capture.py"
```

## Which model writes the comment

Picked by `--provider` (default `auto`), or `HINGE_PROVIDER`:

| Provider | Needs | Default model | Override |
|---|---|---|---|
| `claude-cli` | the `claude` CLI, already logged in | `haiku` | `HINGE_CLAUDE_CLI_MODEL` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-opus-5` | `HINGE_ANTHROPIC_MODEL` |
| `openai` | `OPENAI_API_KEY` | `gpt-5.4-mini` | `HINGE_OPENAI_MODEL` |

`auto` takes `ANTHROPIC_API_KEY`, then `OPENAI_API_KEY`, then the `claude` CLI. The CLI path needs
no API key at all but spawns a full agent per capture, so it runs ~5-10s instead of ~2s.

## Tests

```powershell
cd dating-assistant; npm test          # 11 tests
cd ..; .\.venv\Scripts\python.exe -m pytest capture   # 11 tests
```
