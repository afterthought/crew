# A forecast reads what a unit already took

## Why

On the Willdan box (wldn, crew main), atl-1's conductor forecast a conflict between two unmerged units of atlas-kit's bolt `atlass-gateway-is-the-installs`. The later unit already held the earlier one's work, so the forecast started a settle stage that had nothing to settle. Signal: `2026-11-07-atl-1-conductor-d88c52fa/01` on `wldn/main` of WilldanGroup/crew-state.

The later unit, `atlass-gateway-is-the-installs-and-fronts-its-broker-and-catalog`, comes after `atlass-warehouse-roles-trust-the-installs-broker`. Its construct's place took the warehouse unit's head, 9bb35a9, at 22:02Z on 2026-11-06, and its start's `Took` records that head. The warehouse unit then moved on: it was constructed again three times and coded to 53bd5bb. Its new heads reached the gateway unit, and the gateway unit's settle at 01:58Z merged 53bd5bb into its place. At 02:04Z the wait still forecast the gateway unit at c8d4b71 against the warehouse unit at 53bd5bb, on `.moon/workspace.yml`, `cloudformation/CLAUDE.md`, `cloudformation/atlas-lakehouse.yaml` and `scripts/check-switchboard-manifest.test.mjs`.

`forecasts_due` compared a unit with one it comes after from the head its place took, whenever `Took` named one (`plan.13`, `teams.12`). It never asked git whether the unit holds anything newer of the other's. The warehouse unit changed those four files only after 9bb35a9, so for them that base is the bolt, which is what the conductor found: `git merge-tree --merge-base=<bolt>` gives exactly those four paths. The gateway unit holds 53bd5bb and has its own edits beside the warehouse unit's lines, so a merge from a base that predates them sees both sides change the same lines. Their real merge is clean, since the gateway unit holds the warehouse unit's head. It cost atl-1 one needless settle.

The user ruled that the box's crew faults are fixed on crew main: "Yes: fix them on crew main, for the box".

## What Changes

- **A forecast reads from git what the later unit holds of the earlier one.** A later unit whose head holds the earlier unit's head, by a merge in its place, a settle or anything else, is forecast nothing against it, so no settle starts.
- **Otherwise it is forecast from the newest of the earlier unit's work it holds.** That is their merge base, which git takes at the head the place took or a newer one merged since. The head the place took is the base only where the earlier unit's line no longer holds it, because its rebase or settle rewrote that work, and the two share nothing newer of the earlier unit's. This is `plan.13`'s case: the later unit carries that rewritten work as it took it.
- **The head the place took is a base whatever `After` says now**, once git says the later unit still holds it. An order lifted since the take no longer makes that work a conflict of the later unit's.
- **What the later unit holds is read from git** (`merge-base --is-ancestor`, `merge-base --all`), never from a merge commit's words.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "A conflict is forecast on the conductor's waits". A unit is compared with one ahead of it only on what each adds beyond the newest of that one's work it holds, read from git, and is forecast nothing when it holds that one's head.

## Impact

- `plugin/lib/plan.py`: `forecasts_due` takes git's answers about what a unit holds. `forecast_base` decides each pair's base from them. `git_holds` and `shared_beyond` read them in the kit's main checkout. `reach` wires them in.
- Tests: `tests/py/test_forecast.py` (logic) covers each base and the box's case. `tests/contract/test_git.py` covers the box's case, a unit ahead that moved on, and a newer head merged after the one taken, on real git.
- README's paragraph on forecasts says what a forecast is read from. The rule pages are unchanged: `plan.13` and `teams.12` hold as written, and their details are the design agent's (`docs.7`).
- Nothing the board or the mod draws changes (`code.8` is not reached). Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
tests/py/test_forecast.py
tests/contract/test_git.py
README.md
openspec/specs/bolt-teams/spec.md
openspec/changes/archive/2026-11-06-a-forecast-reads-what-a-unit-already-took/**
```
