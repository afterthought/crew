# Spec Delta

## ADDED Requirements

### Requirement: A bolt's units are constructed in waves
Once a team holds a bolt, the conductor SHALL run construct, as slots allow and in the file's order, for every unit whose `After` units have all finished construct. A unit's construct SHALL NOT wait on the user, on another unit's merge, or on another unit's Touches. Changes are so written in waves: the units with no `After` first, then each unit as soon as the changes it builds on are committed.

#### Scenario: A bolt is given
- **WHEN** a team with four slots is given a bolt of three units, C with `After: A`
- **THEN** A's and B's constructs run at once, and C's starts as soon as A's change is committed

#### Scenario: More units than slots
- **WHEN** a team with two slots holds a bolt of five units with no `After`
- **THEN** two constructs run, and the next unit in the file's order is constructed as each slot frees

### Requirement: A dependent builds on its After units' work as it stands
When a unit's place is made, crew SHALL bring into `unit/<unit>` the head of each of its `After` units that has not merged, as that head stands. When an `After` unit merges into the bolt, crew SHALL rebase the dependent's place onto the bolt, leaving out that unit's work as the place took it, only while the dependent's agent is not working and its place has no uncommitted changes. A rebase that conflicts SHALL be undone and handed to the dependent as a conflict is.

#### Scenario: Construct on a constructed dependency
- **WHEN** B has `After: A`, A's change is committed and A is in code, and B's construct starts
- **THEN** B's place holds A's commits as they stood when B's place was made

#### Scenario: The dependency merges
- **WHEN** A merges into the bolt while B's agent is idle
- **THEN** B's place is rebased onto the bolt, and holds no commit of A's that the bolt already holds

#### Scenario: The dependency settled before it merged
- **WHEN** A's settle rewrote A's change, which B's place holds as it took it, and A merges into the bolt while B's agent is idle
- **THEN** B's place is rebased onto the bolt with only B's own commits replayed, and nothing conflicts on A's files

#### Scenario: The dependent is working
- **WHEN** A merges into the bolt while B's agent is working
- **THEN** B's place is not touched until the agent is idle

### Requirement: A dependent is told when its After unit is amended
When an `After` unit is amended after its dependent's code has started, the dependent SHALL NOT be held. crew SHALL tell the dependent of the amendment, with the path of the revised change, the way a forecast reaches it.

#### Scenario: The dependency is amended
- **WHEN** B has `After: A`, B is in code, and A is constructed again with the user's notes
- **THEN** B's code goes on, and B is told that A's change was revised, with its path

### Requirement: Touches is a list crew reads
A unit's `proposal.md` SHALL end with a `## Touches` heading holding one fenced block of repository paths or globs, one to a line. crew SHALL read it before the unit's code starts, and SHALL refuse code when the heading or the block is missing or empty.

#### Scenario: No Touches
- **WHEN** a unit's proposal has no `## Touches` block
- **THEN** its code is refused, saying the change must declare what it touches

### Requirement: Overlapping Touches are told before code
When a unit's code is about to start and its Touches overlap those of an unmerged unit ahead of it in the bolt, crew SHALL tell the later unit which entries overlap and where the other unit's change is. Overlap SHALL NOT hold the unit's code.

#### Scenario: Two units declare the same file
- **WHEN** units A and B, A first in the file, both list `plugin/lib/plan.py`, and B's code is about to start
- **THEN** B's code starts, and its prompt names the overlap with A on `plugin/lib/plan.py` and the path of A's change

### Requirement: Verify names what a unit changed and did not declare
At verify, every path `git diff --name-only bolt/<bolt>...unit/<unit>` names that no entry of the unit's Touches matches SHALL be a finding of the verify report. The code stage that acts on the finding SHALL correct the Touches block of `proposal.md`, and change nothing else of the change.

#### Scenario: A path not declared
- **WHEN** a unit changed `README.md` against its bolt and its Touches do not match it
- **THEN** the verify report names `README.md` as changed and not declared, and the code stage run on the finding adds it to the Touches block

### Requirement: A conflict is forecast on the conductor's waits
Each time the conductor waits on a stage or a proof through crew, crew SHALL dry-run, with `git merge-tree`, the merge of each unmerged unit's head with `bolt/<bolt>` and with the head of each unmerged unit ahead of it in the file's order, writing no ref. A dependent SHALL be compared with a unit it comes after only on what it adds beyond the head of that unit its place took.

#### Scenario: The dry run moves nothing
- **WHEN** the conductor's wait forecasts the merges of three unmerged units
- **THEN** no branch of the kit has moved

#### Scenario: A dependent carries its After unit's rewritten work
- **WHEN** B, after A, holds A's work as its place took it, A is rebased onto the bolt and its settle revises A's own file, and the conductor's wait runs
- **THEN** B is forecast nothing against A for that file, and a line B's own commit changed that A's settle also changed is forecast

### Requirement: A forecast reaches the later unit once
A predicted conflict SHALL reach the later unit once for the same two heads, with the conflicting paths and the other unit's OpenSpec change: told to its agent once the agent is not working, when its stage is running; carried in the prompt of its next stage, when no agent of it is running; or as a settle stage, when it has delivered and waits to merge. Overlap SHALL order merging only, and SHALL NOT hold any unit's construct, code or verify.

