# bolt-plan Specification

## Purpose
Keeps what a partition means to build, its bolts and their units, in one plain-text plan per blueprints repo. Every stage of the work is read from the kits rather than recorded by hand.

## Requirements

### Requirement: The file's order and dependencies are the plan
A bolt's units SHALL be ordered by the file: bolts SHALL be given out in the order they appear, and a unit is ahead of every unit after it in its bolt. A unit's `After` SHALL name units of the same bolt that it builds on, or whose work its settle took after a forecast conflict between them; a forecast alone SHALL NOT put a unit after another. The unit's construct SHALL NOT start until each of them has finished construct, its OpenSpec change committed, and SHALL NOT wait for any of them to merge. The unit SHALL NOT merge into the bolt until each of them has merged. A unit with no `Bolt` SHALL be queued work.

#### Scenario: A dependency still in construct
- **WHEN** unit B has `After: A`, and A's construct has not committed
- **THEN** B's stage is `waiting`, and crew refuses to start B's construct

#### Scenario: A dependency constructed
- **WHEN** unit B has `After: A`, and A's change is committed while A is in code
- **THEN** crew accepts B's construct

#### Scenario: A dependency not yet merged
- **WHEN** unit B has `After: A`, B is verified and A has not merged into the bolt
- **THEN** crew refuses B's merge, naming A

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
`crew bolt new` SHALL add a bolt with its repo, goal and sources. `crew bolt give <team> [<bolt>]` SHALL set the bolt's team; with no bolt named it takes the first planned bolt in the team's kit. It SHALL have sluice make `bolt/<bolt>` on GitHub from main, `sluice branch create bolt/<bolt> --from main` on the team's host, and no worktree, before the plan is written. It SHALL be refused, with the plan unchanged and no branch made, while the team holds two bolts, and while a bolt it holds is not proven: it holds no unit or chore yet, a unit or chore of it has not merged, or sluice's verdict at its head is not green, naming the bolt and what holds it; a fix in flight on a proven bolt SHALL refuse nothing. What crew cannot read of a held bolt SHALL refuse the give, naming what could not be read. It SHALL be refused, with the plan unchanged and no branch made, naming the file, when the kit's `.config/sluice.toml` at `origin/main` names no checks or no `remote` for its bolt branches; naming the version it needs and the one the host has when the host's sluice lacks `branch create` or its version cannot be read; and in sluice's words when sluice refuses the create. `crew bolt order` SHALL move a bolt. `crew bolt drop` SHALL remove a bolt and its units, or with `--requeue` queue them, and SHALL refuse `--requeue` while a unit of the bolt has a worktree, since a queued unit has none. `crew bolt submit` SHALL submit a held bolt's branch to its kit's main through sluice, and `crew bolt land` SHALL remove a landed bolt and its units and have sluice delete its branch, `sluice branch delete bolt/<bolt> --into main`, naming a refusal in sluice's words. `crew bolt drop` of a bolt a team holds SHALL have sluice delete its branch the same way after the plan write; when sluice refuses, as while the branch's tip is not in main, the branch SHALL be kept where it lives, on GitHub and on the team's host, named in the drop's output as the drop's unmerged work with sluice's words, and recorded once in the run record, and the team's reads SHALL ask sluice's delete again once main holds its tip; crew SHALL NOT delete a dropped bolt's branch with git. A dropped or landed bolt's worktrees SHALL then go from its team's host. A bolt whose branch crew made on its host before gives went through sluice SHALL stay local until it lands: crew SHALL run no create for it, its places SHALL be cut from the local branch, each read of its team SHALL say once that it is local until it lands, and its land SHALL have sluice delete it wherever its tip's policy routes it, on GitHub once its landing's pull request put it there.

#### Scenario: A team still holds a bolt
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds a bolt with a unit that has not merged
- **THEN** it is refused, naming that bolt and that unit with its stage

#### Scenario: A team's bolt is merged but not yet green
- **WHEN** `crew bolt give swb-1` runs while every unit of swb-1's bolt has merged and its head is no landing of sluice's
- **THEN** it is refused, naming the bolt and what its verification is now

#### Scenario: A team's bolt is proven
- **WHEN** `crew bolt give swb-1` runs while every unit of swb-1's bolt has merged, sluice is green at its head, and a fix of it is in flight
- **THEN** swb-1 is given the next planned bolt and holds both

