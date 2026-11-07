# Design: a landing sluice sent back reads as its team's fix, not a stop

## Context

The proposal gives the box's case. Rules this change relies on: `plan.16`, whose landing is ops's submission and whose refused landing is held for its team's fix; `plan.8`, which has a conflict with main taken into the bolt by a fix submitted to the bolt; `plan.18`'s reading of 2026-10-24, which makes a refusal the bolt's only when sluice names the bolt's content, a conflict or a failed check, and any other refusal a stop that holds nothing; `read.1`, which says what crew can't read is said and never guessed; `read.2`, which has crew read another tool's output by facts checked against the tool as it is now; `code.7`, which makes a decision a function of facts; `roles.5`, which has crew build no mechanism a tool of the family holds. The change touches the areas of `plan.md` (`plugin/lib/plan.py`), `teams.md` (`plugin/bin/crew`), `briefs.md` (`plugin/skills/`), `tests.md` (`tests/`) and `docs.md` (`README.md`, `openspec/`). It departs from no rule.

What crew reads of sluice was read at agentplot/sluice v0.68.1, the fleet's pin on swancloud's main on 2026-11-06, and at its main, `0b15d250`:

- **The record.** `crates/sluice-core/src/records.rs`, `Submission`: `state`, `head`, `failed` (each `FailedTask` with `task`, `hash` empty for a check left without a result, `system`, `flaky`, `not_run`), `result`, `conflict` (`paths`, `with`) and `tested` (`combination`, `on`, `submissions`). `sluice status <n> --json` prints it, decided or not. `on` is main's revision the candidate was formed on; `combination` is the candidate, which only sluice holds.
- **The driver.** `crates/sluice/src/profiles/worktrunk/wt_submit.rs` reads what stands before it submits (`standing_in`, in `profiles/worktrunk/mod.rs`) with `sluice submit <branch> --status --json --worktree <place>`. Where another host takes the branch's requests in (clause 137), `submit_pull` follows a request across (`pulls.rs` `follow_across`) and answers a request whose head carries sluice's failed check with `{state: "failed" | "conflict", title, summary}`, exit 1 or 2, and no `sends`. `standing` refuses that document, so `wt submit` exits 3, `INTERNAL`, saying "could not read whether a submission stands, so nothing was submitted". That fault is sluice's, and agentplot's planner takes it; crew does not work around it.

## Decisions

### Decision 1: a refusal stands until something is submitted at its head, or the head moves

`sent_back(entries)` reads each bolt's `bolt.submit` entries in order. A refusal naming a head (`Refused` with `Head`, written by `landing_not_landed` from sluice's record) sets the bolt's standing refusal, with its words and sluice's number. A later entry that submitted nothing at that head keeps it: crew's own refusal before submitting, which names no head, and a stop that names no submission of sluice's at the same head, as the box's 22:28Z stop. Every other entry lifts it: a submission queued, a pull request left standing (which readied and submitted it), a landing, a stop naming a submission of its own, and a stop at another head. `refusals` is `sent_back` without the number, and `stops` leaves out a bolt whose refusal stands, so no reader says a stop over it. Each reader already holds a row on `held_at` at its present head, so a fix that moves the head lifts the hold as before.

Considered: rewriting the stop that `landing_end` records when the submit exits 3. That stop is right on its own terms, sluice's driver failing with nothing submitted, and the run record keeps it. What was wrong was reading it as lifting the refusal, which sluice's record still holds.

### Decision 2: crew bolt submit reads sluice's record before it submits at a sent-back head

`landing_submitted`, once it knows the head it would submit (GitHub's head, or the host's copy, `landing_head`), runs `landing_sent_back` before it reads the queue. With a refusal standing at that head, it reads sluice's record of the refused submission on the team's host (`SUBMISSION_STATUS`, `landing_due`) and returns crew's own refusal, so nothing is submitted, no worktree is cut, no `wt submit` runs and the pull request stays a draft. `sent_back_refusal` decides the words:

- the record out and the bolt's (`landing_blame`): what failed, from `sent_back_of` and `sent_back_said`, then the team's fix (Decision 3);
- the record out in any other state, which a decided record does not reach after a refusal: `None`, and the bolt is submitted as before, since sluice's record is what holds the outcome;
- the record standing, or not readable: the words the refusal was recorded with, why, and the team's fix with no command, crew not able to say what failed (`read.1`).

A head crew can't tell before it submits, as for a kit with no origin, asks nothing, and the submission goes on as before. A run record that can't be read refuses the submission, naming why, since whether the landing was sent back can't be told.

Considered: reading sluice's state of the landing's pull request, `sluice submit main --status --json --worktree <place>`, which also answers where another host took the request in. It needs the landing's place cut first, its first pass takes requests in, and for a request followed across it gives sluice's check's title and summary, a check's words, which crew does not read for what failed. It is the read sluice's driver fails on; leaning on it would build crew around sluice's fault (`roles.5`).

### Decision 3: the way on is the team's fix, then the submit

`team_fix_said(bolt, team, s)` gives what is the bolt's and how it moves on, never a submit at the head sluice sent back:

