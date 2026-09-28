# capture: screenshot to opener

`capture/hinge_capture.py` is a hotkey tool. Press the hotkey while a profile is
on screen. It sends a screenshot to a vision model, gets back an opening comment
aimed at one specific photo or prompt, and puts that comment on your clipboard.
You paste and send it yourself.

This tool only reads pixels from your own screen. It does not tap, type or send
anything in the app. The only outbound call is the screenshot going to the model
provider you choose.

```
your screen ──hotkey──► window grab ──► vision model
                                            │
                       your saved preferences (SQLite)
                                            ▼
                         target photo/prompt + comment
                                            ▼
                         clipboard  +  SQLite  +  console
```

## Setup

From the repository root:

```powershell
pip install uv
uv sync
```

Then choose a model provider:

| Provider | What it needs | Default model | Override |
| --- | --- | --- | --- |
| `claude-cli` | the `claude` CLI, signed in | `haiku` | `HINGE_CLAUDE_CLI_MODEL` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-opus-5` | `HINGE_ANTHROPIC_MODEL` |
| `openai` | `OPENAI_API_KEY` | `gpt-5.4-mini` | `HINGE_OPENAI_MODEL` |

`--provider auto` (the default) picks the Anthropic API if `ANTHROPIC_API_KEY`
is set, then OpenAI if `OPENAI_API_KEY` is set, then the `claude` CLI.
Set the provider with `--provider` or `HINGE_PROVIDER`.

## Run

With the emulator from [getting-started.md](getting-started.md):

```powershell
.\run-hinge.ps1 -Capture   # listen for Ctrl+Alt+H, capture the emulator window
.\run-hinge.ps1 -Once      # one capture, then exit
```

Or call the script directly:

```powershell
uv run python capture\hinge_capture.py --window Medium_Phone
uv run python capture\hinge_capture.py --list-windows
uv run python capture\hinge_capture.py --image C:\path\to\profile.png
```

`--image` analyses a saved PNG instead of the screen. It is the cheapest way to
check that your provider works.

| Flag | Default | Meaning |
| --- | --- | --- |
| `--hotkey` | `<ctrl>+<alt>+h` | pynput hotkey string |
| `--window` | `HINGE_WINDOW` | grab this window by title substring, tracked as it moves |
| `--list-windows` | | print visible window titles and exit |
| `--region` | `HINGE_REGION`, else whole monitor | `x,y,width,height`, fixed crop |
| `--monitor` | `1` | mss monitor index (`0` = all screens joined) |
| `--delay` | `0.4` | seconds between hotkey and grab |
| `--image` | | analyse a PNG file instead of the screen |
| `--once` | | capture immediately and exit |
| `--provider` | `HINGE_PROVIDER`, else `auto` | `auto`, `anthropic`, `openai`, `claude-cli` |

`--window` matches a title substring and reads the window position again on
every capture, so you can move or resize the window. It grabs the client area
only, without the title bar.

## Output

```
--- profile #7: Sam, 24
target (prompt): "My simple pleasures..."
why: most specific detail on screen, and it invites a concrete answer

  >> three hours is a commitment. what are you ordering?

alt: which shop is winning right now?
copied to clipboard - paste it into the app yourself
```

The `target` line tells you which photo or prompt to attach the comment to.
A screenshot that is not a profile prints `no profile on screen - nothing drafted`
and writes nothing.

## Preferences

The model writes the comment against the preferences stored in the shared
SQLite database. Set them through the MCP server (`set_preference`, see
[mcp-server.md](mcp-server.md)) or directly:

```sql
INSERT INTO preferences (category, value, created_at, updated_at)
VALUES ('communication style', 'dry, lowercase, no exclamation marks',
        datetime('now'), datetime('now'));
```

Useful categories: `communication style`, `interests`, `deal breakers`,
`relationship goals`.

## Shared database

Captures are written to `dating-assistant/data/assistant.db`, the file the MCP
server reads. Profiles go to `profiles` and comments to `drafts`.

Profiles are deduplicated by a SHA-256 fingerprint of name, age, occupation and
prompts. Capturing the same person twice updates the profile and adds a second
draft. Older databases get the `fingerprint` column added on first connect.

## Using a real phone instead of the emulator

The capture tool reads any window, so it also works with a mirrored Android
phone. [scrcpy](https://github.com/Genymobile/scrcpy) mirrors a phone to the
desktop over USB debugging:

```powershell
winget install Genymobile.scrcpy
scrcpy --window-title=hinge --stay-awake
uv run python capture\hinge_capture.py --window hinge
```

`tools/hinge.py` does not work with a mirrored phone. It needs the emulator
console for input.

## Tests

```powershell
uv run pytest capture
```

The tests cover fingerprint stability, insert and deduplication, empty fields,
preference rendering, the old-database migration, region parsing and the
response schema. No test calls a model or touches the screen.

## Limits

- The model reads only what is on screen. Scroll and capture again for prompts below the fold.
- The captured window must be visible and not minimised when the hotkey fires.
- Every capture is one model call on your own account or key.
