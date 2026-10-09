# Design

## Context

See proposal.md for why, and record 0014 for the operator's ruling of 2026-10-09, D1 to D8. The current state:

- `run_check` in `plan.py` refuses construct for a unit whose stage is `waiting`, that is one with no place whose After units have not all merged; refuses code at `review` ("code waits until the user approves it") and at anything but `approved`, `code` or `verify`; refuses verify until every task is ticked; and sends merge the prompt `wt merge bolt/<bolt> --no-squash --no-remove`.
- `place_stage` reads `verify`, `code`, `approved` (planning complete and a `Reviewed-by` commit since the bolt), `review` (planning complete) or `construct`; an `Amended` mark reads `amended`, then `construct` while the head is where construct started, then `review` until `crew unit approve` clears it (unit-amendments, built and not archived).
- The rail (`rail_rows`) has four groups and four card keys: proposals, `review/<unit>/<head>`, `verify/<unit>/<stamp>` and `land/<bolt>`. A review card links a plannotator session on the change folder (`crew card session`, `briefs.9`).
- Touches is prose at the end of `proposal.md` (`construct.md` line 27), compared by eye by the conductor (`conductor.md` line 83), who builds overlapping units one after the other.
- The conductor waits on every stage with `crew unit wait <unit>` and on a proof with `crew prove <team> --wait`, both background commands that return within the hour (`bolt-teams` "The conductor waits for a stage through crew"). crew runs no service (`state.4`), so these waits are the only clock a team has.

