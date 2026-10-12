# Design

## Context

See proposal.md for why, and record 0014 for the operator's ruling of 2026-10-09. The current state:

- `run_check` in `plan.py` refuses construct for a unit whose stage is `waiting`, one with no place whose After units have not all merged; refuses code at `review` and at anything but `approved`, `code` or `verify`; refuses verify until every task is ticked; and sends merge the prompt `wt merge bolt/<bolt> --no-squash --no-remove`.
- `place_stage` reads `verify`, `code`, `approved` (planning complete and a `Reviewed-by` commit since the bolt), `review` (planning complete) or `construct`; an `Amended` mark reads `amended`, then `construct` while the head is where construct started, then `review` until `crew unit approve` clears it (unit-amendments, archived).
- The rail (`rail_rows`) and the card hook know four card keys (`CARD_KEYS`): `proposal/<n>`, the planner's, and `review/<unit>/<head>`, `verify/<unit>/<stamp>` and `land/<bolt>/<head>`, the conductor's. A review card links a plannotator session on the change folder, started by `crew card session <key>`, one session per key, on the host the command runs on (`briefs.9`).
- Touches is prose at the end of `proposal.md` (`construct.md` line 27), compared by eye by the conductor (`conductor.md` line 83), who builds overlapping units one after the other.
- The conductor waits on every stage with `crew unit wait <unit>` and on a proof with `crew prove <team> --wait`, background commands that return within the hour. crew runs no service (`state.4`), so the conductors' waits are the only clock a partition has.
- A partition's main level holds the design agent, the planner and main-level ops in one herdr workspace (`main-level` spec). The planner already posts the partition's proposal cards.

