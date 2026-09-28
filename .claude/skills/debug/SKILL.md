---
name: debug
description: Find the root cause of a bug, test failure, or unexpected behavior before proposing any fix — reproduce, instrument component boundaries, trace the bad value back to its origin, form one hypothesis, test it minimally, then fix at the source and verify with fresh evidence. Use when the user says "/debug", reports something broken or failing, asks why code misbehaves, or when a previous fix did not hold. Also use when tempted to guess.
---

# debug — root cause before fix

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

A symptom fix is a failure, even when the symptom disappears. It leaves every
sibling caller broken and the next session re-finds the same bug wearing a
different hat.

Use it hardest exactly when it feels skippable: under time pressure, when the
fix looks obvious, when you've already tried something and it didn't work.

---

## Phase 1 — Root cause

**Read the error completely.** Full stack trace, line numbers, paths, exit
codes. The answer is often in text already on screen. A caught-and-logged
exception hides the line that matters — find the original.

**Reproduce.** Exact steps, every time? Not reproducible → gather more data.
Never guess in place of a repro.

**Check what changed.** `git diff`, recent commits, new dependencies, config,
environment differences. Working yesterday narrows the search to the diff.

**Instrument every boundary.** When more than one component is involved
(CI → build → sign, API → service → DB, hook → runtime → transcript), do not
reason about which one fails — measure it:

```
For EACH component boundary:
  log what data enters
  log what data exits
  verify config/env actually propagated
  check state at each layer
Run ONCE. Read where the chain breaks. THEN investigate that component.
```

This is the highest-yield step in the skill. A silent failure between two
layers is invisible to reasoning and obvious to a print statement.

**Trace the bad value backward.** Where does it originate? What called that
with a bad value? Keep walking up until you reach the source. Fix there.
Full technique: `root-cause-tracing.md`.

**Watch for swallowed failures.** A bare `except`, a catch-all that logs and
returns 0, a hook that must never break the session — these convert a crash
into silence. If a component "does nothing", check whether it is erroring
invisibly before assuming it ran and found nothing.

## Phase 2 — Pattern

Find similar code in this repo that **works**. List every difference between
working and broken, however small — "that can't matter" is where the bug
lives. Reading a reference implementation means reading all of it; a skimmed
pattern guarantees a partial application.

## Phase 3 — Hypothesis

State one hypothesis: *"X is the root cause because Y."* Specific, written
down, falsifiable.

Test it with the **smallest possible change**. One variable. Bundling fixes
means you cannot tell which one worked, and one of them is probably a new bug.

Confirmed → Phase 4. Not confirmed → new hypothesis, do not stack another fix
on top. Don't understand something → say so and find out. Never pretend.

## Phase 4 — Fix and verify

**Reproduce it in a test first.** Simplest failing case — a real test, or a
one-off script if there's no framework. It must fail before the fix and pass
after; a test that never went red proves nothing.

**One fix, at the root.** No "while I'm here" cleanup, no bundled refactor.

**Verify with fresh evidence.** Before claiming anything is fixed:

```
1. IDENTIFY  which command proves the claim
2. RUN       it fully, now, not from memory of an earlier run
3. READ      full output, exit code, failure count
4. VERIFY    does the output actually confirm the claim?
5. ONLY THEN say so, with the evidence
```

Skipping a step is asserting, not verifying. "Should work", "probably fixed",
"linter passed so the build passes" are all claims without evidence. So is
trusting a subagent's success report — check the diff.

**Fix didn't work?** Count attempts. Under 3 → back to Phase 1 with what you
learned. **3 or more → stop and question the architecture.** When each fix
uncovers new coupling somewhere else, or fixes demand massive refactors to
apply, that is not a failed hypothesis — it is the wrong design. Raise it
instead of attempting fix #4.

---

## Red flags — stop, return to Phase 1

"Quick fix now, investigate later" · "just try changing X" · "it's probably X"
· several changes at once, then run tests · "skip the test, I'll check by hand"
· "I don't fully understand it but this might work" · listing fixes before
tracing data flow · "one more attempt" after two failures.

From the user: *"Is that not happening?"* (you assumed instead of verifying) ·
*"Stop guessing"* · *"We're stuck?"* — all mean go back to Phase 1.

---

## Genuinely no root cause?

Sometimes it is environmental, timing-dependent, or external. Then: document
what was ruled out, implement real handling (retry, timeout, a clear error),
add logging for next time. But most "no root cause" verdicts are incomplete
investigation — be suspicious of your own.

---

## References

- `root-cause-tracing.md` — backward tracing through the call stack
- `defense-in-depth.md` — validating at multiple layers once the cause is known
- `condition-based-waiting.md` — replacing arbitrary timeouts with condition polling
- `find-polluter.sh` — locating the test that pollutes shared state
