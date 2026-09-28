# Troubleshooting

## Messages from `hinge.py`

Every `stopped: ...` message means the tool saw something it did not expect and
stopped before tapping. Look at the emulator, fix the screen by hand, and run
again.

| Message | Likely cause | What to do |
| --- | --- | --- |
| `ConnectionRefusedError` on start | Emulator not running, or console on another port | Start it with `.\run-hinge.ps1`; set `HINGE_CONSOLE_PORT` if the serial is not `emulator-5554` |
| `FileNotFoundError: ...emulator_console_auth_token` | Emulator never booted on this account | Boot it once with `.\run-hinge.ps1` |
| `emulator console rejected an event` | Console refused a command | Restart the emulator |
| `no photos found - is a profile on screen?` | Not on Discover, or the window is covered | Open Discover; move other windows off the emulator |
| `no photo found on this profile` | Profile has only prompts and videos | Answer by hand, or skip it |
| `lost track of the scroll position` | Screen changed between two frames (popup, reload, another profile) | Check the screen, return to the profile top, run again |
| `could not scroll to the chosen photo` | Page moved while scrolling back | Run again |
| `like sheet not found after tapping the heart` | Heart missed, or the sheet looks different | Check the screen; see "After a Hinge update" |
| `Send button not found after typing` | Keyboard or sheet layout changed | Check the screen; see "After a Hinge update" |
| `unexpected screen after Send, see ...hinge_last.png` | A popup appeared after Send | Open the saved frame; handle the popup by hand |
| `Skip did not bring up the next profile, see ...` | Skip missed, or no more profiles | Open the saved frame |
| `comment '...' is not printable ASCII` | A line in `prompts.txt` has emoji or accents | Edit that line |
| `daily cap of N likes reached` | `--cap` reached for today | Wait until tomorrow, or raise `--cap` |

## The scan sees 0 photos although a profile is on screen

Another window (often a new console window) overlaps the emulator. The tool
grabs screen pixels, so it captures whatever is on top. Move the window off the
emulator, or run the tool from a terminal placed beside it.

## Emulator

| Symptom | Fix |
| --- | --- |
| Hinge renders fully black | Start the emulator with `-gpu swiftshader_indirect` (`run-hinge.ps1` does this) |
| Emulator window opens off-screen or too tall | Run `.\run-hinge.ps1` again; it resizes and centres the window |
| `run-hinge.ps1` fails with `NativeCommandError` about the adb daemon | Fixed in the script; if it returns, run `adb start-server` once by hand |
| `adb exec-out screencap` returns black images | Expected: Hinge marks its screens secure. The tools read the host window instead |
| `adb shell getevent /dev/input/...` prints usage from Git Bash | Git Bash rewrote the path. Prefix the command with `MSYS_NO_PATHCONV=1` |
| Binary output from adb is corrupt | Run `adb exec-out` commands from Git Bash, not PowerShell |

## Capture tool

| Symptom | Fix |
| --- | --- |
| `no visible window matching ...` | Check the title with `--list-windows`, pass part of it to `--window` |
| `window ... is 0x0 - minimized?` | Restore the window |
| `set ANTHROPIC_API_KEY or OPENAI_API_KEY, or install the claude CLI` | Configure a provider, see [capture.md](capture.md) |
| `could not open the clipboard` | Another app holds the clipboard; try again |

## After a Hinge update

Hinge changes its layout from time to time. The detectors in `tools/hinge.py`
then stop finding buttons, and the tool stops with one of the messages above
instead of tapping blindly. To re-tune, see "Re-tuning after a Hinge update" in
[contributing.md](contributing.md).