Pages whose areas this touches: `plan.md` (`plan.py`, `gather.py`), `teams.md` (`plugin/bin/crew`, `crew.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `tests.md` (`tests/`, `.config/`), `docs.md` (`README.md`, `openspec/`, `docs/`). Rules relied on: `plan.1`, `plan.6` and `plan.13` as amended, `plan.9`, `plan.10`, `teams.1`, `teams.2`, `teams.4`, `teams.5` as amended, `teams.7`, `teams.11`, `teams.12`, `teams.13`, `teams.14`, `briefs.1` and `briefs.2` as amended, `briefs.4` and `briefs.9` as amended, `briefs.5`, `briefs.11`, `briefs.12`, `roles.1`, `roles.2`, `roles.4`, `state.2`, `state.4`, `read.1`, `code.5`, `tests.5`, `docs.4`.

## Goals / Non-Goals

**Goals:**
- A bolt's units are built side by side as far as slots allow, their changes written in waves.
- A dependent builds on its dependency's plan and work as they stand, and lands after it.
- A conflict between units is known before either is finished, and is resolved by the later unit with both intents in hand.
- The user sees every change before its bolt lands, a partition's batch at a time, and what the user says reaches the unit while it can still change.

**Non-Goals:**
- Building sluice, or crew's side of it beyond the merge stage's command and the kit's opt-in.
- Amending a merged unit. A defect is a fix, new work a new unit.
- Moving any card off plannotator sessions: a batch card links one session per unit, as a review card did, and is answered in Pending You.

## Decisions

### 0. The change's deltas find their requirements

This change is `concurrent-units` as the operator ratified it and the user settled it, under its unit's name; `openspec/changes/concurrent-units` is removed by its code, and the rules that cite `concurrent-units` cite this change.

unit-amendments' deltas to `bolt-plan`, `bolt-teams` and `plan-proposals` spoke of re-approval, and the cards change, the-rail-is-answered-through-cards, holds the only statement of the card keys and of who posts a row's card. Both were archived by ops before this change was constructed, so that its MODIFIED deltas find their requirements in `openspec/specs/` (`docs.4`; the user, 2026-10-10, on the design agent's card).

Built changes not yet archived change some of the same requirements: a-command-reads-the-kits-once ("A unit's stage is read from the kits"), worktrees-go-with-their-work ("Work happens in fixed places"), a-decision-is-shown-whole ("The user reviews every unit before it is coded"), a-landing-card-is-the-heads ("Each rail row has a card key" and the card-sessions refusals), a-card-links-a-plannotator-session (the `card-sessions` capability) and a-card-reads-whole-at-a-glance (the card's words). Each is archived before this change is, by the same rule; this change's MODIFIED deltas carry what those added, so the order of archiving loses nothing of theirs.

### 1. Construct in waves (D1)

A unit with no place reads `ready` once each of its After units has finished construct, and `waiting` until then. An After unit has finished construct when its stage is `planned`, `code`, `verify`, `merged` or `landed`. `run_check` refuses construct at `waiting`, naming the After units still in construct, and never waits on a merge. The conductor's building loop runs construct for every `ready` unit, in the file's order, as slots free (`teams.1`). Changes are written in waves, so a dependent's change is written with its dependency's change in hand: record 0011's reason for holding a dependent stands, met at its dependency's construct instead of its merge.

### 2. After holds construct and merge (D2)

- **The dependent's place.** When the dependent's place is made, at its construct, crew merges into `unit/<unit>` the head of each After unit not yet merged, as it stands, in the dependent's place: never a push, never a write to the After unit's branch. The heads taken are recorded on the `stage.start` entry.
- **Rebase on merge.** When an After unit merges, crew rebases each dependent's place onto `bolt/<bolt>` at the next read of the team that finds the dependent's agent not working (`teams.2`, `briefs.8`) and its place clean (`plan.9`'s test). Commits the bolt already holds drop out. A rebase that conflicts is aborted with the place as it was, and goes to the dependent as decision 5 says.
- **An After unit amended later.** When an After unit is constructed again after its dependent's code has started, the dependent is not held: crew carries the amendment to it as decision 5 carries a forecast, with the revised change's path.
- **Merge** is refused while any After unit has not merged, naming them. Where the kit opts into sluice, the unit's After units are its after-entries as well.

### 3. No review gate (D5)

`crew unit approve`, the `review` and `approved` stages and the `review/<unit>/<head>` rail row go. A unit whose change's planning is complete reads `planned`, and code is accepted there. An amended unit reads `amended` until construct runs again and `construct` while it runs; once that construct has committed the mark stops counting, the unit reads from its tasks again, and crew removes the mark in the plan write that records the construct's end (`plan.6` as amended). `Reviewed-by` commits already on branches are left alone and read by nothing.

### 4. Touches is parsed and checked (D8)

`construct.md` has the change end `proposal.md` with `## Touches` and one fenced block of paths or globs relative to the kit's root, one to a line; `**` crosses directories. crew reads the block from the place before code starts, and refuses code naming what is missing when there is no heading, no block, or an empty block (`read.1`). Two entries overlap when one matches the other, or when two globs share their literal prefix up to the first wildcard.

When a unit's code is about to start and its Touches overlap those of an unmerged unit ahead of it, the code stage's prompt names the overlapping entries and the other unit's change.

At verify, crew adds to the verify prompt the paths `git diff --name-only bolt/<bolt>...unit/<unit>` names that no Touches entry matches, and `verify.md` has the report name each as "changed and not declared". The code stage the conductor runs on that finding corrects the Touches block of `proposal.md`, the one part of the change a coder may edit (`briefs.2` as amended).

### 5. Conflicts are forecast and reach the later unit (D3, D4)

On every `crew unit wait` and `crew prove --wait`, before it waits, crew runs on the team's host, for each unmerged unit with a place, `git merge-tree --write-tree --name-only bolt/<bolt> unit/<unit>`, and for each unmerged unit ahead of it in the file's order, `git merge-tree --write-tree --name-only unit/<ahead> unit/<unit>`. A dependent is compared with a unit it comes after from the head of that unit its place took, recorded as `Took` on its construct's start, with `--merge-base=<that head>` (git 2.40+), so only what it adds beyond that head is compared: the unit's own work, which the dependent carries and the unit's rebase onto the bolt or its settle rewrote, is no conflict of the dependent's. A start recorded before `Took` existed is compared from the merge base. `merge-tree` writes objects and no ref. A non-zero exit with conflicted paths is a forecast for the later unit. "Ahead" and "later" are the plan's order throughout; under sluice, the queue honours `After` as after-entries.

A forecast is recorded once for a pair of heads, `forecast` in the run record with both heads and the paths, and reaches the later unit once, in one of three ways:

- its stage's agent is running: told with `crew tell` (`roles.4`) once the agent is not working (`teams.11`);
- no agent of it is running and it has not delivered its verify: carried in the prompt of its next stage, which names the forecast entries it carries on its `stage.start`;
- it has delivered its verify and waits to merge: a settle stage (decision 6).

Each carries the other unit's change path, its proposal's *Why* and *What Changes*, and the conflicting paths.

- **With the bolt.** The later unit resolves in its place, rebased onto the bolt (`teams.13`).
- **Between two unmerged units.** The conductor sets `crew unit after <later> <earlier>` (`roles.1`: a conductor sets `After` within its own bolt), and the later unit's agent takes the earlier unit's work into its place itself, `git merge unit/<earlier>`, resolves the conflict there and commits; the later unit merges after the earlier one (`plan.13` as amended). crew does not make this merge, as it takes an After unit's head into a dependent's new place (decision 2): a forecast merge conflicts by definition, so crew could not finish it, and it would abort it as it aborts a take that conflicts.

The earlier unit is never changed for it. `coder.md` gains how: read the other change, keep both intents, run the tests the paths affect, commit.

The later unit's agent merging the earlier unit's work, here and at a rebase, stands in for a merge queue. sluice ([agentplot/sluice](https://github.com/agentplot/sluice), its statement in `agentplot/blueprints:design/sluice/requirements.md`) orders what is submitted, tests each candidate as it would land and names the later submission at fault, so where a kit merges through it (decision 8) that is where these merges are meant to go. (The user, 2026-10-11, on the card for this change's verify.)

### 6. The settle stage

`crew unit run <unit> settle "<what reached it>"` starts a fresh agent in the unit's slot with the coder's brief, for a unit that has delivered its verify and waits to merge, prompted with the forecast or the amendment. Its deliverable (`teams.4`) is a commit on `unit/<unit>` made since the stage began. When nothing needs to change, the agent stops short saying so (`teams.4`'s other ending), and the unit goes on to merge. A settled unit merges without verify being run again; the merge's gate runs the suite (`tests.5`). `run_check` accepts settle only at `verify` with a verify report delivered.

### 7. Batches (D5, D6)

- **What is due.** A unit's change is due each time a construct stage of it ends delivered: the `stage.end` entry names construct's commit. A batch entry, `review.batch`, names the partition, a batch number, and each unit with its team and the commit its change was read at. A change is due while no batch names the unit at its latest construct commit. Everything is read from the run record and the kits (`state.2`, `state.4`).
- **When.** A batch spans the partition, all its teams. On each wait of a conductor of the partition, crew counts the partition's due changes and reads the time of its last `review.batch`. With N or more due, or T hours or more since the last batch and at least one due, a batch is due, and crew tells the partition's planner once, `batch.due` in the run record, with the count. N and T come from the partition's entry in the teams file (decision 10).
- **The reviewer.** A main-level role, `reviewer` (`plugin/roles/reviewer.md`, its model and effort in its frontmatter, `teams.6`). The planner starts it with `crew review <label>` in a `review` tab of the main level's workspace, beside the planner, on the main level's host; it is sent the due units and their commits as its prompt, the way a stage is (`roles.4`), and is not greeted (`teams.7` names the standing agents). It reads each change whole at its commit, through the kit on the team's host, and writes `{{REPORTS}}/batch-<label>-<n>.md`: one section per unit with its team, what the change does, the decisions it took, its risks, its Touches, and what the user would likely care about, in the change's own words where it can. The file is its deliverable (`teams.4`); `crew review <label> --wait` returns its path, and the `review.batch` entry is written when it is delivered. The reviewer writes nothing else (`briefs.1` as amended) and its tab is closed when it ends.
- **The cards.** The planner posts them. `briefs.11` makes a team's cards its conductor's and keeps them from stage agents; a batch is the partition's, not a team's. The planner already owns the partition's rail rows (`proposal/<n>`), has the card discipline filled into its brief, and stays up to act on an answer, where the reviewer ends at its file. One card holds at most five units, Pending You's limit on a choice's options; a batch of more is split, each card keyed `batch/<n>-<k>` and a rail row of its own, added to `CARD_KEYS` and the card hook. Each card's body carries each unit's summary and, first in its words and among its links, the link to a plannotator session crew starts on that unit's whole change, its proposal, design, specs and tasks, one session per unit, started by `crew card session batch/<n>-<k> <unit>`. That command is about the unit's team, so it runs on the host the teams file names for the team (`code.3`), where the unit's kit is, with no browser opened there (`briefs.9`); `crew card wait` and `crew card end` take the key and the unit the same way. The card asks one choice of several, "which need notes?", listing its units, and one question in words for the notes, answered in Pending You, a session's annotations read as that unit's notes. The sessions end when the card closes. An agent never answers it (`roles.2`). (The user, 2026-10-10, on the design agent's card req_efe92149919a475b8ae1: a plannotator session per unit.)
- **Answers.** A unit not picked is fine. For each unit picked, the planner sends the notes verbatim to that unit's team's conductor (`crew tell`); the planner drives no team (`briefs.1`). The conductor runs `crew unit run <unit> construct "<the notes>"` for an unmerged unit, held while that unit's construct is running until it settles (`briefs.5`); the unit goes on with no approval, and its revised change is due again. For a merged unit, a defect is a fix with the user's words, and new work a tell to the planner.
- **Landing guard.** `rail_rows` offers `land/<bolt>` only once every unit's latest construct commit is named by a `review.batch`. When the proof is clean and some are not, a batch is due at once; the conductor's landing card names them, and `crew bolt land` is refused while any remains outside a batch. Since main-ops's `wt merge main` puts the bolt on main before `crew bolt land` closes it, `main-ops.md` has main-ops check, before that merge, that the bolt's landing row in `crew rail` carries its answer, and stop when it does not; that check is the brief's until a bolt's landing goes through a merge queue such as sluice (decision 5). "Appeared in a batch" is the test, as ruled: an unanswered card does not hold a landing.

### 8. Merging (D7)

A kit opts into sluice by a flag in its config, read with the kit. Opted in, the merge stage's prompt is `wt submit bolt/<bolt>`: the kit's pre-merge hooks become `wt submit`'s submit gate and sluice's verdict replaces the merge hooks' suite gate (sluice record 0002; `teams.5` as amended; `tests.5` stands, the suite still gating through sluice). Otherwise the prompt is `wt merge bolt/<bolt> --no-squash --no-remove` and the conductor merges one unit at a time, as now. A merge refused by its gate or by a conflict goes back to the unit's agent (decision 5).

### 9. The briefs

- `conductor.md`: the building loop constructs in waves and starts code as soon as `crew bolts` shows a unit `planned`; line 83's Touches sentence goes; *Review with the user* goes, replaced by acting on the planner's notes; the review row leaves *Cards*; *Changing a unit after it was approved* loses its re-approval; forecasts, `crew unit after` for two unmerged units, and settle; the landing card names units outside a batch.
- `planner.md`: run `crew review` when crew says a batch is due, wait on it, post its cards, send each picked unit's notes to its conductor.
- `construct.md`: the Touches block in its parsed form; a revision goes into the next batch.
- `coder.md`: resolving a forecast or conflict, keeping both intents; correcting Touches on a verify finding; the settle prompt.
- `verify.md`: undeclared paths are findings.
- `reviewer.md`: new.

### 10. The partition's batch setting

`teams.json` gains, per partition, `review: {every: <N>, hours: <T>}`. crew reads both and refuses a partition without them (`code.5`: no field has a default in crew). The defaults, N = 5 to match a card's five options and T = 4, live in swancloud's `lib/crew-teams.nix`, which writes the file. That edit is swancloud's own unit, `partitions-carry-their-batch-setting`, which lands and deploys before this change does; this change's task is crew's refusal (the user, 2026-10-10, on the design agent's card).

### 11. Rules

Amended in the same commit as record 0014: `plan.6`, `plan.13`, `teams.5`, `briefs.1`, `briefs.2`, `briefs.4`, `briefs.9`, and the details of `roles.2`, `teams.1`, `teams.7` and `tests.5`. New: `teams.12`, `teams.13`, `teams.14`, `briefs.12`. All accepted and not built until this change lands (`_open.md`).

## Risks / Trade-offs

- [Code built on a change the user later sends notes on] → notes amend the unit in flight; the cost is rework on noted units, against the idle time of every unit today.
- [A dependent codes against an After unit's work that later changes] → it is told of an amendment, and the rebase at the After unit's merge brings the final form; a conflict there goes to the dependent.
- [More conflicts, since overlapping units now build together] → forecast on every wait, before either is finished; two unmerged units in conflict are ordered by `After`.
- [Forecast cost: one `merge-tree` per unmerged unit plus one per pair] → bounded by slots, run on the team's host in one ssh with the wait's own read.
- [A bolt lands with a batch card unanswered] → as ruled, appearing in a batch is enough; notes that arrive after a merge become a fix or new work.
- [Stage words change in `crew bolts --json`] → `review` and `approved` go, `planned` and `settle` come; the only reader is crew.
- [The partition's clock is its conductors' waits] → a partition with no unit in flight has nothing due.

## Migration Plan

Pull on every host and restart conductors, ops and planners for the new briefs. swancloud writes `review` for every partition before the first crew that reads it; a crew from before this change ignores the field. A unit in `review` or `approved` when this lands reads `planned` and may start code; its change is due for the first batch. Open `review/<unit>` cards are withdrawn by their conductors at restart. Rollback: revert; units read `review` again and wait on `crew unit approve`.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Worked by the partition's main-level ops once the bolt has landed and every host has pulled, with the standing agents restarted:
- Give a team a bolt of three units, one with `After` on another. The two without start construct at once; the dependent's construct starts once its After unit's change is committed, and its merge is refused until the After unit has merged.
- Two units whose Touches overlap build side by side; the later one's code prompt names the overlap, a forecast conflict between them gives it `After` on the earlier, and it merges after it.
- A verified unit forecast to conflict with the bolt gets a settle stage, which ends at its commit.
- After five constructs across the switchboard teams, or four hours, a batch card arrives from the planner in Pending You with each unit's summary and a link to each whole change. Picking one unit and writing notes amends it through its team's conductor, and its code goes on with nothing to approve; the revised change is in the next batch. Seven due changes come as two cards.
- The landing card is offered only once every unit's latest change has been in a batch.

## Task notes

### 0.1

Done by ops before construct (crew main 6b40111): unit-amendments and the-rail-is-answered-through-cards are archived, and `openspec/specs/rail-cards` exists.

### 0.2

`git rm -r openspec/changes/concurrent-units`. In `docs/architecture/` (`plan.md`, `teams.md`, `briefs.md`, `_open.md`), every citation of `concurrent-units` names `units-build-at-once-and-are-reviewed-in-batches`; record 0014 keeps its words, being a record of the day. `openspec validate units-build-at-once-and-are-reviewed-in-batches --strict` passes.

### 1.1

`Stages.of` and `place_stage`: the stage list in the `bolt-plan` delta, `ready` and `waiting` by After units' construct. `run_check`: construct refused at `waiting`; code accepted at `planned` and refused at `construct`, with no refusal for review; merge refused while an After unit has not merged; settle accepted only at `verify` with a report delivered. Remove the review refusal and the mark's "waits for the user's review" message. Fixture kits in `tests/` for each stage and each refusal.

### 1.2

`crew unit approve` and its usage line go; `may_write` no longer lists it; the `review` rail group and the `review/<unit>` key go from `rail_rows`, `lost_rows`, `CARD_KEYS` and the card hook. The construct that ends an amended unit's construct clears the mark in the plan write `stage_ends` makes.

### 2.1

The Touches reader in `gather.py` (stdlib only, `code.1`), returning the entries or what is missing; `run_check` for code refuses without them; the overlap test and the code prompt's overlap lines; the undeclared paths in the verify prompt.

### 2.2

The forecast in the wait (decision 5), with `forecast` entries, once per pair of heads, and the three ways a forecast reaches a unit. Tests build two units in a scratch kit that conflict on one line.

### 2.3

The dependent's place at construct, the rebase at an After unit's merge, the amendment carried to a dependent, and `crew unit after` on a forecast between two unmerged units (decisions 2 and 5).

### 2.4

The settle stage: `run_check`, its prompt, its deliverable in `stage_ends` (a commit since the stage began).

### 3.1

`review.batch` and `batch.due`; the partition-wide count; `crew review <label>` and `--wait`; the reviewer role and its tab; the `batch/<n>-<k>` key in `CARD_KEYS` and the card hook; the split at five; `crew card session|wait|end batch/<n>-<k> <unit>`, forwarded to the unit's team's host, one session per key and unit, refused for a unit the batch does not hold; the landing guard in `rail_rows` and `bolt land`, whose key stays `land/<bolt>/<head>`.

### 3.2

crew's `teams.json` reader requires `review` on every partition, with `every` and `hours` (`code.5`). swancloud's `lib/crew-teams.nix` writes `review = { every = 5; hours = 4; }` for every partition in its own unit, `partitions-carry-their-batch-setting`, landed and deployed before this change merges; crew's reader ignores the field until this change lands, so the order holds.

### 4.1

The kit's sluice flag, read with the kit; the merge prompt `wt submit bolt/<bolt>` when it is on.