Pages whose areas this touches: `plan.md` (`plan.py`, `gather.py`), `teams.md` (`plugin/bin/crew`, `crew.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `tests.md` (`tests/`), `docs.md` (`README.md`, `openspec/`, `docs/`). Rules relied on: `plan.1`, `plan.6` and `plan.13` as amended, `plan.9`, `plan.10`, `teams.1`, `teams.2`, `teams.4`, `teams.5` as amended, `teams.11`, `teams.12`, `teams.13`, `briefs.2`, `briefs.4` and `briefs.9` as amended, `briefs.5`, `briefs.11`, `briefs.12`, `roles.1`, `roles.2`, `roles.4`, `state.2`, `state.4`, `read.1`, `code.5`, `docs.4`.

## Goals / Non-Goals

**Goals:**
- A bolt's units are built side by side as far as slots allow, from the moment the bolt is given.
- A dependent codes on its dependency's plan and lands after it.
- A conflict between units is known before either is finished, and is resolved by the later unit with both intents in hand.
- The user sees every change before its bolt lands, a batch at a time, and what the user says reaches the unit while it can still change.

**Non-Goals:**
- Changing what `After` means (record 0011's point 1 stands).
- Building sluice, or crew's side of its after-entries. D7 only switches the merge command where sluice is available.
- Amending a merged unit. A defect is a fix, new work a new unit.
- Moving proposal, verify or landing cards off plannotator sessions. Only the batch card reads in Pending You alone.

## Decisions

### 1. Construct fans out (D1)

`run_check` drops the `waiting` refusal for construct. A unit with no place reads `ready` whatever its After units are; `waiting` now means a constructed unit whose code is held (decision 2). The conductor's building loop runs construct for every unit of the bolt with no change, in the file's order, as slots free (`teams.1` still caps units in flight).

### 2. After holds code and merge, not construct (D2)

An After unit has finished construct when its stage is `planned`, `waiting`, `code`, `verify`, `merged` or `landed`: its change is committed and its planning complete. `amended` and `construct` are not finished.

- **Code** is refused while any After unit has not finished construct, naming them. The unit reads `waiting`.
- **The dependent's place.** When code starts, crew brings into `unit/<unit>` the head of each After unit not yet merged, as a merge of that head (never a push, never a write to the After unit's branch), in the dependent's place. The heads taken are recorded on the `stage.start` entry.
- **Rebase on merge.** When an After unit merges, crew rebases each dependent's place onto `bolt/<bolt>` at the next read of the team that finds the dependent's agent not working (`teams.2`, `briefs.8`) and its place clean (`plan.9`'s test). Commits the bolt already holds drop out. A rebase that conflicts is aborted with the place as it was, and handed to the dependent's agent as decision 5 says.
- **Merge** is refused while any After unit has not merged, naming them. Under sluice the queue's after-entries hold it as well; crew's refusal stays, so a kit without sluice is held the same way.

### 3. No review gate (D5)

`crew unit approve`, the `review` and `approved` stages and the `review/<unit>/<head>` rail row go. A unit whose change's planning is complete reads `planned` (or `waiting`, decision 2), and code is accepted there. An amended unit reads `amended` until construct runs again and `construct` while it runs; once its construct has committed the mark stops counting, the unit reads from its tasks again, and crew removes the mark in the plan write that records the construct's end (`plan.6` as amended). `Reviewed-by` commits already on branches are left alone and read by nothing.

### 4. Touches is parsed (D8)

`construct.md` has the change end `proposal.md` with `## Touches` and one fenced block of paths or globs relative to the kit's root, one to a line; `**` crosses directories. crew reads the block from the place before code starts, and refuses code naming what is missing when there is no heading, no block, or an empty block (`read.1`). Two units overlap when an entry of one matches a path the other's entry names or a glob of one matches a glob of the other by literal prefix up to its first wildcard; overlap is a forecast, never a refusal.

When a unit's code is about to start and its Touches overlap those of an unmerged unit ahead of it in the file's order, crew tells the later unit's agent, through `crew tell` (`roles.4`), the overlapping entries and the path of the other unit's change.

At verify, crew adds to the verify prompt the output of `git diff --name-only bolt/<bolt>...unit/<unit>` filtered to the paths no Touches entry matches, and `verify.md` has the report name each as "changed and not declared". crew does not change the list itself.

### 5. Conflicts are forecast, and the later unit resolves (D3, D4)

On every `crew unit wait` and `crew prove --wait`, before it waits, crew runs on the team's host, for each unmerged unit with a place, `git merge-tree --write-tree --name-only bolt/<bolt> unit/<unit>` and, for each unmerged unit ahead of it in the file's order, `git merge-tree --write-tree --name-only unit/<ahead> unit/<unit>`. `merge-tree` writes objects and no ref, so no branch moves. A non-zero exit with conflicted paths is a forecast for the later unit. A forecast is told once for a pair of heads: crew records `forecast.tell` in the run record with both heads and the paths, and tells again only when a head has moved and the conflict remains. It is told when the later unit's agent is not working; otherwise at the next wait that finds it idle.

The tell, and the hand-off of a real conflict at a rebase or at merge, carry the other unit's change path, its proposal's *Why* and *What Changes*, and the conflicting paths, and ask the agent to resolve in its own place keeping both intents (`teams.13`). The earlier unit is never changed for it. `coder.md` gains how: read the other change, keep both, run the tests the paths affect, commit.

### 6. Batches (D5, D6)

- **What is due.** A unit's change is due each time a construct stage of it ends delivered: the `stage.end` entry names construct's commit. A batch entry, `review.batch`, names the team, the bolt, a batch number and each unit with the commit its change was read at. A change is due while no batch names the unit at its latest construct commit. Everything is read from the run record and the kit (`state.2`, `state.4`).
- **When.** On each of the conductor's waits, crew counts the team's due changes and reads the time of the team's last `review.batch`. With N or more due, or T hours or more since the last batch and at least one due, a batch is due, and the wait answers with it before waiting. N and T come from the team's entry in the teams file (decision 9).
- **The reviewer.** `crew review <team>` starts a fresh agent of a new role, `reviewer` (`plugin/roles/reviewer.md`, its model and effort in its frontmatter, `teams.6`), with the list of due units and the commit of each. It reads each change whole at that commit and writes `{{REPORTS}}/batch-<bolt>-<n>.md`: one section per unit, with what the change does, the decisions it took, its risks, its Touches, and what the user would likely care about, in the change's own words where it can. The file is its deliverable (`teams.4`); `crew review <team> --wait` returns its path, and the `review.batch` entry is written when it is delivered. The reviewer changes nothing in any place.
- **The card.** The conductor posts the batch as one card keyed `batch/<bolt>/<n>`, a new rail row and a new card key in the card hook (`briefs.11`). The card carries each unit's summary from the file and attaches or links each unit's whole change, its proposal, design, specs and tasks, so the user reads and answers in Pending You (`briefs.9` as amended); no plannotator session is started. It asks one question per unit, fine or feedback in words. An agent never answers it (`roles.2`).
- **Answers.** Fine changes nothing. Feedback on an unmerged unit runs `crew unit run <unit> construct "<the user's words>"`, held while that unit's construct is running until it settles (`briefs.5`); the unit goes on with no approval, and its revised change is due again. Feedback on a merged unit is a fix with the user's words, or, when it is new work, a tell to the planner.
- **Landing guard.** `rail_rows` offers `land/<bolt>` only once every unit's latest construct commit is named by a `review.batch`. When the proof is clean and some are not, a batch is due at once for them; the conductor's landing card names them as waiting on that batch, and `crew bolt land` is refused while any remains outside a batch.

### 7. Merging (D7)

The merge stage's prompt is `wt submit bolt/<bolt>` where sluice is available for the kit, else `wt merge bolt/<bolt> --no-squash --no-remove` as now (`teams.5` as amended). Without sluice, the conductor merges one unit at a time, as now; a merge refused by the gate or by a conflict goes back to the unit's agent (decision 5). How crew learns that sluice is available is open (question 7).

### 8. The briefs

- `conductor.md`: the building loop constructs every unit at once and starts code as soon as `crew bolts` shows a unit `planned`; the *Touches* sentence at line 83 goes; *Review with the user* becomes batches: run `crew review` when a wait says a batch is due, post the card, act on each answer; the review row leaves *Cards* and the batch row joins it; *Changing a unit after it was approved* loses its re-approval; the landing card names units outside a batch.
- `construct.md`: the Touches block in its parsed form; *Writing a change again* no longer says the user reviews before more is coded, and says the revision goes into the next batch.
- `coder.md`: resolving a forecast or a conflict, keeping both intents.
- `verify.md`: undeclared paths are findings.
- `reviewer.md`: new.

### 9. The team's batch setting

`teams.json` gains, per team, `review: {every: <N>, hours: <T>}`. crew reads both and refuses a team without them (`code.5`: no field has a default in crew); the defaults, 5 and 4, are written by swancloud's `lib/crew-teams.nix`, which writes the file. That edit is in swancloud, not here (open question 1).

### 10. Rules

Amended in the same commit as record 0014: `plan.6`, `plan.13`, `teams.5`, `briefs.4`, `briefs.9`, and `roles.2`'s details. New: `teams.12`, `teams.13`, `briefs.12`. All accepted and not built until this change lands (`_open.md`).

## Risks / Trade-offs

- [Code built on a change the user later rejects] → feedback amends the unit in flight; the cost is rework on the units whose batch came back with feedback, against the idle time of every unit today.
- [A dependent codes against an After unit's work that later changes] → the rebase at the After unit's merge brings the final form; a conflict there goes to the dependent's agent.
- [More conflicts, since overlapping units now build together] → forecast on every wait, told before either is finished; the merge queue attributes any that remain to the later entry.
- [Forecast cost: one `merge-tree` per unmerged unit plus one per pair] → bounded by slots, run on the team's host in one ssh with the wait's own read.
- [A bolt lands with a batch posted and unanswered] → D6 asks only that every change appeared in a batch; see open question 9.
- [Stage words change in `crew bolts --json`] → `review` and `approved` go, `planned` comes; the only reader is crew.

## Migration Plan

Pull on every host and restart conductors, ops and planners for the new briefs. swancloud writes `review` for every team before the first crew that reads it; a crew from before this change ignores the field. A unit in `review` or `approved` when this lands reads `planned` and may start code; its change is due for the first batch. Open `review/<unit>` cards are withdrawn by their conductors at restart. Rollback: revert; units read `review` again and wait on `crew unit approve`.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Once the bolt has landed and every host has pulled, with the standing agents restarted:
- Give a team a bolt of three units, one with `After` on another. All three constructs start at once; the dependent's code starts once its After unit's construct has committed, and its merge is refused until the After unit has merged.
- Two units whose Touches overlap build side by side; the later one's agent is told the overlap before its code, and a forecast conflict while both are in code.
- After the fifth construct, or four hours, a batch card arrives in Pending You with a summary per unit and each whole change readable there. Feedback on one unit amends it, and its code goes on with nothing to approve; the revised change is in the next batch.
- The landing card is offered only once every unit's latest change has been in a batch.

## Open questions

What the operator's ruling and the rules leave unsettled. Each is also under *Decisions waiting* in `docs/architecture/_open.md`; a task that depends on one waits for its answer.

1. **The batch setting's defaults.** D5 gives defaults of 5 and 4 hours; `code.5` says no field of the teams file has a default in crew, and crew never writes the file. Decision 9 puts the defaults in swancloud's `lib/crew-teams.nix`; that needs the operator's word and a change in swancloud.
2. **Where the reviewer runs.** It is not a unit, so not a slot (`teams.1`), and a team's standing roles are its conductor and ops (`bolt-teams` "A team's standing roles are its conductor and ops"; "A team is two herdr workspaces" lists its panes). A pane of its own, a turn in ops's pane, or a slot taken while free are all open.
3. **Who posts the card.** D5 has the reviewer post it; `briefs.11` says a team's cards are its conductor's and no stage agent posts one. Decision 6 follows `briefs.11`: the reviewer writes the file, the conductor posts. To be confirmed.
4. **One question per unit on one card.** The rail and the card hook know four card keys; a batch card adds a fifth. Whether Pending You carries a question per unit with an answer per unit on one card, and how a whole change of several files is attached or linked from a host that may not be the user's, is not settled by the ruling or by record 0005.
5. **Where a forecast or a conflict goes when no stage is running.** Every stage is a fresh agent (`teams.2`) and ends at its deliverable (`teams.4`). After a stage delivers, the slot's agent is idle with its stage over: a tell sets it working outside any stage crew waits on. A unit between stages (`planned`, `waiting`) may have no agent at all. Whether a forecast goes to the running agent, into the next stage's prompt, or starts a stage of its own for resolving is open; the same holds for a rebase conflict handed back under D2.
6. **What resolving a forecast means before either unit merges.** The later unit can't merge the earlier unit's unmerged head without taking its work as D2 does for `After`. Whether it adapts its own code only, or takes the other head as a dependent would, is open.
7. **How crew knows sluice is available** for a kit (a teams-file field, the kit's `wt` configuration, or `wt submit` answering), and whether sluice's verdict replaces or follows the merge hooks' suite gate (`state.3`, `tests.*`, record 0008).
8. **"Ahead of it".** D3 compares a unit with sibling heads ahead of it. Decisions 4 and 5 read that as the file's order (`bolt-plan`); under sluice the queue's order is submission order, and the two can differ.
9. **"Appeared in a batch".** D6 asks that every latest change appeared in a batch, not that its question was answered. A bolt can then land with feedback still to come. Whether an unanswered batch holds the landing is open.
10. **Who corrects Touches.** D8 says the list is corrected after verify; verify changes nothing (`briefs.2`), and a code stage that edits `proposal.md` changes the change. Whether it is the code stage acting on the finding, or construct run again (which makes the change due for a batch again), is open.
11. **A dependent's construct before its After unit's change exists.** Record 0011's first driver: a spec written before the contour exists invents it. D1 lets the dependent's construct run before its After units' changes are written; D2 holds only its code. Whether the dependent's change is revised once its After units' changes commit is open.
12. **An After unit amended after its dependent started code.** The After unit goes back to `amended` and `construct`; the dependent's code is already running on its old plan. Whether the dependent is told, held or left is open.
13. **unit-amendments is built and not archived.** Its deltas to `bolt-plan`, `bolt-teams` and `plan-proposals` say an amended unit returns to the user's review and waits for `crew unit approve`; its `plan-proposals` requirement "An amendment is read as before and after" has `crew plan proposed` say so. It must be archived before this change, and that requirement then needs a MODIFIED delta here, which can't be written until it is in `openspec/specs/`.

## Task notes

### 1.1

`Stages.of` and `place_stage`: the stage list in the `bolt-plan` delta. A unit with no place reads `ready` in a held bolt whatever its After units. `run_check`: construct has no `waiting` refusal; code is refused while an After unit has not finished construct, naming them, and accepted at `planned`; merge is refused while an After unit has not merged. Remove the code refusal at `review` and the mark's "waits for the user's review" message. Fixture kits in `tests/` for each stage and each refusal.

### 1.2

`crew unit approve` and its usage line go; `may_write` no longer lists it; the `review` rail group and `review/<unit>` key go from `rail_rows`, `lost_rows` and the card hook. The construct that ends an amended unit's construct clears the mark in the plan write `stage_ends` makes.

### 2.1

The Touches reader in `gather.py` (stdlib only, `code.1`), returning the entries or what is missing; `run_check` for code refuses without them. The overlap test and the tell before code.

### 2.2

The forecast in the wait (decision 5), with `forecast.tell` entries and the once-per-pair-of-heads rule. Stub git is not needed: the tests build two units in a scratch kit that conflict on one line.

### 2.3

The dependent's place at code start and the rebase at an After unit's merge (decision 2), with the hand-off on conflict.

### 3.1

`review.batch` and the due count; `crew review <team>` and `--wait`; the reviewer role; the batch rail row and card key; the landing guard in `rail_rows` and `bolt land`. Waits for open questions 1 to 4.

### 4.1

The merge prompt with `wt submit` where sluice is available. Waits for open question 7.
