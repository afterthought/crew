# A unit is verified, fixed and archived in one round

## Why

Once a unit's code has delivered every task ticked, its conductor runs verify, reads the report, and posts a verify card of its options, and the unit waits on the user, who almost always takes the recommendation. Record 0027 (accepted 2026-10-13, on the user's words: "if we just did one round of verify, fixed if necessary, and then archived, that would be a pretty simple standard process to start with", and "the whole point of verify is that it should be grounded in the original proposal") makes it one round with no card: verify checks the code against the change as written, its report says what to fix, a fresh coder fixes it, and the merge archives the change. Record 0006's archive at the merge was never built either, so changes reach main open; this builds it (`a-merged-change-is-archived`).

## What Changes

- **The report says what to do.** Verify checks the code against the unit's change as written, its proposal, specs, design and tasks, and ends its report with *What to do*: each finding marked fix or leave, a unit's as a chore's.
- **One fix round, by a fresh coder.** The conductor takes the marks as they stand: when one says fix, it runs code once more with the report's path, and the coder fixes every finding marked fix and only those; no verify runs after it, and the unit merges. Nothing from verify goes to the planner or waits on the user; a fix round that stops short or fails is a stuck stage (`teams.17`).
- **A unit's merge archives its change first.** The merge stage runs `openspec archive <unit> --yes` in the unit's place, commits it, then merges; crew reads the merge as delivered only once the bolt holds the change archived, and reads a place whose change its merge archived from the archive, still waiting to merge (record 0006).
- **No verify card and no verify row.** `crew rail` has four groups; no row, card key, card form, board marker or card session is a verify report's. crew refuses a conductor's card under `verify/<unit>/<stamp>`; a card posted under one before is a card whose row is gone, closed and swept as any. No stage start names a row's card to close, and a write names only a landing row a team lost.
- **A verify stands through its fix round.** A unit that has delivered its verify, and its fix round when one ran, waits to merge, so a forecast reaches it as a settle (`teams.14`); a chore merges once its verify has delivered, its fix round needing none again (`teams.5`).
- **The briefs and docs say so.** The conductor's table, building loop and chore paragraph; verify's check against the change and its *What to do*; the coder's fix round and its merge's archive; the operator's waits; README, the crew skill and the usage headers (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a verify is one round, fixed by a fresh coder with no card; a unit's merge archives its change first and delivers once the bolt holds it archived.
- `rail-cards`: no row, key or card is a verify report's, and `crew card`'s requirements show a landing card where they showed a verify card.
- `crew-rail`: four groups; a verify report is no row.
- `card-sessions`: no session is a verify report's.
- `operator-agent`: a wait it is told of is a review or a landing, never a verify report.
- `chores`: a chore's merge needs its verify once; its report is no row.

## Impact

- `plan.py`: `verified`, `chore_refusal`, `run_check`, `chore_check`, `run_unit_stage`, `deliverable_facts`, `delivered`, `lost_rows`, `op_unit_amend`, `amend_told`, `RAIL`, `rail_rows`, `stray_cards`, `sweep_sessions`, `sweep_judgment`, `card_refusal`, `card_of`, `card_row`, `card_session`, `survey`; `ends_row` and `stage_ended_row` go.
- `gather.py` reads a place's archived change and a branch's archived changes, and no longer reads the reports folders.
- The card hook keeps recording a close under an old verify key and has no verify form; the board, its views and the page draw no verify marker (`code.8`).
- A verify card open when this lands matches no row: the rail names it with its owner, who closes it.
- Four `rail-cards` requirements and one `card-sessions` requirement are also modified by changes still open on main (design: *Specs that other open changes touch*).

## Touches

```
plugin/lib/plan.py
plugin/lib/gather.py
plugin/lib/crew.py
plugin/lib/board.py
plugin/lib/page.html
plugin/hooks/cards
plugin/bin/crew
plugin/roles/conductor.md
plugin/roles/coder.md
plugin/roles/verify.md
plugin/roles/planner.md
plugin/roles/operator.md
plugin/skills/crew/SKILL.md
README.md
tests/py/
tests/contract/test_gather.py
tests/t-briefs.sh
tests/t-card-commands.sh
tests/t-journey-board.sh
tests/t-journey-chores.sh
tests/t-journey-land.sh
tests/t-journey-merge.sh
tests/t-journey-plan.sh
tests/t-journey-review.sh
```
