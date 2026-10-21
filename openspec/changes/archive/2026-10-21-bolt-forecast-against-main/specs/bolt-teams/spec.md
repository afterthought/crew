## ADDED Requirements

### Requirement: The bolt is forecast against main on the conductor's waits
Each time the conductor waits on a stage through crew, crew SHALL forecast each bolt the team holds against its kit's main and everything queued there, by `sluice submit main --check --head bolt/<bolt> --json` in the kit's main checkout, moving no branch, and the wait SHALL say each forecast once for the same bolt head, revision of main and submissions queued on main it meets, recording it as a `forecast` on the bolt.

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
