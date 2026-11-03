## RENAMED Requirements

- FROM: `### Requirement: A crossed team's work reads its stage from the runner's records`
- TO: `### Requirement: A started bolt's work reads its stage from the runner's records`
- FROM: `### Requirement: A crossed place's stage is where Flume's status has it`
- TO: `### Requirement: A launched place's stage is where Flume's status has it`

## ADDED Requirements

### Requirement: A bolt is created, dropped and landed through crew
`crew bolt new` SHALL add a bolt with its repo, goal and sources; `crew bolt order` moves it; `crew bolt drop` SHALL remove it and its units, or with `--requeue` queue them, and in either case SHALL drop each of the bolt's launches still standing in the drop's own commit, a requeued unit's among them, so a requeued unit is launched afresh once a bolt it is placed in is started. `crew bolt submit` SHALL submit its branch to its kit's main through sluice; `crew bolt land` SHALL remove a landed bolt and its units, and land and drop SHALL have sluice delete its branch, keeping and naming one holding work main lacks. No command SHALL give a bolt to a team.

#### Scenario: Landing too early
- **WHEN** `crew bolt land` runs while one of the bolt's units has not landed on main
- **THEN** it is refused, naming that unit

#### Scenario: The bolt's branch is deleted at its land
- **WHEN** `crew bolt land` runs for a landed bolt whose branch is on GitHub
- **THEN** the bolt leaves the plan, sluice deletes `bolt/<bolt>` from GitHub, and the branch is gone from the kit's host

#### Scenario: A delete sluice refuses
- **WHEN** `crew bolt land` runs and sluice refuses to delete `bolt/<bolt>` because a submission is still queued on it
- **THEN** the bolt leaves the plan, the branch stays on GitHub, and crew names it with sluice's words

#### Scenario: Dropping a bolt in flight
- **WHEN** the planner drops a bolt whose branch's tip main holds
- **THEN** the bolt and its units are gone from the plan, sluice deletes `bolt/<bolt>` from GitHub, and the branch is gone from the kit's host

#### Scenario: A dropped bolt holds work main lacks
- **WHEN** the planner drops a bolt into which a unit has merged that main does not hold
- **THEN** the bolt and its units are gone from the plan, sluice refuses the delete, the branch stays on GitHub and on the kit's host, and the drop names it as its unmerged work with sluice's words, the user's to keep or delete, and records it once

#### Scenario: The drop's host does not answer
- **WHEN** the planner drops a bolt while its kit's host does not answer
- **THEN** the drop names the host and the command, and the bolt is gone from the plan

#### Scenario: Requeuing a unit that has a place
- **WHEN** `crew bolt drop x "Later." --requeue` runs while unit `a` of started `x` has a launched place
- **THEN** `a` is in its repository's queue with no bolt or `After`, `x` is gone from the plan, and `requests.rec` gains a drop of `a`'s launch, in the drop's commit

#### Scenario: A give
- **WHEN** anyone runs `crew bolt give swb-1`
- **THEN** crew refuses it as no command it has, and the plan is unchanged

### Requirement: A unit's intent is amended through crew, its construct run again
`crew unit amend <unit> "<new intent>"` SHALL replace the unit's intent. A unit with a place SHALL also be marked amended, its construct run again with the new intent as the bolt's work is started, never handed to a team's host or told to a conductor. The command, direct or by an approval, SHALL answer once its write is made and wait on no agent (`code.9`). A unit merged into its bolt or landed SHALL be refused; run by the planner it SHALL be refused outside a proposal.

#### Scenario: A queued unit
- **WHEN** an amendment to a queued unit's intent is applied
- **THEN** the unit's intent is the new one, and nothing else changes

#### Scenario: A unit in code
- **WHEN** an amendment to a unit in code is applied
- **THEN** the unit's intent is the new one, the unit is marked amended, and the command answers once its write is made, naming no team, host or conductor

#### Scenario: A merged unit
- **WHEN** `crew unit amend` names a unit that has merged into its bolt
- **THEN** it is refused; what is needed is a fix or a new unit

### Requirement: A command reads each kit and the plan once, and fetches again only when refused
A crew command SHALL read each kit once and fetch the state branch once on each host it runs on, however many steps it has. A step that makes or removes a worktree in a kit SHALL leave the next step to read that kit again. A plan write SHALL start from the tip the command holds and fetch again only when its push is refused. The host's follower and `crew events --follow` SHALL check at each look whether what they read has moved, and read again only what has.

#### Scenario: Bolts with three units in flight
- **WHEN** `crew bolts` runs for a partition whose one bolt has three units in flight on one host
- **THEN** that host reads the kit once and fetches the state branch once, and `openspec` is not started

