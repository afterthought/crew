## MODIFIED Requirements

### Requirement: The bolt is forecast against main on the conductor's waits
Each time the conductor waits on a stage through crew, crew SHALL forecast each bolt the team holds against its kit's main and everything queued there, by `sluice submit main --check --head bolt/<bolt> --json` in the kit's main checkout, moving no branch, and the wait SHALL say each forecast once for the same bolt head, revision of main and submissions queued on main it meets, recording it as a `forecast` on the bolt. For a bolt the user left on its kit's landings card or stopped in their words to main-level ops, the wait SHALL say a conflict with what main has landed once as one to take nothing in for while it is left, and SHALL give no take-main fix; once the user ticks it, the wait SHALL give the fix for the same heads as for any bolt.

#### Scenario: Main landed a change to the bolt's lines
- **WHEN** main has landed a change to `shared.txt` that the bolt's own work also changed, and the conductor waits on a unit's stage
- **THEN** the wait says the bolt is forecast to conflict with main on `shared.txt` and gives `crew fix <team> take-main-<main's short sha> "Take main into the bolt: it is forecast to conflict on shared.txt"`, and the forecast is recorded with `Reached: wait`

#### Scenario: Told once
- **WHEN** the conductor waits again and neither the bolt nor main has moved
- **THEN** the wait says nothing of the forecast

#### Scenario: A submission queued on main
- **WHEN** the bolt would conflict on `shared.txt` with `#7` from `design/x`, queued on main ahead of it
- **THEN** the wait says so and that nothing is to be taken in for it, since it may yet fail and leave the queue

#### Scenario: A sluice that can't forecast a branch
- **WHEN** the host's sluice refuses `--head`
- **THEN** the wait says once for the bolt's head that it can't forecast the bolt against main, and why, and goes on

#### Scenario: A bolt the user left
- **WHEN** swc-3 holds `builds-reach-the-phone`, which the user cleared on their send of `land/swancloud`, and main has landed a change to `packages/swancloud-doctor/default.nix` that the bolt also changed
- **THEN** the wait says once that the bolt, which the user left, is forecast to conflict with main on `packages/swancloud-doctor/default.nix`, that nothing is to be taken in while it is left, and that crew tells the take-main fix once they tick it; it gives no `crew fix` command, and the forecast is recorded with `Reached: left`

#### Scenario: Ticked at the same heads
- **WHEN** the user ticks `builds-reach-the-phone` on a later send, neither it nor main having moved, and the conductor waits again
- **THEN** the wait gives the take-main fix for it, unless the card's raise already told it at those heads

### Requirement: A waiting bolt's conflict with main tells its conductor the take-main fix
When the forecast of a bolt's row on its kit's landings card finds a conflict with what main holds, crew SHALL tell the bolt's conductor, through `crew tell`, the take-main fix to start now, in the words a conductor's wait gives for a conflict with main, and SHALL record the forecast on the bolt with the bolt's head, main's revision and the files. It SHALL be told once for the same bolt head and revision of main, whichever forecast recorded it first. A bolt the user left SHALL NOT be told: its forecast SHALL be recorded once as one found while it is left, which holds no tell back once the user ticks it.

#### Scenario: Main moves under a waiting bolt
- **WHEN** swc-1 holds `y`, proven and a row of `land/crew`, and main lands a change to `README.md` that `y` also changes, moving GitHub's main to `e4f5a6b`
- **THEN** swc-1-conductor is told `y` is forecast to conflict with main on `README.md`, with `crew fix swc-1 take-main-e4f5a6b "Take main into the bolt: it is forecast to conflict on README.md"`, and a `forecast` on `bolt/y` is recorded with `y`'s head, `main@e4f5a6b` and `README.md`

#### Scenario: Told once
- **WHEN** the card is raised again and neither `y` nor main has moved
- **THEN** swc-1-conductor is told nothing more, and `y` is still held taking main first

#### Scenario: The wait said it first
- **WHEN** a conductor's wait recorded `y`'s forecast against main at the same head and revision of main
- **THEN** the card's raise tells swc-1-conductor nothing of it

#### Scenario: The team holds two bolts
- **WHEN** swc-1 holds `y`, waiting to land, and `x`, which it builds
- **THEN** the fix's command names `--bolt y`

#### Scenario: The conductor cannot be told
- **WHEN** swc-1-conductor's pane does not take the tell
- **THEN** nothing is recorded for the forecast, `y` is still held taking main first, and the next raise tells it again

#### Scenario: A left bolt
- **WHEN** `z` is left on `land/crew` and main lands a change to `README.md` that `z` also changes
- **THEN** swc-1-conductor is told nothing, and a `forecast` on `bolt/z` is recorded with `Reached: left`

#### Scenario: A left bolt ticked
- **WHEN** the user then ticks `z`, neither `z` nor main having moved
- **THEN** swc-1-conductor is told the take-main fix for `z`, and a `forecast` on `bolt/z` is recorded with `Reached: told`
