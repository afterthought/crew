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
2. A deploy is one act by the kit's deployer under the environment's policy, `auto` once or `manual` per deploy, the word given through the rail's card: it targets a repository state, its contents are the landings since the environment's last deployed state, and it is recorded in the run record as it runs, with its environment, from, to, bolts, checks, outcomes and log. Main-level ops deploys nothing: it monitors the record and the after-deploy suite, confirms the environment is healthy, and works what the suite cannot as a fix on main (the user, 2026-10-08: "the engine iteslf is a reconcile deploy and mainops won't do the deploy. just monitor it and ensure it succeeds"; swancloud's record 0019).
3. What must be true once a state is deployed is code in the change that makes it true, by the kit's own rules (a doctor row, a service's test, a pin's assertion; swancloud `testing.6`), and a deploy's checklist is the kit's after-deploy suite, run once per deploy by the deployer. A unit's `design.md` lists under *After deploy* only the steps no check can be code, saying why, each naming the environments it applies to (every environment when it names none) and who does it: an agent, when the step is one an agent can do once the time is right (restart the teams; wait for the crew's work to end, then restart the herdr server so the teams come back with the new plugins), or the user, when only they can do or verify it, a test plan's step. A deploy's steps are the union of the lists of the landings it carries, deduplicated by what each does, and every one is recorded on the deploy's record with its doer and its state: an agent's step runs when its condition holds and is recorded done or failed; the user's step is a rail row keyed to the deploy with a card, open until the user marks it done or declines it, so nothing is lost when they do not get to it at once (the user, 2026-10-09: "I'd love it if this set of steps could be in this deterministic post-deploy system so that whatever needs to happen is tracked as pending for me. Even if I don't get to it right away, I don't lose track of it. Ideally, the state is not just pending for me, but recorded somehow"; and 2026-10-08: "I'm not sure about each unit carrying proof after deploy. I think we need to decide in our open spec instructions what is appropriate"; `docs.6`).
4. A deploy's record is the release note: the environment, the bolts it carried and what was proven there, read from state, never written by hand.
5. Environments are many and each keeps its own last deployed state. Promotion from one environment to the next is a deploy to that environment, over the landings it has not seen; once versions exists it is a channel promotion through that channel's gate.

### Consequences

- `plan.14` added in `docs/architecture/plan.md`, recorded in `_open.md` as accepted and not built.
- Amended 2026-10-08, after the user's exploration of release signals and a reconcile deploy: the deployer is the actor and main-level ops monitors (point 2); after-deploy truth is code in the kit (point 3). `roles.2` and `docs.6` follow; swancloud's records 0018 and 0019 say the environments and the deployer.
- Amended 2026-10-09, on the user's two cases (restart the teams; wait for quiet, then restart the herdr server): an *After deploy* step names its doer, an agent's runs when its condition holds, the user's is a rail row with a card until done, and every step is on the deploy's record (point 3). `plan.14` follows; `a-deploy-is-approved-and-recorded-through-crew` and `a-change-holds-what-is-true-and-what-is-proved` carry it.
- Amended 2026-10-13 by record 0025: *Proof in dev* leaves the change, whose verification is the kit's checks alone; and a deploy is of a revision to an environment the kit gives it, main's head or a bolt's, with the same after-deploy checks and the carried changes' *After deploy* steps recorded on it whichever branch it came from (the user: "these deployments could be from main or from a bolt and it really doesn't matter").
- The `main-level` spec's requirement splits into "lands bolts" and "deploys main" with the change that builds this (`docs.4`); `main-ops.md` step 4 and the `construct.md` proof rule change with it.
- In Flywheel Next the coalesced list is the claims whose verdicts fell due at those landings; in versions each environment is a channel, and a deploy is a promotion through that channel's gate. crew's record is the form until then.
