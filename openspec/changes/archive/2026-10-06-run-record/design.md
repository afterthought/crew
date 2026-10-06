# Design

## Context

See proposal.md for why. What shapes the approach:

- crew is a bash command (`plugin/bin/crew`) over a Python builder (`plugin/lib/crew.py`) and the plan module (`plugin/lib/plan.py`). It has no service and no process that outlives a command.
- Every write to a shared record already passes through two functions in `plan.py`: `write` (the plan) and `land` (anything committed by path, which signals and moves use). A refusal is the `Refusal` exception, caught once at the bottom of `plan.py`.
- Team, main-level and operator commands are bash: `start`, `stop`, `run_stage`, `teardown`, `free`, and the `case` at the bottom of `plugin/bin/crew`. A command about a team is run again on the team's host over ssh (`forward`, `there`), carrying `CREW_AGENT` and `CREW_LABEL` (`identity`).
- An agent crew starts has `CREW_AGENT` (its name) and `CREW_LABEL` in its environment, set by `plugin/bin/crew-role`. The user at a shell has neither.
- herdr knows the Claude session running in a pane. `crew status` already reads it: `herdr --session <s> agent get <pane>` gives `.result.agent.agent_session.value`, and the transcript is `~/.claude*/projects/*/<id>.jsonl` on that host.
- crew cannot wait on an agent. The conductor's brief has it run `herdr agent wait <team>-unit-<n> --timeout 3600000` in the background after starting a stage.
- recutils is on every host and in `devenv.nix`; `plan.py` has its own small reader and writer of rec files (`Rec`, `Plan`), and `recfix` checks them.
- `tests/run` gives each simulated host a scratch `HOME` and stub `herdr`, `ssh` and `claude`.

Flywheel Next's run record is the model (`flywheel-next/main/openspec/specs/observability/run-record/spec.md`; its git-only profile keeps it at `runs/<host>/<date>.rec`). The findings-to-design proposal's section 4 gives the reasoning this design follows.

## Goals / Non-Goals

**Goals:**
- One entry per act, written by the code that performs the act, so the entry can name the objects and the commit exactly.
- A record that needs nothing running to be read, and that `recsel` reads without crew.
- `crew trace` as a pure function of the entries.
- Nothing an existing command prints, returns or refuses changes.

**Non-Goals:**
- Carrying the record off the host. Until the `state-repository` change, entries live only where they were written and are gathered over ssh; a host that is asleep is named as missing, and a host that is rebuilt loses its entries.
- A graphical view. `lineage-page` adds one over the same entries.
- Recording what agents do inside a session. The Claude transcript is that record; an entry points at it.
- An entry for a read (`crew bolts`, `crew status`, `crew sites`, `crew events`, `crew trace`).

## Decisions

### An entry is a recutils record

```
%rec: Entry
%key: Id
%mandatory: Id At Host By Act
%allowed: Id At Host By Session Act On From Commit Why Refused Result Tasks Head Observed Chars

Id: 20261006T140210Z-chuck-herdr-alpha-48213-1
At: 2026-10-06T14:02:10Z
Host: chuck-herdr-alpha
By: wldn-planner
Session: chuck-herdr-alpha:7be1c0de-…
Act: unit.add
On: unit/cfn-nag-security-check
On: queue/switchboard-kit
From: signals/2026-10-03-swb-2-conductor/02-cfn-nag-templates
Commit: WilldanGroup/willdan-blueprints@4119bf25
Why: plan(queue): add cfn-nag-security-check
```

- `Id` is `<UTC time, compact>-<host>-<pid>-<n>`, `n` counting the entries one process writes. It is unique without coordination and sorts by time.
- `At` is UTC to the second. `Host` is `hostname -s`, the name the teams file uses.
- `On` and `From` repeat, one object each. `Commit` repeats when an act wrote more than one.
- `Why` is the commit's subject without its trailing `(agent)`, or for an act with no commit a subject composed the same way (`team(swb-1): restart conductor`).
- `Result`, `Tasks` and `Head` are a `stage.end`'s: the stage read from the kit, `done/total`, and the unit branch's short sha. `Observed: late` marks an end nobody waited for. `Chars` is a tell's length.
- Each file starts with the descriptor above, so `recfix --check` and `recsel -t Entry` work on it.

*Alternatives:* JSON lines, one object per line, is easier for a browser page and harder for a person at a shell; the lineage page reads `crew events --json` instead. Flywheel's own run record is recutils at this path, and crew already depends on recutils and already parses it.

### Written on the host, one append per entry

