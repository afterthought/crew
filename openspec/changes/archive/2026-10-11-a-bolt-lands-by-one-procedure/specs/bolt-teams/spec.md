## MODIFIED Requirements

### Requirement: A bolt lands on main on the user's word
A proven bolt SHALL be landed by the partition's main-level ops, on the user's approval of its landing card, by one
procedure: it merges `bolt/<bolt>` into main through the kit's merge hooks, pushes main without force, and then runs
`crew bolt land`; it deploys nothing. The bolt's worktree SHALL then be removed, unless it has uncommitted changes, and
the team SHALL hold no bolt. A worktree that is kept SHALL NOT stop the landing. When the landing's rebase conflicts,
main-level ops SHALL abort it so that nothing lands, and tell the bolt's conductor the commit that conflicted and the
files, for the team to carry the bolt onto main by a fix.

#### Scenario: The bolt lands
- **WHEN** the user approves swb-1's landing card
- **THEN** main holds every unit's change, GitHub's main holds it too, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt whose worktree has a modified file
- **THEN** the bolt lands and the team holds no bolt, and crew says the worktree is kept with its branch because it has uncommitted changes

#### Scenario: The landing's rebase conflicts
- **WHEN** main-level ops merges a bolt into main and the rebase stops on a conflict
- **THEN** the rebase is aborted, main and the bolt's branch are where they were, and the conductor is told the conflicting commit and files and starts a fix that carries the bolt onto main
