## MODIFIED Requirements

### Requirement: The bolt is forecast against main on the conductor's waits
Each time the conductor waits on a stage through crew, crew SHALL forecast each bolt the team holds against its kit's main and everything queued there, by `sluice submit main --check --head bolt/<bolt> --json` in the kit's main checkout, moving no branch, and the wait SHALL say each forecast once for the same bolt head, revision of main and submissions queued on main it meets, naming the bolt's head the forecast is of, recording it as a `forecast` on the bolt. A forecast is the bolt's at that head alone: as the wait answers, crew SHALL read where each bolt it said a forecast of stands, where the bolt lives after a fetch, and the wait SHALL say, before its answer, of each bolt that moved from the head forecast while it waited, that the forecast is of that head and not of the bolt now, that nothing is to be taken in for it, and that the next wait forecasts the bolt where it stands; and of each bolt whose head crew can't read then, that it can't tell whether the bolt still stands at the head forecast, and why. For a bolt the user left on its kit's landings card or stopped in their words to main-level ops, the wait SHALL say a conflict with what main has landed once as one to take nothing in for while it is left, and SHALL give no take-main fix; once the user ticks it, the wait SHALL give the fix for the same heads as for any bolt.

#### Scenario: Main landed a change to the bolt's lines
- **WHEN** main has landed a change to `shared.txt` that the bolt's own work also changed, and the conductor waits on a unit's stage
- **THEN** the wait says the bolt, at its head, is forecast to conflict with main on `shared.txt` and gives `crew fix <team> take-main-<main's short sha> "Take main into the bolt: it is forecast to conflict on shared.txt"`, and the forecast is recorded with `Reached: wait`

#### Scenario: Told once
- **WHEN** the conductor waits again and neither the bolt nor main has moved
- **THEN** the wait says nothing of the forecast

#### Scenario: A submission queued on main
- **WHEN** the bolt would conflict on `shared.txt` with `#7` from `design/x`, queued on main ahead of it
- **THEN** the wait says so, naming the bolt's head, and that nothing is to be taken in for it, since it may yet fail and leave the queue

#### Scenario: The bolt moves while the wait waits
- **WHEN** a conductor's wait on another unit's construct forecasts the bolt at `75016a0` to conflict with main on `frontegg.test.ts` as it begins, while a take-main fix's merge into the bolt is under test, and that merge moves the bolt to `2722779`, which main-level ops then submits to main, before the wait answers
- **THEN** the wait's answer says, before its own line, that the bolt moved from `75016a0` to `2722779` while it waited, that the forecast it said as it began is of `75016a0` and not of the bolt now, and that nothing is to be taken in for it; and the next wait forecasts the bolt at `2722779`

#### Scenario: The bolt stands where it was forecast
- **WHEN** the bolt is still at the head forecast when the wait answers
- **THEN** the answer says nothing more of the forecast, which stands as said

#### Scenario: Where the bolt stands can't be read
- **WHEN** crew can't read the bolt's head as the wait answers, its kit's fetch failing
- **THEN** the answer says it can't tell whether the bolt still stands at the head forecast, and why, and to read the bolt's head before taking anything in for that forecast

#### Scenario: A sluice that can't forecast a branch
- **WHEN** the host's sluice refuses `--head`
- **THEN** the wait says once for the bolt's head that it can't forecast the bolt against main, and why, and goes on

#### Scenario: A bolt the user left
- **WHEN** swc-3 holds `builds-reach-the-phone`, which the user cleared on their send of `land/swancloud`, and main has landed a change to `packages/swancloud-doctor/default.nix` that the bolt also changed
- **THEN** the wait says once that the bolt, at its head, which the user left, is forecast to conflict with main on `packages/swancloud-doctor/default.nix`, that nothing is to be taken in while it is left, and that crew tells the take-main fix once they tick it; it gives no `crew fix` command, and the forecast is recorded with `Reached: left`

#### Scenario: Ticked at the same heads
- **WHEN** the user ticks `builds-reach-the-phone` on a later send, neither it nor main having moved, and the conductor waits again
- **THEN** the wait gives the take-main fix for it, unless the card's raise already told it at those heads
