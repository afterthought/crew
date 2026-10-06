# flywheel-state Specification

## Purpose
Keeps each flywheel's own records (its plan, its moves, its run record, and what later capabilities add) in a state repository apart from the design, on a branch of its own, written only through crew, so that several flywheels can share one repository without meeting.

## Requirements

### Requirement: A flywheel's state is one branch of its state repository
Each partition SHALL name one state repository in the teams file, as `state`. The partition's flywheel SHALL keep its state as files on the branch `<label>/main` of that repository. The branch SHALL hold no other flywheel's files and SHALL share no history with another flywheel's branch.

#### Scenario: Willdan's flywheel
- **WHEN** the `wldn` partition names `WilldanGroup/crew-state` as its state repository
- **THEN** its plan, moves and run record are files on the branch `wldn/main` of that repository

#### Scenario: Two flywheels of one organisation
- **WHEN** `madswan` and `swancloud` both name `afterthought/crew-state`
- **THEN** each has its own branch, `madswan/main` and `swancloud/main`, and neither branch holds a commit of the other's

### Requirement: The state is written only through crew, one commit a write
Every write to a flywheel's branch SHALL be made by a crew command. It SHALL fetch the branch over https into crew's own bare cache, apply itself to the tip, check each file it changed, commit without touching any working tree, and push without force. A rejected push SHALL have the write applied again to the new tip, up to five times. A write that changes several files SHALL be one commit.

#### Scenario: Two hosts write at once
- **WHEN** a write from the box and a write from mac-studio reach the same flywheel's branch together
- **THEN** both land, one after the other, and nothing is merged

#### Scenario: A write of two files
- **WHEN** a command changes the plan and appends a move
- **THEN** one commit holds both, and no reader sees the plan change without the move

#### Scenario: A file that fails its check
- **WHEN** a write would leave a recutils file that fails `recfix --check` or crew's rules
- **THEN** nothing is pushed, and the command says which file and why

### Requirement: A commit names its run-record entry
Each commit crew makes on a flywheel's branch SHALL carry, in its message, the id of the run-record entry that describes it, as a `Crew-Entry:` trailer, and that entry SHALL name the commit.

#### Scenario: From a commit to its entry
- **WHEN** a commit on `wldn/main` is read
- **THEN** its `Crew-Entry` id is the `Id` of one run-record entry, whose `Commit` is that commit

### Requirement: Flywheels in one repository never meet
crew SHALL fetch and push only the branch of the flywheel a command acts for. A write to one flywheel SHALL never be refused, delayed or replayed because another flywheel wrote.

#### Scenario: Two flywheels write at the same moment
- **WHEN** `madswan` and `swancloud` each write their plan at the same moment
- **THEN** each write's first push succeeds

#### Scenario: Reading one flywheel
- **WHEN** a command reads wldn's plan
- **THEN** crew fetches `wldn/main` and no other branch

### Requirement: A flywheel's branch is created, and adopts what it had
`crew state init <label>` SHALL create `<label>/main` in the partition's state repository with an empty plan and an empty moves file. Where a blueprints repo of the partition holds `plan/<label>`, the branch SHALL start from that plan's history, and the moves in the first blueprints repo's `signals/moves.rec` SHALL be copied with the commit they were read at. Run again, it SHALL change nothing.

#### Scenario: Willdan's plan is adopted
- **WHEN** `crew state init wldn` runs while willdan-blueprints holds `plan/wldn` and two moves
- **THEN** `wldn/main` holds the same bolts and units, its history reaches back to the plan's first commit, and `moves.rec` holds both moves

#### Scenario: A partition with two plans
- **WHEN** `crew state init madswan` runs while afterthought/blueprints and agentplot/blueprints each hold `plan/madswan`
- **THEN** `madswan/main` holds one plan with the bolts and units of both, the second plan's records added in one commit that names where they came from

#### Scenario: Two plans share a name
- **WHEN** the two plans being joined both hold a bolt or a unit of the same name
- **THEN** init is refused, naming it, and nothing is written

#### Scenario: Run twice
- **WHEN** `crew state init wldn` runs again
- **THEN** nothing is written, and it says the branch exists and at which commit

### Requirement: A flywheel's state is plain files anyone with access can read
A clone of a flywheel's branch SHALL be recutils files that `recsel` and `recfix` read with no crew command, and each commit's subject SHALL say what the write did and who asked.

#### Scenario: Reading with recutils
- **WHEN** the user clones the branch `wldn/main` and runs `recsel -t Unit plan.rec`
- **THEN** the plan's units are printed
