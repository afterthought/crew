# crew

Bolt teams of Claude agents, run in herdr, and each partition's main level above them.

- The teams and partitions are data in `~/.config/crew/teams.json` (version 2), written by the machine's configuration (in swancloud, `lib/crew-teams.nix`). Hosts, sessions, each session's partition and the repos of its space come from `~/.config/swancloud/herdr-hosts.json`.
- `plugin/` is the same for every team: the roles (`roles/`, each an agent definition naming its model and effort), the `crew` and `crew-role` commands (`bin/`), the builder that turns the teams file into briefs and settings (`lib/crew.py`), the plan (`lib/plan.py`, with `lib/gather.py`, which reads a host's kits, and `lib/transcript.py`, which checks a signal's excerpt against its agent's transcript), `crew sites` (`lib/sites.py`), and the skills. It installs as a Claude Code plugin; this repository is its marketplace.

## Teams

```
crew list
crew status   [team]
crew up|down|rebuild|close <team>
crew restart|resume <team> [conductor|ops]
crew clear    <team> conductor|ops
crew unit run <unit> construct|code|verify|merge ["<words>"]
crew unit free <unit> [--team <team>]
crew fix      <team> <name> "<what is wrong>"
crew fix      <team> <name> --merge
crew fix      <team> <name> --wait [--timeout <ms>] [--stuck <ms>]
crew prove    <team> ["<words>"]
crew prove    <team> --wait [--timeout <ms>] [--stuck <ms>]
crew needs    "<what you tried and what you need>"
```

A team builds one **bolt** at a time: a body of work on `bolt/<bolt>`, in `<kit>/bolts/<bolt>`, deployed and tested from that branch and then landed on main. Its standing roles are the **conductor** and **ops**. A bolt is built from **units**, each one OpenSpec change on `unit/<unit>` in `<kit>/places/<unit>`, taken stage by stage: construct writes the change, the user reviews and approves it (`crew unit approve`), code builds it, verify checks it, and merge merges it into the bolt with `wt merge bolt/<bolt> --no-squash --no-remove`. Each stage is a fresh agent at that stage's effort, in one of the team's `units` slots. Construct can be run again with the user's words at any stage before the unit merges: run on a unit that is approved, in code or in verify, it marks the unit amended in the plan, and code, verify and merge are refused until the user has approved the change written again, which clears the mark. A merged unit is not amended: a defect in it is a fix, and a new need a new unit. A **fix** is built the same way on `fix/<bolt>/<name>` from the bolt, in `<kit>/places/fix-<bolt>--<name>`, with no change and no plan record; a fix name already in use on the bolt is refused. Every worktree crew made goes, with its branch, once its work is over: a bolt's once no plan has it (landed or dropped), a unit's once it has merged into its bolt or landed or no plan has it, and a fix's once it has merged into its bolt or no plan has its bolt; when a removed branch held commits of its own, crew says the commit it was at. Each time crew reads a team (`crew status <team>`, `crew unit run`, `crew fix`) it frees every slot whose unit or fix has merged or been dropped, or whose unit has left the team's bolt (queued again by `crew bolt drop --requeue`, or moved to another bolt), once the slot's agent is not working, then removes every such worktree in the team's kit checkout that no slot holds, whatever left it there. `crew bolt drop`, `crew unit drop` and `crew bolt land` do the same on the team's host right after they change the plan; when that host doesn't answer, the team's next read does it. A worktree with uncommitted changes (modified files, or untracked files git doesn't ignore) or a lock is kept with its branch, and every read names it until it is clean, when crew removes it, or gone; ignored files, such as installed dependencies, never keep one. crew removes only worktrees directly under `<kit>/bolts/` or `<kit>/places/` on a `bolt/`, `unit/` or `fix/` branch it names, never the main checkout, a worktree made by hand or a detached one, and nothing while a plan the kit's work goes in can't be read. `crew rebuild` frees those slots too, its agents ended with the rest, and keeps only the slots of work still in flight on the bolt. `crew unit free <unit>` frees a slot still holding a dropped unit, or one no longer in the team's bolt, at once, and refuses a unit still in it.

A stage ends at what it delivers, read in the kit or on the team's host, never when its agent goes quiet: construct's change committed since the stage began, its planning complete; code's commit since it began, with every task ticked at the branch's head; verify's report for the unit saved since it began in the team's reports folder, `~/.local/state/<team>-team/reports`; merge's bolt holding the unit's change or the fix's commits; a fix's commit on its branch since it began; and ops's proof file. When a stage began is the time at the front of its start's entry id. `crew unit wait <unit>`, `crew fix <team> <name> --wait` and `crew prove <team> --wait` run on the team's host and return with one line: the stage delivered, once its agent has stopped working, with what it delivered, and its end recorded; it stopped short, with what its agent needs in the agent's words; it is stuck, its agent quiet past `--stuck` (15 minutes) with nothing delivered, nothing said and no background work of its own still running, which crew reads from the agent's Claude transcript (when it can't, the clock runs and the line says what could not be read); its agent is gone; or it is still running when `--timeout` (an hour) passes, its agent working or waiting on work of its own. Only a delivered end is recorded by a wait. `crew needs "<what it needs>"`, run by a stage's agent, or by ops during a proof, ends the stage short: crew records the end without the words and gives them to the conductor, as the answer of a wait running on the stage, else in a tell marked as from the agent; anyone with no stage owed is refused. The answer comes back as the stage run again with it as its words. `crew prove <team>` asks the team's ops, in a tell marked as from the caller, to deploy the bolt and work each unit's *Proof in dev* list, and owes the proof's end like a stage's; ops writes its results once, whole, to `proof-<bolt>-<YYYYMMDD-HHMM>.md` in the team's reports folder. It is refused while the team holds no bolt or its ops is not up; a proof still owed ends as stopped when another is asked for, or when ops is restarted or taken down.

A team is two herdr workspaces in its session: `<team>`, with a `conductor` tab (the conductor and ops, started in the worktree of the bolt the team holds) and, when the team's host is a Mac, a `git` tab (gitgui in the kit and the blueprints repo; gitgui is unusable over ssh), and `<team> units`, one tiled pane per slot in flight, which exists only while a unit or fix is. A team sits whole on one host, and its panes and state live there: a command about a team run anywhere else is run on the team's host, over ssh, by the crew checkout that host's sessions keep.

## The plan

```
crew bolts [<bolt>] [--label L] [--json]
crew bolt  new <bolt> "<goal>" --repo <kit> [--source S]... [--before <bolt>]
crew bolt  give <team> [<bolt>]
crew bolt  order <bolt> --before <bolt>|--first|--last
crew bolt  drop <bolt> "<reason>" [--requeue]
crew bolt  land <bolt>
crew unit  add <unit> "<intent>" --bolt <bolt>|--repo <kit> [--source S]... [--after U]... [--before U] [--signal ID] [--unblocks <bolt>]
crew unit  split <unit> "<narrowed intent>" --into <unit> "<intent>"
crew unit  amend <unit> "<new intent>"
crew unit  order <unit> --before <unit>|--first|--last
crew unit  after <unit> <unit>...|--none
crew unit  move <unit> <bolt>|queue [--unblocks <bolt>]
crew unit  drop <unit> "<reason>"
crew unit  approve <unit>
```

Each partition keeps one recutils `plan.rec`, for all its kits, on its flywheel's branch of its state repository (see State). It holds only intent: Bolt and Unit records, in build order. A Source is a path in the partition's first blueprints repo, or `<owner>/<name>:<path>` in another. Every stage is read from the kits, one call per host. A write fetches the branch over https into crew's bare cache of the repo (`~/.cache/crew/git/<owner>/<name>.git`), applies itself to the tip, checks each file it changed with `recfix --check` and the plan with crew's rules, commits through a temporary index, and pushes without force; a push refused because someone wrote first is applied again to the new tip, up to five times. Nothing is ever merged. A write that touches a bolt a team holds sends that team's conductor the commit's subject.

A unit's stage, as `crew bolts` shows it and `--json` gives it in `stage`, is the first that holds of `landed` (main has its change), `merged` (its bolt has it), `verify` (every task ticked), `code` (some ticked), `approved` (its planning complete and approved since the bolt), `review` (its planning complete), `construct` (its worktree exists), and `ready` or `waiting` by its `After` units; a unit with no bolt is `queued`. A unit the plan marks `Amended` reads, after `landed` and `merged`, `amended` until construct is run again, then `construct` until that commits, then `review`, whatever its tasks say, so a change written again is reviewed again before it is built. `crew unit approve` clears the mark.

A unit in flight is amended in one of two ways, and both end in the user's review of its change. How it builds what it builds changes when its conductor runs construct again with the user's words (see Teams). What it builds changes with `crew unit amend <unit> "<new intent>"`, which the user runs at a shell and the planner only inside a proposal: it replaces the unit's intent, and a unit that has a worktree is marked amended (`intent`, or `proposal/<n>` from an approval) and its conductor told to run construct again, whose agent is told the intent was amended. A unit that has merged is refused: a defect in it is a fix, and new work is a new unit.

`crew bolt drop` removes a bolt and its units from the plan, or with `--requeue` queues its units, which it refuses while one of them has a worktree, since a queued unit has none. `crew bolt land` removes a bolt whose units have all landed on main. Either way the bolt's worktrees then go from its team's host (see Teams), and a landing whose worktree is kept for uncommitted changes still lands.

## Proposals

```
crew plan propose <file> [--replaces <n>]
crew plan proposed [<n>] [--label L] [--json] [--open]
crew plan agree <n> [--team <team>]
crew plan approve <n>
crew plan drop <n> "<reason>"
```

The planner changes the plan only by a **proposal** the user approves: where new work goes (a new bolt, a unit in a bolt, the queue), and every move, split, amendment, reorder or drop. A proposal is a record in `proposals.rec` on the flywheel's branch: the planner's `Case`, and the plan commands it would run, in order, one `Do` each, as typed without the leading `crew` (`bolt new|order|drop`, `unit add|amend|move|split|order|after|drop`). Proposals are numbered, and never removed or changed.

- `crew plan propose <file>` takes a file of one record, a `Case` and its `Do` lines. Each command is checked in order against the plan as the ones before it leave it, with every refusal it has run directly; a refused command refuses the proposal and nothing is written. The conductor of each bolt in flight the proposal touches is told. `--replaces <n>` drops proposal n and writes its successor in one commit.
- `crew plan proposed` lists the open proposals and what each waits on; `crew plan proposed <n>` prints one as markdown: the case, then each change in plain words, a unit's intent beside what it rests on (a signal's assertion and excerpt) and the goal and team of the bolt it would join, and an amended unit's bolt, team and stage, its intent as it stands and as proposed, and what approval sets in motion; under each change, the command approval runs; and, for an open proposal, who it waits on, in words. It reads only the branch, so any host can answer. With `--open`, it writes that page to `~/.local/state/crew/proposals/<label>-<n>.md` on the host it runs on and opens it in plannotator, for the user to read and annotate: beside the caller in herdr, inline in the terminal otherwise.
- `crew plan agree <n>` is a conductor's recorded agreement to a proposal that touches the bolt its team holds; the user may agree for any team it touches.
- `crew plan approve <n>` applies the proposal's commands, exactly as read, to the plan at the tip and closes the proposal, in one commit, or changes nothing when one no longer applies or a touched bolt's conductor has not agreed. A unit with a worktree that moves is rebased before the push and put back if the approval is refused. The user runs it, or an agent on the user's word.
- `crew plan drop <n> "<reason>"` closes a proposal unapplied, with the reason.