#### Scenario: Two units will conflict while one codes
- **WHEN** A and B, A first, both edit the same lines of `plugin/lib/plan.py`, B's code agent is running, and the conductor's wait runs
- **THEN** B's agent is told, when idle, that its merge after A is forecast to conflict on `plugin/lib/plan.py`, with A's change, and A is told nothing

#### Scenario: No agent running
- **WHEN** a conflict is forecast for a unit in `planned` with no agent in its slot
- **THEN** its code stage's prompt carries the forecast

#### Scenario: Nothing new
- **WHEN** the conductor's wait runs again and neither head has moved
- **THEN** nothing is told again

### Requirement: A forecast conflict between two units orders them
When a conflict is forecast between two units that have both not merged, the later unit SHALL gain `After` on the earlier one and merge after it, and the later unit's agent SHALL take the earlier unit's work into its place and resolve the conflict there.

#### Scenario: Two unmerged units
- **WHEN** a conflict is forecast between A and B, A first, neither merged
- **THEN** B gains `After: A`, B's agent takes A's work into B's place and resolves the conflict there, and B's merge waits for A's

### Requirement: A unit waiting to merge settles
A unit that has delivered its verify and waits to merge, and that a forecast conflict or an amended `After` unit reaches, SHALL be given a settle stage: a fresh agent in its slot, with the coder's brief, prompted with the forecast or the amendment. The stage's deliverable SHALL be a commit on `unit/<unit>` made since the stage began; when nothing needs to change, its agent SHALL stop short saying so, and the unit goes on to merge.

#### Scenario: A verified unit is forecast to conflict
- **WHEN** B is verified and waits to merge, and a conflict with the bolt is forecast for it
- **THEN** a settle stage starts in B's slot with the forecast, and ends at the commit that resolves it

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
- settle: the coder's brief, with the forecast or amendment that reached a unit waiting to merge;
- merge: rebase and merge into the bolt, through `wt submit bolt/<bolt>` where the kit opts into sluice, else `wt merge bolt/<bolt> --no-squash --no-remove`.

Code SHALL start as soon as the unit's change is committed, with no review between.

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
- **WHEN** a kit has not opted into sluice and a verified unit's merge stage runs
- **THEN** it merges with `wt merge`, one merge into the bolt at a time, gated by the kit's merge hooks

#### Scenario: Merging through sluice
- **WHEN** a kit has opted into sluice and a verified unit's merge stage runs
- **THEN** it submits with `wt submit bolt/<bolt>`, the kit's pre-merge hooks run as the submit gate, sluice's verdict decides the merge, and the unit's `After` units are its after-entries

### Requirement: Work happens in fixed places
A bolt SHALL be built on `bolt/<bolt>`, branched from main, in the worktree `<kit>/bolts/<bolt>`. A unit SHALL be built on `unit/<unit>`, branched from its bolt and holding its `After` units' work as it stood when its place was made, in `<kit>/places/<unit>`. A unit SHALL merge into its bolt with the kit's merge hooks, or through sluice where the kit opts into it. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over.

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit finishes
- **THEN** `bolt/<bolt>` holds the unit's change, `places/<unit>` is gone, and the unit's slot is free

### Requirement: A unit in flight goes back through construct and review
`crew unit run <unit> construct "<words>"` SHALL be accepted at any stage before the unit has merged into its bolt. Run on a unit that is in code or in verify, it SHALL mark the unit amended in the plan before the stage starts. While construct runs again, `crew unit run <unit> code`, `verify` and `merge` SHALL be refused; once it has committed, the unit SHALL go on from its tasks with no approval asked, and its revised change SHALL be due for the next batch.

#### Scenario: The user wants a change to a unit in code
- **WHEN** the conductor runs `crew unit run <unit> construct "<the user's words>"` on a unit in code
- **THEN** the unit is marked amended, a fresh construct agent rewrites the change in the unit's slot and place, and when it commits the unit's stage is read from its tasks

#### Scenario: Code on an amended unit
- **WHEN** `crew unit run <unit> code` runs on a unit marked amended whose construct has not committed again
- **THEN** it is refused until that construct has committed

#### Scenario: An amended intent arrives from an approved proposal
- **WHEN** an approved proposal amends the intent of a unit in flight
- **THEN** the conductor is told, runs construct again, and the fresh construct agent is given the new intent and told the change is to be revised to it

#### Scenario: A merged unit
- **WHEN** `crew unit run <unit> construct` runs on a unit that has merged into its bolt
- **THEN** it is refused; a defect is a fix, and a new need is a new unit

## REMOVED Requirements

### Requirement: The user reviews every unit before it is coded
**Reason**: The review gate between construct and code is removed (record 0014, D5). The user reviews constructed and amended changes in the partition's batches (`review-batches`), and code does not wait for them.
**Migration**: The conductor no longer posts `review/<unit>/<head>` cards or runs `crew unit approve`. A unit in `review` or `approved` when this lands reads `planned` and may start code. What the user wants changed still goes back to a fresh construct stage, from a batch's notes.