The file is `~/.local/state/crew/<label>/runs/<host>/<YYYY-MM-DD>.rec`, the date in UTC. The `<host>` directory is redundant on the host itself; it is there so that the `state-repository` change can copy the tree as it stands into a repository where several hosts' files sit side by side.

An append opens the file with `O_APPEND` and writes the whole record, with its leading blank line, in one `write`. Records are a few hundred bytes, so concurrent crew processes on one host never interleave. The directory and the file's descriptor are created on first use.

Any failure (no directory, no space) prints `crew: the run record at <path> could not be written: <reason>` on standard error and returns. The entry is written after the act succeeds, so a crash between the two loses an entry and never invents one.

*Alternatives:* a commit per entry in a repository, Flywheel's way. Rejected here: half of crew's acts write no commit, a push per tell or stage start is slow, and an entry cannot hold the hash of the commit that carries it. A Claude Code hook on each `crew` command was rejected because a hook sees a command string, where crew knows the objects and the commit.

### One module writes and reads entries

A new `plugin/lib/record.py` has `emit(label, act, on, frm, commit, why, refused, **extra)`, the reader, and the `events` and `trace` commands. `plan.py` imports it. Bash calls it as `python3 lib/record.py emit …` through a small `entry` function in `plugin/bin/crew`, which never lets a failure reach `set -e`.

### Who asked, and the session

`By` is `CREW_AGENT`, else `<user>@<host>`. `Session` is `<host>:<session id>`, resolved once per process:

1. if `CREW_SESSION` is set (a forwarded command), use it;
2. else, when `CREW_AGENT` is set, find the agent's host and herdr session from its name and the teams file (`place_of_agent`), and when that host is this one ask herdr: `herdr --session <s> agent get <name>` → `.result.agent.agent_session.value`;
3. else none.

`identity()` in `plugin/bin/crew` adds `CREW_SESSION=<host>:<id>` to what `there` and `forward` carry, resolved before the ssh. `on_machine` calls made by `plan.py` (reading the kits, making a worktree) are not acts of their own and emit nothing; the command that made them does.

A herdr that cannot answer leaves `Session` absent. That is the only cost of a missing session; the entry is still written.

### Which partition's record

The label is the object's: a team's label, the label of the plan a bolt or unit is in, the signal's partition, a main level's or operator's own label. `crew tell` uses the recipient's label, read from its name.

### The acts

| Act | Where it is emitted | On | From |
|---|---|---|---|
| `plan.init` | `plan.py init` | `plan/<label>` | |
| `bolt.new`, `bolt.order`, `bolt.drop`, `bolt.land` | `plan.py write`, after the push | `bolt/<b>` (and `unit/<u>` for each unit a drop or land removes) | |
| `bolt.give` | `plan.py bolt_give` | `bolt/<b>`, `team/<t>` | |
| `unit.add` | `plan.py write` | `unit/<u>`, `bolt/<b>` or `queue/<kit>` | `signals/<id>` with `--signal` |
| `unit.split` | `plan.py write` | `unit/<u>` and each new unit | the unit split |
| `unit.order`, `unit.after`, `unit.drop` | `plan.py write` | `unit/<u>`, its bolt or queue | |
| `unit.move` | `plan.py write` | `unit/<u>`, the bolt or queue it went to | the bolt or queue it left |
| `unit.approve` | `plan.py unit_approve` | `unit/<u>` | |
| `capture` | `plan.py signal` (`land`) | `signals/<id>` | |
| `signal.move` | `plan.py signal_move`, `route` | `signals/<id>`, the target | |
| `stage.start` | `crew unit run`, after the prompt is sent | `stage/<u>/<stage>`, `unit/<u>`, `agent/<slot>` | |
| `stage.end` | `crew unit wait`, or the next read of the team | the same | |
| `fix.start`, `fix.merge` | `crew fix` | `fix/<bolt>/<name>`, `bolt/<b>`, `agent/<slot>` | |
| `slot.free` | `free`, `reap` | `agent/<slot>`, the unit or fix | |
| `tell` | `crew.py tell`, including the tells `notify` sends | `agent/<to>` | |
| `greet` | `crew.py greet` | `agent/<team>-conductor` | |
| `agent.start`, `agent.stop`, `agent.restart`, `agent.resume`, `agent.clear` | `start`, `stop`, and the `restart`, `resume`, `clear` cases | `agent/<name>`, `team/<t>` when it has one | |
| `team.up`, `team.down`, `team.rebuild`, `team.close` | their cases | `team/<t>` | |
| `main.up`, `main.down`, `operator.up` | their cases | `agent/<name>` for each agent started or stopped | |

`plan.py write` is told the act and the objects by each caller (today it is told only the subject); the commit is the sha `land` returns. A plan write's `Commit` names the repository and branch's commit; a `unit.approve` names the kit and the empty commit it made.

