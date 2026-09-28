# Anti-bot measures

This page lists every measure in `tools/hinge.py` that makes its input look and
pace like a person using a phone, and what it cannot hide.

No measure here makes automation safe. Automating Hinge breaks its Terms of
Service, and the account can be banned. The strongest protection is the design
itself: a person approves every like, and the daily cap is low.

## Summary

| Area | Measure |
| --- | --- |
| Input device | Touches arrive on the emulator's touchscreen device, not a synthetic input device |
| Taps | Random position, pressure, contact size, duration and micro-movement |
| Swipes | Eased curves with a sideways arc, started from thumb rest spots |
| Scrolling | Random distance and speed, occasional scroll back, reading pauses |
| Typing | Per-character timing from a log-normal distribution, longer gaps between words |
| Pacing | Random pauses after every action; longer ones after Skip and after a like |
| Choices | Random scroll depth, random photo, random comment |
| Volume | A person answers y/n per profile; default cap of 5 likes a day |
| Screen reading | Pixels come from the host window; nothing runs inside the device |
| Money | Rose, Boost and subscription controls are never tapped |

Coordinates below are device pixels on the 1080x2400 screen. Pressure and
contact size are raw values of the emulator's touchscreen (pressure max 1024).

## Input device

`adb shell input tap` and `input swipe` inject events from a virtual input
device. Every event has pressure 1.0 and no contact size, which is easy to tell
apart from a finger.

`hinge.py` instead sends raw multi-touch events through the emulator console
(`event send` on `127.0.0.1:5554`). They arrive on the emulator's virtio
touchscreen, the same device that receives mouse clicks on the emulator window.
Each event carries position, pressure and contact size, like a real touch
panel (multi-touch protocol B: slot 0, a random tracking ID per touch).

## Taps

Each tap (`tap()` and `touch()`):

- Lands at a random point near the target, up to 12 px away on each axis,
  weighted toward the centre (triangular distribution).
- Is 3 to 7 touch samples, not one. Each sample moves up to 2 px, as a finger
  rolls slightly on the glass.
- Has a random base pressure of 150-500, varying by up to 40 between samples.
- Has a random contact size (`TOUCH_MAJOR` 1200-2200) with the minor axis
  75-95 % of the major, so the contact is an oval.
- Holds for a random 12-25 ms between samples, so the total press time varies.

## Swipes

Each scroll stroke (`stroke()` and `drag()`):

- Starts where a thumb rests when holding a phone in one hand: either just above
  the Skip button (x 90-260) or just above the like-button column
  (x 820-1000), chosen at random each stroke. Upward strokes start at
  y 1650-1880, downward strokes at y 500-900.
- Drifts sideways by up to 60 px between start and end.
- Follows a smootherstep curve (slow start, fast middle, slow end) instead of
  constant speed.
- Bows sideways by up to 30 px in an arc, as a thumb pivots.
- Presses harder in the middle of the stroke than at its ends.
- Sometimes rests on the glass for up to 8 samples before moving.
- Moves at a random 0.6-1.8 px per ms, with one sample about every 16 ms and
  ±20 % jitter on each interval.

## Scrolling a profile

- Each flick travels a random 450-1000 px.
- About 1 flick in 10 scrolls back up 150-350 px instead, as a person does when
  re-checking a photo (never on the first flick).
- After a flick the tool pauses 0.9-2.2 s. One pause in four is a longer
  2.5-5 s "reading" pause.
- In the default mode the tool stops after a random 0-8 flicks, so it does not
  read every profile to the end. `--full` reads the whole profile.

## Typing

Comments are typed one character at a time with `event text`:

- The gap after each letter is drawn from a log-normal distribution with a
  median of 140 ms, so most gaps are short and a few are long.
- The gap after a space is a longer 0.35-0.9 s, as between words.
- Only printable ASCII can be typed. The tool refuses other characters instead
  of pasting them.

## Pacing

| After | Pause |
| --- | --- |
| every tap | 0.8-2.2 s |
| opening the like sheet | 1.2-2.6 s |
| Skip | 2-6 s |
| a sent like | 3-8 s |

A person also answers the y/n/q prompt for every profile, which adds the real
reading time of a human between profiles.

## Choices

- The comment is a random line from `prompts.txt`, or none with `--no-comment`.
- The liked photo is random: any photo on screen in the default mode, or the
  first, second or last in `--full` mode.
- Videos and prompt cards are never liked.

## Volume

- `run` never likes without a `y` from the person at the keyboard.
- `--cap` (default 5) limits likes per calendar day, counted from
  `people/likes.log`, so it holds across restarts.
- Nothing runs in the background or on a schedule.

## Screen reading

- Hinge marks its screens secure (`FLAG_SECURE`), so in-device screenshots are
  black. The tool does not try to disable that. It reads the emulator window
  on the Windows host instead, the same pixels you see.
- No `adb shell` command, accessibility service or UI dump runs while liking.
  Nothing is installed inside the emulator besides Hinge.

## Money

- The Rose button, Boost, HingeX and subscription screens are never tapped.
- When the "Send a Rose instead?" sheet appears after Send, the tool taps
  **Send Like anyway**.
- Every step checks the screen before the next tap: the like sheet must be open,
  Send must be found, and the profile screen must come back. On anything else the
  tool stops and saves a screenshot instead of guessing.

## What this does not hide

- **The emulator itself.** An Android emulator has a detectable build
  fingerprint, sensors and hardware. Hinge has not blocked the emulator in
  testing, but it could.
- **Timing models are guesses.** The ranges above were chosen by hand, not fitted
  to recordings of real phone use.
- **Account-level signals.** Like rate, message style, and when you are active
  are visible to Hinge no matter how input is sent. The cap and per-profile
  confirmation are the controls for that.
- **Repeated comments.** A small `prompts.txt` sends the same lines to many
  people. Keep the pool large and personal.