Work a bolt in flight needs before it can be proven or land goes into that bolt: a `unit add` or `unit move` marked `--unblocks <bolt>` must place the unit in that held bolt, where it goes ahead of the first unit not yet merged, and the mark is shown on the proposal.

Who writes the plan directly, when the command runs as an agent crew started (`CREW_AGENT`):

| Agent | Writes directly | Otherwise |
|---|---|---|
| the user at a shell | everything | |
| `<label>-planner` | proposals | refused, naming `crew plan propose` |
| `<team>-conductor` | `unit split`, `unit order`, `unit after` on units of the bolt its team holds, and the amended mark `crew unit run <unit> construct` sets on one; `plan agree` | refused, naming the planner |
| `<label>-design` | `unit add … --repo <kit>`, the queue | refused, naming the planner |
| `<label>-dispatch-<host>` | `bolt give` | refused, naming the planner |
| `<label>-ops` | `bolt land` | refused, naming the planner |
| any other agent | nothing | refused, naming the planner |

Every refusal is a run-record entry. Writing, agreeing, approving and dropping a proposal are entries naming `proposal/<n>`, and each change an approval applies is an entry of its own, from the proposal, with the approval's commit; `crew trace` follows them.

## State

```
crew state init <label>
```

A partition's **flywheel** is its loop, named by its label. Its state is the files on one branch, `<label>/main`, of the state repository the teams file names for it (`state`, one per organisation, such as `WilldanGroup/crew-state`), apart from the design:

