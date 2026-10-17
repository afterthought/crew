## MODIFIED Requirements

### Requirement: Every merge into a bolt or onto main is a submission sluice gates
Every merge into a bolt, every landing on main, and every commit that reaches a kit's main, the user's and the design agent's among them, SHALL be a submission to sluice from a branch cut from `origin/<target>`, landed on GitHub by a leased push as a merge commit only when the checks the kit's policy requires of the target pass with it merged, and otherwise landing nothing. Nothing of crew's SHALL move a bolt's branch or main by git, level a checkout a landing moved under, or run a merge gate or verification of its own. A stage's wait SHALL read a conflict or a blame sluice names to the stage's place from `sluice overview --json` and report it to the conductor in sluice's words, and SHALL go on by refs alone, saying so, when the overview cannot be read.

#### Scenario: A red check refuses a unit's merge
- **WHEN** a unit's place holds a change under which a required check fails, and its merge stage runs `wt submit bolt/<bolt> --no-remove`
- **THEN** the submission fails naming the check, and `bolt/<bolt>` is at the commit it was at before

#### Scenario: A green submission lands
- **WHEN** every required check passes on the bolt with the unit merged
- **THEN** `bolt/<bolt>` on GitHub is a merge commit sluice made, holding the unit's commits

#### Scenario: The design agent's record
- **WHEN** the design agent writes a decision record for a kit
- **THEN** it commits the record on a branch cut from `origin/main` in a worktree of its own and submits it with `wt submit main`, and the kit's main holds it only once sluice lands it

#### Scenario: A landing is gated the same way
- **WHEN** main-level ops runs `crew bolt submit <bolt>` and a required check of main fails on main with the bolt merged
- **THEN** nothing lands, and main is at the commit it was at before

#### Scenario: A conflict named by the overview
- **WHEN** a merge stage's submission is refused for a conflict and the overview's `recent[]` names the stage's place
- **THEN** the conductor's wait reports the conflict with sluice's words before the stage's agent ends

#### Scenario: The overview cannot be read
- **WHEN** the host's sluice has no `overview`
- **THEN** the wait says so once and goes on reading refs
