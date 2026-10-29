# Design

## Context

See proposal.md for why. What stands today, on this unit's branch:

- `stage_wait` (`plugin/lib/plan.py`) runs on the team's host and looks every ten seconds. On a look where the agent is not working and nothing is delivered, it reads the agent's transcript through `background(info)` for its pending background tasks and when it last wrote, and `quiet_verdict` decides whether the agent is stuck. `look` then prints `<agent> is stuck in <stage>: quiet for <n> minutes, with <what is missing> and nothing it needs said`, and the wait returns. Nothing else is read: the line says what crew did not find, and nothing of what the agent said or committed.
- `transcript.py` reads a session's transcript for its pending tasks (`pending`), its last write (`last_at`) and whether its turn is over (`turn_over`); it reads nothing of what the agent wrote.
- `delivered` already ends a code stage on a commit since it began when its head holds no task list: the planner's chore `a-code-stage-with-no-task-list-delivers-by-its-commit` (c541efc9), which this branch was built on (19a089d8), with its two cases in `tests/py/test_stage_ends.py`. The spec still says code delivers only at every task ticked.
- The conductor's brief (*Running the stages*, **Stuck**) has it tell the user at once, and the building loop's fix-round line calls a stuck fix round a stuck stage for the user.

Rules this design relies on: `teams.4` as amended 2026-10-23 (the stuck report carries the last words and the branch's commits, read before anyone is asked; a code stage whose head has no task list delivers by its commits), and record 0007 as amended, points 2 to 4; `read.1` (what crew cannot read is named, never guessed); `read.2` (a transcript field read only by a fact checked against Claude Code as it is now); `code.7` (the report is a decision on plain facts, the reads thin around it); `code.9` (the wait still answers within its own timeout); `record.3` (an agent's words never enter the run record); `briefs.11` (the conductor asks the design agent, ops or the planner before the user); `docs.2` (README, the skill and the usage header change together); `tests.4`, `tests.6`, `tests.11`, `tests.12`. Pages whose areas this touches: `teams.md` (`plan.py`'s wait), `signals.md` (`transcript.py`), `plan.md` (`gather.py`), `briefs.md` (`conductor.md`, the crew skill), `tests.md`, `docs.md`. No rule is departed from.

## Goals / Non-Goals

**Goals:**
- A stuck answer that says what the agent last wrote and what its branch holds since the stage began, so the conductor, and the user after it, never open a pane to learn it.
- A conductor that acts on what the report settles and asks only when it settles nothing.
- The spec saying what the chore already built for a code stage with no task list.

**Non-Goals:**
- Changing when a stage is stuck: the limit, the clock and the background-task reading stay as `quiet_verdict` has them.
- Crew judging the agent's words: crew quotes them; reading them is the conductor's.
- Any change to `stage.end`, the run record, the board or the mod.
- The agent's uncommitted files in its place: the record names the branch, and an uncommitted edit is not yet the stage's work.

## Decisions

### 1. The last words are the agent's last message since the stage began

The words are the text of the last message the agent's own session wrote since the stage began: every `text` block of the records of type `assistant`, not a subagent's (`isSidechain`), that share the `message.id` of the last such record holding a non-empty text block, joined in order, the message's time the earliest of those records' `timestamp`s. Claude Code writes each content block of one model message as its own record under one `message.id` (read 2026-10-23 on mac-studio from a session of 1,473 records, 135 of its 198 message ids spanning several records, the final `end_turn` message a single `text` record), so a message's text is read across its records; the coder confirms the fact on a current transcript and names it in `transcript.py`'s docstring with the others (`read.2`). A message written before the stage began is never quoted: a stage's agent is fresh, so an older message is another session's or crew's own greeting, and the report says the agent wrote nothing since the stage began. When this fact stops holding the words read as none written, never as another's.

Alternatives: the last record of type assistant, which is often a tool call with no words; the whole turn's text, which repeats the agent's working narration; the pane, which `teams.4` and record 0007 rule out as the source of an outcome.

### 2. The branch's commits since the stage began, read in the kit

The commits are those on the stage's branch (`Owed.branch()`: `unit/<unit>`, `chore/<chore>` or the fix's) along its first parent from its head, committed at or after the stage's start, newest first, each as short sha, committer time and subject, read with one `git log` in the kit's main checkout on the team's host, where `deliverable_facts` reads the head. A chore's range starts beyond its bolt at the ref `gather.bolt_read` reads, as `gather.own_head` reads its own commits, so what its place took of what it comes after is not shown as its work (`plan.11`). The read is `gather.since`, which returns the lines or None when git refuses, and the filter by time is the decision's. The report lists at most ten and counts the rest.

