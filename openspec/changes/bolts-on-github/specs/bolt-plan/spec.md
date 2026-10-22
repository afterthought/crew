## MODIFIED Requirements

### Requirement: A bolt is created, given, dropped and landed through crew
`crew bolt new` SHALL add a bolt with its repo, goal and sources. `crew bolt give <team> [<bolt>]` SHALL set the bolt's team; with no bolt named it takes the first planned bolt in the team's kit. It SHALL have sluice make `bolt/<bolt>` on GitHub from main, `sluice branch create bolt/<bolt> --from main` on the team's host, and no worktree, before the plan is written. It SHALL be refused, with the plan unchanged and no branch made, naming the file, when the kit's `.config/sluice.toml` at `origin/main` names no checks or no `remote` for its bolt branches; naming the version it needs and the one the host has when the host's sluice lacks `branch create` or its version cannot be read; and in sluice's words when sluice refuses the create. `crew bolt order` SHALL move a bolt. `crew bolt drop` SHALL remove a bolt and its units, or with `--requeue` queue them, and SHALL refuse `--requeue` while a unit of the bolt has a worktree, since a queued unit has none. `crew bolt submit` SHALL submit a held bolt's branch to its kit's main through sluice, and `crew bolt land` SHALL remove a landed bolt and its units and have sluice delete its branch, `sluice branch delete bolt/<bolt> --into main`, naming a refusal in sluice's words. A dropped or landed bolt's local branch and worktrees SHALL then go from its team's host. A bolt whose branch crew made on its host before gives went through sluice SHALL stay local until it lands: crew SHALL run no create for it, its places SHALL be cut from the local branch, each read of its team SHALL say once that it is local until it lands, and its land SHALL have sluice delete it wherever its tip's policy routes it, on GitHub once its landing's pull request put it there.

#### Scenario: A team still holds a bolt
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds a bolt with a unit that has not landed
- **THEN** it is refused, naming that bolt

#### Scenario: A kit with no bolt policy
- **WHEN** `crew bolt give swb-1` runs for a kit whose `origin/main` holds no `.config/sluice.toml`, or one with no `[branches."bolt/*"]` table naming its `required` checks
- **THEN** it is refused, naming the file and what it lacks, the plan is unchanged, and no `bolt/` branch is made

#### Scenario: A kit whose bolts have no remote
- **WHEN** `crew bolt give swb-1` runs for a kit whose bolt policy at `origin/main` names checks but no `remote`
- **THEN** it is refused, naming the file and the key, the plan is unchanged, and no branch is made anywhere

#### Scenario: A host whose sluice cannot make a branch
- **WHEN** `crew bolt give swb-1` runs on a host whose sluice is older than 0.20.0, or whose `sluice --version` prints nothing crew can read
- **THEN** it is refused, naming 0.20.0 and what the host's sluice said, and the plan is unchanged

#### Scenario: Sluice refuses the create
- **WHEN** `crew bolt give swb-1` runs and sluice refuses to make `bolt/<bolt>`, as when it is already there
- **THEN** the give is refused with sluice's words, and the plan is unchanged

#### Scenario: A bolt is made on GitHub
- **WHEN** `crew bolt give swb-1` gives swb-1 the bolt `b` for a kit whose policy names `origin` for its bolts
- **THEN** `bolt/b` is on GitHub at main's commit, made by sluice, the plan gives `b` to swb-1, and crew says where the branch was made and at which commit

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

#### Scenario: The bolt's branch is deleted at its land
- **WHEN** `crew bolt land` runs for a landed bolt whose branch is on GitHub
- **THEN** the bolt leaves the plan, sluice deletes `bolt/<bolt>` from GitHub, and the branch is gone from the team's host

#### Scenario: A delete sluice refuses
- **WHEN** `crew bolt land` runs and sluice refuses to delete `bolt/<bolt>` because a submission is still queued on it
- **THEN** the bolt leaves the plan, the branch stays on GitHub, and crew names it with sluice's words

#### Scenario: A bolt made before stays local
- **WHEN** a team's read finds that the team holds a bolt whose branch is on its host only, its tip's policy naming no remote for it, while the policy at the kit's main names `origin` for its bolts
- **THEN** crew says once that the bolt is local until it lands, runs no create, and its places are cut from the local branch

#### Scenario: A bolt made before lands
- **WHEN** `crew bolt land` runs for a landed bolt made before, whose last merge brought it a policy naming `origin` and whose landing's pull request sluice pushed to GitHub
- **THEN** the bolt leaves the plan, sluice deletes `bolt/<bolt>` from GitHub, and the branch is gone from the team's host

#### Scenario: Dropping a bolt a team holds
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** the bolt and its units are gone from the plan, and the bolt's local branch is gone from swb-2's host

#### Scenario: Requeuing a unit that has a worktree
- **WHEN** `crew bolt drop <bolt> --requeue` runs while one of the bolt's units has a worktree
- **THEN** it is refused, naming the unit and its worktree, and the plan is unchanged
