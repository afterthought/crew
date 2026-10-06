# Proposal

## Why

Working out what happened to a bolt, a unit or a signal today means reading several agents' Claude transcripts and the git logs on two hosts, and in practice the user asks an agent to piece it together. On 2026-10-03 a conductor recorded two signals and the planner queued a unit from each within a minute; nothing but a plan commit's subject says so, and nothing at all records the tell between them, the stage that ran, or the restart that followed. crew knows every one of these acts at the moment it performs it. This change has crew write each one down, and gives the user two commands that read them back, so that what happened can be seen without asking an agent.

It is the first step of the findings-to-design work (`openspec/explorations/findings-to-design/proposal.md`, invariants 16 to 20, and `roadmap.md` beside it). It changes no record and no rule, so it can land alone.

## What Changes

- **The run record.** Every crew command that moves work appends one entry, after it has done its work, to a recutils file on the host where it ran: `~/.local/state/crew/<label>/runs/<host>/<date>.rec`. The name, path and format follow Flywheel Next's run record.
- **What an entry holds:** an id, the time, the host, who asked (the agent crew started, or the user at a shell), that agent's Claude session, the act, the objects acted on (`On`), the objects they came from (`From`), the commit written if any, and the subject crew composed. A refusal is an entry with crew's reason. An entry never holds text anyone typed.
- **What is recorded:** every plan write (`crew bolt …`, `crew unit …`), a signal and its move, the user's approval, a stage's start and end, a fix, `crew tell`, a greeting, and every start, stop, restart, resume and clear of an agent or a team.
- **`crew events`** gathers the entries of every host a partition runs on, one call per host, and prints them in time order; `--about <object>` narrows them, `--follow` prints them as they are written, `--json` gives them to another program.
- **`crew trace <object>`** prints one bolt's, unit's or signal's history in order: what was done, by whom, in which session, with which commit, and what it led to.
- **`crew unit wait <unit>`** waits for a unit's stage agent to stop working and records the stage's end. The conductor runs it where its brief says `herdr agent wait` today. A stage whose end nobody waited for is recorded the next time crew reads the team.
- **A `flow` tab** in each operator workspace follows the partition's run record, so the user can leave it open.
- No existing command's output, exit status or refusal changes, and a failed append never fails the command it describes.

## Capabilities

### New Capabilities

- `run-record`: the entries crew writes for every act that moves work, where they are kept, and the commands that gather, follow and trace them.

### Modified Capabilities

- `operator-agent`: the operator workspace gains a tab that follows the run record, and the operator agent answers what happened to a piece of work from `crew trace`.
- `bolt-teams`: a stage's end is recorded through `crew unit wait`.

## Impact

- `plugin/lib/`: a new module beside `plan.py` that writes and reads entries; `plan.py` calls it from its two write functions (`write`, `land`) and from its refusal handler.
- `plugin/bin/crew`: entries from the team, main-level and operator commands; `events`, `trace` and `unit wait`; the session id carried when a command is run again on another host.
- `plugin/roles/conductor.md`: one line, `crew unit wait` in place of `herdr agent wait`. `plugin/roles/operator.md`: `crew trace` for "what happened to".
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header of `plugin/bin/crew`, `tests/`.
- A new directory per partition on each host, `~/.local/state/crew/<label>/`. Nothing in any repository is written.
- swancloud: optionally, zoetrope (`zoe`) on each host, to open the session an entry names.

## Touches

`plugin/bin/crew`, `plugin/lib/plan.py`, `plugin/lib/crew.py`, a new `plugin/lib/record.py`, `plugin/roles/conductor.md`, `plugin/roles/operator.md`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`.
