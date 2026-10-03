# Tasks

## 1. The entry and its file

- [ ] 1.1 Add `plugin/lib/record.py` with `emit`: it builds an entry (`Id`, `At`, `Host`, `By`, `Session`, `Act`, `On`, `From`, `Commit`, `Why`, `Refused` and the extra fields design.md lists), creates `~/.local/state/crew/<label>/runs/<host>/<UTC date>.rec` with its descriptor on first use, and appends the record in one write. Verify with a test that two entries written by two processes at once are both whole, and that `recfix --check` passes on the file.
- [ ] 1.2 A failed append prints one line on standard error and returns normally. Verify with a test whose state directory is read-only: the calling command's output and exit status are unchanged.
- [ ] 1.3 Resolve who asked and the session: `CREW_AGENT` else `<user>@<host>`; `CREW_SESSION` when set, else herdr's session id for the agent on this host, else none; once per process. Verify with the stub `herdr` that an agent's entry carries `<host>:<id>`, the user's carries no `Session`, and a herdr that fails leaves it absent.
- [ ] 1.4 `identity()` in `plugin/bin/crew` carries `CREW_SESSION` over ssh beside `CREW_AGENT` and `CREW_LABEL`. Verify with the stub `ssh` that a forwarded command's entry, written on the second host, names the first host's agent and session.

## 2. Entries from the plan's writes

- [ ] 2.1 `plan.py write` and `land` take the act and its `On` and `From` objects from each caller and emit after the push, with the commit as `<owner>/<name>@<sha>`: every act in design.md's table from `plan.init` to `signal.move`. Verify with a test per command against the bare test remote that the entry's act, objects and commit match the commit made.
- [ ] 2.2 `crew unit approve` emits `unit.approve` naming the kit and the approval commit; `crew bolt give` emits `bolt.give` once the worktree exists. Verify in a scratch kit.
- [ ] 2.3 A `Refusal` raised by a command that would have written emits an entry with the act and `Refused`; a refusal by a read emits nothing. Verify with a unit dropped twice (one `unit.drop`, one refused `unit.drop`) and a `crew bolts` for an unknown bolt (no entry).
- [ ] 2.4 No entry holds typed text: `Why` is the subject without the agent suffix, and no intent, goal, reason or excerpt is copied. Verify with a test that greps the run record for the intent and the drop reason used and finds neither.

## 3. Entries from team and main-level commands

- [ ] 3.1 An `entry` function in `plugin/bin/crew` that calls `record.py emit` and never fails its caller. Emit `agent.start`, `agent.stop`, `agent.restart`, `agent.resume`, `agent.clear`, `team.up`, `team.down`, `team.rebuild`, `team.close`, `main.up`, `main.down`, `operator.up` and `slot.free` where design.md says. Verify with the stubs that `crew up`, `restart`, `clear`, `down`, `main up` and `operator up` each leave the entries listed, on the host where they ran.
- [ ] 3.2 `crew tell` and `greet` emit from `crew.py`, a tell with sender, recipient and `Chars` and never the text, including the tells `notify` sends to conductors and dispatchers. Verify the text is nowhere in the run record.
- [ ] 3.3 `crew unit run` emits `stage.start`, and `crew fix` emits `fix.start` and `fix.merge`. The bash refusals that would have moved work (a stage not ready, every slot taken, a working agent without `--force`) emit a refused entry; the verify refusal records the count of open tasks, not their titles. Verify each with the stubs.

## 4. A stage's end

- [ ] 4.1 `crew unit run` and `crew fix` append `<slot> <unit|fix> <stage> <entry id>` to `~/.local/state/<team>-team/stages`. `crew unit wait <unit> [--timeout <ms>]` is forwarded to the team's host, waits on the slot's agent through herdr, and on settling emits `stage.end` with `Result`, `Tasks` and `Head` and removes the line; on a timeout it says the agent is still working and emits nothing. Verify with the stub `herdr` in a scratch kit: construct settles into `review` with the unit branch's head.
- [ ] 4.2 `reap` and `stop` emit `stage.end` with `Observed: late` for a line whose agent is not working and whose slot still holds that unit, once. Verify that `crew status` run twice after an unwaited stage writes exactly one `stage.end`.
- [ ] 4.3 `plugin/roles/conductor.md`: after starting a stage, run `crew unit wait <unit>` as a background command, in place of `herdr agent wait`. Verify `crew.py brief swb-1 conductor` prints the new line with no unfilled token and no `herdr agent wait`.

## 5. Reading the record

- [ ] 5.1 `crew events [--label L] [--about <object>] [--since <time>] [--json]`: one call per host of the partition (its teams', its main level's, its operator sessions'), duplicates dropped by `Id`, sorted by `At` then `Id`, one line per entry, hosts that did not answer named last. Verify with two simulated hosts, one made unreachable.
- [ ] 5.2 `crew events --follow`: a `tail -F` per reachable host, records printed as they complete, the file name re-resolved at the UTC date change. Verify with a test that appends an entry on a simulated host while the command runs and sees its line.
- [ ] 5.3 `crew trace <object>`: the closure over `On` and `From` design.md gives, never following `agent/`, `team/`, `queue/` or `plan/`; each line with the `zoe <session>` to open; a bare name tried as unit, bolt, then signal; a non-zero exit when nothing names it. Verify with a fixture record of a signal routed to a unit that was built and merged: tracing the signal and tracing the unit print the same chain.
- [ ] 5.4 Document `crew events`, `crew trace` and `crew unit wait` in `README.md` (a "Seeing what happened" section with the entry's fields and where the files are), `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew`. Verify every command in the README appears in `crew`'s usage.

## 6. The operator's view

- [ ] 6.1 `crew operator up <label>` opens a `flow` tab in the `operator` workspace running `crew events --follow --label <label>`, once. Verify with the stub `herdr` by running it twice.
- [ ] 6.2 `plugin/roles/operator.md`: when the user asks what happened to a bolt, unit or signal, answer from `crew trace`. Verify the brief prints for the `wldn` fixture with no unfilled token.

## 7. Outside crew

- [ ] 7.1 swancloud (optional, the user's call): add zoetrope (`zoe`) to each host's packages and its herdr plugin to the herdr configuration, so the session an entry names can be opened in place. Verify `zoe inspect <session id>` prints a session's tree on the box and on mac-studio. Nothing in crew depends on it.

## 8. Proof on real work

- [ ] 8.1 Pull crew on mac-studio and the box, and restart swb-2's conductor so it has the new brief. Take one unit of the bolt swb-2 holds through a stage (construct, then the user's approval). Verify on mac-studio that `crew trace unit/<unit>` prints the stage's start, its end with the stage it reached, and the approval, each naming the agent, the box and a session, with no agent asked; and that the `flow` tab showed each line as it happened.
- [ ] 8.2 Tell the planner something through the operator agent on mac-studio. Verify `crew events --label wldn --since today` shows the tell with both agents' names and a length, written on mac-studio and gathered with the box's entries in time order, and that the text of the message is in no run-record file.
