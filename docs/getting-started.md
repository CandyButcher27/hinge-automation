# Getting started

## Supported setup

`tools/hinge.py` finds every button from screen pixels, so it only works on the
setup it was tuned on. Other setups may work but are not tested.

| Part | Supported | Why it matters |
| --- | --- | --- |
| OS | Windows 11 | Window capture and window placement use Win32 APIs |
| Emulator | Android Studio emulator | Touch and typing go through its console on `127.0.0.1:5554` |
| Device profile | Medium Phone, 1080x2400 | Coordinates and pixel checks assume this screen shape |
| System image | API 35, Google Play | Hinge installs from the Play Store; no root needed |
| Hinge | 10.4.0, English, light theme | Layout and colours were measured on this build (September 2026) |
| Python | 3.11+, managed by [uv](https://docs.astral.sh/uv/) | `capture/` and `tools/` |
| Node.js | 22.5+ | `dating-assistant/` uses the built-in `node:sqlite` module |

A different screen size or a Hinge update can move buttons. The tool then stops
with an error instead of tapping the wrong place. See
[troubleshooting.md](troubleshooting.md) and the re-tuning notes in
[contributing.md](contributing.md).

A real phone is not supported for liking. The capture tool alone can read a
mirrored phone; see [capture.md](capture.md).

## 1. Install the tools

```powershell
git clone https://github.com/CandyButcher27/hinge-automation.git
cd hinge-automation
pip install uv
uv sync
```

`uv sync` creates `.venv` with every Python dependency from `uv.lock`.

For the MCP server (optional):

```powershell
cd dating-assistant
npm install
npm run build
cd ..
```

## 2. Create the emulator

1. Install [Android Studio](https://developer.android.com/studio).
2. Open **Device Manager** and create a virtual device:
   - Hardware: **Medium Phone** (1080x2400)
   - System image: **API 35**, with the **Google Play** label
3. Name it `Medium_Phone_API_35` (the default name for that choice).

If you use another name, pass it to both tools:

```powershell
$env:HINGE_AVD = "My_AVD_Name"
.\run-hinge.ps1 -Avd My_AVD_Name
```

`run-hinge.ps1` looks for the SDK in `%LOCALAPPDATA%\Android\Sdk`. Pass
`-SdkRoot <path>` if yours is elsewhere.

## 3. Boot it and install Hinge

```powershell
.\run-hinge.ps1            # boots the emulator and sizes its window to your screen
.\run-hinge.ps1 -Install   # first time only: opens the Play Store page for Hinge
```

Sign in to the Play Store in the emulator, tap **Install**, then open Hinge and
sign in to your own account. Leave Hinge on the **Discover** tab.

The emulator writes its console token to `%USERPROFILE%\.emulator_console_auth_token`
on first boot. `hinge.py` reads that file to connect.

## 4. Add your comments and settings

Edit [`prompts.txt`](../prompts.txt) at the repository root. Each line is one
comment that can be sent with a photo like. Use printable ASCII only; the
emulator console cannot type emoji or accented letters.

For comments written by a vision model, copy `.env.example` to `.env`. The
default provider, `claude-cli`, uses your Claude Code login and needs no key.
To use an API instead, set `HINGE_PROVIDER` and the matching key there.

## 5. Run

```powershell
uv run python tools\ui.py                  # web front end
uv run python tools\hinge.py run --cap 1   # or the terminal
```

Keep the emulator window visible and do not cover it with another window,
including the browser. The tool reads the screen from that window. In the
default ask mode you answer `y`, `n` or `q` for each profile. See
[usage.md](usage.md) for every mode and flag.

## Next

- [usage.md](usage.md): modes, comment sources, the web front end, records
- [safety.md](safety.md): what the tool will and will not do
- [anti-bot.md](anti-bot.md): how input is made to behave like a person