#### Scenario: A write after the plan moved
- **WHEN** another agent's write lands on the state branch after a command fetched it, and the command then writes
- **THEN** the command's push is refused, it fetches the new tip and applies its change there, as any write does

#### Scenario: Nothing is left behind
- **WHEN** a command ends, whether it succeeded or was refused
- **THEN** what it kept for its steps is gone, and the next command reads afresh

#### Scenario: A follower's look after nothing moved
- **WHEN** the host's follower looks again and nothing it read has moved
- **THEN** it reads no kit and fetches no branch at that look

### Requirement: A bolt on GitHub is fetched before crew bolts and a landing read it
As main is read (plan.18), crew SHALL read a bolt on GitHub as the host last fetched it on every read of a kit and every refresh of the rail and the board, fetching nothing. `crew bolts` and a landing's submission SHALL fetch the kit's origin first. A fetch that fails SHALL be named with git's words, never read past to the host's copy.

#### Scenario: crew bolts after a landing elsewhere
- **WHEN** a merge has landed on GitHub's `bolt/b` since the host last fetched, and `crew bolts` runs
- **THEN** it fetches the kit's origin once on the kit's host and shows the merged unit as `merged`

#### Scenario: The board does not fetch
- **WHEN** the rail's or the board's refresh reads the kit
- **THEN** no fetch is run, and the bolt is read at `origin/bolt/b` as the host last fetched it

#### Scenario: A fetch that fails
- **WHEN** `crew bolts` runs and the fetch of the kit's origin on the kit's host fails
- **THEN** the kit's stages read `unknown`, naming that GitHub could not be fetched and git's words, and nothing is read from the host's `bolt/b`

### Requirement: A bolt's work starts by crew bolt start
`crew bolt start <bolt>` SHALL make `bolt/<bolt>` through sluice from the kit's main, in the checkout the partition's main-level host keeps of the kit, mark the bolt `Path: flume` and request a launch of each unit and chore of it in its repository, with its `After` and priority and naming no host or stream, for a runner whose configuration names the repository to take, in one plan write, starting no agent, and record `bolt.start`. A proposal MAY hold it; the user runs it directly; no other agent SHALL. It SHALL be refused, with the plan unchanged and no branch made, while that host keeps no checkout of the kit or is held, or no runner answers for the partition.

#### Scenario: A bolt is started
- **WHEN** the user approves a proposal holding `crew bolt start b`, a bolt of switchboard-kit with two units, and a runner answers for wldn
- **THEN** `bolt/b` is made on GitHub by sluice, `b` is marked `Path: flume`, two launch requests name switchboard-kit and no host or stream, no agent starts, and the run record has `bolt.start` on `bolt/b`

#### Scenario: A partition no runner answers for
- **WHEN** `crew bolt start b` runs and wldn's state repository holds no runner's branch
- **THEN** it is refused, naming that no runner answers for wldn, the plan is unchanged and no branch is made

#### Scenario: An agent starts a bolt directly
- **WHEN** `wldn-ops` runs `crew bolt start b` outside a proposal
- **THEN** it is refused, naming the planner and the user, and the plan is unchanged

### Requirement: A fix names its bolt, and a fix of main its kit alone
`crew fix <bolt> <name> "<words>"` SHALL request a fix place on `bolt/<bolt>`, and `crew main fix <kit> <name> "<words>"` one on the kit's main, each in the kit's repository and naming no host or stream, for a runner whose configuration names it to take, in the stream its host maps it to. Neither SHALL take a team; `--drop` SHALL drop either's launch, and `crew fix` SHALL take no `--merge`, `--wait` or `--bolt`. A fix of main where no runner answers for the partition SHALL be refused, naming it.

#### Scenario: A fix on a bolt
- **WHEN** wldn-planner runs `crew fix b zone-check "the zone check fails on tenants with no region"`
- **THEN** a launch request of a fix on `bolt/b` names its kit's repository and the words and no host or stream, and no slot or agent of crew's is involved

#### Scenario: A team's name where the bolt goes
- **WHEN** an agent runs `crew fix swb-1 zone-check "<words>"` and no bolt is named `swb-1`
- **THEN** it is refused, naming no bolt `swb-1`, and nothing is requested

### Requirement: A unit's stage is read from the runner, or from the plan before its bolt starts
crew SHALL read each unit's and chore's stage from the plan and the runner's records alone, never from a place in the kit: `queued` while it has no bolt; for a bolt not started, `ready`, or `waiting` while it names `After` work, which builds only once the bolt starts; for a started bolt, as "A started bolt's work reads its stage from the runner's records" and "A launched place's stage is where Flume's status has it" give it, `landed` once main holds its change, open or archived, or a chore's trailer; and `unknown`, naming why, where crew cannot read what it rests on. Nothing SHALL be kept by hand to say how far work has got.

