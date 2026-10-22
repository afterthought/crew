# Proposal

## Why

A team that has finished building sits idle until its bolt has landed: the proof, the landing card, the user's yes and main-level ops's submission, and a carrying fix when main moved. On 2026-10-11 the emergency ssh bolt, approved as proposal 114, could not be given while swc-1 held a bolt whose every unit had merged, its four slots idle; the user: "I approved it and you added it to a bolt that's going to end up waiting on six other things." Record 0020, accepted by the user on 2026-10-18, decides that a team is free for its next bolt once its current one is proven, and `teams.16` states the rule.

## What Changes

- `crew bolt give` gives a team its next bolt once every bolt it holds is proven: every unit and chore merged and sluice's verdict green at the bolt's head. It refuses only while a held bolt has a unit or chore not merged, has none yet, or has a verification not green, and while the team already holds two bolts. A fix in flight on the proven bolt refuses nothing.
- A team holds at most two bolts: the one it builds, the last given, and one proven that waits to land. The proven bolt keeps of the team only what its landing needs: a fix's slot, when a landing or a forecast conflicts, and its team's ops. Slots stay bounded by `units`.
- `crew fix` takes `--bolt <bolt>`, required to start a fix while the team holds two bolts, so a carrying fix goes to the bolt that waits to land; a fix in flight is found by its name.
- The bolt a team builds is what its conductor and ops carry for sluice, what the ops greeting names and what a team of several kits works in.
- A give to a team holding a proven bolt restarts its conductor and ops at their next stop, not at once, and greets the conductor with both bolts: the one to build, and the one waiting to land with its open landing card and any fix in flight.
- When a merge leaves a team free and a bolt is planned for it, crew tells the partition's dispatchers, as it does for a landing.
- The rail's landing row says the bolt waits to land, what its team builds meanwhile, and what a yes frees: the team's next planned bolt, once nothing but this landing holds it. The landing card says the same.
- The conductor's band and the board draw a proven bolt as waiting to land.
- The conductor's, ops's and dispatcher's briefs, README, the crew skill and `crew`'s usage say a team builds one bolt and may hold one more waiting to land.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a team may hold a proven bolt beside the one it builds; fixes name their bolt; a landing leaves the team its other bolt; the branch a conductor carries is the bolt it builds.
- `bolt-plan`: `crew bolt give` refuses only while a held bolt is not proven, or the team holds two.
- `crew-rail`: the landing row says what the team builds meanwhile and what a yes frees.
- `rail-cards`: the landing card says what a yes frees.
- `crew-board`: a proven bolt's ledger says it waits to land.

## Impact

`plugin/lib/plan.py` (`bolt_give`, `holding`, `held_by`'s single-bolt callers, `fix_cmd`, `fix_in_slot`, `landing_after_merge`, `land_facts`, `landing_facts`, `rail_rows`, `bolt_land`, `greet_team`, `team_holds`, `held_repo`, `bolt_of_unit`, `where_of`, the forecast's take-main words, `Stages.bolt_state`), `plugin/lib/crew.py` (`team_bolt`), `plugin/lib/cards.py` (`landing_card`), `plugin/lib/board.py` (`bolt_row`), `plugin/bin/crew` (`crew fix --bolt`, usage), `plugin/roles/conductor.md`, `ops.md`, `dispatcher.md`, `README.md`, `plugin/skills/crew/SKILL.md`, the `bolt-teams` spec's purpose, and their tests. Rules: `teams.16` (built here), `teams.1`, `teams.3`, `teams.7`, `teams.20`, `plan.8`, `plan.16`, `roles.2`, `read.1`, `code.7`, `code.8`.

## Touches

```
plugin/lib/plan.py
plugin/lib/crew.py
plugin/lib/cards.py
plugin/lib/board.py
plugin/lib/hold.py
plugin/bin/crew
plugin/roles/conductor.md
plugin/roles/ops.md
plugin/roles/dispatcher.md
plugin/skills/crew/SKILL.md
README.md
openspec/specs/bolt-teams/spec.md
tests/py/**
tests/t-*.sh
tests/moon.yml
plugin/tests/**
```
