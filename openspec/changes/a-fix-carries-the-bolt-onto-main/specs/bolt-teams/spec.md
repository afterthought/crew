# Spec Delta

## MODIFIED Requirements

### Requirement: Fixes during a bolt are built beside its units
`crew fix <team> <name> "<what is wrong>"` SHALL make `fix/<bolt>/<name>` from the team's bolt at `<kit>/places/fix-<bolt>--<name>`. It SHALL start a fresh code agent there in a free slot with the words given. `crew fix <team> <name> --merge` SHALL start its merge stage, and the fix SHALL merge into the bolt like a unit, unless the fix carries the bolt onto main, when crew SHALL make the fix's head the bolt's head instead. A fix SHALL have no OpenSpec change and no plan record.

#### Scenario: A red suite on the bolt
- **WHEN** the bolt's verification is red after a merge
- **THEN** the conductor starts a fix on the bolt, before any other unit's code

#### Scenario: A fix that adds commits merges
- **WHEN** a fix's branch holds the bolt's commits and a commit of its own beyond them, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** crew starts the fix's merge stage, as for a unit

### Requirement: A bolt lands on main on the user's word
A proven bolt SHALL be landed by the partition's main-level ops, which merges `bolt/<bolt>` into main through the kit's merge hooks, deploys main, and then runs `crew bolt land`. The bolt's worktree SHALL then be removed, and the team SHALL hold no bolt. When the landing's rebase conflicts, main-level ops SHALL abort it so that nothing lands, and tell the bolt's conductor the commit that conflicted and the files, for the team to carry the bolt onto main by a fix.

#### Scenario: The bolt lands
- **WHEN** the user says swb-1's bolt may land
- **THEN** main holds every unit's change, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: The landing's rebase conflicts
- **WHEN** main-level ops merges a bolt into main and the rebase stops on a conflict
- **THEN** the rebase is aborted, main and the bolt's branch are where they were, and the conductor is told the conflicting commit and files and starts a fix that carries the bolt onto main

## ADDED Requirements

### Requirement: A fix that carries the bolt onto main becomes its head
A fix SHALL carry the bolt when the bolt's head is not an ancestor of the fix, the fix's commits beyond the kit's main are each paired by `git range-diff` with one of the bolt's commits beyond main, in the same order, equal or changed, and neither side holds a commit left unpaired. On `--merge`, crew SHALL then move `bolt/<bolt>` to the fix's head in the bolt's worktree, end the fix's agent, record the move, and say the bolt's old and new heads; no merge or submission SHALL run.

#### Scenario: A fix replays the bolt onto main
- **WHEN** a landing's rebase conflicted, the fix's agent replayed the bolt's three commits onto main resolving one of them, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** `bolt/<bolt>` is at the fix's head, the fix reads as merged, its slot and place are freed as after a merge, and crew's output names the bolt's old head and new head

#### Scenario: A fix that drops one of the bolt's commits does not carry it
- **WHEN** the fix's branch, on main, pairs two of the bolt's three commits and lacks the third
- **THEN** crew does not move the bolt, starts the fix's merge stage, and says which of the bolt's commits found no pair

#### Scenario: A bolt's worktree that is not clean is not moved
- **WHEN** the fix carries the bolt and the bolt's worktree has modified or untracked files git does not ignore, or a rebase or merge in progress
- **THEN** crew moves nothing, starts no merge, names what keeps the worktree from moving, and the refusal is recorded

### Requirement: A carried bolt is checked and proven again
After crew moves a bolt to a fix that carries it, crew SHALL run the kit's post-merge hooks in the bolt's worktree with the bolt as the target, as a merge into the bolt would, and SHALL say that the bolt must be proven again before it lands. The conductor SHALL ask ops for a new proof and post the bolt's landing card only once that proof is clean.

#### Scenario: The bolt's checks run on the new head
- **WHEN** crew has moved `bolt/<bolt>` to the fix's head in a kit whose post-merge hook verifies the bolt
- **THEN** that hook runs on the new head, and the bolt's verification reads that head

#### Scenario: The kit refuses the checks
- **WHEN** the kit's post-merge hooks are not approved on the host
- **THEN** the bolt is still moved, and crew says the checks did not start, with worktrunk's own words, so ops can run the bolt's verification again

#### Scenario: A proof before the move does not land the bolt
- **WHEN** a bolt that ops had proven is carried onto main by a fix
- **THEN** the conductor asks ops to prove it again, and the landing card is posted only after that proof is clean
