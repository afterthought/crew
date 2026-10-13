# bolt-plan Specification

## Purpose
Keeps what a partition means to build, its bolts and their units, in one plain-text plan per blueprints repo. Every stage of the work is read from the kits rather than recorded by hand.

## Requirements

### Requirement: The file's order and dependencies are the plan
A bolt's units SHALL be built in the order they appear in the file, and bolts SHALL be given out in the order they appear. A unit's `After` SHALL name units of the same bolt, and the unit SHALL NOT start until each of them has merged into the bolt. A unit with no `Bolt` SHALL be queued work.

#### Scenario: A dependency not yet merged
- **WHEN** unit B has `After: A` and A is in code
- **THEN** B's stage is `waiting`, and crew refuses to start B

#### Scenario: Queued work
- **WHEN** a unit is added with no bolt
- **THEN** `crew bolts` lists it under the queue of its repo

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

### Requirement: A bolt is created, given, dropped and landed through crew
`crew bolt new` SHALL add a bolt with its repo, goal and sources. `crew bolt give <team> [<bolt>]` SHALL set the bolt's team; with no bolt named it takes the first planned bolt in the team's kit. It SHALL then make `bolt/<bolt>` from the kit's main as it stands on the team's host, and no worktree. It SHALL be refused, with the plan unchanged and no branch made, naming the file, when the kit's `.config/sluice.toml` on main names no checks for its bolt branches. `crew bolt order` SHALL move a bolt. `crew bolt drop` SHALL remove a bolt and its units, or with `--requeue` queue them, and SHALL refuse `--requeue` while a unit of the bolt has a worktree, since a queued unit has none. `crew bolt submit` SHALL submit a held bolt's branch to its kit's main through sluice, and `crew bolt land` SHALL remove a landed bolt and its units. A dropped or landed bolt's branch and worktrees SHALL then go from its team's host.

#### Scenario: A team still holds a bolt
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds a bolt with a unit that has not landed
- **THEN** it is refused, naming that bolt

#### Scenario: A kit with no bolt policy
- **WHEN** `crew bolt give swb-1` runs for a kit whose main holds no `.config/sluice.toml`, or one with no `[branches."bolt/*"]` table naming its `required` checks
- **THEN** it is refused, naming the file and what it lacks, the plan is unchanged, and no `bolt/` branch is made

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

#### Scenario: Dropping a bolt a team holds
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** the bolt and its units are gone from the plan, and the bolt's branch is gone from swb-2's host

#### Scenario: Requeuing a unit that has a worktree
- **WHEN** `crew bolt drop <bolt> --requeue` runs while one of the bolt's units has a worktree
- **THEN** it is refused, naming the unit and its worktree, and the plan is unchanged

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
- `merged`: `bolt/<bolt>` holds it archived, as the unit's own merge leaves it;
- `amended`: the plan marks the unit amended, and construct has not been run again;
- `construct`: construct has been run again on an amended unit, and has not yet committed;
- `verify`: every task is ticked;
- `code`: some task is ticked;
- `planned`: the change's planning is complete;
- `construct`: the unit's worktree exists;
- `ready` or `waiting`: neither, depending on whether each of its `After` units has finished construct;
- `queued`: the unit has no bolt.

A unit whose change `bolt/<bolt>` holds open, carried there inside another unit's merge, has not merged: it reads at its own stage, from its worktree, or, once that is gone, from its change as the bolt holds it, its planning complete.

A task, a ticked task and a complete planning mean what OpenSpec means by them. crew SHALL read them from the change's files without the `openspec` command line when the change uses OpenSpec's own spec-driven workflow, and through `openspec` otherwise; on the same worktree both readings SHALL agree.

#### Scenario: A squashed merge
- **WHEN** a unit's commits reached its bolt inside another unit's merge, its change open there with every task ticked, and its worktree and branch were removed
- **THEN** its stage is `verify`, read from the change on `bolt/<bolt>`, and not `merged`

#### Scenario: Merged by its own merge
- **WHEN** a unit's merge archived its change and the bolt holds it archived
- **THEN** its stage is `merged`

#### Scenario: Nothing kept by hand
- **WHEN** a coder ticks the last task of a unit's change
- **THEN** `crew bolts` shows the unit in `verify`, and no file was edited to say so