- `plan.rec`, the plan;
- `moves.rec`, every signal's one move;
- `proposals.rec`, the planner's proposals;
- `signals/<capture>/`, the captures and signals recorded through crew (see Signals);
- `runs/<host>/<YYYY-MM-DD>.rec`, the run record each host has carried.

Flywheels sharing a repository never meet: each command fetches and pushes only its own flywheel's branch, and no branch shares history with another. A write that changes several files is one commit, and its message ends with a `Crew-Entry:` trailer naming the run-record entry that describes it. `crew state init <label>` creates the branch: it adopts the first blueprints repo's `plan/<label>` with its history where there is one, joins another blueprints repo's `plan/<label>` in one commit naming where it came from, and copies the first blueprints repo's `signals/moves.rec`; run again, it finishes what a stopped run left, or says the branch exists. A clone of the branch reads with `recsel` and nothing else.

## Signals

```
crew signal <slug> "<what it asserts>" --excerpt "<the words, verbatim>"|--excerpt-file <path> [--kind K] [--subject a,b]
crew signal show <id>
crew signal move <id> attach|challenge|new-territory|answered|drop [--target T] [--reason R]
```

A **signal** is one thing noticed, with the words that show it, in the shape the blueprints' `signals/README.md` gives: a directory per capture, holding `capture.md` and one file per signal. Signals have two homes. What the agents and the user record with `crew signal` is under `signals/` on the flywheel's branch of its state repository; what the daily pass reads from meetings and channels stays under `signals/` in the partition's first blueprints repo. An id is unique across both, and every command looks it up on the flywheel's branch first.

