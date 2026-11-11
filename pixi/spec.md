# hinge-automation — landing page spec

Brief: landing page for hinge-automation, a human-in-the-loop Hinge helper that drives an Android emulator on a Windows PC, for people who want fewer, better-considered likes.

Reference: archier.com.au (luxurious feel). Borrowed: one full-bleed image carrying the whole first screen, small white Helvetica set in the corners, warm film-still colour, a strip of thumbnails in the lower right. Not borrowed: layout grid, photography, logo, copy.

## Concept
The phone at dusk on a walnut desk, scrolling slowly by itself, and a hand that only ever moves when you say yes. The page is one long evening: every section is the same desk, lit lower.

## Material
Matte film still. Walnut grain drawn as fine wavering SVG lines, brass edges, the emulator glass with a faint reflection band. A light film grain (SVG feTurbulence, 6 % opacity) over everything. No paper, no cream.

## Mood and palette
Quiet, private, unhurried, expensive.
- Ink `#120e0c` — page ground, the night
- Walnut `#2a1d16` — desk, panels
- Tan `#a8865f` — wood highlights, fine rules
- Stone `#d8cdbf` — body text, phone frame
- Brass `#d4a35a` — reserved: the like, the cap counter, the one call to action

## Typography
- Display: Palatino Linotype / Palatino / "Book Antiqua" / Georgia, regular and italic, large and light-handed, tight leading.
- Labels and body: "Helvetica Neue", Helvetica, Arial, light weights, 12–15 px, generous tracking on labels.
- Figures: Palatino with tabular numerals.

## Structure
1. **Hero (full bleed)**. The desk scene fills the viewport. Top left, stacked small links: Modes, Comments, The hand, Safety, Install. Bottom left: `hinge-automation`. Bottom centre, two lines: "Fewer likes. / Each one meant —". Bottom right: thumbnail strip of five drawn profile cards, the active one framed in brass.
2. **01 The pace**. Headline "It reads before it likes." Copy: "Ask mode stops on every profile and waits for y, n or q. Auto mode pauses 4 to 12 seconds as if reading, then likes. Both stop at a daily cap of 5 that holds across runs." Large figure: `5` / "a day, by default".
3. **02 The words**. Headline "Your words, its eyes, or silence." Three columns as a ledger: From my list — a random line from prompts.txt (40 lines); Vision model — one line written about the chosen photo; None — the like, unaccompanied. The comment types itself out from the real list.
4. **03 The hand**. Headline "Touch, not injection." Specs set as a quiet table: pressure 150–500 of 1024, contact 1200–2200, 3–7 samples per tap, offset up to 12 px, thumb rests x 820–1000, typing on a log-normal rhythm. Illustration: a pressure oval breathing.
5. **04 What it will not do**. "Never taps a Rose, a Boost or HingeX. Never messages. Never runs on a schedule. Stops, without tapping, when the screen is not what it expects." Plus the ToS warning in full sentence form.
6. **05 Begin**. Install block: `uv sync`, `.\run-hinge.ps1`, `uv run python tools\ui.py`. Brass link to the repository.

## Signature moment
The phone in the hero is a working miniature of the run loop. A drawn profile scrolls in eased strokes with a sideways arc; a brass thumb trace draws the curve each stroke followed, starting from the thumb rest at the right edge. It stops, and three keys appear under the phone: y, n, q. Press `y` (key or click): the heart on the visible photo fills brass, the comment field types a random real line from prompts.txt with per-character log-normal delays, the counter rises 1 → 5. Press `n`: the card slides away left and the next profile arrives. At 5 the phone dims and says "Cap reached. See you tomorrow." `q` resets. With no input for 6 s, the page answers itself (alternating n, y) so it is never still.

## Motion
Entrance (2.4 s): the walnut grain lines draw left to right (stroke-dashoffset, 1.4 s, `cubic-bezier(0.19,1,0.22,1)`), then the phone frame clip-wipes up, then the display copy rises 12 px and fades in, last the thumbnails one by one at 90 ms.
Idle: the lamp glow drifts on a slow sine (9 s); the grain shimmer; the phone breathes 2 px.
Pointer: moving over the hero shifts the lamp reflection on the glass toward the cursor (spring). In section 03 the pointer becomes a touch: pressing anywhere draws a pressure oval sized by press duration with its pressure value written beside it.
Sections reveal with a 1.2 s eased rise once.

## Reduced motion
The phone shows one profile, already liked, comment fully written, counter at 1 of 5. Grain lines drawn, no drift, no breathing. Keys still work but change state instantly. The touch oval appears without growth.