#### Scenario: An amended unit with ticked tasks
- **WHEN** a unit in code is marked amended and construct has been run again and has committed
- **THEN** its stage is `code`, read from its tasks, and no approval is asked

#### Scenario: A constructed unit
- **WHEN** a unit's construct has committed a change whose planning is complete, and no task is ticked
- **THEN** its stage is `planned`, and its code may start

#### Scenario: A task OpenSpec counts is counted
- **WHEN** a unit's `tasks.md` holds an indented sub-task `  - [ ] 1.1.1 …`, a numbered `1. [ ] …` or a `- [~] …`
- **THEN** crew counts each as a task not done, as `openspec list` does, and the unit stays in `code`

#### Scenario: A link is not a task
- **WHEN** a unit's `tasks.md` holds a bullet `- [design](./design.md)`
- **THEN** crew does not count it, as `openspec list` does not

#### Scenario: Planning complete without specs
- **WHEN** a unit's change declares `skip_specs: true` in its `.openspec.yaml` and has its proposal, design and tasks
- **THEN** its planning is complete, as `openspec status` says, and the unit is in `planned`

#### Scenario: Another workflow
- **WHEN** a unit's change names a workflow other than spec-driven, or its kit redefines spec-driven
- **THEN** crew reads that unit's tasks and planning through `openspec`, and every other unit's from its files

#### Scenario: The readings are held together
- **WHEN** the suite runs
- **THEN** a test reads a set of changes covering every case above both ways, on the same worktrees, and fails on any difference

### Requirement: The user's approval is a commit
`crew unit approve <unit>` SHALL record the review as an empty commit on `unit/<unit>` with a `Reviewed-by:` trailer naming the user. It SHALL refuse a unit whose change's planning is not complete. Approving a unit that is marked amended SHALL also clear the mark in the plan, after which the unit's stage is read from its tasks again.

#### Scenario: The approval travels with the work
- **WHEN** an approved unit is rebased onto a newer bolt tip
- **THEN** its approval commit comes with it, and its stage stays `approved`

#### Scenario: An amended unit is approved again
- **WHEN** the user approves an amended unit whose rewritten change is in review
- **THEN** a new approval commit is on `unit/<unit>`, the plan no longer marks the unit amended, and its stage is `code` if any task is ticked, else `approved`

#### Scenario: Approving before construct has run again
- **WHEN** `crew unit approve` names a unit whose stage is `amended`
- **THEN** it is refused, saying construct has not been run again

### Requirement: What is in flight can be read from anywhere
`crew bolts [<bolt>] [--json]` SHALL list each of the partition's bolts with its repo, team, host and state, each unit's stage and worktree, any `fix/*` worktrees branched from the bolt, and the queue. Bolts that are not active, and queued work, SHALL be listed without reaching any host. Each host holding active bolts SHALL be read once.

#### Scenario: A host is unreachable
- **WHEN** the box is asleep
- **THEN** its bolts are listed from the plan, with every stage shown as unknown and the host named

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

### Requirement: A conductor hears about writes to its bolt
When anyone other than a bolt's conductor writes to an active bolt or its units, crew SHALL send that conductor the commit's subject.

#### Scenario: The planner adds a unit
- **WHEN** the planner adds a unit to swb-1's active bolt
- **THEN** swb-1's conductor receives the commit's subject

### Requirement: A flywheel keeps one plan in its state repository
Each flywheel SHALL keep one plan, the recutils file `plan.rec` on its branch of its state repository, for all of its kits. The plan SHALL hold only Bolt and Unit records. A Bolt has its name, repo, goal, sources and team. A Unit has its name, repo, bolt, intent, sources and dependencies (`After`); a Unit record marked `Kind: chore` is a chore, whose intent is its words. The plan SHALL hold what is meant to be built and any hold on it, never how far the work has got.

#### Scenario: Business and agentplot work
- **WHEN** the business partition (label `madswan`) builds kits whose design is in afterthought/blueprints and kits whose design is in agentplot/blueprints
- **THEN** its bolts and units for both are in one `plan.rec` on `madswan/main`, and personal's plan is `plan.rec` on `swancloud/main`

