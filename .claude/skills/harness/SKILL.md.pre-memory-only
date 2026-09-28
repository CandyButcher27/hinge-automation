---
name: harness
description: Create or refresh a project's `.harness/` directory and `memory/` knowledge base, plus a project-level `CLAUDE.md`, so a cold Claude session understands the project, its current state, its major subsystems, past mistakes, architectural decisions, and how to maintain that knowledge over time. Use when the user says "/harness", "set up the harness", "make this project cold-start readable", "add goal and memory files", or asks to refresh or audit an existing harness.
---

# harness — the project's persistent working memory

Three layers:

1. **`CLAUDE.md`** — operating instructions: how Claude works this repo, and how it maintains the memory system.
2. **`.harness/`** — compact operational memory for cold-starting a session.
3. **`memory/`** — deeper, component-specific technical knowledge.

`/harness` creates and curates all three, and installs the project-level skills and agents that maintain them. `/carryover` is the runtime half — reads and enforces `.harness/` at session start, manages the obligation ledger.

**Scope: project-level only.** `/harness` writes inside the repo — `.harness/`, `memory/`,
`CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, `.gitignore`. It never touches
`~/.claude/settings.json`, plugins, MCP servers, or hooks. Those are environment-level
capabilities that outlive any one project; a bootstrapper that configures them becomes the
orchestration monster this skill exists to avoid. Report a missing hook (below) — do not install one.

Goal: a cold session understands the project quickly, works safely, and continues where the last session stopped — without the user reconstructing history. Not: document everything.

```text
Project/
├── CLAUDE.md
├── .harness/  GOAL.md STATE.md MISTAKES.md DECISIONS.md  (+ ledger.json, written by the hook)
├── memory/    README.md <component>.md <system>.md ...
└── .claude/
    ├── skills/  harness/ wrapup/ think/ debug/
    └── agents/  debugger.md
```

---

## What belongs where

| File | Holds | Lifecycle |
|---|---|---|
| `CLAUDE.md` | How Claude should work here: constraints, commands, testing, architectural rules, how/when memory is maintained | Never overwritten — read first, add only what's missing |
| `.harness/GOAL.md` | Purpose, done-looks-like, non-goals, settled constraints | Rewritten when the goal genuinely changes |
| `.harness/STATE.md` | What works / broken / next, `verified-at` | Updated as work lands — goes stale fastest |
| `.harness/MISTAKES.md` | Structured, reusable lessons from things that went wrong | Append-only; consolidated during maintenance |
| `.harness/DECISIONS.md` | Choices + reasons + what would reverse them | Appended; superseded entries marked, not removed |
| `.harness/ledger.json` | `/carryover` obligation state | Machine-written — never hand-edit, and never scaffolded: the hook creates it on the first discharge and treats a missing file as an empty ledger |
| `memory/<component>.md` | How a subsystem works now: purpose, location, I/O, architecture, interfaces, config, tests, constraints, change history | Updated when that subsystem's architecture/behavior/interfaces changes |
| `memory/README.md` | Index: what each memory file covers, when to read it, when to add one | Updated whenever memory files are added/renamed/merged/removed |

One example per file is enough to calibrate tone:

- GOAL: "The system converts PDFs into structurally meaningful chunks for retrieval."
- STATE: "PDF ingestion works for native-text PDFs. Scanned PDFs need the vision fallback."
- MISTAKES: "Generating benchmark gold from the parser being evaluated inflates its own score."
- DECISIONS: "Geometry-first layout detection, because the benchmark showed vision-only was less reliable on native PDFs."
- memory/*: "Reading order is reconstructed after block fusion because downstream section detection assumes globally ordered blocks."

Create a memory file only when a component is substantial enough that a future session benefits from reading it before touching the component. Don't create one for a helper function, one bug, or random notes. Small facts go in the existing relevant file, not a new one. Prefer several focused files over one `memory.md`.

---

## Decide the mode first

```text
ls .harness/ GOAL.md MISTAKES.md memory/ CLAUDE.md 2>/dev/null
```

- **Nothing** → fresh scaffold.
- **`.harness/` or `memory/` exists** → refresh and audit.
- **`CLAUDE.md` exists** → read and preserve it; add only missing harness instructions.
- **Loose `GOAL.md` / `MISTAKES.md` / `memory/` at repo root** → old layout, migrate (below).

Never overwrite prose the user wrote.

## Fresh scaffold

1. **Understand the project first** — README, entry points, dependency manifests, layout, config, tests, major source dirs. Empty repo → ask for the goal, don't invent one.
2. **`CLAUDE.md`** (if missing) — must instruct Claude to maintain project memory:
   - *Before substantial work*: read GOAL.md, STATE.md, relevant memory/*.md, relevant DECISIONS/MISTAKES entries; inspect actual code before trusting memory.
   - *After every major change window* (a feature, a significant bug fix, an architecture/API/pipeline/dependency change, a substantial refactor, a completed debugging investigation — not a trivial edit): update STATE.md if state changed; update affected memory/*.md; create a new memory file for a new substantial subsystem; update memory/README.md; add a DECISIONS.md entry for important choices; add a MISTAKES.md record for reusable lessons; correct stale claims rather than leaving them beside new ones.
3. **CLAUDE.md must carry the `/think` line.** Whenever `CLAUDE.md` is created or
   updated, its Workflow section includes, verbatim:

   > `/think` — for non-obvious design work, use it before committing to an approach

   `/think`'s description triggers on natural language, but design questions are
   the case where answering directly is indistinguishable from doing the work, so
   the skill gets skipped silently. This line is the per-project reminder.
   `/debug` needs no equivalent — a stack trace announces itself.

4. **GOAL.md** — fill every section with real content; unknown facts become explicit questions, never placeholders.
5. **STATE.md** — what's actually true now, `verified-at` = today.
6. **MISTAKES.md** — seed from the current conversation/repo history if a real mistake is already evident; empty is fine only if nothing concrete has surfaced yet. Schema below.
7. **DECISIONS.md** — settled choices already made, with reasons and reversal evidence.
8. **`memory/`** — one file per real component (see template below); `memory/README.md` as index.
9. **`.gitignore`** — `.harness/` under a `# Claude / personal` section by default (personal working memory, keep out of public remotes). `memory/` and `CLAUDE.md` are durable project knowledge — track them in git, unless the project already chooses otherwise. If the user wants `.harness/` shared too, track it.