#### Scenario: Queued work
- **WHEN** a unit has no bolt
- **THEN** its stage is `queued`

#### Scenario: A bolt not started
- **WHEN** bolt `y` is planned and not started, unit `a` names no `After` and `b` has `After: a`
- **THEN** `a` reads `ready` and `b` `waiting`, and nothing of a runner or a place in the kit is read for them

#### Scenario: Nothing kept by hand
- **WHEN** `x` is started and deneb's runner reports `a`'s place in code with 6 of 26 tasks ticked
- **THEN** `crew bolts` shows `a` at `code 6/26`, and no file was edited to say so

#### Scenario: A worktree of crew's from before
- **WHEN** a `unit/a` worktree from before teams left stands under the kit's `places/` with every task ticked, and `x` is started
- **THEN** `a`'s stage is the runner's, and nothing of that worktree is read for it

## MODIFIED Requirements

### Requirement: The file's order and dependencies are the plan
A bolt's units SHALL be ordered by the file: a bolt's launches SHALL take their priority from the order the bolts appear, and a unit is ahead of every unit after it in its bolt. A unit's `After` SHALL name units or chores of the same bolt that it builds on. Its launch SHALL be held by the runner until each of them has landed on the bolt, so its place is cut from a bolt that holds their work, as bolt-teams "A dependent launches once its After work has landed" has it. A unit with no `Bolt` SHALL be queued work.

#### Scenario: A dependency still in construct
- **WHEN** unit B of started bolt `x` has `After: A`, and A's construct has not committed
- **THEN** B's stage is `waiting` on A, and its launch is held

#### Scenario: A dependency constructed
- **WHEN** unit B has `After: A`, and A's change is committed while A is in code
- **THEN** B still waits on A, its launch held until A has landed on `bolt/x`

#### Scenario: A dependency not yet merged
- **WHEN** unit B has `After: A`, and A has not landed on `bolt/x`
- **THEN** no place of B's is launched, so nothing of B's merges into the bolt before A

#### Scenario: Queued work
- **WHEN** a unit is added with no bolt
- **THEN** `crew bolts` lists it under the queue of its repo

### Requirement: A flywheel keeps one plan in its state repository
Each flywheel SHALL keep one plan, the recutils file `plan.rec` on its branch of its state repository, for all of its kits. The plan SHALL hold only Bolt and Unit records. A Bolt has its name, repo, goal and sources. A Unit has its name, repo, bolt, intent, sources and dependencies (`After`); a Unit record marked `Kind: chore` is a chore, whose intent is its words. The plan SHALL hold what is meant to be built and any hold on it, never how far the work has got. A Bolt record that still carries a `Team` field, written before teams left, SHALL be read as any bolt, the field read by nothing; a new branch's schema SHALL allow no `Team`.

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

#### Scenario: A bolt given before teams left
- **WHEN** `plan.rec` holds a Bolt record with `Team: swb-1`, and its branch's schema allows the field
- **THEN** `recfix --check` passes, `crew bolts` shows the bolt with no team, and the next write leaves the field as it is

#### Scenario: A new branch
- **WHEN** `crew state init` starts a flywheel's branch
- **THEN** its `plan.rec` declares no `Team` field and its `proposals.rec` no `Agreed` field

### Requirement: What is in flight can be read from anywhere
`crew bolts [<bolt>] [--json]` SHALL list each of the partition's bolts with its repo, its kit's host and its state, each unit's and chore's stage and place, the fixes in flight on it, and the queue. Bolts with no work started, and queued work, SHALL be listed without reaching any host. Each host holding a bolt's work SHALL be read once. No line SHALL name a team.

#### Scenario: A host is unreachable
- **WHEN** the box is asleep
- **THEN** its bolts are listed from the plan, with every stage shown as unknown and the host named

### Requirement: A bolt on GitHub is read where it lives
crew SHALL read a bolt at GitHub's copy of its branch, `origin/bolt/<bolt>`, when the host holds that copy and the policy in it names a remote for the bolt, and otherwise at the host's own `bolt/<bolt>`. Its head, verification, the changes and chores it holds, and every stage read from it SHALL come from that ref. crew SHALL never read a bolt on GitHub from the host's own `bolt/<bolt>`, sluice's copy, whether or not sluice has levelled it.

