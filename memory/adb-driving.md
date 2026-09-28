# adb-driving — reading and liking profiles on the emulator

## Purpose
User-directed control of Hinge in the emulator via `adb shell input` + `screencap`, run from Claude's
shell. The user watches it happen live on the emulator window. `tools/hinge.py` (stdlib only) wraps the
fixed steps: `shot`, `scroll <folder>`, `like <heart_y> "<comment>"` (stops before Send), `tap <x> <y>`.
Taps, swipes and pauses are randomly jittered (coords +-12px, swipe 350-900ms, pauses 0.8-2.6s).
`scroll` uses `flick()`: start x 430-700 / y 1550-1900, distance 450-1000 device px at 0.9-1.8 px/ms, x drift +-60,
10% chance of a 150-350px scroll back up (never on the first flick, since at the top it would not move and would end the
loop), and 25% chance of a 2.5-5s dwell.

### Touch injection (since 2026-09-28)
Taps and drags no longer use `adb shell input`. `input` marks events as a virtual device with a fixed pressure.
- `sendevent` to `/dev/input/*` is **denied** (SELinux; the shell user is in group `input`, but this Play image has no root).
- Taps and drags go through the **emulator console** instead: telnet `127.0.0.1:5554`, `auth <~/.emulator_console_auth_token>`,
  then `event send EV_ABS:ABS_MT_...:v ... EV_SYN:0:0`. The name `SYN_REPORT` is rejected, so use the number.
  Events land on `/dev/input/event2` (`virtio_input_multi_touch_1`). That is the same device that mouse clicks on the emulator window use.
- Coordinates are raw 0-32767 (x*32767/1080, y*32767/2400). Android reads `ABS_MT_PRESSURE` (0-1024) with physical
  calibration, so 300 becomes 0.29. Touch size uses GEOMETRIC calibration, so TOUCH_MAJOR is sent as a finger-sized 1200-2200 raw (about 40-70px).
- `drag()` follows a minimum-jerk curve (s = 10t^3 - 15t^4 + 6t^5), which starts and ends slow. It bows +-30px sideways. Points are
  about 16ms apart. Pressure 150-500 rises and falls through the stroke. `tap()` sends 3-7 wobble points of +-2px over 40-170ms.
- Verified 2026-09-28 with `getevent`: 14 touch-downs and 14 releases, and 252 distinct pressure values. `scroll` took 13 frames and stopped at the end.
  Frames overlapped (one pair checked by eye).
- **Typing** also goes through the console: `event text <chunk>`, which lands on `qwerty2` (`/dev/input/event13`) as hardware key
  events. `event send EV_KEY:...` is answered OK but **never delivered** (checked with getevent), so it cannot be used.
  `event text` drops leading spaces and keeps trailing ones, so each chunk is one character plus an optional trailing space. Key gaps are
  lognormal (median 140ms), with a 0.35-0.9s gap after each space. Down/up hold time cannot be controlled. Only printable ASCII works, no emoji.
  Hardware keys make Gboard swap the soft keyboard for its floating toolbar, so `like` no longer sends ESC.
  The screen can lag behind the typing by about 1-2s. Verified 2026-09-28 in the Settings search box: `Hi there, it's 5 o'clock! you look really cute?` came out exact.
- `hinge.py` no longer calls adb at all. Everything goes through the console or the host window grab.

### `hinge.py run --cap N` (written 2026-09-28, NEVER RUN)
Loop: scroll the profile, then prompt y/n/q in the terminal. On y it picks the first, second or last photo at random and a random line from
`tools/comments.txt`, scrolls to that photo's heart and taps it. It swipes, finds the Send pill, taps the comment box (pill y - 68), types,
re-finds the pill and taps Send. If the Rose sheet appears it taps "Send Like anyway" once. It waits for a normal profile screen, then saves frames to
`people/<YYYY-MM-DD_HHMMSS>/` with a minimal profile.md and appends to `people/likes.log`, which the daily cap counts. n taps skip (X) and discards the frames.
Any unrecognised screen raises Stop, and nothing more is tapped.
- Frames are normalised to 415x923. `tools/heart.png` is a 28x28 crop of the heart glyph (circle at x 336-383).
- `offset()` is a coarse-to-fine match (4x downscale, d step 4, then +-4 at full res) over the whole overlap of two frames, with x 100-395 and y 70-836.
  An earlier small-block version gave a false -443. Verified 2026-09-28 on neee's 15 frames: every offset is plausible, it takes about 0.2s per pair,
  and it found 6 photos. That is correct; it is one purple photo seen in 3 frames, which the hand-written profile.md had double-counted.
  Heart search takes about 0.1s per frame (rows prefiltered on dark pixel (342, y)).