#### Scenario: A team holding two bolts
- **WHEN** `crew bolt give swb-1` runs while swb-1 holds two bolts, both proven
- **THEN** it is refused, naming the bolt waiting to land longest, whose landing frees the team

#### Scenario: A kit with no bolt policy
- **WHEN** `crew bolt give swb-1` runs for a kit whose `origin/main` holds no `.config/sluice.toml`, or one with no `[branches."bolt/*"]` table naming its `required` checks
- **THEN** it is refused, naming the file and what it lacks, the plan is unchanged, and no `bolt/` branch is made

#### Scenario: A kit whose bolts have no remote
- **WHEN** `crew bolt give swb-1` runs for a kit whose bolt policy at `origin/main` names checks but no `remote`
- **THEN** it is refused, naming the file and the key, the plan is unchanged, and no branch is made anywhere

#### Scenario: A host whose sluice cannot make a branch
- **WHEN** `crew bolt give swb-1` runs on a host whose sluice is older than 0.20.0, or whose `sluice --version` prints nothing crew can read
- **THEN** it is refused, naming 0.20.0 and what the host's sluice said, and the plan is unchanged

#### Scenario: Sluice refuses the create
- **WHEN** `crew bolt give swb-1` runs and sluice refuses to make `bolt/<bolt>`, as when it is already there
- **THEN** the give is refused with sluice's words, and the plan is unchanged

#### Scenario: A bolt is made on GitHub
- **WHEN** `crew bolt give swb-1` gives swb-1 the bolt `b` for a kit whose policy names `origin` for its bolts
- **THEN** `bolt/b` is on GitHub at main's commit, made by sluice, the plan gives `b` to swb-1, and crew says where the branch was made and at which commit

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

#### Scenario: The bolt's branch is deleted at its land
- **WHEN** `crew bolt land` runs for a landed bolt whose branch is on GitHub
- **THEN** the bolt leaves the plan, sluice deletes `bolt/<bolt>` from GitHub, and the branch is gone from the team's host

#### Scenario: A delete sluice refuses
- **WHEN** `crew bolt land` runs and sluice refuses to delete `bolt/<bolt>` because a submission is still queued on it
- **THEN** the bolt leaves the plan, the branch stays on GitHub, and crew names it with sluice's words

#### Scenario: A bolt made before stays local
- **WHEN** a team's read finds that the team holds a bolt whose branch is on its host only, its tip's policy naming no remote for it, while the policy at the kit's main names `origin` for its bolts
- **THEN** crew says once that the bolt is local until it lands, runs no create, and its places are cut from the local branch

#### Scenario: A bolt made before lands
- **WHEN** `crew bolt land` runs for a landed bolt made before, whose last merge brought it a policy naming `origin` and whose landing's pull request sluice pushed to GitHub
- **THEN** the bolt leaves the plan, sluice deletes `bolt/<bolt>` from GitHub, and the branch is gone from the team's host

#### Scenario: Dropping a bolt a team holds
- **WHEN** the planner drops a bolt that swb-2 holds, whose branch's tip main holds
- **THEN** the bolt and its units are gone from the plan, sluice deletes `bolt/<bolt>` from GitHub, and the branch is gone from swb-2's host

#### Scenario: A dropped bolt holds work main lacks
- **WHEN** the planner drops a bolt that swb-2 holds, into which a unit has merged that main does not hold
- **THEN** the bolt and its units are gone from the plan, sluice refuses the delete, the branch stays on GitHub and on swb-2's host, and the drop names it as its unmerged work with sluice's words, the user's to keep or delete, and records it once

#### Scenario: Main comes to hold a dropped bolt's work
- **WHEN** a read of swb-2 finds a dropped bolt's kept branch whose tip the kit's main now holds, as after a landing that carried it
- **THEN** crew asks sluice to delete it, and it is gone from GitHub and from swb-2's host

#### Scenario: A dropped bolt's kept branch while main lacks it
- **WHEN** a read of swb-2 finds a dropped bolt's kept branch whose tip main does not hold
- **THEN** nothing is asked of sluice and nothing is said, and the branch stays

#### Scenario: The drop's host does not answer
- **WHEN** the planner drops a bolt that swb-2 holds while swb-2's host does not answer
- **THEN** the drop names the host and the command, and swb-2's next read asks sluice's delete as the drop would have

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

#### Scenario: The unit's stage cannot be read
- **WHEN** an amendment to a unit with a worktree is applied while its team's host does not answer, so the unit's stage cannot be read
- **THEN** the amendment, or the approval holding it, is refused naming the host that did not answer, and nothing is written

