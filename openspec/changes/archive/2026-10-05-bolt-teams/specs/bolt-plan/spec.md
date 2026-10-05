# Spec Delta

## Purpose

Keeps what a partition means to build, its bolts and their units, in one plain-text plan per blueprints repo. Every stage of the work is read from the kits rather than recorded by hand.

## ADDED Requirements

### Requirement: A partition keeps one plan per blueprints repo
Each blueprints repo a partition names SHALL hold that partition's plan as one recutils file, `plan.rec`, alone on the branch `plan/<label>`. The plan SHALL hold only Bolt and Unit records. A Bolt has its name, repo, goal, sources and team. A Unit has its name, repo, bolt, intent, sources and dependencies (`After`). The plan SHALL hold no stage, date or author.

#### Scenario: Business and agentplot work
- **WHEN** the business partition (label `madswan`) names afterthought/blueprints and agentplot/blueprints
- **THEN** its plans are `plan/madswan` in each of those repos, and personal's plan is `plan/swancloud` in afterthought/blueprints

#### Scenario: A plan that fails its schema
- **WHEN** a hand edit leaves a duplicated key or a field the schema does not allow
- **THEN** crew refuses to read that plan, and names the commit and `recfix --check`'s message

### Requirement: The file's order and dependencies are the plan
A bolt's units SHALL be built in the order they appear in the file, and bolts SHALL be given out in the order they appear. A unit's `After` SHALL name units of the same bolt, and the unit SHALL NOT start until each of them has merged into the bolt. A unit with no `Bolt` SHALL be queued work.

#### Scenario: A dependency not yet merged
- **WHEN** unit B has `After: A` and A is in code
- **THEN** B's stage is `waiting`, and crew refuses to start B

#### Scenario: Queued work
- **WHEN** a unit is added with no bolt
- **THEN** `crew bolts` lists it under the queue of its repo

### Requirement: Writes go through crew and are never merged
Agents SHALL write the plan only through `crew bolt …` and `crew unit …`. Each write SHALL fetch the plan branch over https into crew's own bare cache of the repo, with no working tree, and apply the change to its tip. It SHALL then check the result with `recfix --check` and crew's own rules, commit it without touching any working tree, and push without force. A push that is rejected SHALL have its write applied again to the new tip, up to five times.

#### Scenario: Two writes race
- **WHEN** the planner moves a unit while a conductor narrows the same unit's intent, from different hosts
- **THEN** both writes land, one after the other, and neither is merged

#### Scenario: The subject is gone
- **WHEN** a write names a unit that another write has just dropped
- **THEN** it is refused, naming the commit that dropped the unit

#### Scenario: No ssh on a Mac
- **WHEN** a write runs on a Mac
- **THEN** git reaches the blueprints repo over https and never waits on 1Password

### Requirement: A bolt is created, given, dropped and landed through crew
`crew bolt new` SHALL add a bolt with its repo, goal and sources. `crew bolt give <team> [<bolt>]` SHALL set the bolt's team; with no bolt named it takes the first planned bolt in the team's kit. It SHALL then make `bolt/<bolt>` from main and its worktree at `<kit>/bolts/<bolt>` on the team's host. `crew bolt order` SHALL move a bolt. `crew bolt drop` SHALL remove a bolt and its units, or with `--requeue` queue them. `crew bolt land` SHALL remove a landed bolt and its units.

#### Scenario: A team still holds a bolt
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds a bolt with a unit that has not landed
- **THEN** it is refused, naming that bolt

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

### Requirement: Units change while a bolt runs
`crew unit add` SHALL add a unit to a bolt, or to the queue, at the end or before a named unit. `crew unit split` SHALL narrow a unit and add the remainder right after it. `crew unit order` SHALL move a unit within its bolt. `crew unit after` SHALL set or clear a dependency, refusing a cycle or a unit of another bolt. `crew unit move` SHALL move a unit to another bolt of the same repo, or to the queue. `crew unit drop` SHALL remove a unit, with the reason in the commit.

