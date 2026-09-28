---
name: wrapup
description: Close a work session by writing what actually happened into the project's `memory/` files and index, logging durable decisions, and writing a checkpoint — and, in older projects that still carry `.harness/`, also updating STATE.md and appending reusable lessons to MISTAKES.md. Use when the user says "/wrapup", "wrap up", "close out this session", "update the memory before I stop", "end of session", or when substantial work has landed and the memory has not been updated since.
---

# wrapup — session close

`/harness` builds the memory system. `/wrapup` closes the loop at the end of a
work session, so the next cold session reads facts rather than a stale snapshot.

The failure this prevents: `STATE.md` says `verified-at: 2026-08-29` while the
code moved three sessions ago. A cold session trusts it and works from a lie.
Stale memory is worse than no memory.

Runs against the current repo's `memory/`, and against `.harness/` only in the
older projects that still have one.

Steps 1, 5, 5a, 5b and 6 always run — the decision log and the checkpoint live
outside the repo and need no harness.

- **`memory/` only** (what `/harness` now builds) → steps 2-4 do not apply; say
  so rather than silently skipping them. **Never create `.harness/` here** — its
  absence is deliberate.
- **`.harness/` present** → steps 2 and 3 apply as well. It is still read at
  session start, so a stale `STATE.md` there still misleads a cold session.
- **Neither, and no `memory/`** → say so and offer `/harness`. Do not scaffold
  anything here.

---

## The one rule

**Nothing enters `works:` this session that was not run this session.**

Carrying an existing `works:` line forward is fine — it was verified when it was
written. Leaving it untouched is fine; re-running its check and noting that you
did is better. *Adding* a line is not fine, unless a command ran and produced
output you read. Anything implemented but not executed, anything asserted but
unverified, goes to `next:`, marked unverified.

The tempting case is code you just wrote and are sure about. Sureness is not
execution. If a new claim cannot be traced to a command and its output, it is
not state. This is the whole point of the skill; everything below is mechanics.

---

## Steps

Each step is skippable when nothing changed. Skipping is normal — a session that
fixed one typo should touch nothing. Say what you skipped.

### 1. Establish what actually happened

Before writing anything, gather from this session:

- commands that ran and their exit status
- files created, modified, deleted
- tests run and their result
- what was decided
- what broke, and whether it was fixed or merely diagnosed

Read the current `.harness/STATE.md` before rewriting it. Compare against the
above. Do not write from recollection of intent — write from evidence.

### 2. `.harness/STATE.md`

Rewrite in place, preserving the existing `works:` / `broken:` / `next:` /
`verified-at:` / `notes:` shape.

- `works:` — two kinds of entry, and nothing else. Something **run and verified
  this session**. Or an **existing** line carried forward — untouched, or with
  a note that you re-ran its check. A line that was neither run this
  session nor already in `works:` does not go here, however confident you are
  that it works — write it in `next:` instead, saying it is unverified.
  Delete entries the code no longer supports; never leave a correct line beside
  a stale one.
- `broken:` — known-broken with enough detail to resume. `none known` if clean.
- `next:` — the actual next action, specific enough to start cold.
- `verified-at:` — today, **only** if something was verified today. Otherwise
  leave the old date; bumping it without verification is the lie this file exists
  to prevent.

Past ~150 lines, consolidate rather than append.

### 3. `.harness/MISTAKES.md`

Append only mistakes with a **reusable trigger** — a future session in a
different context would benefit. A one-off typo does not qualify. A wrong
assumption that cost a re-run does.

Use the schema `/carryover` validates mechanically (invalid records are silently
never injected):

```markdown
## short imperative title

TRIGGER: before <the situation, never task wording>
RULE: <the imperative>
CONSEQUENCE: <what actually breaks>
SCOPE: global-rule | project-incident
EVIDENCE: <what happened, the causal chain, with a concrete referent>
MATCH: <optional regex over a tool call>
```

`SCOPE: global-rule` is injected into every future session and costs context
forever — be sparing. Default to `project-incident` unless the lesson genuinely
generalises beyond this repo.

Append-only. Retire with `STATUS: retired` and a reason; never delete.

### 4. `.harness/DECISIONS.md` — frozen, read only

Do not append here. New decisions go to the log in step 5a, which is the one
place a session is shown them. Where the file exists it is history: read it, and
when a decision in it is being reversed, log the replacement with `--decide` and
say in the rationale which entry it replaces.

### 5. `memory/<component>.md`

Touch only files whose subsystem changed **architecture, interfaces, or
behavior**. A bug fix inside an unchanged interface usually changes nothing here.

Correct stale statements in place. Update `memory/README.md` if a file was added,
renamed, merged, or removed.

A decision explains *why*; `memory/` explains *what exists now*; `MISTAKES.md` is
the reusable lesson from getting it wrong. Do not log the same fact in two of them.

### 5a. Log durable decisions

A **durable** decision is one a later session would otherwise re-litigate:
architecture, scope, a tool or vendor choice, a reversal. Not a turn-level choice,
not "used a dict here".

```text
python "C:\Users\sriva\.claude\hooks\carryover_hook.py" --decide "<what was decided>" "<why>"
python "C:\Users\sriva\.claude\hooks\carryover_hook.py" --supersede <id> "<what replaced it>"
python "C:\Users\sriva\.claude\hooks\carryover_hook.py" --redact <id> "<why it was wrong>"
```

Reverse a decision with `--supersede`, never by editing the log. The log is
append-only and "active" is computed from it; a hand-edited row makes the file
disagree with what the next session is shown. `--decisions` lists what is active.

In a project that still has `.harness/DECISIONS.md`, that file is frozen history —
read it, add to the log instead.

### 5b. Write a checkpoint

One file per session close, so the next session can answer "where was I" without
re-reading a transcript.

```text
python "C:\Users\sriva\.claude\hooks\carryover_hook.py" --checkpoint "<3-6 word title>"
```

That prints the path to write; it does not write the file. Write exactly:

```markdown
---
status: in-progress | done
branch: {current branch}
timestamp: {ISO-8601}
files_modified:
  - path/one
---

## Working on: {title}

### Summary
{1-3 sentences: the goal, and how far it got}

### Remaining Work
{numbered, concrete, in priority order}

### Notes
{gotchas, blocked items, what was tried and didn't work}
```

Only the path and the branch appear at session start — the body is read on demand.
So write the body for someone who has already decided to open it.

### 6. Report the diff, do not narrate the session

Print what changed in memory, and nothing else:

```text
memory/     gpt-bridge.md updated (CDP reconnect path)
decisions   +1 [8a384624] scope: repo | superseded 3f21c0aa
checkpoint  20260905-181400-cdp-reconnect.md (branch feat/bridge)
STATE.md    works: +2 -1 | next: rewritten | verified-at: 2026-08-29 -> 2026-09-05
MISTAKES.md +1  "detector scanned its own explanation" (project-incident)
```

Then stop. The user reviews and vetoes. Do not summarise what was built — they
were there.

---

## Rules

1. **Evidence over intent.** Written memory reflects what ran, not what was meant.
2. **Correct in place.** Never append a fact beside a contradictory one.
3. **Skipping is the common case.** Do not manufacture entries to look thorough.
4. **Nothing leaves the repo.** No Obsidian, no external notes, no commits.
5. **Never mention harness internals externally** — not in commits, PRs, code
   comments, or anything client-facing. State the underlying project fact instead.
6. **Do not fix code during wrapup.** Found a bug? It goes in `broken:` or
   `next:`. Fixing it starts a new work session, which then needs its own wrapup.

The test for every line written: *would a cold session make a better decision
after reading this?* If not, do not write it.