#### Scenario: A plan that fails its schema
- **WHEN** a hand edit leaves a duplicated key or a field the schema does not allow
- **THEN** crew refuses to read that plan, and names the commit and `recfix --check`'s message

#### Scenario: A source in a blueprints repo
- **WHEN** a unit's source is a page of the partition's first blueprints repo
- **THEN** its `Source` is that page's path, and a page of another repo is `<owner>/<name>:<path>`

#### Scenario: A chore among the units
- **WHEN** a bolt holds two units and a chore between them
- **THEN** `plan.rec` holds the chore's Unit record, marked `Kind: chore`, between the two units' records, and the file's order is their build order

### Requirement: A unit's intent is amended through crew
`crew unit amend <unit> "<new intent>"` SHALL replace the unit's intent in the plan. A unit that has a worktree SHALL also be marked amended, and once the write has landed its construct SHALL be handed to its team's host, where it SHALL start again in the name of whoever applied the amendment and the conductor SHALL be told from that host what started or why nothing did. The command, run directly or by a proposal's approval, SHALL answer once its write is made and the construct is handed to the host, and SHALL NOT wait on an agent's session coming up or its prompt landing. `crew unit wait <unit>` SHALL wait for a handed construct to start before it waits on the stage, and say why when it did not start; a stage of the unit SHALL be refused while a handed construct starts. A unit that has merged into its bolt or landed SHALL be refused. Run by the planner it SHALL be refused outside a proposal; the user at a shell runs it directly.

#### Scenario: A queued unit
- **WHEN** an amendment to a queued unit's intent is applied
- **THEN** the unit's intent is the new one, and nothing else changes

#### Scenario: A unit in code
- **WHEN** an amendment to a unit in code is applied
- **THEN** the unit's intent is the new one, the unit is marked amended, the command answers once its construct is handed to the team's host, and that host starts construct again and tells the conductor to wait for it

#### Scenario: A team taken down
- **WHEN** an amendment to a unit in verify is applied while its team is down
- **THEN** the unit is marked amended, the start is recorded refused, and the command says construct did not start because the team is down and tells the conductor so

#### Scenario: A wait on a handed construct
- **WHEN** the conductor runs `crew unit wait <unit>` while the construct an amendment handed is starting
- **THEN** the wait waits for it to start and then on its stage, within its timeout; and when it could not start, the wait says why

#### Scenario: A stage while a handed construct starts
- **WHEN** the conductor runs a stage of a unit whose handed construct is starting
- **THEN** crew refuses it, saying the construct is starting and that `crew unit wait <unit>` waits for it

#### Scenario: A merged unit
- **WHEN** `crew unit amend` names a unit that has merged into its bolt
- **THEN** it is refused; what is needed is a fix or a new unit

### Requirement: A command reads each kit and the plan once
A crew command SHALL read each kit once and fetch the state branch once on each host it runs on, however many steps it has. A step that makes or removes a worktree in a kit SHALL leave the next step to read that kit again. A plan write SHALL start from the tip the command holds and fetch again only when its push is refused. A wait, the rail tab's loop and `crew events --follow` SHALL read afresh each time they look.

#### Scenario: Status with three units in flight
- **WHEN** `crew status <team>` runs for a team with three units in flight
- **THEN** the team's host reads the kit once and fetches the state branch once, and `openspec` is not started

#### Scenario: Running a stage
- **WHEN** `crew unit run <unit> construct` frees finished slots, tidies worktrees, checks the stage and makes the unit's place
- **THEN** the team's host fetches the state branch once and reads the kit once before the place is made

#### Scenario: A write after the plan moved
- **WHEN** another agent's write lands on the state branch after a command fetched it, and the command then writes
- **THEN** the command's push is refused, it fetches the new tip and applies its change there, as any write does

#### Scenario: A wait sees what changes while it waits
- **WHEN** `crew unit wait <unit>` is waiting and the coder ticks the last task
- **THEN** the wait's next look reads the new head and returns with the delivered end

#### Scenario: Nothing is left behind
- **WHEN** a command ends, whether it succeeded or was refused
- **THEN** what it kept for its steps is gone, and the next command reads afresh
