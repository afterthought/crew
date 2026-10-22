## MODIFIED Requirements

### Requirement: A bolt is created, given, dropped and landed through crew
`crew bolt new` SHALL add a bolt with its repo, goal and sources. `crew bolt give <team> [<bolt>]` SHALL set the bolt's team; with no bolt named it takes the first planned bolt in the team's kit. It SHALL then make `bolt/<bolt>` from the kit's main as it stands on the team's host, and no worktree. It SHALL be refused, with the plan unchanged and no branch made, while the team holds two bolts, and while a bolt it holds is not proven: it holds no unit or chore yet, a unit or chore of it has not merged, or sluice's verdict at its head is not green, naming the bolt and what holds it; a fix in flight on a proven bolt SHALL refuse nothing. What crew cannot read of a held bolt SHALL refuse the give, naming what could not be read. It SHALL be refused, with the plan unchanged and no branch made, naming the file, when the kit's `.config/sluice.toml` on main names no checks for its bolt branches. `crew bolt order` SHALL move a bolt. `crew bolt drop` SHALL remove a bolt and its units, or with `--requeue` queue them, and SHALL refuse `--requeue` while a unit of the bolt has a worktree, since a queued unit has none. `crew bolt submit` SHALL submit a held bolt's branch to its kit's main through sluice, and `crew bolt land` SHALL remove a landed bolt and its units. A dropped or landed bolt's branch and worktrees SHALL then go from its team's host.

#### Scenario: A team still holds a bolt
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds a bolt with a unit that has not merged
- **THEN** it is refused, naming that bolt and that unit with its stage

#### Scenario: A team's bolt is merged but not yet green
- **WHEN** `crew bolt give swb-1` runs while every unit of swb-1's bolt has merged and its head is no landing of sluice's
- **THEN** it is refused, naming the bolt and what its verification is now

#### Scenario: A team's bolt is proven
- **WHEN** `crew bolt give swb-1` runs while every unit of swb-1's bolt has merged, sluice is green at its head, and a fix of it is in flight
- **THEN** swb-1 is given the next planned bolt and holds both

#### Scenario: A team holding two bolts
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds two bolts, both proven
- **THEN** it is refused, naming the bolt waiting to land longest, whose landing frees the team

#### Scenario: A kit with no bolt policy
- **WHEN** `crew bolt give swb-1` runs for a kit whose main holds no `.config/sluice.toml`, or one with no `[branches."bolt/*"]` table naming its `required` checks
- **THEN** it is refused, naming the file and what it lacks, the plan is unchanged, and no `bolt/` branch is made

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

#### Scenario: Dropping a bolt a team holds
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** the bolt and its units are gone from the plan, and the bolt's branch is gone from swb-2's host

#### Scenario: Requeuing a unit that has a worktree
- **WHEN** `crew bolt drop <bolt> --requeue` runs while one of the bolt's units has a worktree
- **THEN** it is refused, naming the unit and its worktree, and the plan is unchanged
