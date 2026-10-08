---
number: 12
title: A deploy is one act over the landings since the last
status: accepted
date: 2026-10-08
decision-makers:
- Chuck Swanberg
- the merge-queue design session
---

# A deploy is one act over the landings since the last

Deciders: the user, in the merge-queue exploration of 2026-10-08; the design session there.
Sources: `openspec/specs/main-level/spec.md` "Main-level ops lands bolts and deploys main"; `openspec/specs/bolt-teams/spec.md` "A bolt is deployed and tested from its branch"; `plugin/roles/main-ops.md` steps 3–5; `plugin/roles/construct.md` "Its tasks carry no proof in dev"; Flywheel Next requirements 34a and 185; the versions statement (`agentplot/blueprints:design/versions/requirements.md`) on channels and their gates.

## Context and problem statement

The main-level spec fuses three acts: main-level ops merges a proven bolt into main, deploys main, and runs `crew bolt land`. Each landing implies a deploy. With several bolts landing close together the user wants one deploy, not one per bolt, and then a list of what that deploy was expected to prove, worked once.

The proof a unit needs from a live system is written under *Proof in dev* in its `design.md` and worked by the team's ops from the bolt's branch before landing. Early in a project that list holds steps that only make sense once main is deployed (push to AWS, check the console), and nothing says they are worked again on main. Nothing records which bolts a deploy of main carried, so there is no list to work and no release note to read.

## Decision drivers

- Landing is main moving; a deploy is an environment moving to a repository state. Fused, a deploy per landing is the only shape possible.
- A deploy's contents must be derivable from the record, never remembered: which landings since the environment's last deployed state.
- What a unit expects to be true after main is deployed is a different list from what ops proves on the bolt, and the two should not be one list.
- A deploy, like a landing, runs only on the user's word (`roles.2`).
- Flywheel Next already says a landing makes the claims it serves due for a verdict (34a) and that main's commit subjects are readable by release tooling (185); versions says a channel's head moves only through its gate.

## Considered options

1. Keep the fusion and ask main-ops to batch landings by hand before deploying.
2. Decouple: a landing records the state it produced; a deploy is its own act, on the user's word, over every landing since the environment's last; each unit carries a short *Proof after deploy* beside *Proof in dev*; the deploy's checklist is the union, deduplicated, and its outcomes are recorded on the deploy.
3. Decouple and defer the record entirely to versions' channels.

## Decision outcome

Option 2, with option 3 as where it goes once versions exists.

1. `crew bolt land` records the landing with the sha main holds afterwards. Landing deploys nothing.
2. A deploy is one act by main-level ops on the user's word: it targets a repository state, its contents are the landings since the environment's last deployed state, and it is recorded with its environment, from, to, bolts, checks and outcomes.
3. A unit's `design.md` carries two lists: *Proof in dev*, worked by the team's ops from the bolt before landing as today, and *Proof after deploy*, what must be true once the state is deployed. An item under *Proof after deploy* names the environments it applies to, and applies to every environment when it names none. Only this list coalesces: a deploy's checklist is the union of the items for its environment, deduplicated by what each item checks, and is worked once per deploy.
4. A deploy's record is the release note: the environment, the bolts it carried and what was proven there, read from state, never written by hand.
5. Environments are many and each keeps its own last deployed state. Promotion from one environment to the next is a deploy to that environment, over the landings it has not seen; once versions exists it is a channel promotion through that channel's gate.

### Consequences

- `plan.14` added in `docs/architecture/plan.md`, recorded in `_open.md` as accepted and not built.
- The `main-level` spec's requirement splits into "lands bolts" and "deploys main" with the change that builds this (`docs.4`); `main-ops.md` step 4 and the `construct.md` proof rule change with it.
- In Flywheel Next the coalesced list is the claims whose verdicts fell due at those landings; in versions each environment is a channel, and a deploy is a promotion through that channel's gate. crew's record is the form until then.