An agent crew started gives an **excerpt**: the words that show the finding, copied as its session received them, from the user or from a tool's output (`--excerpt-file` for words the shell would mangle). crew looks for them, whitespace aside, in the agent's own Claude transcript, `~/.claude*/projects/*/<session>.jsonl` for the session herdr names for the agent, and records a grade on the capture:

- `verified`: the words are in a record the session received, and the capture says who asserted them: `user`; `tool`, for a command's output; `agent:<name>`, for what another agent sent with `crew tell`; or `crew`, for crew's own notice;
- `found`: they are in the transcript, in a record crew cannot classify;
- `unverified`: crew could not read the transcript, and the capture says why: herdr names no session, there is no file, its lines are not JSON, or it has not been written for 15 minutes, so crew may be reading another session's.

A signal is refused only when the transcript is the live session's, its last record written within 15 minutes, and the words are nowhere in it but in what the agent wrote itself: a paraphrase. A change in Claude Code's format lowers a grade and never stops a capture, and no command refuses anything for its grade; the grade is shown wherever the excerpt is.

A capture is the one record the excerpt came from. Its `capture.md` names the host, the Claude session, the record and its time, who asserted it, and where the agent was working: its team, the bolt the team holds and the unit its slot holds, or the main level. The record itself is copied to `~/.local/state/crew/<label>/raw/<capture>.jsonl` on the host, and the capture points at it as `<host>:<path>`; of the source, only the excerpt enters git. A second signal from the same record joins its capture as its next signal, and the same signal again writes nothing. The capture and its signal are one commit on the flywheel's branch. The user's own note, `crew signal` at a shell, is its own excerpt (`excerpt: own`), of kind `ask` unless another is given.

`crew signal show <id>` prints a signal, its capture's fields (the grade, who captured it, where and when, the session and the raw record) and its move, from any host. Curation's moves, `crew signal move`, are appended to `moves.rec` on the flywheel's branch, and a signal becomes work only through its `route` move, which `crew unit add --signal` writes in the same commit as the unit. Each signal has one move, and nothing is ever merged.

What crew sends an agent is marked as crew's: `crew tell` sends `[crew tell from <sender>] <text>`, the sender being the agent or `<user>@<host>`, and crew's greetings and notices send `[crew] <text>`, so neither is taken for the user's typing.

## The main level and the operator agent

```
crew main     up|down|status <label>
crew operator up <label>
crew rail     [--label L]
crew revive
crew tell     <agent> "<text>"
crew sites    [<label>] [--json]
```

