# Spec Delta

## ADDED Requirements

### Requirement: Every unit of a bolt is constructed at once
Once a team holds a bolt, the conductor SHALL run construct for every unit of the bolt that has no change yet, as slots allow, in the file's order. Construct SHALL NOT wait on a unit's `After`, on the user, or on another unit's Touches.

#### Scenario: A bolt is given
- **WHEN** a team with four slots is given a bolt of three units, one of them with `After`
- **THEN** all three constructs run at once

#### Scenario: More units than slots
- **WHEN** a team with two slots holds a bolt of five units
- **THEN** two constructs run, and the next unit in the file's order is constructed as each slot frees

### Requirement: A dependent builds on its After units' work as it stands
Before a unit's code starts, crew SHALL bring into `unit/<unit>` the head of each of its After units that has not merged, as that head stands. When an After unit merges into the bolt, crew SHALL rebase the dependent's place onto the bolt, but only while the dependent's agent is not working and its place has no uncommitted changes. A rebase that conflicts SHALL be undone and handed to the dependent's agent to resolve, as a conflict is.

#### Scenario: Code on a constructed dependency
- **WHEN** B has `After: A`, A's construct has committed and A is in code, and B's code starts
- **THEN** B's place holds A's commits as they stood when B's code started

#### Scenario: The dependency merges
- **WHEN** A merges into the bolt while B's code agent is idle
- **THEN** B's place is rebased onto the bolt, and holds no commit of A's that the bolt already holds

#### Scenario: The dependent is working
- **WHEN** A merges into the bolt while B's code agent is working
- **THEN** B's place is not touched until the agent is idle

### Requirement: Touches is a list crew reads
A unit's `proposal.md` SHALL end with a `## Touches` heading holding one fenced block of repository paths or globs, one to a line. crew SHALL read it before the unit's code starts, and SHALL refuse code when the heading or the block is missing or empty.

#### Scenario: No Touches
- **WHEN** a unit's proposal has no `## Touches` block
- **THEN** its code is refused, saying the change must declare what it touches

### Requirement: Overlapping Touches are told before code
When a unit's code is about to start and its Touches overlap those of an unmerged unit ahead of it in the bolt, crew SHALL tell the later unit's agent which entries overlap and where the other unit's change is. Overlap SHALL NOT hold the unit's code.

#### Scenario: Two units declare the same file
- **WHEN** units A and B, A first in the file, both list `plugin/lib/plan.py`, and B's code is about to start
- **THEN** B's code starts, and B's agent is told that it overlaps A on `plugin/lib/plan.py`, with the path of A's change

### Requirement: Verify names what a unit changed and did not declare
At verify, every path `git diff --name-only bolt/<bolt>...unit/<unit>` names that no entry of the unit's Touches matches SHALL be a finding of the verify report.

#### Scenario: A path not declared
- **WHEN** a unit changed `README.md` against its bolt and its Touches do not match it
- **THEN** the verify report names `README.md` as changed and not declared

### Requirement: A conflict is forecast on the conductor's waits
Each time the conductor waits on a stage or a proof through crew, crew SHALL dry-run, with `git merge-tree`, the merge of each unmerged unit's head with `bolt/<bolt>` and with the head of each unmerged unit ahead of it in the file's order, writing no ref.

#### Scenario: The dry run moves nothing
- **WHEN** the conductor's wait forecasts the merges of three unmerged units
- **THEN** no branch of the kit has moved

### Requirement: A forecast is told to the later unit once
A predicted conflict SHALL be told to the later unit's agent once it is not working, with the conflicting paths and the other unit's OpenSpec change. The same conflict between the same two heads SHALL be told once. Overlap SHALL order merging only, and SHALL NOT hold any unit's construct, code or verify.

#### Scenario: Two units will conflict
- **WHEN** A and B, A first, both edit the same lines of `plugin/lib/plan.py`, and the conductor's wait runs
- **THEN** B's agent is told, when idle, that its merge after A is forecast to conflict on `plugin/lib/plan.py`, with A's change, and A is told nothing

#### Scenario: Nothing new
- **WHEN** the conductor's wait runs again and neither head has moved
- **THEN** nothing is told again

### Requirement: A conflict is resolved by the later unit's agent
A conflict between two units, forecast, met at a rebase or met at merge, SHALL be resolved in the later unit's place by the later unit's agent, which SHALL be given the other unit's OpenSpec change and the conflicting paths, and SHALL keep both changes' intents. The earlier unit SHALL NOT be changed for it.

#### Scenario: A merge conflicts
- **WHEN** B's merge into the bolt conflicts with A, which merged first
- **THEN** B's agent resolves it in B's place with A's change in hand, and B merges again

## MODIFIED Requirements

### Requirement: A unit is built stage by stage, each by a fresh agent
`crew unit run <unit> <stage>` SHALL start the stage in the unit's slot with a new agent, after ending the one there. The new agent gets that stage's brief and effort, starts in the unit's worktree, and is sent its command. The stages are:

- construct: `/opsx:propose` with the unit's intent and sources;
- code: `/opsx:apply`;
- verify: `/opsx:verify`;
- merge: rebase and merge into the bolt, through `wt submit bolt/<bolt>` where sluice is available for the kit, else `wt merge bolt/<bolt> --no-squash --no-remove`.

Code SHALL start as soon as the unit's change is committed and its After units have finished construct, with no review between.

#### Scenario: Construct
- **WHEN** `crew unit run a-tenant-creates-its-environments construct` runs
- **THEN** a fresh agent in `places/a-tenant-creates-its-environments` writes the unit's OpenSpec change from its intent and sources, commits it, and stops

#### Scenario: Code before review
- **WHEN** `crew unit run <unit> code` runs on a unit whose stage is `planned`, whose change no batch has yet held
- **THEN** a fresh code agent starts, and nobody was asked to approve the change

#### Scenario: Code before construct has committed
- **WHEN** `crew unit run <unit> code` runs on a unit in `construct`
- **THEN** it is refused until its change is committed

#### Scenario: Verify before the tasks are done
- **WHEN** `crew unit run <unit> verify` runs on a unit in `code`
- **THEN** it is refused, naming the tasks still open

#### Scenario: Merging without sluice
- **WHEN** a kit has no sluice and a verified unit's merge stage runs
- **THEN** it merges with `wt merge`, one merge into the bolt at a time

### Requirement: Work happens in fixed places
A bolt SHALL be built on `bolt/<bolt>`, branched from main, in the worktree `<kit>/bolts/<bolt>`. A unit SHALL be built on `unit/<unit>`, branched from its bolt and holding its After units' work as it stood when its code started, in `<kit>/places/<unit>`. A unit SHALL merge into its bolt with the kit's merge hooks. Its place SHALL be removed once it has merged.

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit finishes
- **THEN** `bolt/<bolt>` holds the unit's change, `places/<unit>` is gone, and the unit's slot is free

## REMOVED Requirements

### Requirement: The user reviews every unit before it is coded
**Reason**: The review gate between construct and code is removed (record 0014, D5). The user reviews constructed and amended changes in batches (`review-batches`), and code does not wait for them.
**Migration**: The conductor no longer posts `review/<unit>/<head>` cards or runs `crew unit approve`. A unit in `review` or `approved` when this lands reads `planned` and may start code. What the user wants changed still goes back to a fresh construct stage, from a batch's feedback.
