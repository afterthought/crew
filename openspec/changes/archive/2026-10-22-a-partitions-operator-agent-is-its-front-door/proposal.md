# Proposal

## Why

Nothing tells a crew agent who receives something meant for another team or another partition, so a session asked to send findings to swancloud's crew offered to send them to the conductors. The user asked for "an obvious way for me to instruct any crew agent to send something to another crew or team and have it know what to do" (signal 2026-10-08-swancloud-operator-mac-studio-5fda4ef7/01). Record 0013 makes the partition's operator its one door, and record 0035 makes that door one agent, `<label>-operator`, in the main level's session; rule `briefs.10` says how it is reached. It is not built yet (`_open.md`).

## What Changes

- **One command to send across teams and partitions.** `crew send <team or partition> "<text>"` works out the door itself: a partition by its label, a team by the partition it belongs to, and the door is always that partition's operator, `<label>-operator`, wherever it runs. The sender never has to know which operator, which host or which conductor.
- **It arrives marked, and says who it was for.** The operator sees `[crew tell from <sender>] (sent to <team or partition>) <text>`, the same mark every tell carries, so it knows who sent it and which team it was meant for.
- **It is recorded.** Each send is one entry in the receiving partition's run record, naming the sender, the operator, the team when one was named, and the length of the text, never the text.
- **It refuses what it can't place.** A name that is no team and no partition is refused, naming the teams and partitions there are; the operator sending to its own partition is refused, since it carries with `crew tell`; an operator that is not up, or waits on a question, gets nothing typed, as with any tell.
- **Every brief says so in one line.** Beside its roster every brief says that anything for another team or partition goes with `crew send`, and to nobody else. A team's agents reach their own team and their main level with `crew tell`, as now; the main level's agents reach their own partition's teams with `crew tell`, as now.
- **The operator carries what is sent to it**: a finding becomes a signal, a design question goes to the design agent, work to the planner, a message for a team to its conductor, each in the sender's words. Its request to change the teams from a box goes to a Mac's partition with `crew send` rather than a tell to another operator.
- The crew skill, the README and crew's usage list `crew send`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `operator-agent`: the operator is the door for whatever another team or partition sends, by `crew send`, and every brief names that one way.
- `run-record`: a send is one entry in the receiving partition's record.

## Impact

`plugin/lib/crew.py` (the door's resolution, the send, the roster's line, the operator's teams-change token), `plugin/bin/crew` (the `send` command and its usage), `plugin/roles/operator.md`, `plugin/skills/crew/SKILL.md`, `README.md`, a comment in `plugin/lib/record.py`; the logic tier and `tests/t-briefs.sh`, `tests/t-journey-main.sh`. `briefs.10`'s "not built" and its line in `_open.md` are the design agent's to clear after the landing (`docs.7`).

## Touches

```
plugin/lib/crew.py
plugin/lib/record.py
plugin/bin/crew
plugin/roles/operator.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_send.py
tests/t-briefs.sh
tests/t-journey-main.sh
tests/moon.yml
```