Alternatives: `<start head>..<head>`, which needs the head at the start, a field `stage.start` does not carry; the diff, which is too long for a wait's line and says what the commits' subjects already say.

### 3. The report is one decision on the facts both reads give

`stuck_said(o, agent, doing, missing, unread, words, commits)` builds the answer, a pure function (`code.7`); `look` calls it when the verdict is stuck, and `stage_wait` makes both reads in that look, only when `quiet_verdict` has said stuck, so no answer of stuck is made before them. The answer opens with today's line, its end now "and nothing it needs said through crew", then two parts, each on lines of its own:

```
swb-1-unit-1 is stuck in code on a: quiet for 20 minutes, with 2 of 4 tasks ticked at its head and nothing it needs said through crew.
Since it began, unit/a holds 2 commits, newest first:
  def5678 23:02Z feat(a): the second task
  abc1234 22:51Z feat(a): the first task
Its last words, at 23:06Z:
  > I stopped: tests/py/test_tenants.py fails the same way after two attempts.
  > The second task is committed; the third needs the table's name decided.
```

Where the branch holds none: `Since it began, unit/a holds no commit; its head is abc1234.` Where git refused: `crew could not read what unit/a holds since it began: <why>.` Where the agent wrote nothing since: `It has written nothing since the stage began.` Where the transcript cannot be read: `crew could not read its last words: <why>`, the why the one `background` already gives (no session, no transcript, not JSON lines). The clause on its own work (`unread`) stays on the first line as today. Times are UTC, as HH:MMZ when they fall on the stage's start's day and in full otherwise.

The words are quoted whole up to 2,000 characters; a longer message is cut at the last line's end under that, and a line says `(<n> more characters in <transcript path>)`. Ten commits and 2,000 characters keep the answer readable in the conductor's background-task output while carrying a whole final summary, which agents write in a few paragraphs.

The answer stays several lines: the words keep their own line breaks, and a one-line answer would fold a summary into one paragraph. README's "return with one line" is reworded for a stuck answer.

Alternatives: a report file the line names, which is one more read for the conductor and a file crew must sweep; the words in the run record, which `record.3` rules out.

### 4. When crew cannot read, it says so and still reports

A stuck verdict is a report to the conductor, not a removal or a stage decided, so a read that fails names what failed in the report and the report stands (`read.1`): no default text stands in, and nothing is retried in a loop. A wait that cannot read the words or the branch is not held back from answering, which would leave the conductor waiting an hour on a stage that is already stuck (record 0007, point 4).

### 5. The conductor acts on what the report settles

The brief's **Stuck** bullet says: read the report's words and commits first; when the words say the agent needs something, get it as for a stop-short (the design agent, ops, or the user through a card or the operator, `briefs.11`) and run the stage again with the answer as its words; when the commits and words show the stage's work done and its next step following, take that step, telling the user what crew refuses of it; only when the report settles nothing, tell the user which agent and stage, what the report carries, and run the stage again or wait again on the user's word. The fix-round line of the building loop sends a stuck fix round through the same reading. A stop-short and an agent gone are unchanged. The brief never sends the conductor to the pane (`teams.4`).

### 6. The code stage's deliverable goes into the spec as built

The chore's code and its two cases stand; this change's delta puts the rule in *The deliverable of each stage* and adds slc-1's case to `tests/py/test_stage_ends.py`: a fix round on a unit whose change is archived at its head (a head whose `openspec/changes/<unit>/tasks.md` is gone, so `ticks` reads 0 of 0) delivers at its commit (`tests.4`).

## Risks / Trade-offs

