# Design

## Context

See proposal.md for why. The decision is ADR 0007 (`docs/adr/0007-a-stage-ends-at-its-deliverable.md`); its rule is `teams.4`, listed in `_open.md` as accepted, not built. The ADR rules the outcome and leaves three things to this change: how crew tells "still running" from "stuck", how the wait finds each stage's deliverable, and whether the briefs change how agents wait.

What is built today:

- `crew unit run` (`plugin/bin/crew` `run_stage`) records `stage.start` and appends `<slot> <unit|fix> <stage> <entry id> <object>` to `~/.local/state/<team>-team/stages`. A fix's stages are `fix` and `merge`.
- `crew unit wait <unit> [--timeout <ms>]` (`unit_wait`) runs `herdr agent wait` once, which returns at herdr's first idle, done or blocked, then `plan _ends --slot <slot> --waited` records `stage.end` with `Result` (the stage read from the kit), `Tasks` and `Head`, and prints "settled: <unit> is in <stage>".
- `reap` (`crew status`, `crew unit run`, `crew fix`) runs `plan _ends`, which records a late end for every owed stage whose agent is not working. `stop` runs `plan _ends --slot <slot> --ending` before ending a slot's agent.
- There is no wait for a fix: the conductor's brief says "when its agent settles, merge it". Ops's proof is a `crew tell` from the conductor, its results written to `/tmp/ops-proof-<bolt>.md`, and nothing in crew waits on it.
- Verify saves its report to `~/.local/state/<team>-team/reports/verify-<unit>-<YYYYMMDD-HHMM>.md` (the `{{REPORTS}}` token); `gather.reports` already finds each unit's newest one.
- A run-record entry's id begins with the UTC second it was made (`record.new_id`: `%Y%m%dT%H%M%SZ-<host>-<pid>-<n>`).
- Chores are not in crew (`plan.11` accepted, not built).

