<p align="center">
  <img src="docs/assets/header.gif" alt="hinge-automation" width="100%">
</p>

# hinge-automation

A Hinge helper that runs Hinge in the Android emulator on your Windows PC. It
scrolls each profile the way a person would, picks a photo and sends a like,
with a comment from your own list, one written by a vision model, or none.
By default it asks you before every like; an auto mode likes on its own up to a
daily cap. Drive it from the terminal or from a local web page that shows the
phone screen live.

```text
> uv run python tools\hinge.py run --cap 5
scanning profile...
stopped here, 2 photo(s) on screen. like one? [y/n/q] y
comment: 'okay i need the story behind this photo' - enter to keep, type a new one, or - for none:
liking the on-screen photo: 'okay i need the story behind this photo'
sent (1/5 today), saved to C:\src\hinge-automation\people\2026-09-28_231502
scanning profile...
stopped here, 1 photo(s) on screen. like one? [y/n/q] q
```

> [!WARNING]
> Automating Hinge is against its Terms of Service and can get your account
> banned. Use this on your own account, at your own risk. This project is not
> affiliated with Hinge or Match Group. Read [docs/safety.md](docs/safety.md)
> first.

## Features

- **Two modes.** Ask mode stops on each profile for `y`, `n` or `q`. Auto mode
  (`--auto`) likes every profile it scans. Both stop at a daily cap (default 5)
  that holds across runs.
- **Three comment sources.** A random line from [`prompts.txt`](prompts.txt), a
  comment a vision model writes about the chosen photo (`--model`), or no
  comment (`--no-comment`). In ask mode you can keep, rewrite or drop each one.
- **Web front end.** `tools\ui.py` serves a local page with the live phone
  screen, every setting, y/n/q keys, the comment editor, the run log and your
  comment list.
- **Human-like input.** Taps and swipes go to the emulator's touchscreen device
  with random pressure, contact size, curves and timing. Typing has
  per-character rhythm. See [docs/anti-bot.md](docs/anti-bot.md).
- **Reads the screen from outside the phone.** Hinge blocks in-device
  screenshots, so every image, including the one sent to the vision model, is
  taken from the emulator window on your desktop.
- **Never spends money.** Roses, Boosts and subscriptions are never tapped.
- **Stops instead of guessing.** Every step is checked against a fresh
  screenshot. On an unexpected screen it stops before the next tap.
- **Extras.** A hotkey that drafts an opener for the profile on screen, and an
  MCP server that keeps preferences, profiles and drafts for Claude.

## Supported setup

The tool finds buttons from pixels, so it is tuned to one setup:

- Windows 11
- Android Studio emulator, **Medium Phone** (1080x2400), **API 35 Google Play** image
- Hinge 10.4.0, English, light theme
- Python 3.11+ with [uv](https://docs.astral.sh/uv/); Node.js 22.5+ for the MCP server
- For vision comments: the `claude` CLI signed in, or an Anthropic or OpenAI API key

Other screens or Hinge versions may need re-tuning. See
[docs/getting-started.md](docs/getting-started.md).

## Quick start

```powershell
git clone https://github.com/CandyButcher27/hinge-automation.git
cd hinge-automation
pip install uv
uv sync
copy .env.example .env     # optional: pick the vision model provider

.\run-hinge.ps1            # boot the emulator (create the AVD in Android Studio first)
.\run-hinge.ps1 -Install   # first time: install Hinge from the Play Store, then sign in

uv run python tools\ui.py  # opens the web front end
```

Keep the emulator window open (it may sit behind other windows, but not minimized).
Full steps are in [docs/getting-started.md](docs/getting-started.md).

## Usage

```powershell
uv run python tools\hinge.py run                      # ask mode, comment from prompts.txt
uv run python tools\hinge.py run --model              # comment written by a vision model
uv run python tools\hinge.py run --no-comment         # like without a message
uv run python tools\hinge.py run --auto --cap 3       # like without asking, at most 3 today
uv run python tools\hinge.py run --full               # scan the whole profile first
uv run python tools\ui.py                             # the same, from a web page
```

Each sent like saves the profile frames and a short record under `people/`,
which is gitignored. Details: [docs/usage.md](docs/usage.md).

## Repository layout

```
.
├── tools/              hinge.py (emulator driver), ui.py + ui.html (web front end), tests
├── capture/            vision model calls, window capture, opener hotkey
├── dating-assistant/   MCP server (TypeScript) over the shared SQLite database
├── docs/               documentation
├── prompts.txt         your comment list
├── .env.example        provider, API keys, model and emulator settings
├── run-hinge.ps1       emulator launcher
└── people/             local records of sent likes (gitignored)
```

## Documentation

| Page | Contents |
| --- | --- |
| [Getting started](docs/getting-started.md) | Supported setup, install, first run |
| [Usage](docs/usage.md) | Modes, comment sources, the web front end, records |
| [Safety](docs/safety.md) | What the tool will and will not do; other people's data |
| [Anti-bot measures](docs/anti-bot.md) | How input and pacing are made human-like, and their limits |
| [Architecture](docs/architecture.md) | Screen reading, button detection, input path |
| [Capture tool](docs/capture.md) | Opener hotkey |
| [MCP server](docs/mcp-server.md) | Claude tools for profiles, preferences and drafts |
| [Troubleshooting](docs/troubleshooting.md) | Error messages and emulator fixes |
| [Contributing](docs/contributing.md) | Tests, rules, re-tuning after a Hinge update |

## Tests

```powershell
uv run pytest capture tools
cd dating-assistant; npm test
```

No test touches the network, a model or the emulator.

## License

[MIT](LICENSE)