- a failed check: the bolt's conductor mends it by a fix it submits to the bolt, `crew fix <team> landing-<n> "Mend what sluice sent bolt/<bolt>'s landing back for: <what failed>" --bolt <bolt>`;
- a conflict: the conductor takes main into the bolt by a fix, `crew fix <team> take-main-<main's revision tested on> "Take main into the bolt: sluice's <what conflicted>" --bolt <bolt>`, its words starting `TAKE_MAIN` so its row reads as taking main first, as a conductor's take-main fix does (`plan.8`, `teams.21`);
- then `crew bolt submit <bolt>` submits the landing again at its new head once that fix has merged into the bolt.

`crew fix` takes either path, a team crossed to Flume included (`flume_fix`), so the command runs as printed; its words hold no double quote. `landing_end` takes the bolt's team from `landing_close_out` and gives ops these words in place of "then you submit again". Where it has no team, as a direct `landing_said`, it names "its conductor" and no command.

### Decision 4: every reader says the team's fix

The kit's landings card's held row and the rail's land line keep their words and add that ops submits the bolt again once its team's fix has merged. `crew bolts` reads each partition's run record once (`bolts_sent_back`, `partition_entries`) and gives each held bolt whose refusal stands at its head now `sent_back`, `{head, words, submission}`, its text a line under the bolt, `landing: sent back at <head>, its team's fix: <sluice's words>; once that fix has merged, crew bolt submit <bolt> submits it again`. A run record crew can't read is named once at the end, `<label>'s run record can't be read (<why>): which landings sluice sent back is unknown`, and the command still shows the rest.

### What the box gets, and what waits on sluice

On the box today the landing at `977138a` was taken in on another host, and crew holds no number for it: its 21:28Z entry left the pull request standing, and sluice's record on the box has no submission of it (the sibling fix `a-landing-in-another-hosts-queue-reads-as-in-the-queue`, which waits on sluice). So crew's run record holds no refusal of it, and this change has nothing to hold the row by. Until sluice's fix of `standing_in` reaches the box, a `crew bolt submit` at that head runs `wt submit`, which refuses with exit 3, and crew records it stopped and prints sluice's words, as today. Once crew records a sent-back landing with its number, as it does for a landing taken in on its own host, a submit at that head is refused before `wt submit` runs, and the row and `crew bolts` read the team's fix.

The resubmit after the fix runs through `wt submit`, the landing's own command. It does not wait on sluice's fix: once the fix merges, sluice's push moves `bolt/<bolt>` on GitHub, so the request's head moves, sluice marks it a draft, and the failed check sluice posted was on the old head. `standing_in` then reads the request open at the new head, a draft, standing nothing, and `wt submit` submits it (`pulls.rs` `follow_across` reads sluice's check on the request's current head; `mod.rs` `standing`). sluice's fault is met only by a submit at the head sluice sent back, which crew no longer makes where it holds the refusal.

## After deploy

None. Every case is held by the logic tier on sluice's recorded records and by `t-journey-land` on the stubs; what the box runs is swancloud's pin, not a step of this change.

## Task notes

**1.1** `plugin/lib/plan.py`: `sent_back`, `refusals`, `stops`. Logic: `tests/py/test_landing.py` `TestTheStops` (`test_a_later_landing_or_refusal_supersedes_it` with a stop naming its own submission; `test_a_stop_that_submitted_nothing_leaves_a_sent_back_landing_its_teams_fix`), `tests/py/test_landings.py` (`test_a_submit_that_submitted_nothing_at_the_refused_head_leaves_the_row_held_for_its_teams_fix`).

**1.2** `plugin/lib/plan.py`: `sent_back_of`, `sent_back_said`, `team_fix`, `team_fix_said`, `sent_back_refusal`, `landing_sent_back`, its call in `landing_submitted`; `submission_of` keeps `tested`. Logic: `tests/py/test_landing.py` `TestASentBackLanding` on sluice's recorded `wait-failed-ran.json` and `status-all.json`, and `TestTheSubmission` (`test_a_bolt_whose_landing_failed_a_check_reads_as_its_teams_fix_and_is_not_submitted_again_at_its_head`, `test_a_sent_back_landing_whose_record_cant_be_read_is_still_its_teams_fix`, `test_a_sent_back_landing_at_an_older_head_is_submitted_as_before`). End to end: `tests/t-journey-land.sh`, a conflict's landing submitted again at the same head.

**1.3** `plugin/lib/plan.py`: `landing_end` and `landing_said` take `team`; `landing_close_out` passes it. Logic: `tests/py/test_landing.py` (`test_a_conflict_lands_nothing_and_is_the_bolts_to_take` and the submission case of 1.2).

**1.4** `plugin/lib/plan.py`: `landing_rows`, the rail's land line in `rail_rows`, `bolts_sent_back`, `bolts_data`, `bolts_text`, `bolts_view`. Logic: `tests/py/test_landings.py`, `tests/py/test_rail.py`, `tests/py/test_bolt_submissions.py` (`test_a_landing_sluice_sent_back_at_the_bolts_head_reads_as_its_teams_fix`), `tests/py/test_bolt_commands.py`.

**2.1** README's landings card paragraph, the crew skill's landing row and `crew`'s usage header for `crew bolt submit`.
