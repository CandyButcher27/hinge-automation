---
name: think
description: Turn a rough idea into a design worth building — classify how much process the work needs, ask only the questions that change the answer, then present a design with a recommendation. Use when the user says "/think", "let's design this", "how should I build X", "brainstorm this with me", "what's the right approach here", or brings an idea that isn't yet a spec. Not for tasks whose shape is already settled.
---

# think — idea to design

Classify the work, ask what actually matters, present a design with a
recommendation. Scale the ceremony to the task.

Invoked deliberately. No gate stops implementation — but a design you never
showed is a design nobody agreed to.

---

## Classify first, out loud

Say the classification before the first question, so it can be overridden:

> "This looks bounded — I'll present a short design here rather than write a spec."

**Spike** — a feasibility question. *Can we? Is it possible? Quick and dirty is
fine.* Output is an answer, not code you keep. Say the question and what you'll
try in 2–3 sentences, then find out as cheaply as correctness allows. Anything
built is labeled throwaway. Keeping it is a new request — reclassify.

**Bounded** — a well-scoped change to code **that already exists here**: a new
flag, one endpoint, a one-file fix. Bounded measures the repo, not your
familiarity: if there's no existing flow to read and change, it isn't bounded.
Ask the questions that matter, present a short design in chat — approach, files
touched, how it's tested — then implement.

**Architectural** — new projects, new subsystems, anything that restructures how
components fit or changes an interface something else depends on. Full path
below.

**The ratchet is one-way.** In doubt between two paths, take the heavier one.
Hidden complexity found mid-task upgrades the path — stop, say so, step up.
Nothing downgrades mid-task.

---

## Architectural path

1. **Read the project first** — files, `CLAUDE.md`, relevant `memory/*.md`,
   recent commits, plus `.harness/GOAL.md` and `DECISIONS.md` in the older
   projects that have them. A design that contradicts a recorded decision must
   say so explicitly and argue against it.
2. **Ask clarifying questions one at a time.** Purpose, constraints, success
   criteria. Not a questionnaire — one question, hear the answer, let it change
   the next one. Stop when the remaining unknowns wouldn't change the design.
3. **Propose 2–3 approaches** with real trade-offs and **your recommendation**.
   Not a survey — a position, with the reasoning that would reverse it.
4. **Present the design in sections** scaled to their complexity. Check in after
   each substantial section rather than delivering a wall.
5. **Write it down only if it will be read again** — a spec file for work
   spanning sessions or people. A design that gets implemented this session
   lives in chat. Put the *why* where cold sessions already look: the relevant
   `memory/*.md`, or `.harness/DECISIONS.md` in a project that still has one.
   Never create `.harness/` in a project without it.

---

## Questions worth asking

Ask a question only when different answers produce different designs.

Good: *What happens to in-flight jobs when this restarts?* · *Is this read-heavy
or write-heavy?* · *Who else calls this interface?* · *What's the failure mode
you actually care about?*

Skip: preferences with an obvious default, anything the code answers, anything
you'd build the same way either way. Look it up instead of asking.

---

## Rules

1. **Recommend, don't survey.** Three options and no position is unfinished work.
2. **Read before proposing.** A design for code you haven't opened is a guess.
3. **Say what you're not building.** Explicit non-goals are the cheapest part of
   a design and prevent the most rework.
4. **Name the reversal condition.** What evidence would make this the wrong
   choice? If nothing would, the design isn't falsifiable.
5. **Simplest thing that survives the constraints wins.** Requirements justify
   complexity; anticipation doesn't.
6. **Don't design what exists.** Check the repo for the helper, pattern, or
   library first — reuse beats design.

---

## When to skip this entirely

The shape is already settled, the change is mechanical, or the user told you
what to build. Designing a rename wastes a turn. Say "this is settled, building
it" and go.
