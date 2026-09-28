# Architecture

## Components

| Path | Language | Role |
| --- | --- | --- |
| `tools/hinge.py` | Python | Drives the emulator: scrolls, finds photos, types comments, sends likes |
| `tools/ui.py`, `tools/ui.html` | Python, HTML | Local web front end: live screen, settings, y/n/q, comment editor, log |
| `capture/hinge_capture.py` | Python | Window capture, `.env` loading, vision model calls, and the opener hotkey |
| `dating-assistant/` | TypeScript | Local MCP server over the shared SQLite database |
| `run-hinge.ps1` | PowerShell | Boots the emulator, sizes its window, installs Hinge, starts the hotkey |
| `prompts.txt` | text | Comment pool for likes |

```
                 Android emulator (Hinge)
          window pixels │        ▲ touch + text events
                        │        │ (console, 127.0.0.1:5554)
                        ▼        │
 ┌──────────────────┐  grab   ┌──┴───────────────┐
 │ capture/         │◄────────┤ tools/hinge.py   ├──► people/ (frames, likes.log)
 │ hinge_capture.py │         └──────────────────┘
 └───────┬──────────┘
         │ profiles, drafts
         ▼
 ┌──────────────────────────────┐        ┌─────────────────────┐
 │ dating-assistant/data/       │◄──────►│ dating-assistant/   │◄── Claude (MCP, stdio)
 │ assistant.db (SQLite)        │        │ MCP server          │
 └──────────────────────────────┘        └─────────────────────┘
```

`tools/hinge.py` imports window capture, `.env` loading and the vision model
calls (`photo_comment`) from `capture/hinge_capture.py`. It does not use the
database.

`tools/ui.py` runs `run()` in a background thread. `run()` takes three hooks:
`ask` (defaults to `input`), `say` (defaults to `print`) and `stopped`. The web
server supplies its own: `ask` publishes the pending question and blocks until
the page posts an answer, `say` appends to the log the page polls, and
`stopped` reads the Stop flag. The page polls `/state` and `/frame.png`; the
frame is the same host-side window grab the tool uses.

## Reading the screen

Hinge sets `FLAG_SECURE`, so `adb exec-out screencap` returns black frames and
the UI exposes no text to `uiautomator`. The only source is the pixels of the
emulator window on the Windows host.

`screen()` finds the window titled `Android Emulator - <AVD>:<port>` and asks
Windows to render its client area into memory (`PrintWindow` with
`PW_RENDERFULLCONTENT`, in `window_png()`). That works while other windows cover
the emulator; it fails only when the emulator is minimized. `frame()` scales every grab
to 415x923 so all pixel checks work at one scale, whatever the window size.
Device coordinates are frame coordinates times about 2.6 (`SX`, `SY`).

## Finding things on screen

Every detector is a small pixel heuristic on the 415x923 frame.

| Function | Finds | How |
| --- | --- | --- |
| `hearts()` | like buttons | Template match of `tools/heart.png` (28x28) down the column at x 345-347, only on rows where x 342 is dark (the black button circle) |
| `blank()` | prompt vs photo | A prompt card's heart sits on a white card; a photo's heart sits on the photo |
| `still()` | videos | Two grabs 0.4 s apart; rows that changed are marked moving and greyed out |
| `send_button()` | the Send pill | A dark horizontal band with white above and below and the purple rose button to its left |
| `rose_sheet()` | "Send a Rose instead?" | Dimmed header, purple rose icon, then the dark pill; returns the pill's y |
| `profile_screen()` | a profile is showing | White header, no Send pill, at least one photo heart |

## Mapping a profile

The Discover screen is one long scrolling page. To like "the second photo" the
tool needs positions on the whole page, not just on screen.

- `offset(a, b)` finds how far the page moved between two frames. It aligns
  the frames coarse-to-fine: a quarter-size search over -400 to +452 px, then a
  1 px search around the best match. A poor best match raises `Stop` instead of
  guessing.
- `map_profile()` sums the offsets into a page position for each frame and
  merges the hearts it saw into one sorted list of photo positions.
- `goto()` scrolls until a chosen photo's heart is on screen, re-measuring the
  offset after every stroke.
- The end of a profile is a forward flick that moves the page by 2 px or less.
  Moving rows (videos) are masked first, so a playing video does not look like
  movement.

## Sending input

All input goes over a TCP connection to the emulator console, authenticated
with `%USERPROFILE%\.emulator_console_auth_token`.

- Touches: `event send EV_ABS:ABS_MT_...` multi-touch events, positions scaled
  to the 0-32767 range, ending in `EV_SYN:0:0`.
- Text: `event text <chunk>`, one character plus an optional trailing space per
  command. The console trims leading spaces, and key events (`EV_KEY`) are
  accepted but never delivered, so this is the only working way to type.
- Every command is checked; a `KO` reply raises an error.

How taps, swipes and typing are randomised is in [anti-bot.md](anti-bot.md).

## One `run` iteration

```
rewind to top ─► scroll (random depth, or whole profile with --full)
      ─► ask y/n/q  (auto mode: 4-12 s pause, then y unless Stop was pressed)
            n ─► tap Skip ─► wait for a different profile screen
            q ─► exit
            y ─► pick photo ─► scroll to it
                 ─► comment: list line, vision model (--model) or none
                 ─► ask mode: keep, replace or drop it
                 ─► tap heart
                 ─► find Send ─► type comment ─► find Send again ─► tap Send
                 ─► handle Rose sheet if shown ─► wait for profile screen
                 ─► move frames to people/<timestamp>/, write profile.md, append likes.log
```

Every arrow that depends on the app is checked against a fresh screenshot. On
an unexpected screen the tool raises `Stop`, prints the reason and exits with
code 1. When Send or Skip leads to an unexpected screen, it also saves that
frame to `%TEMP%\hinge_last.png`.

## Shared database

`capture/` and the MCP server both use `dating-assistant/data/assistant.db`
(override with `DATING_ASSISTANT_DB` for the server). Tables: `preferences`,
`profiles`, `conversations`, `drafts`. See `capture/hinge_capture.py` (`SCHEMA`)
and `dating-assistant/src/db/schema.ts`.
