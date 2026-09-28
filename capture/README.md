# capture — screenshot → comment on your clipboard

Press a hotkey while a profile is on your screen. It reads the screen, writes an
opening comment aimed at one specific photo or prompt, and puts it on your
clipboard. You paste it and send it yourself.

## Where the data comes from

Pixels on your own screen. Nothing here connects to Hinge or any other service —
no API calls, no login, no cookies, no network inspection, no page scraping. If
the app is on your phone, mirror the phone to your desktop (Phone Link, scrcpy)
and point the capture at that window. Mirroring is you looking at your own
screen.

The one outbound call is the screenshot going to the Anthropic API for analysis.

```
your screen ──hotkey──► mss grab ──► Claude Opus 5 (vision)
                                          │
                     your saved preferences (SQLite)
                                          ▼
                     target photo/prompt + comment
                                          ▼
                        clipboard  +  SQLite  +  console
                                          ▼
                              you paste, you send
```

## Run Hinge on the laptop — no phone needed

Hinge only ships a phone app, so the phone-free way to run it is inside an
Android emulator on your own machine. The `run-hinge.ps1` launcher at the repo
root does the whole loop:

```powershell
.\run-hinge.ps1            # boots the emulator and prints the next steps
.\run-hinge.ps1 -Install   # opens the Play Store to the Hinge page (sign in once, tap Install)
.\run-hinge.ps1 -Capture   # hotkey -> comment on clipboard, targeting the emulator window
.\run-hinge.ps1 -Once      # single capture, then exit
```

No phone, no USB cable, no developer options, no permission bypass. The one
one-time step that only you can do is signing in to the Play Store inside the
emulator with your own Google account and tapping Install.

## Alternative: mirror your phone (Android)

If you would rather use your phone, `scrcpy` mirrors it to the desktop so the
capture tool reads your own screen:

```powershell
winget install Genymobile.scrcpy
```

On the phone: Settings -> About phone -> tap **Build number** seven times ->
back -> Developer options -> **USB debugging** on. Plug in over USB and accept
the "Allow USB debugging?" prompt.

```powershell
scrcpy --window-title=hinge --stay-awake
```

After the first USB pairing you can go wireless — same wifi, phone still plugged
in for one command:

```powershell
scrcpy --tcpip --window-title=hinge --stay-awake
```

Unplug once it connects. Open Hinge on the phone; it shows in the scrcpy window.

## Setup

```powershell
cd "C:\Users\sriva\Desktop\Me\hinge automation"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install anthropic mss pynput pytest pillow
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

`pillow` is optional — it downscales large screenshots before upload, which cuts
cost. Without it the full-size PNG is sent.

If you use `ant auth login` instead of an API key, no env var is needed — the SDK
picks up the profile.

## Run

Listen for the hotkey (default `Ctrl+Alt+H`), grabbing just the scrcpy window:

```powershell
.\.venv\Scripts\python.exe "capture\hinge_capture.py" --window hinge
```

`--window` matches on a title substring and re-reads the window position on every
capture, so you can move or resize it freely. It grabs the client area only — no
title bar, no desktop behind it. Forget the title you gave scrcpy:

```powershell
.\.venv\Scripts\python.exe "capture\hinge_capture.py" --list-windows
```

One-shot, no hotkey:

```powershell
.\.venv\Scripts\python.exe "capture\hinge_capture.py" --once
```

Test on a saved screenshot — no screen grab, cheapest way to check your setup:

```powershell
.\.venv\Scripts\python.exe "capture\hinge_capture.py" --image "C:\path\to\profile.png"
```

Options:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--hotkey` | `<ctrl>+<alt>+h` | pynput hotkey string |
| `--window` | — | grab this window by title substring, tracked as it moves |
| `--list-windows` | — | print visible window titles and exit |
| `--region` | whole monitor | `x,y,width,height` — fixed crop, if you prefer coords |
| `--monitor` | `1` | mss monitor index (`0` = all screens joined) |
| `--delay` | `0.4` | seconds between hotkey and grab |
| `--image` | — | analyze a PNG file instead of the screen |

Use `--window` over `--region` — same benefit (less noise for the model, fewer
tokens, better comments) without hand-measuring coordinates, and it survives
moving the window.

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

## Preferences

The comment is written against the preferences in the shared SQLite database.
Set them through Claude and the MCP server (`set_preference`), or directly:

```sql
INSERT INTO preferences (category, value, created_at, updated_at)
VALUES ('communication style', 'dry, lowercase, no exclamation marks',
        datetime('now'), datetime('now'));
```

Useful categories: `communication style`, `interests`, `deal breakers`,
`relationship goals`.

## Shared database

Writes to `../dating-assistant/data/assistant.db` — the same file the MCP server
reads. Profiles land in `profiles`, comments in `drafts`. Ask Claude to
`list_profiles` or `list_drafts` to review them later.

Profiles are deduped by a SHA-256 fingerprint of name + age + occupation +
prompts. Capturing the same person twice updates the profile and adds a second
draft rather than creating a duplicate. Old databases are migrated automatically
(the `fingerprint` column is added on first connect).

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest capture
```

Covers fingerprint stability and order-independence, insert/dedupe, empty-field
handling, preference rendering, the old-database migration, region parsing, and
the response schema. No test hits the network or any dating service.

## Limits

- The model reads only what is on screen. Scroll the phone and capture again for prompts below the fold.
- scrcpy must be in the foreground and not minimized when you fire the hotkey.
- A screenshot that is not a profile returns `no profile on screen` and writes nothing.
- Every capture is one API call against your own key.