A refusal is emitted where the `Refusal` is caught in `plan.py`, and by `entry` before each `exit 1` in the bash refusals that would have moved work (a stage not ready, every slot taken, an agent that is working without `--force`). It carries the act that was refused and `Refused: <crew's own message>`. crew's refusal messages are composed from names and stages, never from typed text; the one exception, a unit's open task titles in the verify refusal, is replaced in the entry by their count.

### A stage's end

crew learns that a stage ended only when something runs. Two places record it, and a small file makes sure it is recorded once:

- `crew unit run` appends `<slot> <unit> <stage> <entry id>` to `~/.local/state/<team>-team/stages` after it records `stage.start`.
- `crew unit wait <unit> [--timeout <ms>]` (default 3600000) is forwarded to the team's host, runs `herdr agent wait <team>-unit-<n> --timeout <ms>` for the slot holding the unit, and when herdr returns with the agent not working, reads the unit's stage as `crew status` does (`plan _slots`), emits `stage.end` with `Result`, `Tasks` and `Head`, and removes the line. On a timeout it prints that the agent is still working, emits nothing and exits 0.
- `reap`, which `crew status`, `crew unit run` and `crew fix` already call, emits `stage.end` with `Observed: late` for every line whose slot's agent is not working, and removes the line. `stop` does the same for the slot it ends, before ending it.

The conductor's brief changes one line: after starting a stage it runs `crew unit wait <unit>` in the background where it ran `herdr agent wait`. Fixes use the same file with the fix's name.

### Gathering

`crew events` finds the partition's hosts from the teams file (the machines of its teams, its main level, and each host with an operator session named for the label) and makes one `on_machine` call per host that prints the files from `--since` on (default: seven days). It parses them with `record.py`'s reader, drops duplicates by `Id`, sorts by `At` then `Id`, and prints one line per entry:

```
10-06 14:02:10  unit.add      wldn-planner         chuck-herdr-alpha  4119bf2  unit/cfn-nag-security-check queue/switchboard-kit ← signals/…/02-cfn-nag-templates
```

`--about <object>` keeps entries naming the object in `On` or `From`. `--json` prints a list of objects with the fields as keys and `On`, `From` and `Commit` as lists. A host that does not answer is listed after the entries, as `crew bolts` lists one.

`--follow` runs, per reachable host, `ssh <host> tail -n 0 -F <today's file and tomorrow's>` (locally, `tail` itself), assembles lines into records at each blank line, and prints the same one-line form as they complete. It re-resolves the file name when the UTC date changes.

### Trace

`crew trace <object>` gathers the partition's entries with no `--since` bound, then walks: start with the object; add every entry naming an object in the set; add the objects in those entries' `From` (what it came from), and the `On` objects of entries whose `From` names an object in the set (what came from it); repeat until nothing is added. Objects of kind `agent/`, `team/`, `queue/` and `plan/` are printed but never followed, or every trace would pull in everything a team ever did.

Output is the event lines above, in time order, with one more column: `zoe <session id>` on `<host>` when the entry has a session. An object given without its kind (`cfn-nag-security-check`) is tried as a unit, then a bolt, then a signal.

### The flow tab

`crew operator up <label>` adds a tab `flow` to the `operator` workspace, running `crew events --follow --label <label>`, tracked in the operator's panes file like the agent's pane so a second `up` finds it.

## Risks / Trade-offs

- [A herdr call on every command to find the session] → one call per process, only when `CREW_AGENT` is set and `CREW_SESSION` is not; it is local and takes tens of milliseconds.
- [Entries exist only on the host that wrote them] → accepted for this change; `crew events` names a host that does not answer. `state-repository` carries them to git.
- [Clocks differ between hosts] → entries sort by `At` then `Id`; a few seconds of skew can misorder two hosts' entries, never one host's.
- [An act succeeds and its entry is lost in a crash] → the record may miss an entry and never holds a false one. The plan's own commit still exists.
- [A refusal message leaks typed text] → refusal messages are crew's own; the verify refusal's task titles are counted, not copied.
- [The stages file and the slots file disagree after a crash] → a `stage.end` is emitted only for a line whose slot still holds that unit; other lines are dropped.
- [Tests start writing files under each scratch home] → the harness's homes are already per host; tests assert on those files.

## Migration Plan

None. The change is live on a host when its crew checkout is pulled; entries start from that moment, and nothing earlier is reconstructed. A conductor started before the pull keeps its old brief and its stages' ends are recorded late until it is restarted. Rollback is reverting the commit; the files left under `~/.local/state/crew/` are inert.