Each partition has a main level in the session the teams file names: the **design agent** (elaboration on main and curation of signals), the **planner** (the only writer of bolts and placements) and the main-level **ops** (lands proven bolts and deploys main), as tabs of the `<label>` workspace; and a **dispatcher** on each host the partition's teams run on, in `<label> dispatch`, which gives that host's teams their bolts. The **operator agent** stands in each operator session (the session named `<label>`), started there with `crew operator up <label>`, and works for the user. `crew tell` prompts any of these agents by name, wherever it runs, marked with who sent it.

`crew rail` lists everything that waits on the user, from any host, in four groups, always in this order: open proposals, units in review, verify reports the user hasn't answered, and bolts whose every unit has merged, waiting to land. Each row says what waits, when it began to wait and how long ago that was, and carries the commands that answer it, written to be pasted; within a group, the oldest comes first. A proposal waits from its entry in the run record (or the day it was opened), a unit in review from its branch's last commit, a verify report from when it was written, once it is newer than that commit, and a bolt from its last merge. Every row and every time is read from the plan, the proposals, the kits and the run record, and nothing is kept by hand: a row leaves the list as soon as its answer is recorded. A host that doesn't answer is named. `crew operator up` also opens a `rail` tab in the `operator` workspace, beside `flow`: the list above, printed again every 30 seconds and as soon as the run record gains an entry, and a shell below with crew on its path, to paste a row's command into.

Each row of the rail is also answered through one **Pending You** card, posted by the agent that owns its decision: the planner's for each proposal it opens, and a team conductor's for each of its units in review, each verify report the user decides on, and its bolt once proven. The landing card is marked high stakes, so it is approved only by holding the button in the Pending You app, never with a key in Herdr's popup. Answering a card wakes its owner, which acts on the user's word and closes the card with what it did; when crew records a change that ends a row, it names the row's card to its owner, in the command's output when the owner made the change and by a tell otherwise. Under each row's commands, `crew rail` prints the row's card key (`proposal/<n>`, `review/<unit>/<head>`, `verify/<unit>/<stamp>` or `land/<bolt>`) and whether a card with that key is open, and who asked it; after the groups, it lists each open card whose row is gone, oldest first, with a `crew tell` asking its owner to close it. crew learns of the cards from its agents' own sessions: its PostToolUse hook records each card a crew agent posts, updates, withdraws or closes in the run record, with the card's id and key and nothing written on the card. A partition or host without Pending You keeps the rail as it is, and its conductors tell the operator agents of every wait instead.

A herdr server that restarts resumes each agent in its saved pane folder, which is the folder crew moved the pane to before starting the agent, since Claude finds a conversation only from the folder it began in. crew's SessionStart hook gives a resumed agent its name and identity back. An agent that never had a message has no conversation to resume, so its pane comes back as a shell: `crew revive`, run on a host after a restart, brings back each standing agent of that host whose pane came back empty, from its last conversation or fresh, and leaves a team or main level taken down with `crew down` as it is. `crew sites` lists each host's bolts, units and fixes with the URL of each running dev server, named by swancloud's `devurl` and found among the host's portless routes.

## Seeing what happened

```
crew events [--label L] [--about <object>] [--since <time>] [--follow] [--json]
crew events --push [--label L]
crew trace  <object>
crew unit wait <unit> [--timeout <ms>] [--stuck <ms>]
```

Every crew command that moves work appends one entry per act, after the act, to the **run record** of the partition it acts for, on the host where it ran: `~/.local/state/crew/<label>/runs/<host>/<YYYY-MM-DD>.rec`, one recutils file per UTC day, each entry one write, never rewritten. An entry holds:

