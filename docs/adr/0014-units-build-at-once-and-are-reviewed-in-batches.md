---
number: 14
title: Units build at once and are reviewed in batches
status: accepted
date: 2026-10-09
decision-makers:
- Chuck Swanberg
- the concurrent-units design session
---

# Units build at once and are reviewed in batches

Deciders: the user, Chuck Swanberg, ruling in the operator's side session on 2026-10-09 (decisions D1 to D8 below, with their answers that day on how each is carried out; their word to the design agent the same day: "The operator ratified the design on 2026-10-09", crew tell from chuck@mac-studio) and on 2026-10-10 on the design agent's card req_efe92149919a475b8ae1 (a plannotator session per unit; the cards change archived and a `rail-cards` delta; the batch setting as swancloud's unit; this line); the concurrent-units design session, which wrote this record and the change `concurrent-units`; swancloud-design, which reviewed both.
Sources: `openspec/specs/bolt-plan/spec.md` "The file's order and dependencies are the plan" and "A unit's stage is read from the kits"; `openspec/specs/bolt-teams/spec.md` "The user reviews every unit before it is coded"; `plugin/roles/conductor.md` line 83 (the building loop's Touches rule); `plugin/roles/construct.md` line 27 (the Touches list); `plugin/roles/planner.md` *Cards*; `plugin/lib/plan.py` `run_check` and `CARD_KEYS`; record 0011; the sluice statement, `agentplot/blueprints:design/sluice/requirements.md`, on order at landing and conflict attribution, and sluice's record 0002 on the submit gate; Pending You's limit of five options on a choice.

## Context and problem statement

A bolt's units are built nearly one at a time. Three gates hold them back:

1. **After waits on merge.** A unit with `After` cannot start construct until each After unit has merged into the bolt (record 0011, `plan.13`), so a chain of three units runs end to end: construct, review, code, verify and merge, three times over.
2. **Overlapping Touches serialize building.** The conductor builds two units side by side only when their *Touches* lists do not overlap (`conductor.md` line 83), and "when in doubt, don't". The lists are prose at the end of `proposal.md` (`construct.md` line 27), compared by eye; nothing reads them, and nothing checks them against what the unit changed.
3. **Every unit waits on the user's review before code** (`teams.5`, `bolt-teams` "The user reviews every unit before it is coded"). A unit constructed at night sits in review until the user reads it, and the user reads changes one card at a time, across four switchboard teams.

The user's time is the scarcest thing in a partition, and a merge queue (sluice) lands units in order and attributes a conflict to the later entry. What the gates protect can be had more cheaply: a dependent needs its dependency's plan, not its merge; an overlap matters only at merge; and the user's view of every change can come in batches across the partition, after building has started, with notes that amend the unit in flight.

## Decision drivers

- Concurrency is bounded by slots, not by the user's reading speed or by the longest chain of `After`.
- A dependent builds on its dependency's contour (record 0011), and a change written before the contour has a name invents it. Once the dependency's change is written, the contour has a name and a shape.
- A conflict between two units is found most cheaply before either is finished, and is resolved best by an agent that knows both intents.
- The user sees every change before its bolt lands, and what the user says about a change still reaches it while it can be changed.
- Only the user approves (`roles.1`, `roles.2`): notes in a batch are the user's word, and nothing here lets an agent approve on its own judgment.

## Considered options

1. **Keep the review gate**: code waits for the user's approval of each unit. Keeps the user ahead of every line of code, at the cost of every unit idling between construct and the user's next look; the user reads one change per card and the bolt moves at the user's pace.
2. **Serialize building on Touches overlap**, as the building loop does today. Avoids conflicts by never building overlapping units together; costs the concurrency a merge queue makes safe, and rests on lists nothing reads.
3. **Dependents wait for merge**, record 0011's point 2. The dependent reads the contour as merged code; a chain runs end to end.
4. **Plan in waves, then fan out; dependencies on plans; conflicts forecast; batch review across the partition**, the operator's ruling of 2026-10-09.

## Decision outcome

Option 4, as the operator ruled on 2026-10-09:

- **D1 Plan in waves, then fan out.** Once a bolt is given, every unit whose After units have finished construct is constructed, slots permitting: the units with no `After` at once, each dependent as soon as the changes it builds on are committed. Construct never waits on a merge. Record 0011's reason, that a dependent's spec must not invent its dependency's contour, is met at the dependency's construct.
- **D2 Dependencies are on plans, not merges.** A dependent's place is made from the bolt's line with each After unit's work taken as it stands; when an After unit merges, the dependent's place is rebased onto the bolt while its agent is idle. An After unit amended after its dependent's code started is told to the dependent, which is not held. A unit never merges before its After units; under sluice the queue's after-entries enforce it. Record 0011's meaning of `After` stands, widened by D3: a forecast conflict between two unmerged units also sets it.
- **D3 Overlapping Touches no longer serialize building.** Overlap only orders merging. On each wait of the conductor's, crew dry-runs with `git merge-tree` the merge of each unmerged unit's head with the bolt's line and with the heads of sibling units ahead of it, "ahead" and "later" being the plan's order. A forecast reaches the later unit once: told to its agent when idle; carried in its next stage's prompt when no agent of it runs; or, when it has delivered and waits to merge, as a settle stage, a fresh agent in its slot whose deliverable is a commit on its branch. A forecast conflict between two unmerged units gives the later unit `After` on the earlier: it takes the earlier unit's work, resolves, and merges after it. The building loop's "build them one after the other" goes.
- **D4 The later unit resolves.** A conflict, forecast or real, is resolved by the later unit's agent, which is handed the other unit's OpenSpec change and the conflicting paths, so that keeping both intents is informed.
- **D5 No review gate; batch review across the partition.** Code starts as soon as construct is done; `crew unit approve` and the gate in `teams.5` go. A batch spans every team of a partition. Every N constructed or amended changes across the partition, or T hours since its last batch, whichever comes first (the partition's setting; N = 5, T = 4 hours, written by swancloud's `lib/crew-teams.nix`), a reviewer summarizes each change not yet seen: what it does, the decisions it took, its risks, its Touches, and anything the user would likely care about. The reviewer is a main-level role, beside the planner, run fresh for each batch. The planner posts the batch: `briefs.11` makes a team's cards its conductor's and keeps them from stage agents, and a batch is the partition's; the planner already owns the partition's proposal cards and stays up to act on an answer, where the reviewer ends at its file. A card holds at most five units, Pending You's limit on a choice; a larger batch is split across cards. Each card's body carries each unit's summary and the link to a plannotator session on its whole OpenSpec change, one per unit, first in the card's words, and it asks one choice of several, "which need notes?", and one question in words for the notes, answered in Pending You, a session's annotations read as that unit's notes (the user, 2026-10-10: a plannotator session per unit; the first draft started none; 2026-10-12: one session for the batch, on its folder with the summary whole and every change, and one card that says what it is and asks nothing, record 0005 as amended 2026-10-11 and 2026-10-12). The planner sends each picked unit's notes to its team's conductor, which amends the unit in flight through the existing amend path, construct run again with the user's words; the unit goes on with no re-approval. A unit that has merged is never amended: a defect is a fix, new work a new unit.
- **D6 Landing guard.** A bolt is offered for landing only once every unit's latest change has appeared in a batch; the landing card lists any that have not, and a batch is triggered for them. Appearing is the test; an unanswered card does not hold a landing. (Amended 2026-10-19 by the user's answer on card req_5ff4d31dc54241c29da8: "Wait for my answer on the batch card." A bolt is offered for landing only once every unit's latest change has been in a batch whose card the user has answered, `briefs.12`.)
- **D7 Merging.** A kit opts into sluice by a flag in its config. Opted in, the merge stage is `wt submit bolt/<bolt>`: the kit's pre-merge hooks become the submit gate and sluice's verdict replaces the merge hooks' suite gate (sluice record 0002). Otherwise `wt merge` stays, one merge at a time as now. (Amended 2026-10-13 by record 0026: sluice is the one merge path and the flag goes.)
- **D8 Touches is read and checked.** Construct writes Touches as a fenced list of repository paths or globs under a `## Touches` heading in `proposal.md`. crew reads it before code and tells a unit whose Touches overlap a unit ahead of it in flight, which feeds D3's forecast before any code exists. At verify, `git diff --name-only <bolt>...<unit head>` is compared with the declared list; a path changed and not declared is a verify finding, and the code stage on that finding corrects the Touches block, the one part of the change a coder may edit.

unit-amendments is archived before `concurrent-units` is built, so that its requirements can be modified by this one's deltas.

### Consequences

- **`plan.6`** is amended: an amended unit reads amended, then construct, and is refused code, verify and merge only until construct has committed again; no approval is asked.
- **`plan.13`** is amended: `After` names a unit the dependent builds on, or one a forecast conflict put it after; the dependent's construct waits on each After unit's construct, never its merge, and its merge on each After unit's merge.
- **`teams.5`** is amended: the approval gate goes; merge is refused before every After unit has merged; a merge goes through `wt merge bolt/<bolt> --no-squash --no-remove`, or `wt submit bolt/<bolt>` where the kit opts into sluice, whose verdict replaces the merge hooks' suite gate. `tests.5`'s details note that under sluice the suite gates through the submit gate.
- **`briefs.1`** gains the reviewer, which writes only its summary file. **`briefs.2`** gains its one exception: after a verify finding, the code stage may edit the Touches block of `proposal.md`.
- **`briefs.4`** is amended: a change is put before the user on a batch card, not as a review of its own. **`briefs.5`** stands; its last clause covers notes to a unit whose construct is still running, which wait until that construct settles.
- **`briefs.9`** stands for a batch card as for every card that asks the user to read something: one plannotator session per unit, its link first in the card's words, the card answered in Pending You.
- **`briefs.11`** stands: a team's cards are its conductor's. A batch card is the partition's and the planner's, as a proposal card is.
- **`roles.1` and `roles.2`** stand: only the user approves. A batch's notes are the user's word; nothing in a batch is an approval an agent can give, and `crew unit approve` leaves the approvals crew does not refuse by caller. A conductor's `After` on a forecast conflict is a write within its own bolt, which `roles.1` already gives it.
- **`teams.1`** and **`teams.7`**: the reviewer takes no slot and, sent its batch as a stage is sent its prompt, is not greeted.
- New rules `teams.12` (Touches is read; forecasts reach the later unit once and order only merging), `teams.13` (the later unit resolves a conflict), `teams.14` (the settle stage) and `briefs.12` (the partition's batch review and the landing guard).
- The `bolt-plan`, `bolt-teams`, `plan-proposals` and `rail-cards` specs, and a new `review-batches` spec, change only through `concurrent-units`' deltas (`docs.4`); the cards change is archived first, as unit-amendments is, so the `rail-cards` delta finds its requirement. The briefs, a reviewer role, `plan.py`, `plugin/bin/crew` and the card hook follow in that change; swancloud's `lib/crew-teams.nix` is swancloud's own unit, `partitions-carry-their-batch-setting`, landed and deployed before it, since crew's reader will refuse a partition without the setting. Until it is built, the amended and new rules are accepted and not built (`_open.md`).