10. **Install the skills and agents** — copy them in; see *Installing the skills* below. This step is
    done only when `.claude/skills/` and `.claude/agents/` actually exist and you have listed their
    contents to confirm it. Report the file list, not the intention.

**Never invent project knowledge.** An empty project gets `works: nothing verified yet`,
`broken: unknown`, `next: establish baseline`. Inspecting an existing repo may produce a *proposed*
STATE for the user to confirm — a guess written as fact is the stale-memory failure, seeded on day one.

**memory/\<component\>.md template** — Purpose · Location · Inputs · Outputs · Architecture · Interfaces · Configuration · Testing · Important Constraints · Change History (major changes only). Skip sections with nothing useful; keep each file focused, not a copy of the source.

## Refresh an existing harness

Read `CLAUDE.md`, every `.harness/` file, `memory/README.md`, relevant memory files, and enough code to judge accuracy. **Report before editing** what's:

- **Stale** — describes code/backends/plans that no longer exist (usually STATE.md)
- **Missing** — real project knowledge nothing covers
- **Contradictory** — two sources disagree, or a source disagrees with the code
- **Invalid** — a mistake record that would fail the schema (silently never injected)
- **Orphaned** — a memory file for a system that's gone
- **Duplicated** — overlapping memory files that should merge

Every piece resolves to one of four states, and only two of them mean work:

| State | Action |
|---|---|
| **Missing** | Install it |
| **Present + correct** | Leave it alone. Say so; do not re-write an identical file |
| **Present + outdated** | Update in place, preserving anything the user wrote |
| **Present + conflicting** | **Stop and ask.** Never auto-resolve |

A conflicting `CLAUDE.md` rule — the project says one thing, the harness convention says another —
is a decision for the user, not something the installer quietly "fixes". Show both, recommend one,
wait.

**Idempotent.** Running `/harness` twice in a row must produce `harness already compliant, nothing
to do` on the second run — never `CLAUDE-2.md`, `debug-2/`, or a duplicated MISTAKES entry.

Then fix. **Deleting a wrong statement beats adding a correct one beside it** — a memory system that contradicts the code is actively harmful, because future sessions trust it.

## Migrating the old layout

Root-level `GOAL.md`/`MISTAKES.md`/`memory/` → move GOAL.md and MISTAKES.md into `.harness/`; split old `memory/` into current status (STATE.md), choices (DECISIONS.md), and per-component files; rewrite mistakes into the schema below; anything that can't be safely classified goes into a `## Quarantine` section rather than being dropped. Update `.gitignore`, create/update `memory/README.md` and `CLAUDE.md`, remove obsolete paths only after migrating their content. Tell the user what moved and what was quarantined — never silently destroy project knowledge.

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
  not the project it lands in — copying it drops a file describing a scaffold into a repo that is
  no longer a scaffold. Take `.harness/`, `memory/`, `.claude/`, and `CLAUDE.md`; leave the rest.
