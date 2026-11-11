# hinge-automation — one-screen page spec

Brief: a single fixed screen for hinge-automation, a human-in-the-loop Hinge helper that drives an Android emulator. No scroll. The phone is the hero; its screen is a slot that will show the real emulator.

References (Unsplash, viewed 2026-11-11):
- unsplash.com/photos/Kx3GDDf_gWc — evening sun through blinds raking across a wooden counter, phone lying flat, iced coffee. Borrowed: diagonal slat light, long warm shadows, top-down camera.
- unsplash.com/photos/girB-ESnfq0 — dark walnut nightstand, phone resting face down, seen from above. Borrowed: deep red-brown wood, quiet emptiness.
Not borrowed: the photographs themselves, composition, products.

## Concept
A walnut table at 18:47. The sun comes through a blind and lies across the wood in slats; a plant out of frame throws leaf shadows that sway. The phone lies on the table, face up, doing the work. Your pointer is the sun.

## Material
Walnut drawn with stretched fractal noise (SVG feTurbulence, grain running diagonally), oiled, with a soft sheen. Light is warm slats with blurred edges. A black letterpress card with brass foil type. A cut-crystal tumbler of whisky throwing a shimmering amber caustic. Three dark keycaps with brass letters.

## Palette
- Walnut `#2b1810`, deep shadow `#0d0705`
- Slat light `#ffc47a`
- Card black `#14100d`, stone type `#d8cdbf`
- Brass `#d4a35a` — reserved for the like key, the counter and the written line

## Typography
Palatino Linotype / Palatino / Book Antiqua / Georgia for display and the card line (italic). Helvetica Neue / Helvetica / Arial light for small labels.

## Layout (one viewport, overflow hidden)
- Top left: `hinge-automation`. Top right: `GitHub`.
- Centre-right: the phone, flat, rotated -8°, ~78vh tall, long soft shadow toward bottom-left. Screen = `#screen` slot.
- Left-bottom: the card. "Tonight's line" / the comment in brass italic / "1 of 5 tonight".
- Right of the phone, low: keycaps y, n, q.
- Top right of the phone: the tumbler and its caustic.
- Bottom left over the wood: "Fewer likes. / Each one meant —"

## Signature moment
Press y (key or click): the keycap sinks (shadow shrinks, 2 px), the card's line writes itself letter by letter from prompts.txt on a log-normal rhythm, a brass heart is pressed into the card, the counter rises; at 5 the card reads "That's tonight. See you tomorrow." n: the line fades and a new one is chosen. q: a new evening, counter 0. Idle 7 s: the page answers on its own.

## Motion
Entrance: the room starts dark; the light fades up over 2.4 s, the phone settles from 1.03 scale with its shadow tightening, then the card and keys rise.
Idle: the slats drift slowly (60 s cycle), leaf shadows sway on layered sines, the caustic shimmers, the whisky surface breathes.
Pointer: moving the pointer shifts the slats and the shadow angle a little, with a spring.

## Reduced motion
Light fully up, no drift, no sway, no shimmer. Keys change the card instantly.

## Live emulator
When served by `tools/ui.py` (http), the slot loads `/frame.png` every second; opened as a file it shows the drawn placeholder.