#### Scenario: A merge landed on GitHub while the host's copy stayed behind
- **WHEN** sluice lands a unit's merge and a chore's merge on GitHub's `bolt/b`, the host has fetched it, and the host's own `bolt/b` is still at the commit before them
- **THEN** the unit and the chore read `merged`, the bolt's head is GitHub's, and its verification is the verdict at that head

#### Scenario: A proven bolt whose copy lags
- **WHEN** every unit of a bolt on GitHub has merged and the `Sluice-Result` at GitHub's head starts `passed`, while the host's `bolt/b` is at an earlier landing
- **THEN** the bolt reads proven, and its row on its kit's landings card is offered

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

### Requirement: A started bolt's work reads its stage from the runner's records
For every unit, chore and fix of a bolt marked `Path: flume`, a bolt started by `crew bolt start`, crew SHALL read its stage from its newest launch not dropped, that launch's answer and its place's record on the runner's branch, never from a place in the kit: unknown where its host was not read or it has no launch, launching before an answer, waiting while held for its After work, refused with the runner's words. `crew bolts` and every decision that reads a stage SHALL read the same.

#### Scenario: A dependent waits
- **WHEN** `b`'s launch is answered held, `a`'s place not yet landed
- **THEN** `crew bolts` shows `b` waiting on `a`

#### Scenario: The runner's host is silent
- **WHEN** deneb's runner branch can't be read
- **THEN** every piece launched on deneb reads unknown, and `crew bolts` names deneb

### Requirement: A launched place's stage is where Flume's status has it
Once launched, a unit, chore or fix SHALL read queued while Flume waits for room; construct, code with its ticked tasks of all, or verify while a stage runs; needing an answer with the agent's question when it stopped short asking; its stage, sent back, with sluice's words when a submission failed or conflicted; submitted with sluice's number; waiting on its caller with Flume's words past its bound; stalled; merged once it has landed on its bolt and landed once its bolt has; or dropped.

#### Scenario: A unit in code
- **WHEN** deneb's runner record for `a`'s launch carries Flume's status of its place in code with three of seven tasks ticked
- **THEN** `crew bolts` shows `a` at `code 3/7`

#### Scenario: A construct that asked
- **WHEN** the runner's record shows `a`'s construct stopped short with "Which partition's rail?"
- **THEN** `crew bolts` shows `a` as needing an answer, with the question

#### Scenario: Sent back by sluice
- **WHEN** the runner's record shows `b`'s place back in code after sluice found its submission in conflict on `plugin/lib/plan.py`
- **THEN** `crew bolts` shows `b` in code, sent back, with sluice's words

#### Scenario: Landed on the bolt
- **WHEN** the runner's record shows `a`'s place landed on `bolt/x`, and `x` has not landed
- **THEN** `crew bolts` shows `a` merged

## REMOVED Requirements

### Requirement: A unit's stage is read from the kits
**Reason**: Record 0047 move 5: crew reads no stage from a place in the kit; a started bolt's stages are the runner's, and a bolt not started reads only `ready`, `waiting` or `unknown`. The ladder of `amended`, `construct`, `planned`, `code` and `verify` read from a place's tasks and planning leaves with the places crew made.
**Migration**: "A unit's stage is read from the runner, or from the plan before its bolt starts", added by this change; a launched place's tasks are Flume's status's ("A launched place's stage is where Flume's status has it").

### Requirement: A conductor hears about writes to its bolt
**Reason**: Record 0047 move 5: no conductor stands; a bolt's work is launched and moved on by the crossed path, which reads the plan at each launch.
**Migration**: None: the plan is read where it is needed (`state.4`).

### Requirement: A bolt is created, given, dropped and landed through crew
**Reason**: Record 0047 move 5: no bolt is given to a team; `crew bolt give` and its scenarios leave.
**Migration**: "A bolt is created, dropped and landed through crew", added by this change.

### Requirement: A unit's intent is amended through crew
**Reason**: Record 0047 move 5: no construct is handed to a team's host and no conductor is told; `crew unit wait` leaves.
**Migration**: "A unit's intent is amended through crew, its construct run again", added by this change.

### Requirement: A command reads each kit and the plan once
**Reason**: Record 0047 move 5: its scenarios of `crew status`, `crew unit run` and a stage wait leave with those commands.
**Migration**: "A command reads each kit and the plan once, and fetches again only when refused", added by this change.

### Requirement: A bolt on GitHub is fetched where a decision rests on it
**Reason**: Record 0047 move 5: its give and stage-wait fetches leave with the give and the wait.
**Migration**: "A bolt on GitHub is fetched before crew bolts and a landing read it", added by this change.