- `tools/test_hinge.py` builds synthetic noise pages and checks offsets forward/back and photo-vs-prompt mapping. It passes.
- **Videos (found 2026-09-28 on K):** a playing video makes consecutive screenshots differ forever. The old md5 end-check never fired, and
  `run` silently looped to its 40-flick limit. Now `look()` takes two screenshots 0.4s apart, and `still()` greys out rows that changed (>24 level on
  >~1% of the row, padded +-4) in a "flat" copy. `offset()` runs on the flat copies. The end of the profile is a forward flick with |offset| <= 2, and
  `rewind()` stops the same way (drag 600-750 device px, which stays inside the offset search range of -400..452). Hearts whose card rows (y-120..y-40)
  are moving count as video and are never chosen. Verified live on K: 12 frames, stopped at the end with the video playing, 5 photos plus the video excluded.
  `goto` to the second photo from the bottom landed on the right card (checked by eye).
- Live screen check (Discover profile): `profile_screen` True, `send_button` None, `rose_sheet` None. `rewind()` (drag down until
  the frame stops changing) reaches the top of the profile. **Still never checked live:** `send_button` / `rose_sheet` on real sheets,
  the full `open_sheet` -> `send_like` flow, and the skip tap.
Heart y, the Send button y and the optional Rose sheet still need a look at a screenshot.

## Scope agreed with the user (2026-09-26)
- One profile at a time, only on the user's explicit instruction, at human pace. Never loop over
  Discover liking everyone. The reason is Hinge ToS: bot-like liking risks an account ban.
- **Never tap anything that spends money without asking first**: Rose, "Boost your profile",
  HingeX "Benefits", or any purchase screen.
- The user has explicitly authorised sending likes with comments on their instruction.
- This contradicts the "never touches Hinge" statements in the root, `capture/` and
  `dating-assistant/` READMEs. Those READMEs have not been updated.

## Reading the screen
- **2026-09-28: Hinge's AppActivity now sets FLAG_SECURE** on every tab, so `adb screencap` returns black.
  The app build did not change (10.4.0, installed 2026-09-21), and device screenshots worked on 2026-09-26.
  So this is a server-side or account-level switch. The cause is unknown.
- `hinge.py` therefore grabs the emulator window on the host. It reuses `window_region` + `grab` from
  `capture/hinge_capture.py` and sets the window always-on-top so that other windows cannot cover it.
  Frames are 415x923. Multiply by 2.6 to get device coordinates. Run it with `.venv\Scripts\python.exe`
  because it needs `mss`. Verified 2026-09-28: `shot` works, and `scroll` took 13 frames and stopped at the end of the profile.
- The old `exec-out screencap` workflow below is dead while FLAG_SECURE is on.
- `uiautomator dump` returns **no text** for Hinge, so screenshots are the only source. Read them visually.
- Screenshot: `"$adb" exec-out screencap -p > file.png` (Git Bash; PowerShell redirection corrupts binary).
- Screenshots display at 900x2000. Multiply displayed coordinates by 1.2 to get device coordinates.

## Workflow: full profile
Scroll loop (Git Bash), one screenshot per step, stops when two consecutive screenshots are identical:
```bash
adb="$LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe"; d="people/<Name>_<YYYY-MM-DD>"; mkdir -p "$d"
prev=""; for i in $(seq -w 1 25); do
  "$adb" exec-out screencap -p > "$d/$i.png"; h=$(md5sum "$d/$i.png" | cut -d' ' -f1)
  [ "$h" = "$prev" ] && { rm "$d/$i.png"; break; }; prev=$h
  "$adb" shell input swipe 540 1700 540 900 600; sleep 1.5
done
```
Then read the screenshots and write `profile.md` (see [[people]]).

## Workflow: like with comment
1. Tap the heart icon (bottom-right of the card, x≈936) on the target photo or prompt. Take its y from the latest screenshot.
2. A like sheet opens with the photo, a comment box and a button row that starts below the screen.
   Tap the comment box at `720 2032`, then type the comment (`hinge.py like` does steps 1-3).
3. Swipe `540 1500 540 900` to bring the button row into view. **Screenshot and locate the button.**
   Its position varies: it was at y=2029 once and y=1680 another time.
4. The button reads **"Send Priority Like"**, and the send uses no paid feature. Since 2026-09-28 the account has
   **1 rose**, shown as a rose button left of Send. Never tap it. On 2026-09-28 Send was at device (684, 1820).
5. Sometimes a **"Send a Rose instead?"** sheet appears. Tap **"Send Like anyway"** at `540 2200`,
   never "Send a Rose". Other times Hinge skips that sheet and goes straight to the next profile.
6. Confirm by screenshot. Either "Nice, <name> will see your Like sooner." or the next profile loads.
7. Log it in that person's `profile.md` under `## Actions`.

The user's standing instruction for the comment is: last photo, "you look really cute". If the last photo does not show the person
(e.g. food), use the last photo that does, and say so.

## Fixed UI coordinates (device 1080x2400)
- Bottom tabs: Discover `115 2258` · Chats/Matches `756 2256`.
- Skip (X) button floats at about `134 2043`. Keep swipes and taps away from it.
- A floating stylus/handwriting toolbar appears on the left of the like sheet. It is harmless; ignore it.

## Testing
None automated. Every step is verified by screenshot before the next irreversible tap.
