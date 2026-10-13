# Design

## Context

Before this change the conductor, once every unit had merged, ran `crew prove <team>`, which told ops to deploy the bolt and work each unit's *Proof in dev* list, owed the proof's end like a stage's, and waited with `crew prove <team> --wait` for ops's proof file, `proof-<bolt>-<stamp>.md`; ops wrote under *Left for the user* the steps only the user could take, and the conductor put them on the landing card's `action`, which the card hook allowed. The rail offered the landing once every unit had merged and been in a batch.

Record 0025 makes a bolt's proof its verification, and record 0026 makes that verification sluice's verdict on the bolt's last landing (`units-merge-and-bolts-land-only-through-sluice`, which reads it: `kit.verification`). The rules this rests on: `plan.16` (the conductor posts the landing card once the verification is green), `briefs.1` (ops proves and deploys nothing), `briefs.3` (no brief names a proof list), `briefs.11` (a step only the user can do is an after-deploy step on a deploy's card, never a question on the landing card), `briefs.13` (a landing card is a high-stakes approval), `tests.5`, `teams.4`, `code.7`, `code.8` (the board and the agents' views follow what crew models), `docs.4`. Pages whose area this touches: `plan.md`, `teams.md`, `briefs.md`, `tests.md`.

## Goals / Non-Goals

**Goals:**
- Nothing proves a bolt by hand: the landing is offered on the verification alone.
- A record from before keeps reading: a `proof/<file>` an entry delivered is still found by `crew trace`, and a proof line in a team's stages file is dropped, owed nothing.

**Non-Goals:**
- Where a revision is deployed from, before or after landing: the kit's and its deployer's (record 0025, point 5).
- What a change holds: `a-change-holds-what-is-true-and-what-is-proved`.

## Decisions

### The rail's land row waits on the verification

`rail` reads each held bolt's verification from the kit's gather (`kit.verification` on the bolt's head and its `Sluice-Result`). A bolt whose units have all merged and been in a batch, and whose verification is not green, is a row that says "lands once its verification is green; now <what it is>" and carries no command, so no card is posted for it; once green the row carries the tell to main-level ops as before. `crew bolts` shows the verification line for each held bolt. Alternative: no row until green (hides from the user that the bolt waits on its checks).

### The proof's stage goes, and old lines are dropped

`prove_cmd`, its parser entry and its owed end go. `stage_ends` still reads a `proof` line left in a stages file by a crew from before, and drops it with nothing owed, so a team that was mid-proof when this lands is not held.

### The landing card has no steps

The card hook's landing form refuses steps, as for every other row's approval; ops's *Left for the user* goes, and so does the conductor's putting them on the card.

## Risks / Trade-offs

- [A kit whose checks do not reach what a proof list did] → that is a missing check the kit's change adds (`docs.6`), or an after-deploy step on the deploy's card (`plan.14`).
