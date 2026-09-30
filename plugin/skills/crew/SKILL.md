---
name: crew
description: Manage teams of Claude agents running in herdr: see which teams exist and how healthy each agent is, start, rebuild, restart, resume or clear them, recover a team after a crash, and define a new team. Use when asked about "the teams", a named team, a team's conductor, coder, fable, explorer, ops or verifier, or to keep teams running.
---

# Managing teams with crew

Teams are data in `~/.config/crew/teams.json`, which the machine's configuration writes. A team's briefs are built from that data and the role templates in `plugin/roles/`; nothing about a team lives anywhere else. Each agent's whole brief is its system prompt, and the work list and the commits are the state, so restarting an agent is cheap and is the normal cure.

A team is one herdr workspace with three tabs: **conductor** (the conductor and ops), **design** (fable), and **build**, which exists only while a coder, the verifier or the explorer holds work. The explorer is started for one OpenSpec command or lookup and released after it. A coder builds one whole change in that change's own worktree with `/opsx:apply <slug>`. When it is built, the verifier runs `/opsx:verify <slug>` in the same worktree. The conductor and the user decide what to fix. The coder then merges. Tests run as the repository's worktrunk hooks, never as an agent's step: `wt merge` gates the merge, and main runs its full verification afterwards.

The command is `${CLAUDE_PLUGIN_ROOT}/bin/crew`.

| to | run |
|---|---|
| see every team and agent: state, context use, compactions, age, the change held | `crew status` |
| start a team that is not up | `crew up <team>` |
| end everything a team has, close its old panes, stand it up fresh | `crew rebuild <team>` |
| give agents fresh sessions, same panes | `crew restart <team> [role...]` |
| bring back agents that died, conversations intact | `crew resume <team> [role...]` |
| clear one agent and restore its name | `crew clear <team> <role>` |
| give a coder a change, start the verifier on a built one, or start the explorer | `crew assign <team> <coder-n\|verifier\|explorer> <change>` |
| free a coder, the verifier or the explorer | `crew release <team> <coder-n\|verifier\|explorer>` |
| end a team's sessions | `crew down <team>` |

## Keeping a team healthy

- **Context.** A standing agent above 40% context, or with any compaction, is due. The conductor restarts fresh with no loss. Ops and fable hold findings and conversations that may not be committed yet: read the pane first, prefer `resume` after a crash, and `clear` only once what they know is written down. **Never clear or restart a coder that is mid-change**; if its context runs high, tell the user.
- **A dead agent** shows `not up`. `crew resume` brings it back with its conversation; if there is none it starts fresh. The command resets the pane first, because a Claude that dies badly leaves the terminal reporting mouse movement, which types escape codes into the shell.
- **`free`** means a coder, the verifier or the explorer holds no work. That is normal, and assigning is the conductor's call, not yours.
- **Never act on an agent that is `working`** unless the user says so. `--force` exists for that.
- **A brief or the teams file changed.** Agents take their brief at launch, so a change reaches an agent on its next restart, not on a clear. When a lot has changed, `crew rebuild`.
- **Blocked** means a question for the user. Read the pane and tell the user which agent is waiting and on what. Do not answer it for them.
- **`release` refuses** while a coder's branch has commits that are not on main. That is unmerged work: tell the conductor, don't force it.

## What is not yours

You keep teams running. You do not do a team's work or steer it: no sending changes to a coder, no design answers, no edits to a team's repositories. If a conductor has gone off course, restart it, and if that does not fix it, tell the user what you saw. Text sitting in an agent's input box is usually Claude Code's suggested prompt, not something the user typed; never submit it.

## Defining a team

A team is declared in the machine's configuration, which writes `~/.config/crew/teams.json`; crew never edits that file. The team names a machine and a herdr session, and both must already be declared there as herdr hosts: a team does not create either. Every field is read by `plugin/lib/crew.py`; `python3 plugin/lib/crew.py brief <team> <role>` prints a brief, and missing data is an error, never blank text.
