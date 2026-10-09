# Units build at once and are reviewed in batches

## Why

A bolt's units are built nearly one at a time. A unit with `After` cannot even be constructed until each After unit has merged, so a chain runs end to end. Two units whose *Touches* lists overlap are built one after the other, compared by eye from prose nothing reads. And every unit stops after construct until the user reviews it, one card per unit, so a unit constructed at night idles until the user's next look. The user's time is the scarcest thing in a partition, and a merge queue (sluice) lands units in order and attributes a conflict to the later entry, so the gates cost more than they protect.

The operator ruled on 2026-10-09 (record 0014): plan, then fan out, changes written in waves; dependencies are on plans, not merges; overlap only orders merging, and a conflict is forecast and resolved by the later unit with both intents in hand; review comes in partition-wide batches after building has started, with notes that amend the unit in flight; and Touches is a list crew reads and checks.

## What Changes

- **Changes are written in waves.** Once a bolt is given, every unit whose After units have finished construct is constructed, slots permitting: the units with no `After` at once, each dependent as soon as the changes it builds on are committed. Construct never waits on a merge.
- **A dependent builds on its After units' work as it stands.** Its place takes each unmerged After unit's head when it is made; when an After unit merges, crew rebases the dependent's place onto the bolt while its agent is idle. An After unit amended later is told to the dependent, which is not held. A unit never merges before its After units.
- **No review gate.** Code starts as soon as construct has committed. `crew unit approve` and the unit review card go, and the `approved` and `review` stages with them.
- **Partition-wide batch review.** Every N constructed or amended changes across the partition's teams, or T hours since the last batch, whichever comes first (the partition's setting, 5 and 4 hours by default, written by swancloud), crew tells the planner, which starts a fresh reviewer, a main-level role, to summarize each change not yet seen. The planner posts the batch as cards of at most five units, each with every unit's summary and a link to its whole change, a "which need notes?" choice and one question for the notes, read and answered in Pending You. Notes go to each picked unit's team's conductor, which runs construct again with them, and the unit goes on with no re-approval. A merged unit is never amended.
- **Landing guard.** A bolt is offered for landing only once every unit's latest change has appeared in a batch; the landing card names any that have not, and a batch is due at once for them.
- **Touches is a list crew reads.** Construct ends `proposal.md` with a fenced list of paths or globs under `## Touches`. crew reads it before code and names an overlap with a unit ahead in the later unit's code prompt. At verify, paths the unit changed and did not declare are a finding, and the code stage on that finding corrects the Touches block.
- **Conflicts are forecast.** On each of the conductor's waits, crew dry-runs with `git merge-tree` the merge of each unmerged unit's head with the bolt and with the heads of the units ahead of it in the plan. A forecast reaches the later unit once: told to its agent when idle, in its next stage's prompt when none runs, or as a new settle stage when it waits to merge. Two unmerged units forecast to conflict are ordered by `After`. Overlap orders merging, never building.
- **The later unit resolves.** A conflict, forecast or real, at a rebase or at merge, is resolved by the later unit's agent, handed the other unit's change and the conflicting paths.
- **Merging through sluice.** A kit opts into sluice by a flag in its config; its merge stage then runs `wt submit bolt/<bolt>`, its pre-merge hooks the submit gate and sluice's verdict the merge gate. Otherwise `wt merge` stays, one merge at a time.
- unit-amendments is archived first.

## Capabilities

### New Capabilities

- `review-batches`: constructed and amended changes reach the user in partition-wide batches, summarized by the main level's reviewer and posted by the planner as cards of at most five units; notes amend the unit in flight; a bolt lands only once every unit's latest change has been in a batch.

### Modified Capabilities

- `bolt-plan`: `After` holds a dependent's construct until its After units' construct and its merge until their merge; a unit's stages lose `review` and `approved`; the user's approval commit goes.
- `bolt-teams`: changes written in waves; code needs no review; a dependent's place takes its After units' work and is rebased as they merge; Touches is read and checked; conflicts are forecast and reach the later unit, by a settle stage when it waits to merge; the merge stage runs through sluice where the kit opts in; an amended unit goes on with no re-approval.
- `plan-proposals`: an amendment's page says the unit goes on from its tasks, its revised change in the next batch.

## Impact

- `plugin/lib/plan.py`: `run_check` (construct waits on After units' construct; code accepted at `planned`; merge waits on After units' merge; settle), `Stages.of`, `unit approve` removed, the forecast, the dependent's place and rebase, batch bookkeeping read from the run record, `crew review`, the rail's batch rows and `CARD_KEYS`, the landing guard.
- `plugin/lib/gather.py`: the Touches reader. `plugin/lib/crew.py`: the partition's batch setting, the reviewer's tab.
- `plugin/bin/crew`: the merge stage's command, the settle stage, the usage header. `plugin/hooks/cards`: the batch key.
- `plugin/roles/conductor.md`, `planner.md`, `construct.md`, `coder.md`, `verify.md`, and a new `reviewer.md`.
- swancloud's `lib/crew-teams.nix`, outside this repository: each partition's batch setting.
- `README.md`, `plugin/skills/crew/SKILL.md`, `tests/`.

## Touches

```
openspec/changes/unit-amendments/**
openspec/changes/archive/**
openspec/specs/**
plugin/lib/plan.py
plugin/lib/gather.py
plugin/lib/crew.py
plugin/bin/crew
plugin/hooks/cards
plugin/roles/conductor.md
plugin/roles/planner.md
plugin/roles/construct.md
plugin/roles/coder.md
plugin/roles/verify.md
plugin/roles/reviewer.md
plugin/skills/crew/SKILL.md
README.md
tests/**
docs/architecture/plan.md
docs/architecture/teams.md
docs/architecture/briefs.md
docs/architecture/core.md
docs/architecture/tests.md
docs/architecture/_open.md
```