- [Claude Code changes how it writes a message's blocks] → The words read as none written and the report says the agent wrote nothing since it began; the conductor then asks the user, as today. The fact is named in `transcript.py`'s docstring with its version, so the next reading finds it.
- [An agent's words are long or hold secrets the agent echoed] → The quote is capped and goes only to the conductor's wait output, never the run record or a card; the conductor puts what it tells the user in its own words.
- [A commit whose committer time is earlier than the stage's start, as a cherry-pick keeps] → It is not listed; the head is still named, and the deliverable is judged as before. A rebase crew makes of a dependent rewrites committer times and may list rebased commits as new; the subjects say what they are.

## Migration Plan

None: the wait's answer changes on the host once crew's plugin reaches it (live or released, `plan.19`); a conductor on an older brief reads a longer stuck answer and still tells the user. Nothing is stored.

## After deploy

None: every behaviour here is a decision or a read the logic, contract and end-to-end tiers prove; nothing needs a live host.

## Task notes

**1.1** `plugin/lib/transcript.py`: add `last_words(path, since)`: None when the transcript is missing or can't be read (`lines` returns a string), else `(text, at)`, `text` "" and `at` None when no message since `since` holds text. Records: `kind(v) == "assistant"`, not `v.get("isSidechain")`, `message` a dict, `message.content` a list of dicts with `type == "text"` and a string `text`, or a string content. Group by `message.id`; a record with no id is its own message. `at` is `stamp(timestamp)` of the message's first record; a message with no readable time is skipped, never taken as since. Add the format fact to the module docstring, read from a current Claude Code transcript on the host, with its version and the session it was read from, as the other facts are. Cases in `tests/py/test_transcript.py`: a final message across two text records under one id, with a tool-use record between them that is skipped; the last text message chosen over a later tool-use-only record; a subagent's message never; a message before `since` not quoted, `("", None)`; a missing transcript None.

**1.2** `plugin/lib/gather.py`: add `since(cwd, ref, base=None)`: `git log --first-parent --format=%h%x09%cI%x09%s -n 200 <base>..<ref>` (or `<ref>` when no base), lines as `(sha, iso time, subject)`, None when git refuses. Contract case in `tests/contract/test_gather.py`: a unit branch with two commits after a start and one before lists all three with their times, newest first, and a chore's with its bolt as base lists only its own, naming in its docstring that `stuck_said`'s commit list assumes it.

**2.1** `plugin/lib/plan.py`: add `stuck_said(o, agent, doing, missing, unread, words, commits, branch, head, start)` as Decision 3 lays out; `words` is `(text, at)`, `("", None)`, or a string saying what could not be read; `commits` the lines `since` gave or a string saying what could not be read; it filters commits to those at or after `start`, caps at ten with "and <n> more", cuts the words at 2,000 characters on a line's end with the count and path, and quotes each line of the words with `  > `. `look` takes the report's facts as one more argument, `report=None`, and calls `stuck_said` when stuck; a stuck verdict with no report facts is a programming error (`fail`), never a bare line. Cases in `tests/py/test_wait.py`: the two existing stuck cases rewritten for "through crew" and the report's parts; commits and words both; none committed with the head; nothing written; each unread form; the ten-commit cap; the 2,000-character cut with its count and path; commits before the start left out; the unread clause on its own work kept on the first line.

**2.2** `plugin/lib/plan.py` `stage_wait`: when the look's `quiet` says stuck, read the words (`transcript.last_words` on the path `background` found, refactoring `background` to give the path or its why through one helper both use) and the commits (`gather.since` on `refs/heads/<branch>` in `t["kit"]["main"]`, a chore's base from `bolt_of_unit` and `gather.bolt_read` as `deliverable_facts` reads its own head), and pass them to `look`; read nothing more on a look that is not stuck. The end-to-end case in `tests/t-journey-units.sh`: a code stage with a task still open, one commit since it began and an agent message in its transcript (the stub's transcript, as the verify case writes it), waited on with `--stuck 0`, answers stuck listing the commit and quoting the message. Run `tests/moon-tasks` if the test's reads change, and commit `tests/moon.yml`.

**3.1** `tests/py/test_stage_ends.py`: add slc-1's case, a fix round's code stage (`owed("code")` with a start, a commit after it, `ticks` (0, 0)) delivering `unit/a@<head>` with "with no task list at its head", in a test named for a change archived at its head, citing the signal.

**4.1** `plugin/roles/conductor.md`: rewrite the **Stuck** bullet and the fix-round line of *The building loop* step 3 as Decision 5 says, the user still reached through the partition's operator as *Talking to the user* says. `tests/t-briefs.sh`: keep "**Stuck**" and "run the stage again or wait again only on the user's word" and pin the new words, among them "read the report's words and commits first" and "only when the report settles nothing"; replace the fix-round phrase with its new words.

**4.2** README (the paragraph on how a stage ends), `plugin/skills/crew/SKILL.md` (*A stuck stage*) and `plugin/bin/crew`'s usage header for `crew unit wait`: a stuck answer quotes the agent's last words since the stage began and lists its branch's commits since then, saying what crew could not read; a code stage whose head has no task list ends at its commit; the conductor reads the report before it asks.
