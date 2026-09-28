# Usage

All commands run from the repository root. Hinge must be open on the
**Discover** tab. The emulator window can sit behind other windows, but must
not be minimized.

## The web front end

```powershell
uv run python tools\ui.py              # opens http://127.0.0.1:8765/ in your browser
uv run python tools\ui.py --port 9000 --no-browser
```

The page shows the phone screen live and every setting below. Press **Start**,
then answer with the **y / n / q** keys on the page or on your keyboard. In ask
mode a comment box appears after `y`: send it as is, edit it, or choose
**no comment**. **Stop** ends the run before the next like. The log streams
under the controls, and **My comment list** edits `prompts.txt`.

The server listens on 127.0.0.1 only.

## `run` in the terminal

```powershell
uv run python tools\hinge.py run                   # ask mode, comment from prompts.txt
uv run python tools\hinge.py run --model           # comment written by a vision model
uv run python tools\hinge.py run --no-comment      # no comment
uv run python tools\hinge.py run --auto            # like without asking
uv run python tools\hinge.py run --full --cap 3    # scan whole profiles, at most 3 likes today
```

For each profile, `run` scrolls back to the top, scrolls down through it, then
either asks you or, in auto mode, likes it.

### Modes

| Mode | Flag | What happens on each profile |
| --- | --- | --- |
| Ask | (default) | Waits for `y` (like), `n` (skip) or `q` (quit). After `y` you can keep, rewrite or drop the comment |
| Auto | `--auto` | Pauses 4-12 s as if reading, then likes. Never skips |

Both modes stop when today's likes reach `--cap`. `run` counts them from
`people/likes.log`, so the cap holds across runs on the same day.

### Comment sources

| Source | Flag | Where the comment comes from |
| --- | --- | --- |
| List | (default) | A random line from `prompts.txt` |
| Vision model | `--model` | A model looks at the phone screen, with the chosen photo's like button circled, and writes one line about that photo |
| None | `--no-comment` | The like is sent without a message |

In ask mode, after `y` the terminal shows:

```
comment: 'love the lighting in this one' - enter to keep, type a new one, or - for none:
```

The vision model reply is reduced to printable ASCII before typing. If the model
call fails, the run logs it and uses a line from `prompts.txt` instead.

### Scroll depth

| Setting | Flag | What it scrolls | Which photo it likes |
| --- | --- | --- | --- |
| Random depth | (default) | a random 0-8 flicks, stopping at the first photo after that | a random photo fully on screen |
| Whole profile | `--full` | the whole profile | the first, second or last photo, at random |

Videos and prompt cards are never liked.

### All flags

| Flag | Default | Meaning |
| --- | --- | --- |
| `--cap N` | `5` | maximum likes per calendar day |
| `--auto` | off | like without asking |
| `--model` | off | vision model comments |
| `--no-comment` | off | no comment |
| `--provider` | `HINGE_PROVIDER`, else `auto` | `auto`, `claude-cli`, `anthropic` or `openai` |
| `--full` | off | scan the whole profile |

## Settings: `.env`

Copy `.env.example` to `.env` and uncomment what you need. Variables already set
in your shell win over the file.

| Variable | Default | Meaning |
| --- | --- | --- |
| `HINGE_PROVIDER` | `auto` | vision model provider |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` | | keys for the API providers |
| `HINGE_CLAUDE_CLI_MODEL` | `haiku` | model for `claude-cli` |
| `HINGE_ANTHROPIC_MODEL` | `claude-opus-5` | model for `anthropic` |
| `HINGE_OPENAI_MODEL` | `gpt-5.4-mini` | model for `openai` |
| `HINGE_AVD` | `Medium_Phone_API_35` | AVD name, used to find the emulator window |
| `HINGE_CONSOLE_PORT` | `5554` | emulator console port |

`auto` picks the Anthropic API if `ANTHROPIC_API_KEY` is set, then OpenAI if
`OPENAI_API_KEY` is set, then the `claude` CLI. The CLI uses your Claude Code
login and needs no key; each comment takes 15-25 s.

## Comment list: `prompts.txt`

One comment per line; blank lines are ignored. Every line must be printable
ASCII, because the emulator console cannot type emoji or accented letters. `run`
checks the whole file at start-up. Write lines that fit any photo: the list
source does not look at what the photo shows.

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

## Lower-level commands

| Command | Effect |
| --- | --- |
| `shot` | Save the current emulator frame to `%TEMP%\hinge_last.png` and print its path |
| `scroll <folder>` | Scroll the current profile to the end, saving numbered frames |
| `like <heart_y> "<comment>"` | Tap the heart at device y, type the comment, stop before Send |
| `tap <x> <y>` | Tap device coordinates (1080x2400), then save a frame |

## Tests

```powershell
uv run pytest capture tools
cd dating-assistant; npm test
```

No test touches the network, a model or the emulator.