Rules this relies on: `teams.4` (the rule built), `teams.2` (a stage never starts over a working agent), `teams.9` (the stages file changes only under `flock`), `record.1`, `record.3` (no typed text in an entry), `record.5` (one end per start), `read.1` (what crew can't read is named, never guessed), `read.2` (another tool's output read only by facts checked against it now), `state.4` (no service: the clock lives in the wait), `roles.4` (what crew types into a pane is marked), `code.1`, `code.2`, `code.3` (forwarded to the team's host), `briefs.2`, `briefs.6`, `briefs.8`, `tests.4`, `tests.6`, `docs.2`. Pages whose area the change touches: `teams.md` (`plugin/bin/crew`, `crew.py`), `plan.md` and `signals.md` (`plan.py`, `transcript.py`), `record.md` (`record.py`), `briefs.md` (the roles), `tests.md`, `docs.md`.

One departure: `plan.12` (accepted, not built) has a command read each kit once. A wait is a watch: it reads one unit's place, or one report folder, every ten seconds until the stage ends. Each poll reads only what that stage's deliverable needs, never the whole survey.

## Goals / Non-Goals

**Goals:**
- A stage's end, waited or late, is recorded only at its deliverable, at its agent's stop-short, or when crew ends its agent.
- The conductor learns every end with its outcome from crew, and a stage quiet too long is reported stuck instead of waited out.
- Units, fixes and ops's proof wait the same way.

**Non-Goals:**
- Chores. When the chore kind is built, its code stage takes the fix's row ("a commit on its branch since it began") and its merge the merge row; that is the chores unit's work.
- The rail. Its verify row keeps reading "a report newer than the branch's head" (the ADR's consequence about the rail is a separate change).
- Main-level waits (main-level ops's landing, the planner, the design agent). The ADR is about a team's stages.
- Ending or restarting a stuck agent. crew reports it; the user decides (`briefs.8`).

## Decisions

### The end is the deliverable, read when the agent has stopped working

A stage ends when its deliverable exists **and** its agent is not working (herdr: anything but `working`), or when its agent has run `crew needs`. Requiring both keeps `teams.2` true without `--force`: a coder whose last commit is in but who is still writing its summary is waited for, so the next stage never meets a working agent. A deliverable alone, while the agent works, is "still running".

*Alternative:* end at the deliverable alone. The next stage would often be refused ("is working; add --force"), and the conductor would learn the end before the agent's final words were written.

### "Since the stage began" is read from the start entry's id

Several deliverables only count when made during this run: a verify run again with nothing committed since would otherwise end at the old report at once, and code run again with findings starts with every task already ticked. The start time is the UTC second at the front of the stage's `stage.start` id, which the stages file already holds. No new field, and lines written before this change read the same way.

### What each deliverable is, and how it is read

Read locally on the team's host, since every wait is forwarded there (`code.3`):

| stage | delivered when | `Delivered` |
|---|---|---|
| construct | the unit branch's head was committed at or after the start, and the kit reads the unit as `review` (planning complete, not yet approved) | `unit/<unit>@<head>` |
| code | the head was committed at or after the start, and `tasks.md` at the head (`git show HEAD:…`) has no `- [ ]` | `unit/<unit>@<head>` |
| verify | a `verify-<unit>-<stamp>.md` in the team's reports folder modified at or after the start | `report/<file name>` |
| merge (unit) | `bolt/<bolt>` holds the unit's change (`gather.changes`) | `bolt/<bolt>@<bolt head>` |
| fix | the fix branch's head was committed at or after the start | `fix/<bolt>/<name>@<head>` |
| merge (fix) | `gather.fix_merged` | `bolt/<bolt>@<bolt head>` |
| proof | a `proof-<bolt>-<stamp>.md` in the team's reports folder modified at or after the start | `proof/<file name>` |

For an amended construct, `place_stage` already reads `review` once the head has moved past the mark. Code reads the ticks at the head, not in the working tree, so "each in a commit" holds.

### The wait

`crew unit wait <unit> [--timeout <ms>] [--stuck <ms>]`, `crew fix <team> <name> --wait [same]` and `crew prove <team> --wait [same]` each find the slot (`ops` for the proof) and run one Python loop on the team's host, `plan _wait <team> --slot <slot> --timeout <ms> --stuck <ms>`. It holds a lock (`waits/<slot>.lock` under the team's state folder) for its whole life, and every ten seconds, or less when the timeout is nearer:

1. a stop-short handed to it (`needs/<slot>`) → print the words, delete the file, return;
2. no stage owed for the slot (it was ended meanwhile) → say how it ended, from the newest `stage.end` for it, and return;
3. the agent is not up → say it is gone with nothing delivered, return, record nothing (`stop` records the end when the slot is next used or freed);
4. deliverable and not working → record `stage.end` (`Ended: delivered`), remove the line, print what was delivered, return;
5. quiet past the limit with nothing to wait on (below) → print that it is stuck, return, record nothing;
6. timeout → print that it is still running and why, return, record nothing.

What it prints, each one line the conductor reads as the outcome:

```
swb-1-unit-1 delivered construct on a: its change is committed at 1a2b3c4, ready for review
swb-1-unit-1 delivered code on a: every task is ticked (4/4) at 1a2b3c4
swb-1-unit-1 delivered verify on a: the report is /home/…/reports/verify-a-20261008-1412.md
swb-1-unit-1 delivered merge on a: bolt/tenant-environments holds it at 1a2b3c4
swb-1-unit-2 delivered fix fix/tenant-environments/tidy: its branch is at 1a2b3c4
swb-1-ops delivered the proof of tenant-environments: /home/…/reports/proof-tenant-environments-20261008-1630.md
swb-1-unit-1 stopped short in code on a. It needs: <the agent's words>
swb-1-unit-1 is stuck in verify on a: quiet for 16 minutes, with no report saved and nothing it needs said
swb-1-unit-1 is no longer running: construct on a delivered nothing and said nothing it needs
code on a is still running after the wait's 3600000 ms: swb-1-unit-1 is waiting on 1 background task of its own; nothing is recorded yet
```

A stuck line adds "; crew could not read whether it waits on work of its own (<why>)" when the transcript could not be read. The defaults: `--timeout` stays 3600000; `--stuck` is 900000 (15 minutes), long enough for a turn's thinking and short enough that nobody waits an hour on a stage that is already over.

*Alternative:* keep `herdr agent wait` as the whole wait and check the deliverable after it. That is the ADR's option 3 moved into crew: herdr returns at the first idle, so the wait would have to loop anyway.

### Still running or stuck: herdr's state, then the agent's own background work

"Quiet" is herdr reporting anything but `working`. A quiet agent is still running when its session has background work it started and has not yet been told is over; the clock runs only when it has none.

The reading, from Claude Code 2.1.286's transcript (`~/.claude/projects/…/f9b10eee-83e1-4c51-991f-820f7a2fe367.jsonl`, a coder that ran suites in the background on 2026-10-08):

- a Bash call run in the background is answered by a record whose `toolUseResult` holds `"backgroundTaskId": "<id>"`;
- when it ends, the session receives `<task-notification>\n<task-id><id></task-id>…<status>completed</status>…`, recorded as a `queue-operation` and again as an `attachment` (`queued_command`).

`transcript.py` gains `pending(path)`: the background ids started in the transcript with no notification naming them. The session is found as `crew status` and `record.session` find it (`herdr agent get` → `agent_session.value` → `transcript.find`). The clock starts at the time of the transcript's last record, so a wait started long after the agent fell quiet does not wait the whole limit again; when the transcript can't be found or read, the clock starts when the wait first saw the agent quiet, and the stuck line says what could not be read (`read.1`). Nothing is refused for an unreadable transcript, and an id format that stops matching only makes the clock run sooner (`read.2`).

*Alternatives:* the processes under the agent's pane (an agent's process tree also holds MCP servers and shells, so "a child is running" says little); the agent declaring what it waits on (a brief rule in every brief, which ADR 0007 already rejected as option 2); the deliverable alone with a clock (a twenty-minute `wt merge` or a suite run would be reported stuck every time).

### Stopping short: `crew needs`, which ends the stage

`crew needs "<what it needs>"` is run by a stage's agent (`CREW_AGENT` is `<team>-unit-<n>`, or `<team>-ops` while a proof is owed). On the team's host it:

1. refuses anyone else, an agent with no stage owed, and empty words (`code.2`);
2. under the stages file's lock (`teams.9`), records `stage.end` with `Ended: short` and no `Delivered`, and removes the line;
3. hands the words to the waiter: if a wait holds the slot's lock, it writes them to `needs/<slot>` for that wait to print; otherwise it tells `<team>-conductor`, marked `[crew tell from <agent>]` (`roles.4`): "<agent> stopped short in <stage> on <unit>. It needs: <words>".

The words reach only the conductor, never the run record (`record.3`); the entry's `Why` is "unit(a): code stopped short".

A stage that stopped short is over. The conductor gets the answer (the design agent's ruling, ops's reading, the user's word) and runs the stage again with the answer as its words: `crew unit run <unit> <stage> "<the answer>"`, `crew fix <team> <name> "<the answer>"`, `crew prove <team> "<the answer>"`. That is how every stage already starts (`teams.2`: a fresh agent), keeps one end per start (`record.5`) without a "resumed" state, and the fresh agent reads where the work stands from the kit, as every stage does.

*Alternative:* the conductor tells the waiting agent the answer and the stage carries on. The stage would have ended in the record and then gone on working, so crew would need a resume act, a mark to clear when the agent works again, and a guard against a wait that returns "short" again before the answer lands. A fresh stage needs none of it.

### Ops's proof is a stage

`crew prove <team> ["<words>"]`, forwarded to the team's host, refuses when the team holds no bolt or `<team>-ops` is not up; ends any proof still owed as `stopped`; tells ops, marked as from the caller, "Deploy the bolt and work the Proof in dev list of each of its units." with the words after it; records `stage.start` on `stage/<bolt>/proof`, `bolt/<bolt>` and `agent/<team>-ops` (`Why` "bolt(<bolt>): start proof"); and appends `ops <bolt> proof <entry id> bolt/<bolt>` to the stages file. Ops is not ended or restarted: it is a standing agent. `stop` on ops (a restart or `crew down`) ends an owed proof like a slot's stage.

Ops writes its results, the glyph list first, once, whole, when every list is worked or a failure stops it, to `{{REPORTS}}/proof-<bolt>-<YYYYMMDD-HHMM>.md`; a file written as it goes would be read as delivered at the first result.

### A fix waits the same way

`crew fix <team> <name> --wait [--timeout <ms>] [--stuck <ms>]` finds the fix's slot as `--merge` does and runs the same wait. The fix's stage is `fix` or `merge`, from the stages line.

### The run record

`stage.end` gains `Ended` (`delivered`, `short` or `stopped`) and, when delivered, `Delivered` (the object in the table above). Both go in `record.py`'s `EXTRA` and the descriptor's `%allowed`; a carry rewrites each branch file with the current descriptor, as `Card` and `Key` were added. `report/` and `proof/` join `KINDS`, so `crew trace report/<file>` finds its end. `Result`, `Tasks`, `Head` and `Observed` stay as they are.

Where ends are recorded:

- the wait: delivered (`Observed` absent);
- `crew needs`: short;
- `reap` (late): delivered only, `Observed: late`; a quiet stage with nothing delivered is left owed;
- `stop` (`--ending`): delivered when the deliverable exists, else `stopped`.

### The briefs

A `{{NEEDS}}` token, built once in `crew.py` beside `RESULTS` and filled for construct, coder, verify and ops, says: when you cannot finish without something only someone else can give (a decision, a fact about a live system, the user's word), run `<crew> needs "<what you tried and what you need>"` and end your turn; never ask in your pane, which nobody watches. Ending a turn to wait on something you started in the background is fine: crew knows your stage is over only when what it delivers is there.

- **conductor**: after `crew unit run`, `crew fix` or `crew prove`, run the matching wait in the background; its answer is the outcome, and you never read a pane for one. Delivered: go on (verify's report path is in the answer). Stopped short: get what it needs (the design agent, ops, or the user, through a card or the operator agents), then run the stage again with the answer as its words. Stuck: tell the user which agent and stage, through the operator agents, and run it again or wait again only on the user's word. Still running: wait again. Step 5 of the building loop becomes `crew prove {{TEAM}}`; the fix paragraph says to wait with `--wait` before `--merge`. The line "If it is waiting on a question for the user, leave it for the user" goes.
- **construct**: a premise found wrong, or a decision the stage can't finish without, goes through `{{NEEDS}}`; design gaps it can write around still go in its final message with the commit.
- **coder**: "When you pause, say what you tried and what you need" and the fix's "stop and say so" become `{{NEEDS}}`.
- **verify**: the report is saved once the command finishes; if the command can't run, `{{NEEDS}}`.
- **ops**: the proof file's path and "once, whole"; a proof that can't go on without the user's word or another team's environment goes through `{{NEEDS}}`.

## Risks / Trade-offs

- [The transcript format is Claude Code's, undocumented, and may change] → `pending` knows two facts, named in its docstring; when they stop holding, a quiet agent waiting on background work is reported stuck after 15 minutes: noise, never a wrong end.
- [A background task that never ends keeps a stage from ever reading stuck] → the wait's timeout still returns "still running … waiting on N background tasks", and the conductor sees it each hour.
- [A deliverable made by hand, such as a report file copied into the folder, ends the stage] → the deliverables are what crew already reads for stages; nothing else stops a person doing the agent's work.
- [Running a stage again after a stop-short loses the agent's context] → stages are already fresh agents that read the kit; a coder commits per task, so its successor starts from the ticks.
- [A conductor on the old brief waits for up to an hour where it used to return at once] → it returns at the deliverable, usually sooner than its pane-reading did; each conductor takes the new brief at its next fresh start.

## Migration Plan

Land, then pull on every host in one step. Stages owed when the bolt lands keep their lines; the start time comes from the entry id, so they are read the new way at once. Conductors and ops take the new briefs at their next fresh start; stage agents are fresh for every stage. Rollback: revert; owed lines read as before.

## Proof in dev

None: crew has no dev environment, and the bolt's proof is its verification.

## Proof on real work

Once the bolt has landed and every host has pulled, and the conductors and ops have started fresh:

1. The next verify that runs suites in the background: `crew unit wait` does not return when the agent goes idle, and returns with the report's path once it is saved; `crew trace unit/<unit>` shows its `stage.end` with `Ended: delivered` and `Delivered: report/…`.
2. The next code stage that pauses: its agent runs `crew needs`, the conductor's wait returns with its words, and the run record shows `Ended: short` without them.
3. The next bolt proven: the conductor runs `crew prove`, ops writes `proof-<bolt>-<stamp>.md` to the reports folder, and the wait returns with its path.
4. A stuck stage, should one happen: the wait reports it within about 15 minutes of the agent falling quiet, and the conductor takes it to the user rather than waiting it out.

## Task notes

### 1.1

In `record.py`, add `Ended` and `Delivered` to `EXTRA` and to `DESCRIPTOR`'s `%allowed` (keep the comment above `EXTRA` true), and `report/` and `proof/` to `KINDS` and the docstring's object list. `oneline` in `crew events` shows `Ended` after `Result` ("→ review, delivered unit/a@1a2b3c4"); keep the line short.

### 1.2

`transcript.py` `pending(path)`: parse each line as JSON; collect every `toolUseResult.backgroundTaskId` (a dict field, guarded); collect every id in `<task-id>(…)</task-id>` within any string holding `<task-notification>`; return the started ids not notified, in order. Also `last_at(path)`, the newest `timestamp` of any record. Say both facts, and the version and session they were read from, in the module docstring. A missing or unreadable file returns `None` from both, never an empty list read as "nothing pending".

### 1.3

`plan.py`: one function per kind of deliverable, `delivered(t, line) -> (object, sentence) | None`, from the table in *What each deliverable is*. The start is `datetime.strptime(id[:16], "%Y%m%dT%H%M%SZ")` in UTC; a line whose id doesn't parse gives `unknown` and no end (`read.1`). Read the place with `gather.place` for construct (its `planning` and the `place_stage` rule, honouring the plan's `Amended` mark as `slot_stages` does) and git directly for heads, times (`%cI`) and `git show HEAD:openspec/changes/<unit>/tasks.md`; the reports folder with `gather.REPORT` and a proof pattern beside it.

### 1.4

`plan.py` `_wait <team> --slot <slot> --timeout <ms> --stuck <ms>`: the loop in *The wait*, holding `fcntl.flock` on `<state>/waits/<slot>.lock` (created as needed) for its life. Read the agent with `crew.agent_status`; its transcript through `herdr agent get` → `transcript.find`. Record ends through the same code `stage_ends` uses, under the stages file's lock, so a wait and a `reap` can never both record one end. Poll with `time.sleep(min(10, remaining))`.

### 1.5

`stage_ends` (`plan _ends`): the late path records only lines whose deliverable exists and whose agent is not working, with `Ended: delivered`, `Delivered` and `Observed: late`; `--ending` records `delivered` when the deliverable exists, else `stopped`. Keep `ops` lines (whose slot is not in the slots file) instead of dropping them; drop an `ops` line only when the team no longer holds its bolt. The `--waited` path goes; the wait records its own end.

### 1.6

`crew needs "<words>"` in `plugin/bin/crew`: the team and slot come from `CREW_AGENT` (`<team>-unit-<n>` or `<team>-ops`; anything else is refused naming the caller), then `load_team`, `forward`, and `plan _needs <team> --slot <slot> "<words>"`, which does *Stopping short*. The tell, when nobody waits, goes through `crew.tell(..., sender=<agent>)`. The lock test is `flock(LOCK_EX | LOCK_NB)` on the slot's wait lock: taken means nobody waits (release it at once).

### 1.7

`plugin/bin/crew`: `unit_wait` passes `--timeout` and `--stuck` to `plan _wait` and prints its line; `crew fix <team> <name> --wait [--timeout <ms>] [--stuck <ms>]`; `crew prove <team> ["<words>"]` and `crew prove <team> --wait [...]` as in *Ops's proof is a stage* (the start recorded with `entry`, like `run_stage`; the tell through `py tell` with the caller as sender); `stop` runs `plan _ends --slot ops --ending` for ops when a proof is owed, as it does for a slot. Update the usage header (`docs.2`).

### 1.8

`crew.py`: `NEEDS`, built from the crew path like `signal_how`, filled as `{{NEEDS}}` for the team's roles. Briefs as *The briefs* says; keep each brief's other lines. In `conductor.md`, the *Running the stages* paragraph after the table, step 3 and step 5 of the building loop, the stop-short paragraph after it, and *Fixes*. In `ops.md`, *Proving the bolt*. In `verify.md`, *The report*.

### 1.9

`tests/t-stage-ends.sh` (new, its opening comment saying what it proves; `tests.2`), driving the stub herdr's status and a scratch transcript at `$HOME/.claude/projects/x/sid-<pane>.jsonl` for the stub's session id (change the stub only if it can't give one; `tests.4`):

- construct quiet with nothing committed and `--stuck 0`: stuck, nothing recorded; commit the change: delivered, `Ended: delivered`, `Delivered: unit/a@<head>`;
- code with every task ticked before it began: not delivered until a new commit;
- verify with an old report in the folder: not delivered; a report saved after the start: delivered with its path;
- a transcript with a `backgroundTaskId` and no notification: not stuck, the timeout line says "waiting on 1 background task"; add the notification: stuck;
- no transcript: stuck, saying what could not be read;
- `crew needs` with a wait holding the lock (start the wait in the background with a long `--stuck`): the wait prints the words; without a wait: the conductor is told, marked as from the agent; neither puts the words in the run record; refused for the conductor and for an agent with no stage owed;
- the agent gone: said, nothing recorded;
- a fix's `--wait` and `crew prove` / `--wait` with a proof file, the start and end on `stage/<bolt>/proof`.

### 1.10

Existing tests that read the old behaviour: `t-record-team.sh` (the wait's "settled" line; the late code end at 1/2 tasks, which is no longer an end, so tick the last task in a commit first, or assert that no end is written and then that one is once it is ticked), `t-amend.sh` (its construct wait), `t-fix.sh` (the merge end's fields). `t-briefs.sh`: pin `crew needs` in construct, coder, verify and ops; in the conductor, `fix … --wait`, `prove`, "never read a pane" and stuck; ops's `proof-<bolt>-` path, and `/tmp/ops-proof` gone (`tests.6`).

### 1.11

`teams.4`'s *Details* in `docs/architecture/teams.md` lose "`crew unit wait` still ends at herdr's settle until … lands: `_open.md`." and gain the sources (`plan.py` `_wait`, `_needs`, `transcript.py` `pending`, `tests/t-stage-ends.sh`); the `teams.4` bullet leaves `_open.md`. README's *Seeing what happened* gains `Ended` and `Delivered`, and the commands `crew needs`, `crew fix … --wait` and `crew prove`; `plugin/skills/crew/SKILL.md` the same (`docs.2`).
