---
name: harness
description: Create or refresh a project's `memory/` knowledge base plus a project-level `CLAUDE.md`, so a cold Claude session understands how the project's major subsystems actually work. Use when the user says "/harness", "set up the harness", "make this project cold-start readable", "add memory files", or asks to refresh or audit an existing memory base.
---

# harness — the project's persistent working memory

Two layers:

1. **`CLAUDE.md`** — operating instructions: how Claude works this repo, and how it maintains the memory base.
2. **`memory/`** — component-specific technical knowledge, one file per real subsystem.

`/harness` creates and curates both, and installs the project-level skills and agents that maintain them.

**Scope: project-level only.** `/harness` writes inside the repo — `memory/`, `CLAUDE.md`,
`.claude/skills/`, `.claude/agents/`, `.gitignore`. It never touches `~/.claude/settings.json`,
plugins, MCP servers, or hooks. Those are environment-level capabilities that outlive any one
project; a bootstrapper that configures them becomes the orchestration monster this skill exists to
avoid.

Goal: a cold session understands the project quickly and works safely. Not: document everything.

```text
Project/
├── CLAUDE.md
├── memory/    README.md <component>.md <system>.md ...
└── .claude/
    ├── skills/  harness/ wrapup/ think/ debug/
    └── agents/  debugger.md
```

## Legacy `.harness/`

Some projects on this machine still carry a `.harness/` directory (`GOAL.md`, `STATE.md`,
`MISTAKES.md`, `DECISIONS.md`, `ledger.json`). It is no longer part of what `/harness` builds.

- **Never scaffold one.** A fresh run creates `memory/` and `CLAUDE.md` only.
- **Never delete or migrate an existing one.** It is still read at session start by
  `carryover_hook.py`, and removing it destroys accumulated project knowledge for nothing.
- Leave it untouched, and out of the report unless the user asks about it.

The memory layer is what is being kept and grown right now. The other layers come back only if
something concrete shows they earn their cost.

---

## What belongs where

| File | Holds | Lifecycle |
|---|---|---|
| `CLAUDE.md` | How Claude should work here: constraints, commands, testing, architectural rules, how/when memory is maintained | Never overwritten — read first, add only what's missing |
| `memory/<component>.md` | How a subsystem works now: purpose, location, I/O, architecture, interfaces, config, tests, constraints, change history | Updated when that subsystem's architecture/behavior/interfaces changes |
| `memory/README.md` | Index: what each memory file covers, when to read it, when to add one | Updated whenever memory files are added/renamed/merged/removed |

One example is enough to calibrate tone:

- `memory/*`: "Reading order is reconstructed after block fusion because downstream section detection assumes globally ordered blocks."

Create a memory file only when a component is substantial enough that a future session benefits from
reading it before touching that component. Don't create one for a helper function, one bug, or
random notes. Small facts go in the existing relevant file, not a new one. Prefer several focused
files over one `memory.md`.

---

## Decide the mode first

```text
ls memory/ CLAUDE.md 2>/dev/null
```

- **Nothing** → fresh scaffold.
- **`memory/` exists** → refresh and audit.
- **`CLAUDE.md` exists** → read and preserve it; add only the missing memory instructions.
- **Loose notes at the repo root, or a single `memory.md`** → old layout, split it (below).

Never overwrite prose the user wrote.

## Fresh scaffold

1. **Understand the project first** — README, entry points, dependency manifests, layout, config,
   tests, major source dirs. Empty repo → ask what it is for, don't invent an answer.
2. **`CLAUDE.md`** (if missing) — must instruct Claude to maintain project memory:
   - *Before substantial work*: read `memory/README.md` and the relevant `memory/*.md`; inspect
     actual code before trusting memory.
   - *After every major change window* (a feature, a significant bug fix, an
     architecture/API/pipeline/dependency change, a substantial refactor, a completed debugging
     investigation — not a trivial edit): update the affected `memory/*.md`; create a new memory
     file for a new substantial subsystem; update `memory/README.md`; correct stale claims rather
     than leaving them beside new ones.
3. **CLAUDE.md must carry the `/think` line.** Whenever `CLAUDE.md` is created or updated, its
   Workflow section includes, verbatim:

   > `/think` — for non-obvious design work, use it before committing to an approach

   `/think`'s description triggers on natural language, but design questions are the case where
   answering directly is indistinguishable from doing the work, so the skill gets skipped silently.
   This line is the per-project reminder. `/debug` needs no equivalent — a stack trace announces
   itself.
4. **`memory/`** — one file per real component (template below); `memory/README.md` as the index.
5. **`.gitignore`** — `memory/` and `CLAUDE.md` are durable project knowledge, so track them in git
   unless the project already chooses otherwise. Nothing new needs ignoring.
6. **Install the skills and agents** — copy them in; see *Installing the skills* below. This step is
   done only when `.claude/skills/` and `.claude/agents/` actually exist and you have listed their
   contents to confirm it. Report the file list, not the intention.

