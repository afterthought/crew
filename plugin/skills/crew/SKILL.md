---
name: crew
description: Manage Chuck's teams of Claude agents running in herdr: see which teams exist and how healthy each agent is, start, restart, resume or clear them, recover a team after a crash, and set up a new team. Use when asked about "the teams", a named team (switchboard, breadboard), a team's conductor, coder, fable, explorer or ops agent, or to keep teams running.
---

# Managing teams with crew

A team is a set of Claude agents in one herdr tab or workspace: a conductor that keeps the coders fed and reports status, fable for design, an explorer that writes OpenSpec changes and the backlog, ops for everything live, and a pool of coders. A coder builds one change at a time inside that change's own worktree and merges each finished group to main through the repository's gate, so main is always a tested state and two changes can be built at once. Each agent's whole brief is its system prompt, rendered from `plugin/roles/<role>.md` and the team's folder under `teams/<org>/<team>/`. Nothing a team needs lives in an agent's head: the work list and the commits are the state. That is why restarting an agent is cheap and is the normal cure.

The command is `${CLAUDE_PLUGIN_ROOT}/bin/crew`.

| to | run |
|---|---|
| see every team and agent: state, context use, compactions, age | `crew status` |
| start a team that is not up | `crew up <team>` |
| give agents fresh sessions, same panes | `crew restart <team> [role...]` |
| bring back agents that died, conversations intact | `crew resume <team> [role...]` |
| clear one agent and restore its name | `crew clear <team> <role>` |
| give a coder a change: makes its worktree, starts the coder fresh inside it | `crew assign <team> <coder-n> <change>` |
| free a coder whose change is merged; its worktree goes | `crew release <team> <coder-n>` |
| end a team's sessions | `crew down <team>` |

## Keeping a team healthy

- **Context.** An agent above 40% context, or with any compaction, is due. The coder, the explorer and the conductor restart fresh with no loss. Ops and fable hold findings and conversations that may not be committed yet: read the pane first, and prefer `resume` after a crash and `clear` only once what they know is written down.
- **A dead agent** shows `not up`. `crew resume` brings it back with its conversation; if there is none it starts fresh. The command resets the pane first, because a Claude that dies badly leaves the terminal reporting mouse movement, which types escape codes into the shell.
- **Never restart an agent that is `working`** unless the user says so. `--force` exists for that.
- **A brief changed.** Agents take their brief at launch, so a change reaches an agent on its next restart, not on a clear.
- **Blocked** means a permission prompt or a question. Read the pane and tell the user which agent is waiting and on what. Do not answer it for them.

- **A coder shows `free`** when it holds no change. That is normal: a coder runs only while it holds one, and assigning is the conductor's call, not yours. A coder that holds a change and is `not up` has died; `crew resume` it.
- **`release` refuses** while the change's branch has commits that are not on main. That is unmerged work: tell the conductor, don't force it.

## What is not yours

You keep teams running. You do not do a team's work or steer it: no sending groups to a coder, no design answers, no edits to a team's repositories. If a conductor has gone off course, restart it, and if that does not fix it, tell the user what you saw. Text sitting in an agent's input box is usually Claude Code's suggested prompt, not something the user typed; never submit it.

## Setting up a team

Copy an existing folder under `teams/<org>/`, then set `team.sh` (the system, its repositories relative to the org folder, the design repository, the machine, the herdr session, agent names qualified by the team) and the five short fragments: what the record is (`record.md`), where fable writes (`where.md`), how a coder proves work (`prove.md`), what the console is built to (`console.md`), and how a coder merges its worktree in that repository (`worktree.md`). `CODERS` sets the size of the pool. The machine's file under `machines/` says where each org folder is on that machine. `python3 plugin/lib/render.py <team> <role>` prints a brief; an unfilled token is an error.
