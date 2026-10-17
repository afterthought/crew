## MODIFIED Requirements

### Requirement: A bolt is created, given, dropped and landed through crew
`crew bolt new` SHALL add a bolt with its repo, goal and sources. `crew bolt give <team> [<bolt>]` SHALL set the bolt's team; with no bolt named it takes the first planned bolt in the team's kit. It SHALL then have sluice make `bolt/<bolt>` on GitHub from `origin/main`, `sluice branch create bolt/<bolt> --from origin/main` on the team's host, and no worktree. It SHALL be refused, with the plan unchanged and no branch made, naming the file, when the kit's `.config/sluice.toml` at `origin/main` names no checks or no `remote` for its bolt branches, and naming the version it needs when the host's sluice lacks `branch create`. `crew bolt order` SHALL move a bolt. `crew bolt drop` SHALL remove a bolt and its units, or with `--requeue` queue them, and SHALL refuse `--requeue` while a unit of the bolt has a worktree, since a queued unit has none. `crew bolt submit` SHALL submit a held bolt's branch to its kit's main through sluice, and `crew bolt land` SHALL remove a landed bolt and its units and have sluice delete its branch, `sluice branch delete bolt/<bolt>`, naming a refusal. A dropped or landed bolt's local branch and worktrees SHALL then go from its team's host. A bolt crew made before its kit's bolts were on GitHub SHALL be put there at its tip by the first read of its team after, which says so.

#### Scenario: A team still holds a bolt
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds a bolt with a unit that has not landed
- **THEN** it is refused, naming that bolt

#### Scenario: A kit with no bolt policy
- **WHEN** `crew bolt give swb-1` runs for a kit whose `origin/main` holds no `.config/sluice.toml`, or one with no `[branches."bolt/*"]` table naming its `required` checks
- **THEN** it is refused, naming the file and what it lacks, the plan is unchanged, and no `bolt/` branch is made

#### Scenario: A kit whose bolts have no remote
- **WHEN** `crew bolt give swb-1` runs for a kit whose bolt policy names checks but no `remote`
- **THEN** it is refused, naming the file and the key, the plan is unchanged, and no branch is made anywhere

#### Scenario: A host whose sluice cannot make a branch
- **WHEN** `crew bolt give swb-1` runs on a host whose sluice is older than the one with `branch create`
- **THEN** it is refused, naming the version crew needs and the one the host has, and the plan is unchanged

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

#### Scenario: A delete sluice refuses
- **WHEN** `crew bolt land` runs and sluice refuses to delete `bolt/<bolt>` because a submission is still queued on it
- **THEN** the bolt leaves the plan, the branch stays on GitHub, and crew names it with sluice's words

#### Scenario: Dropping a bolt a team holds
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** the bolt and its units are gone from the plan, and the bolt's local branch is gone from swb-2's host

#### Scenario: Requeuing a unit that has a worktree
- **WHEN** `crew bolt drop <bolt> --requeue` runs while one of the bolt's units has a worktree
- **THEN** it is refused, naming the unit and its worktree, and the plan is unchanged
