## MODIFIED Requirements

### Requirement: A bolt is created, given, dropped and landed through crew
`crew bolt new` SHALL add a bolt with its repo, goal and sources. `crew bolt give <team> [<bolt>]` SHALL set the bolt's team; with no bolt named it takes the first planned bolt in the team's kit. It SHALL then make `bolt/<bolt>` from main, and the bolt's checkout at `<kit>/bolts/<bolt>` on `land/<bolt>`, a branch made from it and tracking it, on the team's host; no worktree SHALL hold `bolt/<bolt>`. `crew bolt order` SHALL move a bolt. `crew bolt drop` SHALL remove a bolt and its units, or with `--requeue` queue them, and SHALL refuse `--requeue` while a unit of the bolt has a worktree, since a queued unit has none. `crew bolt land` SHALL remove a landed bolt and its units. A dropped or landed bolt's worktrees and branches SHALL then go from its team's host.

#### Scenario: A bolt is given
- **WHEN** `crew bolt give swb-1` gives swb-1 the bolt `tenant-environments`
- **THEN** `bolt/tenant-environments` is at main's head, `bolts/tenant-environments` is on `land/tenant-environments` tracking it, and no worktree is on `bolt/tenant-environments`

#### Scenario: A team still holds a bolt
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds a bolt with a unit that has not landed
- **THEN** it is refused, naming that bolt

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

#### Scenario: Dropping a bolt a team holds
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** the bolt and its units are gone from the plan, and the bolt's checkout and both its branches are gone from swb-2's host

#### Scenario: Requeuing a unit that has a worktree
- **WHEN** `crew bolt drop <bolt> --requeue` runs while one of the bolt's units has a worktree
- **THEN** it is refused, naming the unit and its worktree, and the plan is unchanged
