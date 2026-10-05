# Spec Delta

## ADDED Requirements

### Requirement: A flywheel keeps one plan in its state repository
Each flywheel SHALL keep one plan, the recutils file `plan.rec` on its branch of its state repository, for all of its kits. The plan SHALL hold only Bolt and Unit records. A Bolt has its name, repo, goal, sources and team. A Unit has its name, repo, bolt, intent, sources and dependencies (`After`). The plan SHALL hold what is meant to be built and any hold on it, never how far the work has got.

#### Scenario: Business and agentplot work
- **WHEN** the business partition (label `madswan`) builds kits whose design is in afterthought/blueprints and kits whose design is in agentplot/blueprints
- **THEN** its bolts and units for both are in one `plan.rec` on `madswan/main`, and personal's plan is `plan.rec` on `swancloud/main`

#### Scenario: A plan that fails its schema
- **WHEN** a hand edit leaves a duplicated key or a field the schema does not allow
- **THEN** crew refuses to read that plan, and names the commit and `recfix --check`'s message

#### Scenario: A source in a blueprints repo
- **WHEN** a unit's source is a page of the partition's first blueprints repo
- **THEN** its `Source` is that page's path, and a page of another repo is `<owner>/<name>:<path>`

## MODIFIED Requirements

### Requirement: Writes go through crew and are never merged
Agents SHALL write the plan only through `crew bolt …` and `crew unit …`. Each write SHALL fetch the flywheel's branch of its state repository over https into crew's own bare cache of that repository, with no working tree, and apply the change to its tip. It SHALL then check the result with `recfix --check` and crew's own rules, commit it without touching any working tree, and push without force. A push that is rejected SHALL have its write applied again to the new tip, up to five times.

#### Scenario: Two writes race
- **WHEN** the planner moves a unit while a conductor narrows the same unit's intent, from different hosts
- **THEN** both writes land, one after the other, and neither is merged

#### Scenario: The subject is gone
- **WHEN** a write names a unit that another write has just dropped
- **THEN** it is refused, naming the commit that dropped the unit

#### Scenario: No ssh on a Mac
- **WHEN** a write runs on a Mac
- **THEN** git reaches the state repository over https and never waits on 1Password

### Requirement: Work is queued from a signal
`crew unit add … --signal <id>` SHALL queue the unit with the signal as its source, `signals/<id>`, and SHALL record the signal's one move, `route`, targeting the unit, in `moves.rec` on the flywheel's branch, in the same commit as the unit. A signal that is missing from the partition's first blueprints repo, already moved, or whose move would fail `recfix --check` SHALL be refused, and nothing written.

#### Scenario: A signal routed to work
- **WHEN** the planner queues a unit from a signal
- **THEN** one commit on the flywheel's branch adds the unit with `Source: signals/<id>` and a `route` move for that signal

#### Scenario: A signal in another blueprints repo
- **WHEN** madswan's planner queues a flywheel-next unit, whose design is in agentplot/blueprints, from a signal in afterthought/blueprints, the partition's first blueprints repo
- **THEN** the unit's `Source` is `signals/<id>`, which names that signal in afterthought/blueprints, and the route move is in `moves.rec` on `madswan/main`, in the same commit as the unit

#### Scenario: A signal already moved
- **WHEN** the signal named already has its move
- **THEN** the command is refused, naming the move it has, and the plan is unchanged

## REMOVED Requirements

### Requirement: A partition keeps one plan per blueprints repo
**Reason**: The plan is the machinery's record, not part of the design, and its branch and frequent commits do not belong in a design repository. One plan per blueprints repo also split a flywheel's work across files that no single write could change together.
**Migration**: `crew state init <label>` carries each `plan/<label>` branch, with its history, to the flywheel's branch of its state repository, joining the plans of a partition that had two. The `plan/<label>` branches are deleted from the blueprints repos once `crew bolts` answers from the state. The requirement "A flywheel keeps one plan in its state repository" replaces this one.