**Never invent project knowledge.** A project you cannot read yet gets a `memory/README.md` saying
what is not yet mapped, not a confident description of a subsystem nobody inspected. A guess written
as fact is the stale-memory failure, seeded on day one.

**memory/\<component\>.md template** — Purpose · Location · Inputs · Outputs · Architecture ·
Interfaces · Configuration · Testing · Important Constraints · Change History (major changes only).
Skip sections with nothing useful; keep each file focused, not a copy of the source.

## Refresh an existing memory base

Read `CLAUDE.md`, `memory/README.md`, the memory files, and enough code to judge accuracy.
**Report before editing** what's:

- **Stale** — describes code, backends or plans that no longer exist
- **Missing** — real project knowledge nothing covers
- **Contradictory** — two files disagree, or a file disagrees with the code
- **Orphaned** — a memory file for a system that's gone
- **Duplicated** — overlapping memory files that should merge

Every piece resolves to one of four states, and only two of them mean work:

| State | Action |
|---|---|
| **Missing** | Install it |
| **Present + correct** | Leave it alone. Say so; do not re-write an identical file |
| **Present + outdated** | Update in place, preserving anything the user wrote |
| **Present + conflicting** | **Stop and ask.** Never auto-resolve |

A conflicting `CLAUDE.md` rule — the project says one thing, the memory convention says another —
is a decision for the user, not something the installer quietly "fixes". Show both, recommend one,
wait.

**Idempotent.** Running `/harness` twice in a row must produce `memory base already compliant,
nothing to do` on the second run — never `CLAUDE-2.md`, `debug-2/`, or a duplicated memory file.

Then fix. **Deleting a wrong statement beats adding a correct one beside it** — a memory base that
contradicts the code is actively harmful, because future sessions trust it.

## Splitting an old layout

A single root `memory.md`, or loose notes at the repo root, become one file per real subsystem under
`memory/`, indexed by `memory/README.md`. Anything that can't be safely classified goes into a
`## Quarantine` section rather than being dropped. Remove the obsolete paths only after migrating
their content. Tell the user what moved and what was quarantined — never silently destroy project
knowledge.

---

## Installing the skills and agents

Template source: `C:\Users\sriva\Desktop\Me\final-harness`

```text
.claude/skills/  harness/ wrapup/ think/ debug/   (each a directory holding SKILL.md)
.claude/agents/  debugger.md                      (flat .md, frontmatter: name, description, tools, model)
```

`.claude/skills/<name>/SKILL.md` and `.claude/agents/<name>.md` are the only paths Claude Code
discovers. A bare `skills/` folder, or one directory per agent, loads nothing.

- **Copy, never symlink** — the project must stay portable to another machine.
- **Never overwrite a project's own skill** of the same name without asking; a project copy may be
  deliberately pinned or modified.
- `gpt/` is optional — it needs the CDP bridge on this machine. Install it only when asked.
- **Install by default.** The user-level copies in `~/.claude/skills/` are already active on this
  machine, so a project copy buys portability and version-pinning, not availability. That is worth
  having: copy unless the user says otherwise, and report the reason as portability rather than
  implying the skills were missing. Skip only on an explicit instruction, and then say in the report
  that `.claude/` was deliberately left empty. Never skip silently — a run that installs nothing and
  still calls this step done is the failure this paragraph exists to prevent.
- Diff before copying. Identical content is **present + correct** — report it, don't rewrite it.
- **Never copy the template wholesale.** `final-harness/README.md` documents the template itself,
  not the project it lands in. Take `memory/`, `.claude/` and `CLAUDE.md`; leave the rest, and never
  copy the template's `.harness/` into a project that has none.

---

## Rules

1. **Code is the source of truth.** Memory conflicting with implementation gets corrected — never bend code to match stale memory.
2. **Keep `memory/*.md` focused** — readable before modifying that component, not a copy of the source.
3. **Record reasons**, not just choices — undocumented reasoning can't be safely reversed.
4. **Correct stale knowledge in place** — never append a new fact beside a contradictory old one.
5. **Facts, not aspirations** — "uses SQLite" is state; "should use Postgres" is a goal, not fact.
6. **Never mention memory internals externally** (`memory/`, and in older projects `.harness/`) in commits, PRs, code comments, READMEs, or client-facing output — state the underlying project fact instead.
7. **No documentation for its own sake** — the test is "would a cold session make a better decision after reading this?" If not, don't write it.

## Report

Close with what changed and what was already fine — file states, not a narrative:

```text
memory/            created  ingest.md retrieval.md eval.md
memory/README.md   created
CLAUDE.md          exists   added memory-maintenance section, preserved 3 existing sections
.claude/skills/    created  harness wrapup think debug
.claude/agents/    created  debugger
CONFLICTS          1        CLAUDE.md says "never write tests"; memory convention expects a test
                            per non-trivial change. Not resolved - your call.
```

Nothing to do is a valid, expected report.

```text
cold session → CLAUDE.md → relevant memory/<subsystem>.md → work
   → major change window complete → update the affected memory files and the index
   → next cold session starts accurate
```