#### Scenario: Splitting a unit in code
- **WHEN** `crew unit split` names a unit whose stage is code or later
- **THEN** it is refused; the remainder is added as a new unit instead

#### Scenario: Moving a unit with a worktree
- **WHEN** a unit in construct moves to another bolt in the same checkout
- **THEN** its branch is rebased onto the new bolt; a conflict aborts the move and leaves the plan unchanged

#### Scenario: Dropping merged work
- **WHEN** `crew unit drop` names a unit that has merged into its bolt
- **THEN** it is refused

### Requirement: A unit's stage is read from the kits
crew SHALL derive each unit's stage from its kit on the team's host. The first rule that holds is the unit's stage:

- `landed`: main holds the unit's OpenSpec change, open or archived;
- `merged`: `bolt/<bolt>` holds it;
- `verify`: every task is ticked;
- `code`: some task is ticked;
- `approved`: the change's planning is complete, and a review has been approved since the bolt;
- `review`: the change's planning is complete, with no approval;
- `construct`: the unit's worktree exists;
- `ready` or `waiting`: neither, depending on its `After` units;
- `queued`: the unit has no bolt.

#### Scenario: A squashed merge
- **WHEN** a unit was merged into its bolt with `wt merge`, and its worktree and branch were removed
- **THEN** its stage is still `merged`, read from the change folder on `bolt/<bolt>`

#### Scenario: Nothing kept by hand
- **WHEN** a coder ticks the last task of a unit's change
- **THEN** `crew bolts` shows the unit in `verify`, and no file was edited to say so

### Requirement: The user's approval is a commit
`crew unit approve <unit>` SHALL record the review as an empty commit on `unit/<unit>` with a `Reviewed-by:` trailer naming the user. It SHALL refuse a unit whose change's planning is not complete.

#### Scenario: The approval travels with the work
- **WHEN** an approved unit is rebased onto a newer bolt tip
- **THEN** its approval commit comes with it, and its stage stays `approved`

### Requirement: What is in flight can be read from anywhere
`crew bolts [<bolt>] [--json]` SHALL list each of the partition's bolts with its repo, team, host and state, each unit's stage and worktree, any `fix/*` worktrees branched from the bolt, and the queue. Bolts that are not active, and queued work, SHALL be listed without reaching any host. Each host holding active bolts SHALL be read once.

#### Scenario: A host is unreachable
- **WHEN** the box is asleep
- **THEN** its bolts are listed from the plan, with every stage shown as unknown and the host named

### Requirement: Work is queued from a signal
`crew unit add … --signal <id>` SHALL queue the unit with the signal as its source, and SHALL record the signal's one move, `route`, targeting the unit in the `signals/moves.rec` of the partition's first blueprints repo, where its signals are. The source SHALL be `signals/<id>` when the plan is in that repo, else `<owner/name>:signals/<id>`. A signal that is missing, already moved, or whose move would fail `recfix --check` SHALL be refused before the plan is written.

#### Scenario: A signal routed to work
- **WHEN** the planner queues a unit from a signal
- **THEN** the unit's `Source` is `signals/<id>`, and `moves.rec` gains a `route` move for that signal

#### Scenario: A signal in another blueprints repo
- **WHEN** madswan's planner queues a flywheel-next unit in agentplot/blueprints' plan from a signal in afterthought/blueprints
- **THEN** the unit's `Source` is `afterthought/blueprints:signals/<id>`, and the route move is in afterthought/blueprints

### Requirement: A conductor hears about writes to its bolt
When anyone other than a bolt's conductor writes to an active bolt or its units, crew SHALL send that conductor the commit's subject.

#### Scenario: The planner adds a unit
- **WHEN** the planner adds a unit to swb-1's active bolt
- **THEN** swb-1's conductor receives the commit's subject
