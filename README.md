# crew

Bolt teams of Claude agents, run in herdr, and each partition's main level above them.

- The teams and partitions are data in `~/.config/crew/teams.json` (version 2), written by the machine's configuration (in swancloud, `lib/crew-teams.nix`). Hosts, sessions, each session's partition and the repos of its space come from `~/.config/swancloud/herdr-hosts.json`.
- `plugin/` is the same for every team: the roles (`roles/`, each an agent definition naming its model and effort), the `crew` and `crew-role` commands (`bin/`), the builder that turns the teams file into briefs and settings (`lib/crew.py`), the plan (`lib/plan.py`, with `lib/gather.py`, which reads a host's kits), `crew sites` (`lib/sites.py`), and the skills. It installs as a Claude Code plugin; this repository is its marketplace.

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
```

A team builds one **bolt** at a time: a body of work on `bolt/<bolt>`, in `<kit>/bolts/<bolt>`, deployed and tested from that branch and then landed on main. Its standing roles are the **conductor** and **ops**. A bolt is built from **units**, each one OpenSpec change on `unit/<unit>` in `<kit>/places/<unit>`, taken stage by stage: construct writes the change, the user reviews and approves it (`crew unit approve`), code builds it, verify checks it, and merge merges it into the bolt with `wt merge bolt/<bolt> --no-squash --no-remove`. Each stage is a fresh agent at that stage's effort, in one of the team's `units` slots. A **fix** is built the same way on `fix/<name>` from the bolt, with no change and no plan record. A merged unit's or fix's slot is freed, and its place removed, the next time crew reads the team. A unit dropped from the plan (`crew unit drop`) has its slot freed and its worktree and branch removed at once, unless its stage is still working or its worktree has uncommitted changes; `crew unit free <unit>` frees such a slot later, and refuses a unit the plan still has.

A team is two herdr workspaces in its session: `<team>`, with a `conductor` tab (the conductor and ops, started in the worktree of the bolt the team holds) and, when the team's host is a Mac, a `git` tab (gitgui in the kit and the blueprints repo; gitgui is unusable over ssh), and `<team> units`, one tiled pane per slot in flight, which exists only while a unit or fix is. A team sits whole on one host, and its panes and state live there: a command about a team run anywhere else is run on the team's host, over ssh, by the crew checkout that host's sessions keep.

## The plan

```
crew bolts [<bolt>] [--label L] [--json]
crew bolt  new <bolt> "<goal>" --repo <kit> [--source S]... [--before <bolt>]
crew bolt  give <team> [<bolt>]
crew bolt  order <bolt> --before <bolt>|--first|--last
crew bolt  drop <bolt> "<reason>" [--requeue]
crew bolt  land <bolt>
crew unit  add <unit> "<intent>" --bolt <bolt>|--repo <kit> [--source S]... [--after U]... [--before U] [--signal ID]
crew unit  split <unit> "<narrowed intent>" --into <unit> "<intent>"
crew unit  order <unit> --before <unit>|--first|--last
crew unit  after <unit> <unit>...|--none
crew unit  move <unit> <bolt>|queue
crew unit  drop <unit> "<reason>"
crew unit  approve <unit>
```

Each partition keeps one recutils `plan.rec`, for all its kits, on its flywheel's branch of its state repository (see State). It holds only intent: Bolt and Unit records, in build order. A Source is a path in the partition's first blueprints repo, or `<owner>/<name>:<path>` in another. Every stage is read from the kits, one call per host. A write fetches the branch over https into crew's bare cache of the repo (`~/.cache/crew/git/<owner>/<name>.git`), applies itself to the tip, checks each file it changed with `recfix --check` and the plan with crew's rules, commits through a temporary index, and pushes without force; a push refused because someone wrote first is applied again to the new tip, up to five times. Nothing is ever merged. A write that touches a bolt a team holds sends that team's conductor the commit's subject.

## State

```
crew state init <label>
```

A partition's **flywheel** is its loop, named by its label. Its state is the files on one branch, `<label>/main`, of the state repository the teams file names for it (`state`, one per organisation, such as `WilldanGroup/crew-state`), apart from the design:

- `plan.rec`, the plan;
- `moves.rec`, every signal's one move;
- `runs/<host>/<YYYY-MM-DD>.rec`, the run record each host has carried.

Flywheels sharing a repository never meet: each command fetches and pushes only its own flywheel's branch, and no branch shares history with another. A write that changes several files is one commit, and its message ends with a `Crew-Entry:` trailer naming the run-record entry that describes it. `crew state init <label>` creates the branch: it adopts the first blueprints repo's `plan/<label>` with its history where there is one, joins another blueprints repo's `plan/<label>` in one commit naming where it came from, and copies the first blueprints repo's `signals/moves.rec`; run again, it finishes what a stopped run left, or says the branch exists. A clone of the branch reads with `recsel` and nothing else.

## Signals

```
crew signal <slug> "<what it asserts>" [--kind K] [--subject a,b] [--excerpt "<text>"]
crew signal move <id> attach|challenge|new-territory|answered|drop [--target T] [--reason R]
```

Signals are in the partition's first blueprints repo, in the shape its `signals/README.md` gives. A finding is recorded with `crew signal`, by its own paths on that repo's main. Curation's moves, `crew signal move`, are appended to `moves.rec` on the flywheel's branch, and a signal becomes work only through its `route` move, which `crew unit add --signal` writes in the same commit as the unit. Each signal has one move, and nothing is ever merged.

## The main level and the operator agent

```
crew main     up|down|status <label>
crew operator up <label>
crew revive
crew tell     <agent> "<text>"
crew sites    [<label>] [--json]
```

Each partition has a main level in the session the teams file names: the **design agent** (elaboration on main and curation of signals), the **planner** (the only writer of bolts and placements) and the main-level **ops** (lands proven bolts and deploys main), as tabs of the `<label>` workspace; and a **dispatcher** on each host the partition's teams run on, in `<label> dispatch`, which gives that host's teams their bolts. The **operator agent** stands in each operator session (the session named `<label>`), started there with `crew operator up <label>`, and works for the user. `crew tell` prompts any of these agents by name, wherever it runs.

A herdr server that restarts resumes each agent in its saved pane folder, which is the folder crew moved the pane to before starting the agent, since Claude finds a conversation only from the folder it began in. crew's SessionStart hook gives a resumed agent its name and identity back. An agent that never had a message has no conversation to resume, so its pane comes back as a shell: `crew revive`, run on a host after a restart, brings back each standing agent of that host whose pane came back empty, from its last conversation or fresh, and leaves a team or main level taken down with `crew down` as it is. `crew sites` lists each host's bolts, units and fixes with the URL of each running dev server, named by swancloud's `devurl` and found among the host's portless routes.

## Seeing what happened

```
crew events [--label L] [--about <object>] [--since <time>] [--follow] [--json]
crew events --push [--label L]
crew trace  <object>
crew unit wait <unit> [--timeout <ms>]
```

Every crew command that moves work appends one entry per act, after the act, to the **run record** of the partition it acts for, on the host where it ran: `~/.local/state/crew/<label>/runs/<host>/<YYYY-MM-DD>.rec`, one recutils file per UTC day, each entry one write, never rewritten. An entry holds:

- `Id`, `At` (UTC) and `Host`, where crew ran;
- `By`, the agent crew started that asked (`CREW_AGENT`), or `<user>@<host>`, and `Session`, that agent's Claude session as `<host>:<id>`, carried with a command crew runs again on another host;
- `Act`, such as `unit.add`, `bolt.give`, `stage.start`, `stage.end`, `tell`, `team.up` or `agent.restart`;
- `On`, each object acted on, and `From`, each object it came from, as typed names: `unit/<unit>`, `bolt/<bolt>`, `queue/<kit>`, `signals/<id>`, `team/<team>`, `agent/<name>`, `stage/<unit>/<stage>`, `fix/<bolt>/<name>`;
- `Commit`, `<owner>/<name>@<sha>`, when the act wrote one, and `Why`, the subject crew composed from the names of things;
- `Refused`, crew's reason, when a command that would have moved work was refused;
- a stage's end's `Result` (the stage the unit reached), `Tasks`, `Head` (the unit branch's head) and `Observed: late` when nobody waited for it, and a tell's `Chars`.

No entry holds text anyone typed: not a tell's text, an intent, a goal, a reason or an excerpt. A read writes nothing, and a record that can't be written is said on standard error and changes nothing about the command. `recsel -t Entry` reads the files with no crew involved.

Every write to the flywheel's branch also carries the host's uncarried entries there, to `runs/<host>/`: each day's file on the branch becomes the union by `Id` of what it had and what the host has, so a host only ever adds to its own files, and one that is asleep or rebuilt loses nothing it had carried. `crew events --push` carries in a commit of its own, and makes none when nothing is left. `crew events` reads the branch, then gathers what every host the partition runs on (its teams', its main level's and its operator sessions') has not yet carried, one call per host, and prints them in time order, naming a host that does not answer, whose entries are shown as far as it had carried them; `--follow` prints them as they are written, and the operator workspace's `flow` tab runs it. `crew trace <object>` prints one bolt's, unit's or signal's history from the entries alone: what was done, by whom, with which commit, what it came from and what came from it, each line with the `zoe <session>` to open on its host. A bare name is tried as a unit, then a bolt, then a signal. `crew unit wait <unit>` waits on the team's host for the unit's stage agent to settle and records the stage's end; an end nobody waited for is recorded, once and marked late, the next time crew reads the team.

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
