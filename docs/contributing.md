# Contributing

## Set up

```powershell
pip install uv
uv sync
cd dating-assistant; npm install; cd ..
```

## Tests

```powershell
uv run pytest capture tools
cd dating-assistant; npm test
```

The `tools/` tests build synthetic profile pages from `tools/heart.png` and
noise, so they run without the emulator. Add a test when you change a detector,
the scroll mapping or anything in `run()` that decides what gets tapped.

## Rules for changes

- Ask mode stays the default. Every mode, including auto, must respect the
  daily cap and Stop. Changes that bypass either will not be merged.
- Never tap anything that can spend money. New screens that offer a purchase
  must stop the run, not be dismissed blindly.
- Check the screen before each irreversible tap, and raise `Stop` when it is not
  what you expect.
- Never commit anything from `people/` or `dating-assistant/data/`, including in
  tests or issue screenshots.
- Python 3.11+, managed with uv (`uv add <pkg>`). Keep the code flat; no new
  dependencies for what a few lines can do.
- Conventional commit prefixes: `feat:`, `fix:`, `docs:`, `test:`,
  `refactor:`, `chore:`.

## Re-tuning after a Hinge update

All positions are in the 415x923 frame unless marked device (1080x2400).

1. Save a frame of each screen involved:
   ```powershell
   uv run python tools\hinge.py shot
   ```
2. Open the saved PNG and measure the new positions.
3. Update what moved in `tools/hinge.py`:

| What | Where |
| --- | --- |
| Heart glyph | `tools/heart.png`, a 28x28 crop of the heart inside the like button |
| Heart column | `hearts()`: dark-circle check at x 342, match at x 345-347 |
| Scroll area | `TOP`, `BOTTOM` |
| Skip button | `SKIP` (device coordinates) |
| Send pill | `send_button()`, `purple()` |
| Comment box | `open_sheet()`: 68 px above the Send pill |
| Rose sheet | `rose_sheet()`; **Send Like anyway** is tapped 60 px below the pill |
| Profile screen | `profile_screen()`: white header at y 35-60 |

4. Run the tests, then check one profile with `run --cap` set to one more than
   today's count, watching every step.

Note the Hinge version you tuned against in
[getting-started.md](getting-started.md).