#### Scenario: The construct cannot start
- **WHEN** an amendment to a unit in flight is applied once its stage has been read, and its handed construct cannot start because its team's host stops answering before the run reaches it or its team is down
- **THEN** the amendment stands, the unit's stage reads `amended`, the command says why construct did not start, and the conductor, when it can be told, is told why and to run construct once it can, with the card the amendment ended named

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

### Requirement: A bolt on GitHub is read where it lives
crew SHALL read a bolt at GitHub's copy of its branch, `origin/bolt/<bolt>`, when the host holds that copy and the policy in it names a remote for the bolt, and otherwise at the host's own `bolt/<bolt>`. Its head, verification, the changes and chores it holds, and every stage read from it SHALL come from that ref. crew SHALL never read a bolt on GitHub from the host's own `bolt/<bolt>`, sluice's copy, whether or not sluice has levelled it.

#### Scenario: A merge landed on GitHub while the host's copy stayed behind
- **WHEN** sluice lands a unit's merge and a chore's merge on GitHub's `bolt/b`, the host has fetched it, and the host's own `bolt/b` is still at the commit before them
- **THEN** the unit and the chore read `merged`, the bolt's head is GitHub's, and its verification is the verdict at that head

#### Scenario: A proven bolt whose copy lags
- **WHEN** every unit of a bolt on GitHub has merged and the `Sluice-Result` at GitHub's head starts `passed`, while the host's `bolt/b` is at an earlier landing
- **THEN** the bolt reads proven, and a give to its team is not refused for it

#### Scenario: A bolt kept on its host
- **WHEN** a bolt was made before gives went through sluice, the policy at GitHub's copy of it names no remote for its bolts, and the host's own `bolt/b` holds merges GitHub's copy lacks
- **THEN** the bolt is read at the host's `bolt/b`, those merges counted

#### Scenario: A bolt GitHub's copy of which this host has not got
- **WHEN** the host holds no `origin/bolt/b`
- **THEN** the bolt is read at the host's `bolt/b`, the only copy the host has, and is missing when that is not there either

#### Scenario: A policy crew can't read
- **WHEN** the policy in GitHub's copy of the bolt is not TOML
- **THEN** the bolt's stages read `unknown`, naming the file and the bolt, and nothing is read from the host's `bolt/b`

#### Scenario: A chore's place and a fix beside a bolt on GitHub
- **WHEN** a chore's place holds one commit of its own beyond GitHub's `bolt/b`, and a fix's tip is in GitHub's `bolt/b` but not in the host's
- **THEN** the chore reads `verify` and the fix reads merged

### Requirement: A bolt on GitHub is fetched where a decision rests on it
As main is read (plan.18), crew SHALL read a bolt on GitHub as the host last fetched it on every team read and every refresh of the rail and the board, fetching nothing. `crew bolts`, a give's check that the team's bolts are proven, each look a wait takes at a merge stage, and a give's making of a branch SHALL fetch the kit's origin first. A fetch that fails SHALL be named with git's words, never read past to the host's copy.

#### Scenario: A wait on a merge sees it at once
- **WHEN** `crew chore wait <chore>` waits on a merge, and sluice lands it on GitHub's `bolt/b` without moving the host's `bolt/b` or its tracking ref
- **THEN** the wait's next look fetches, reads the chore in GitHub's `bolt/b`, and returns with the merge delivered at GitHub's head

#### Scenario: crew bolts after a landing elsewhere
- **WHEN** a merge has landed on GitHub's `bolt/b` since the host last fetched, and `crew bolts` runs
- **THEN** it fetches the kit's origin once on the team's host and shows the merged unit as `merged`

#### Scenario: The board does not fetch
- **WHEN** the rail's or the board's refresh reads the team's kit
- **THEN** no fetch is run, and the bolt is read at `origin/bolt/b` as the host last fetched it

#### Scenario: A fetch that fails
- **WHEN** `crew bolts` runs and the fetch of the kit's origin on the team's host fails
- **THEN** the kit's stages read `unknown`, naming that GitHub could not be fetched and git's words, and nothing is read from the host's `bolt/b`

#### Scenario: A give fetches the branch it made
- **WHEN** `crew bolt give` has sluice make `bolt/b` on GitHub
- **THEN** the host holds `origin/bolt/b` at the commit sluice made it at before the give's plan write, and the team's next read reads the bolt there
