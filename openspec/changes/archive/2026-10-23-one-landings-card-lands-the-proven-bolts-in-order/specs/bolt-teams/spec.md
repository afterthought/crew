## MODIFIED Requirements

### Requirement: A bolt lands on main on the user's word
Bolts whose verification is green SHALL be landed by the partition's main-level ops on the user's word, by one procedure: `crew bolt submit <bolt>...` submits each bolt's branch to its kit's main through sluice, in the order given, and closes each with `crew bolt land` as it lands; it deploys nothing, pushes nothing and levels no host. Each SHALL be submitted from a short-lived worktree on its branch at `<kit>/places/land-<bolt>` on its team's host, in the name of whoever asked, removed once its outcome is in. A bolt that does not land SHALL move nothing, and the bolts after it SHALL go on. The command SHALL exit non-zero when any bolt did not land, naming each.

#### Scenario: The bolt lands
- **WHEN** the user sends swb-1's bolt ticked on its kit's landings card and main-level ops runs `crew bolt submit <bolt>`
- **THEN** sluice lands the bolt on GitHub's main as a merge commit, the landing's worktree is gone, `crew bolt land` has closed it, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: Three bolts queued as one chain
- **WHEN** main-level ops runs `crew bolt submit y z w`, the three held by teams on one host
- **THEN** `y` is submitted first, `z` once sluice has queued `y`, and `w` once it has queued `z`, none waiting for the one before to land, so sluice tests them as one chain and lands them in that order

#### Scenario: Bolts on two hosts
- **WHEN** main-level ops runs `crew bolt submit y z`, `y` held by a team on deneb and `z` by one on mac-studio
- **THEN** `z` is submitted only once `y`'s submission has ended, so `z` never lands before `y`

#### Scenario: One refused, the rest go on
- **WHEN** `crew bolt submit y z w` runs and sluice refuses `z` for a conflict with main
- **THEN** `y` and `w` land and are closed, `z` and main are where they were for `z`, the command says `z` did not land in sluice's words and that its team takes main into it by a fix, and it exits non-zero

#### Scenario: Bolts of two kits
- **WHEN** `crew bolt submit y w` names a bolt of crew and a bolt of swancloud
- **THEN** it is refused before anything is submitted, saying it lands one kit's bolts at a time

#### Scenario: The waiting bolt lands while the team builds another
- **WHEN** swc-1 holds `doctor-rows`, proven, and builds `ssh-fix`, and `crew bolt submit doctor-rows` lands it
- **THEN** swc-1 holds `ssh-fix` alone, the command says swc-1 builds `ssh-fix`, and the conductor's and ops's restart is not made due by the landing, since the branch they carry is `bolt/ssh-fix`

#### Scenario: The landing's rebase conflicts
- **WHEN** the bolt and main changed the same lines and `crew bolt submit` runs
- **THEN** the command says the bolt did not land with sluice's words, main and the bolt's branch are where they were, the landing's worktree is gone, and the conductor is to take main into the bolt by a fix

#### Scenario: Main is behind GitHub's
- **WHEN** `crew bolt submit` runs while the kit's main on the team's host lacks a commit GitHub's main has
- **THEN** nothing is refused for it, since sluice forms each landing on GitHub's main and pushes it with a lease

#### Scenario: A landed bolt crew could not close
- **WHEN** sluice lands bolt `y` and `crew bolt land y` then refuses, its plan unreadable
- **THEN** the command says `y` landed and was not closed, naming why and `crew bolt land y` as the act that closes it, and goes on to the next bolt

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt given before bolts were branches, whose worktree has a modified file
- **THEN** the bolt lands and the team no longer holds it, and crew says the worktree is kept with its branch because it has uncommitted changes