- **`.gitignore` is appended, never replaced.** Add `.harness/` under a `# Claude / personal`
  section if it is absent. A project's existing ignore rules are its own.

## Verify the runtime

The files do nothing on their own; `carryover_hook.py` is what reads and enforces them.

```text
python "C:\Users\sriva\.claude\hooks\carryover_hook.py" --selftest
```

Then confirm `~/.claude/settings.json` wires it as `SessionStart --session-start` and
`Stop --stop`. **Report a missing or broken hook; do not install one** — that is environment
configuration, and it is the user's call.

A hook whose failure is swallowed looks installed and does nothing. `--selftest` passing is the
evidence that it runs; a wired entry in `settings.json` is not.

Then confirm the result: the orientation block is non-empty; `global-rule` triggers appear;
every mistake record passes validation (an invalid one is silently never injected, so it looks
present and does nothing); `memory/README.md` indexes every memory file; every major subsystem
has a memory file or an explicit reason it doesn't need one; `CLAUDE.md` carries the
major-change-window maintenance instructions.

A memory file that exists but never gets updated is worse than no file — it creates false confidence.

---

## MISTAKES.md schema

`/carryover` mechanically validates these. Filler like "be careful with this" is rejected — every record needs a concrete referent (file, flag, error class, threshold, command, subsystem, artifact).

```markdown
## eval gold generated from the tool being benchmarked

TRIGGER: before generating any evaluation or benchmark dataset
RULE: source Q&A from raw data (raw text, raw pages) the tool under test has never processed
CONSEQUENCE: the benchmarked tool scores against its own output and the number is meaningless
SCOPE: global-rule
EVIDENCE: gold set built from parser output in `gen_eval.py` inflated that parser's own score
MATCH: gen_eval\.py|--build-gold
```

- **TRIGGER** — the danger condition as a situation, never task wording.
- **RULE** — the imperative.
- **CONSEQUENCE** — what actually breaks.
- **SCOPE** — `global-rule` (injected every session) or `project-incident` (on demand only). Be sparing with `global-rule` — every resident line costs context forever.
- **EVIDENCE** — what happened, the causal chain.
- **MATCH** *(optional)* — regex over a tool call for mechanical firing.
- **STATUS: retired** — retires without deleting, with a reason. Never delete a mistake because the code changed. Consolidate duplicate variants during maintenance.

**memory/ vs MISTAKES.md**: memory explains how the system works now ("gold answers must originate from source material independent of the parser output"); MISTAKES.md is the reusable lesson from getting it wrong ("before generating benchmark gold, source it from raw material the evaluated parser has never processed"). Don't log the same fact in both.

**DECISIONS.md vs memory/**: DECISIONS explains *why* ("chose geometry-first over vision-first because the benchmark..."); memory explains *what exists now* ("the pipeline is geometry-first and falls back to vision when...").

---

## Rules

1. **Code is the source of truth.** Memory conflicting with implementation gets corrected — never bend code to match stale memory.
2. **Keep `.harness/` short** — cold-start context, not documentation. Past ~150 lines/file, consolidate.
3. **Keep `memory/*.md` focused** — readable before modifying that component, not a copy of the source.
4. **Record reasons**, not just choices — undocumented reasoning can't be safely reversed.
5. **Correct stale knowledge in place** — never append a new fact beside a contradictory old one.
6. **Facts, not aspirations** — "uses SQLite" is state; "should use Postgres" is a goal, not fact.
7. **Never mention harness internals externally** (`.harness/`, `memory/`, `MISTAKES.md`, `DECISIONS.md`, `STATE.md`) in commits, PRs, code comments, READMEs, or client-facing output — state the underlying project fact instead.
8. **No documentation for its own sake** — the test is "would a cold session make a better decision after reading this?" If not, don't write it.

## Report

Close with what changed and what was already fine — file states, not a narrative:

```text
.harness/          created  GOAL STATE MISTAKES DECISIONS  (no ledger - the hook writes it)
memory/README.md   created
CLAUDE.md          exists   added memory-maintenance section, preserved 3 existing sections
.claude/skills/    created  harness wrapup think debug
.claude/agents/    created  debugger
.gitignore         updated  + .harness/
hook               ok       selftest passes, SessionStart + Stop wired
CONFLICTS          1        CLAUDE.md says "never write tests"; harness expects a test per
                            non-trivial change. Not resolved - your call.
```

Nothing to do is a valid, expected report.

```text
cold session → CLAUDE.md → GOAL.md/STATE.md → relevant memory/<subsystem>.md → work
   → major change window complete → update STATE, affected memory, decisions, mistakes
   → next cold session starts accurate
```
