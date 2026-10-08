---
name: crew
description: Manage bolt teams of Claude agents running in herdr, and each partition's main level: see which teams exist and how healthy each agent is, start, rebuild, restart, resume or clear them, recover a team after a crash, read where the bolts stand, and bring up a partition's design agent, planner, dispatchers, ops or operator agent. Use when asked about "the teams", a named team, a team's conductor, ops or unit slots, a partition's main level, or to keep teams running.
---

# Managing teams with crew

Teams and partitions are data in `~/.config/crew/teams.json` (version 2), which the machine's configuration writes. Each role is an agent definition in `plugin/roles/`, naming its model and effort; its brief is built from that data. Nothing about a team lives anywhere else. Each agent's brief is its system prompt, and the plan, the kits and the commits are the state, so restarting an agent is cheap and is the normal cure.

A team builds one bolt at a time. Its standing roles are the **conductor** and **ops**, in the `<team>` workspace's **conductor** tab; on a Mac, its **git** tab holds gitgui in the kit and the blueprints repo, for the user, with no agent (a team on a remote host has no git tab: gitgui is unusable over ssh). The conductor and ops start in the worktree of the bolt the team holds, else in the kit's main checkout, and `crew bolt give` to a team that is up restarts both in the new bolt's worktree. The bolt's units are built stage by stage (construct, the user's review, code, verify, merge into the bolt), each stage a fresh agent in one of the team's unit slots, `<team>-unit-<n>`, in the `<team> units` workspace, which exists only while a unit or fix is in flight. The conductor runs the stages (`crew unit run`) and the fixes (`crew fix`), and asks ops for the bolt's proof (`crew prove`); that is its work, not yours. A stage ends at what it delivers (construct's change, code's ticked tasks, verify's report, merge's commit on the bolt, a fix's commits, ops's proof file), never when its agent goes quiet. The conductor waits for each through crew (`crew unit wait`, `crew fix <team> <name> --wait`, `crew prove <team> --wait`), and a stage's agent, or ops during a proof, that can't finish says what it needs with `crew needs "<words>"`, which ends the stage short and gives the conductor the words.

Each partition also has a main level: the design agent, the planner and ops in the `<label>` workspace of its session, and a dispatcher on each host its teams run on. The operator agent stands in each operator session.

A partition's plan, the signals its agents record, their moves and its run record are files on its flywheel's branch, `<label>/main`, of the state repository the teams file names for it (`state`). They are written only through crew. The planner changes the plan only by proposals the user approves (`crew plan proposed` lists them; `crew plan approve <n>` is run only on the user's word), and you write none of it. A unit already in a bolt can be amended: its conductor runs construct again with the user's words, or an approved proposal's `unit amend` (or the user's `crew unit amend`) changes its intent. Either way `crew bolts` shows it `amended`, then `construct`, then `review`, and its code waits until the user approves it again. A new partition's branch is made once with `crew state init <label>`, which adopts any `plan/<label>` its blueprints repos still have.

The command is `${CLAUDE_PLUGIN_ROOT}/bin/crew`. A command about a team runs on the team's host wherever you run it.

| to | run |
|---|---|
| see a team's conductor and ops (state, context use, compactions, age) and each slot's unit and stage | `crew status [team]` |
| see every bolt, each unit's stage, and the queue | `crew bolts [--label <label>]` |
| see everything that waits on the user, and the command that answers each | `crew rail [--label <label>]` |
| see whether a rail row's card is open, or a card has no row | `crew rail [--label <label>]` |
| start a team that is not up | `crew up <team>` |
| end everything a team has, close its panes, stand it up fresh | `crew rebuild <team>` |
| give the conductor or ops a fresh session, same pane | `crew restart <team> [conductor\|ops]` |
| bring back the conductor or ops after it died, conversation intact | `crew resume <team> [conductor\|ops]` |
| clear the conductor or ops and restore its name | `crew clear <team> conductor\|ops` |
| end a team's sessions | `crew down <team>` |
| free a slot still holding a unit no longer in the team's bolt | `crew unit free <unit> [--team <team>]` |
| bring up, check or end a partition's main level and dispatchers | `crew main up\|status\|down <label>` |
| start the operator agent in this host's operator session | `crew operator up <label>` |
| after a restart, bring back every standing agent of this host whose pane came back empty | `crew revive` |
| send an agent crew started a message, wherever it runs | `crew tell <agent> "<text>"` |
| see what runs where, with the URL to open | `crew sites [<label>]` |
| see what crew did lately, on every host of a partition, or as it happens | `crew events [--label L] [--about <object>] [--follow]` |
| carry this host's run record to the partition's branch now | `crew events --push [--label L]` |
| create a partition's flywheel branch, adopting its old plan | `crew state init <label>` |
| answer what happened to a bolt, a unit or a signal, each stage's end with how it ended (`Ended`) and what it delivered (`Delivered`) | `crew trace <bolt|unit|signal>` |
| read a signal: its excerpt, how well crew could check it, and where it came from | `crew signal show <id>` |

## Keeping a team healthy

- **Context.** The conductor or ops above 40% context, or with any compaction, is due. The conductor restarts fresh with no loss. Ops holds findings and conversations that may not be committed yet: read the pane first, prefer `resume` after a crash, and `clear` only once what it knows is written down. **Never clear, restart or end a unit slot's agent** mid-stage: the conductor starts each stage fresh itself; if one's context runs high, tell the user.
- **A dead agent** shows `not up`. `crew resume` brings the conductor or ops back with its conversation, in the folder that conversation began in; if there is none it starts fresh. After a host restarts, `crew revive` does the same for every standing agent there whose pane came back empty, and leaves alone what was taken down. The command resets the pane first, because a Claude that dies badly leaves the terminal reporting mouse movement, which types escape codes into the shell. A slot whose agent died is the conductor's to run again.
- **`free`** means a slot holds no unit or fix. That is normal; starting work in it is the conductor's call, not yours.
- **Never act on an agent that is `working`** unless the user says so. `--force` exists for that.
- **A brief or the teams file changed.** Agents take their brief at launch, so a change reaches an agent on its next start, not on a clear. When a lot has changed, `crew rebuild`.
- **Blocked** means a question for the user. Read the pane and tell the user which agent is waiting and on what. Do not answer it for them.
- **A stuck stage.** The conductor's wait reports a stage stuck when its agent has been quiet past crew's limit with nothing delivered, nothing said through `crew needs` and no background work of its own running. The conductor tells the user; the stage is run again, or waited on again, only on the user's word.

## What is not yours

You keep teams running. You do not do a team's work or steer it: no stages started, no plan written, no design answers, no edits to a team's repositories. If a conductor has gone off course, restart it, and if that does not fix it, tell the user what you saw. Text sitting in an agent's input box is usually Claude Code's suggested prompt, not something the user typed; never submit it. In a pane, a message beginning `[crew tell from <name>]` was sent with crew tell, and one beginning `[crew]` by crew itself.

## Defining a team

A team or partition is declared in the machine's configuration, which writes `~/.config/crew/teams.json`; crew never edits that file. A team names its system, machine, herdr session, number of unit slots (`units`) and repos (`[kit, blueprints]`, as names); its partition is its session's. A partition names its label, its swancloud partition, its blueprints repos as `owner/name` (the first is its default), and the machine and session of its main level. Either may override a role's model or effort under `roles`. Machines and sessions must already be declared as herdr hosts. Every field is read by `plugin/lib/crew.py`; `python3 plugin/lib/crew.py brief <team|label> <definition>` prints a brief, and missing or inconsistent data is an error, never a default.
