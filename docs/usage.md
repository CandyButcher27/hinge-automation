# Usage

All commands run from the repository root. Hinge must be open on the
**Discover** tab, with the emulator window visible.

## `run`: like profiles with a person confirming each one

```powershell
uv run python tools\hinge.py run                # default mode
uv run python tools\hinge.py run --full         # scan the whole profile first
uv run python tools\hinge.py run --no-comment   # send likes without a message
uv run python tools\hinge.py run --cap 3        # stop after 3 likes today
```

For each profile, `run`:

1. Scrolls back to the top of the profile.
2. Scrolls down through it (see the modes below).
3. Asks `[y/n/q]` and waits for you.

| Answer | Effect |
| --- | --- |
| `y` | Opens the like sheet on a photo, types a random line from `prompts.txt`, taps Send |
| `n` | Taps Skip and waits for the next profile to load |
| `q` | Exits without touching the app |

`run` stops when today's likes reach `--cap`. It counts them from
`people/likes.log`, so the cap holds across separate runs on the same day.

### Modes

| Mode | What it scrolls | Which photo it likes |
| --- | --- | --- |
| default | a random 0-8 flicks down, stopping at the first photo after that | a random photo fully on screen there |
| `--full` | the whole profile, top to bottom | the first, second or last photo, at random |

Neither mode likes a video or a prompt card.

### Flags

| Flag | Default | Meaning |
| --- | --- | --- |
| `--cap N` | `5` | maximum likes per calendar day |
| `--full` | off | scan the whole profile before asking |
| `--no-comment` | off | send the like with no message |

### Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `HINGE_AVD` | `Medium_Phone_API_35` | AVD name; used to find the emulator window |
| `HINGE_CONSOLE_PORT` | `5554` | emulator console port |

## Comments: `prompts.txt`

`prompts.txt` at the repository root holds the comment pool, one per line.
Blank lines are ignored. `run` picks one line at random for each like.

Every line must be printable ASCII. `run` checks the whole file at start-up and
stops if a line has emoji, accented letters or other characters the emulator
console cannot type.

Write lines that fit any photo. `run` does not look at what the photo shows.

## Records: `people/`

Each sent like creates one folder and one log line. `people/` is gitignored.

```
people/
├── likes.log                    one line per like
└── 2026-09-28_231502/
    ├── 01.png, 02.png, ...      frames captured while scrolling
    └── profile.md               what was sent and when
```

`likes.log` is tab-separated: timestamp, folder name, which photo, comment.

```
2026-09-28 23:15:02	2026-09-28_231502	on-screen	you look so happy here, i love that
```

`profile.md` starts with the heading `# (not read)`. Replace it with the
person's name if you want to keep a readable record.

## Lower-level commands

Used when driving the app by hand, or by Claude Code during a session.

| Command | Effect |
| --- | --- |
| `shot` | Save the current emulator frame to `%TEMP%\hinge_last.png` and print its path |
| `scroll <folder>` | Scroll the current profile to the end, saving numbered frames |
| `like <heart_y> "<comment>"` | Tap the heart at device y, type the comment, stop before Send |
| `tap <x> <y>` | Tap device coordinates (1080x2400), then save a frame |

`like` does not tap Send. Tap it yourself, or with `tap`, after checking the
screenshot.

## Opener suggestions and the MCP server

- [capture.md](capture.md): hotkey that writes a tailored opener for the profile on screen
- [mcp-server.md](mcp-server.md): store profiles, preferences and conversations for Claude

## Tests

```powershell
uv run pytest capture tools
cd dating-assistant; npm test
```

No test touches the network, a model or the emulator.
