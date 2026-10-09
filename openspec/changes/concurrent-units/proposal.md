# Units build at once and are reviewed in batches

## Why

A bolt's units are built nearly one at a time. A unit with `After` cannot even be constructed until each After unit has merged, so a chain runs end to end. Two units whose *Touches* lists overlap are built one after the other, compared by eye from prose nothing reads. And every unit stops after construct until the user reviews it, one card per unit, so a unit constructed at night idles until the user's next look. The user's time is the scarcest thing in a bolt, and a merge queue (sluice) lands units in order and attributes a conflict to the later entry, so the gates cost more than they protect.

The operator ruled on 2026-10-09 (record 0014): plan, then fan out; dependencies are on plans, not merges; overlap only orders merging, and a conflict is forecast and resolved by the later unit with both intents in hand; review comes in batches after building has started, with feedback that amends the unit in flight; and Touches is a list crew reads and checks.

## What Changes

- **Every unit's construct runs at once**, slots permitting, once its bolt is given. Construct never waits on `After`.
- **A dependent codes on its After units' plans.** A unit may start code once each After unit has finished construct. Before its code starts, its place takes each After unit's work as it stands; when an After unit merges, crew rebases the dependent's place onto the bolt while its agent is idle. A unit never merges before its After units: crew refuses the merge, and under sluice the queue's after-entries hold it. What `After` means does not change.
- **No review gate.** Code starts as soon as construct has committed. `crew unit approve` and the unit review card go, and the `approved` and `review` stages with them.
- **Batch review.** Every N constructed or amended changes, or T hours since the last batch, whichever comes first (a team's setting, 5 and 4 hours by default), a fresh reviewer agent summarizes each change not yet seen: what it does, the decisions it took, its risks, its Touches, and what the user would likely care about. The conductor posts the batch as one Pending You card with a question per unit, fine or feedback; the card carries each unit's summary and attaches or links its whole OpenSpec change, so the user reads and answers in Pending You. Feedback runs construct again with the user's words, and the unit goes on with no re-approval. A merged unit is never amended: feedback on it becomes a fix or a new unit.
- **Landing guard.** A bolt is offered for landing only once every unit's latest change has appeared in a batch; the landing card names any that have not, and a batch is triggered for them.
- **Touches is a list crew reads.** Construct ends `proposal.md` with a fenced list of repository paths or globs under `## Touches`. crew reads it before code and tells a unit whose Touches overlap a unit in flight. At verify, the paths the unit changed against its bolt that its Touches do not declare are a finding, and the list is corrected.
- **Conflicts are forecast.** On each of the conductor's waits, crew dry-runs with `git merge-tree` the merge of each unmerged unit's head with the bolt and with the heads of the sibling units ahead of it. A predicted conflict is told to the later unit's agent when it is idle, with the paths and the other unit's change. Overlap orders merging, never building.
- **The later unit resolves.** A conflict, forecast or real, at a rebase or at merge, is resolved by the later unit's agent, handed the other unit's change and the conflicting paths.
- **Merging through sluice.** Where sluice is available the merge stage runs `wt submit bolt/<bolt>`; until then it runs `wt merge` as now, one merge at a time.

## Capabilities

### New Capabilities

- `review-batches`: constructed and amended changes reach the user in batches, one card each, answered per unit; feedback amends the unit in flight; a bolt lands only once every unit's latest change has been in a batch.

### Modified Capabilities

- `bolt-plan`: `After` holds a dependent's code and merge, not its construct; a unit's stages lose `review` and `approved`; the user's approval commit goes.
- `bolt-teams`: every unit is constructed at once; code needs no review; a dependent's place takes its After units' work and is rebased as they merge; Touches is read; conflicts are forecast and resolved by the later unit; the merge stage runs through sluice where it is available.

## Impact

- `plugin/lib/plan.py`: `run_check` (construct never waits; code waits on After units' construct, not on approval; merge waits on After units' merge), `Stages.of` (no `review` or `approved`; `waiting` and `planned`), `unit approve` removed, the Touches reader, the forecast, the dependent's place and rebase, batch bookkeeping read from the run record, the rail's batch row, the landing guard.
- `plugin/bin/crew`: the merge stage's command, `crew review`, the usage header.
- `plugin/roles/conductor.md` (the building loop, review, cards), `plugin/roles/construct.md` (the Touches list; a revision is not re-reviewed), `plugin/roles/coder.md` (resolving a conflict), `plugin/roles/verify.md` (the Touches finding), a new `plugin/roles/reviewer.md`.
- The teams file gains a team's batch setting, written by swancloud's `lib/crew-teams.nix`.
- `README.md`, `plugin/skills/crew/SKILL.md`, `tests/`.
- Depends on `unit-amendments` being archived first: its deltas to `bolt-plan` and `bolt-teams` speak of re-approval, which this change removes.

## Touches

```
plugin/lib/plan.py
plugin/lib/gather.py
plugin/lib/crew.py
plugin/bin/crew
plugin/roles/conductor.md
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
docs/architecture/_open.md
```