- `Id`, `At` (UTC) and `Host`, where crew ran;
- `By`, the agent crew started that asked (`CREW_AGENT`), or `<user>@<host>`, and `Session`, that agent's Claude session as `<host>:<id>`, carried with a command crew runs again on another host;
- `Act`, such as `unit.add`, `bolt.give`, `stage.start`, `stage.end`, `tell`, `team.up` or `agent.restart`, and the card acts crew's hook writes, `card.post`, `card.update` and `card.close`;
- `On`, each object acted on, and `From`, each object it came from, as typed names: `unit/<unit>`, `bolt/<bolt>`, `queue/<kit>`, `signals/<id>`, `team/<team>`, `agent/<name>`, `stage/<unit>/<stage>`, `stage/<bolt>/proof`, `fix/<bolt>/<name>`;
- `Commit`, `<owner>/<name>@<sha>`, when the act wrote one, and `Why`, the subject crew composed from the names of things;
- `Refused`, crew's reason, when a command that would have moved work was refused;
- a stage's end's `Result` (the stage the unit reached), `Tasks`, `Head` (the unit's, fix's or proven bolt's branch head), `Ended` (`delivered`; `short`, when its agent said what it needs through crew; or `stopped`, when crew ended its agent first), `Delivered`, what it delivered as an object (`unit/<unit>@<head>`, `fix/<bolt>/<name>@<head>`, `bolt/<bolt>@<head>`, `report/<file>` or `proof/<file>`), and `Observed: late` when nobody waited for it, a tell's `Chars`, `Amended: yes` on the start of a construct that marked its unit amended, whose `Commit` is the plan's, and a card act's `Card` (the Pending You card's id) and `Key` (its rail row's card key), on the row's object, or on `agent/<name>` for a card with no row key.

No entry holds text anyone typed: not a tell's text, what a stage's agent said it needs, an intent, a goal, a reason or an excerpt. A read writes nothing, and a record that can't be written is said on standard error and changes nothing about the command. `recsel -t Entry` reads the files with no crew involved.

Every write to the flywheel's branch also carries the host's uncarried entries there, to `runs/<host>/`: each day's file on the branch becomes the union by `Id` of what it had and what the host has, so a host only ever adds to its own files, and one that is asleep or rebuilt loses nothing it had carried. `crew events --push` carries in a commit of its own, and makes none when nothing is left. `crew events` reads the branch, then gathers what every host the partition runs on (its teams', its main level's and its operator sessions') has not yet carried, one call per host, and prints them in time order, naming a host that does not answer, whose entries are shown as far as it had carried them; `--follow` prints them as they are written, and the operator workspace's `flow` tab runs it. `crew trace <object>` prints one bolt's, unit's or signal's history from the entries alone: what was done, by whom, with which commit, what it came from and what came from it, each line with the `zoe <session>` to open on its host. A bare name is tried as a unit, then a bolt, then a signal; `report/<file>` and `proof/<file>` find the end that delivered them. `crew unit wait <unit>` waits on the team's host for the unit's stage to end at its deliverable and records that end. An end nobody waited for is recorded, once and marked late, the next time crew reads the team, but only once its deliverable is there: a stage whose agent has only gone quiet has no end. A stage whose agent crew ends first, to run it again or to free its slot, is recorded `delivered` when its deliverable is there, else `stopped`; one stopped short is recorded by `crew needs` itself.

## Roles

| role | definition | model | effort |
|---|---|---|---|
| design agent | `design.md` | Fable 5.1 | xhigh |
| planner | `planner.md` | Fable 5.1 | xhigh |
| conductor | `conductor.md` | Opus 5.5 | high |
| ops, team and main level | `ops.md`, `main-ops.md` | Opus 5.5 | high |
| unit: construct | `construct.md` | Opus 5.5 | high |
| unit: code, merge; fix | `coder.md` | Opus 5.5 | xhigh |
| unit: verify | `verify.md` | Opus 5.5 | high |
| dispatcher | `dispatcher.md` | Opus 5.5 | medium |
| operator agent | `operator.md` | Opus 5.5 | medium |

A definition's frontmatter names its model and effort; a team or a partition overrides either in the teams file under `roles.<definition>`. `crew-role` starts each role with them and appends the definition's body, filled from the teams file, to Claude Code's own system prompt. `python3 plugin/lib/crew.py brief <team|label> <definition>` prints a brief.

## Needs

`herdr`, `jq`, `python3`, `git`, and `recutils` for the plan; in each kit `wt`, `moon` and `openspec`; `devurl` and `portless` for `crew sites`. `devenv.nix` declares `jq`, `python3` and `recutils`.

`tests/run` runs crew's tests on stub `herdr`, `ssh` and `claude`, each simulated host with its own scratch home, so no test reaches a real session, host or agent: `devenv shell -- tests/run`. `CREW_TEST_LIVE=1` adds the live `crew sites` check on mac-studio.
