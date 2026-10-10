# Spec Delta

## MODIFIED Requirements

### Requirement: A fix that carries the bolt onto main becomes its head
A fix SHALL carry the bolt when the bolt's head is not an ancestor of the fix, the fix holds as many commits beyond the kit's main as the bolt does, and, in order, each of the fix's commits is the bolt's commit in the same place replayed: the same message and the same author, its patch the same or changed. `git range-diff` of the two SHALL be printed as the reading and SHALL decide nothing. On `--merge`, crew SHALL then move `bolt/<bolt>` to the fix's head in the bolt's worktree, end the fix's agent, record the move, and say the bolt's old and new heads; no merge or submission SHALL run.

#### Scenario: A fix replays the bolt onto main
- **WHEN** a landing's rebase conflicted, the fix's agent replayed the bolt's three commits onto main resolving one of them, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** `bolt/<bolt>` is at the fix's head, the fix reads as merged, its slot and place are freed as after a merge, and crew's output names the bolt's old head and new head

#### Scenario: A replay whose context main rewrote still carries
- **WHEN** main rewrote every line around what one of the bolt's commits edits, so that `git range-diff` at its defaults leaves that commit's faithful replay unpaired, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** crew moves the bolt to the fix's head, counts that commit among those the resolution changed, and prints range-diff's reading as it stands

#### Scenario: A fix that drops one of the bolt's commits does not carry it
- **WHEN** the fix's branch, on main, holds two of the bolt's three commits and lacks the third
- **THEN** crew does not move the bolt, starts the fix's merge stage, and names the bolt's commit that is not in the fix

#### Scenario: A fix with a commit of its own does not carry it
- **WHEN** the fix's branch, on main, holds the bolt's commits replayed and one commit more
- **THEN** crew does not move the bolt, starts the fix's merge stage, and names the fix's commit that is none of the bolt's

#### Scenario: A fix that rewords one of the bolt's commits does not carry it
- **WHEN** the fix's branch, on main, holds the bolt's commits replayed in order, but one has a different message or a different author from the bolt's commit in its place
- **THEN** crew does not move the bolt, starts the fix's merge stage, and names both that commit of the bolt's and the fix's commit in its place

#### Scenario: The reading is printed whatever the judgment
- **WHEN** the conductor runs `crew fix <team> <name> --merge` on a fix whose branch no longer holds the bolt's head
- **THEN** crew's output holds `git range-diff`'s lines for the bolt's commits beyond main and the fix's, whether crew moves the bolt or merges the fix, and a range-diff that fails is named in git's words without changing the judgment

#### Scenario: A bolt's worktree that is not clean is not moved
- **WHEN** the fix carries the bolt and the bolt's worktree has modified or untracked files git does not ignore, or a rebase or merge in progress
- **THEN** crew moves nothing, starts no merge, names what keeps the worktree from moving, and the refusal is recorded
