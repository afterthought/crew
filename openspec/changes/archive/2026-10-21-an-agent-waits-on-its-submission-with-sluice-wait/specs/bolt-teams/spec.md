# Spec Delta

## MODIFIED Requirements

### Requirement: A unit is built stage by stage, each by a fresh agent
`crew unit run <unit> <stage>` SHALL start the stage in the unit's slot with a new agent, after ending the one there. The new agent gets that stage's brief and effort, starts in the unit's worktree, and is sent its command. The stages are:

- construct: `/opsx:propose` with the unit's intent and sources;
- code: `/opsx:apply`;
- verify: `/opsx:verify`;
- settle: the coder's brief, with the forecast or amendment that reached a unit waiting to merge;
- merge: a submission to the bolt made without waiting, `sluice submit bolt/<bolt> --no-wait --json`, which its agent waits on a call at a time with `sluice wait <n> --timeout 9m --json` until it exits other than 5, still waiting, and which sluice lands only when the checks the kit's policy requires of its bolt branches pass on the bolt with the unit merged.

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

#### Scenario: Merging
- **WHEN** a verified unit's merge stage runs
- **THEN** its agent is told to run `sluice submit bolt/<bolt> --no-wait --json` in the unit's place and to wait on the submission with `sluice wait`, and sluice's verdict decides whether the unit lands on the bolt

#### Scenario: A slow gate
- **WHEN** a unit's merge has been testing for twenty minutes
- **THEN** its agent's calls of `sluice wait <n> --timeout 9m --json` have each exited 5 within ten minutes, and its next call ends with sluice's verdict, exiting 0 when the unit landed
