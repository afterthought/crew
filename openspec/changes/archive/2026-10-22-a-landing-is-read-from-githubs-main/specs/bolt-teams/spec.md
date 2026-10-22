## ADDED Requirements

### Requirement: A landing is read from GitHub's main
`crew bolt submit` SHALL judge whether a bolt landed by main now, never by sluice's exit alone. For a kit with an origin remote, main now is GitHub's `origin/main` after a fetch. For a kit with no origin, it is the kit's own `main`. Before it submits, crew SHALL read main now on the team's host, and SHALL refuse, submitting nothing, when it cannot. After sluice's outcome it SHALL read main now again, after a fresh fetch, together with whether it holds the bolt's tip that was submitted. The bolt has landed when main now moved and holds that tip, whatever sluice exited. crew SHALL then say where main holds it, mark the bolt's branch landed, and send ops on to `crew bolt land`. When sluice's exit was not 0, crew SHALL also name the exit and sluice's last words as what came after its push, sluice's to report apart from the landing. crew SHALL say that main is where it was only when main now did not move. When main now moved but does not hold the bolt, crew SHALL say the bolt did not land and name where main now is. When main now cannot be read after the submission, crew SHALL say it cannot tell whether the bolt landed, naming why and sluice's exit, and SHALL mark nothing and say nothing of where main is.

#### Scenario: sluice fails after its push
- **WHEN** main-level ops runs `crew bolt submit <bolt>`, and sluice pushes the bolt's merge to GitHub's main, then fails releasing a place and exits 3, leaving the host's own `main` where it was
- **THEN** the command succeeds, saying the bolt landed on the kit's main at the commit GitHub's main holds, naming sluice's exit 3 and its last words as what came after the push, sluice's to report apart, and saying "now crew bolt land <bolt>"; and the bolt's branch is marked landed

#### Scenario: sluice lands it and exits 0
- **WHEN** sluice lands the bolt and exits 0, and GitHub's main holds the bolt's merge after a fetch
- **THEN** crew says the bolt landed at that commit and "now crew bolt land <bolt>", naming no exit, and marks the branch landed

#### Scenario: GitHub's main did not move
- **WHEN** sluice exits 1 or 2, or any other exit, and GitHub's main after a fetch is at the commit it held before the submission
- **THEN** the command fails, saying the bolt did not land and main is where it was, and the branch is not marked

#### Scenario: Main moved, but not with the bolt
- **WHEN** sluice exits non-zero and GitHub's main after a fetch has moved but does not hold the bolt's submitted tip
- **THEN** the command fails, saying the bolt did not land and naming the commit main is now at; it does not say main is where it was, and the branch is not marked

#### Scenario: GitHub can't be read after the submission
- **WHEN** the fetch after sluice's outcome fails
- **THEN** the command fails, saying crew cannot tell whether the bolt landed, with the fetch's words and sluice's exit; it says neither that the bolt landed nor that main is where it was, and the branch is not marked

#### Scenario: GitHub can't be read before the submission
- **WHEN** `crew bolt submit` runs and the fetch of the kit's origin on the team's host fails
- **THEN** it is refused with the fetch's words, nothing is submitted, and no landing worktree is made

#### Scenario: A kit with no origin
- **WHEN** a kit with no origin remote is landed and sluice moves its own `main` to a merge holding the bolt
- **THEN** crew reads the kit's own `main` before and after, and says the bolt landed
