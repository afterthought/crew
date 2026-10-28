# Design: a landing is read from sluice's record

## Context

A landing today lives in one process. `crew bolt submit` (`plan.py` `bolt_submit`) submits the bolt from its landing worktree on the team's host (`landing_submitted`, `SUBMIT`). It waits on the submission a call at a time (`landing_ended`, `WAIT`), judges the outcome by main now (`LANDED`, `landing_end`, `landing_said`), and records it as a `bolt.submit` entry. Then it closes a landed bolt by calling `bolt_land` in-process. When that close is refused, it prints "bolt/<b> landed and was not closed: …; crew bolt land <b> closes it" on standard error, and nothing else. ops runs the command in the background, and if ops's session or that background task ends before sluice decides, the outcome is never recorded. The landing worktree also starts a second, detached `sluice wait <n> --timeout 24h` (`SUBMIT`'s `nohup`), whose process id in `crew-landing` is how `landing_now` tells that a landing is in flight. That process records nothing and makes one day-long call.

What happened on 2026-10-26 (record 0044, outcome 4; `plan.8`'s reading of 2026-10-27): wldn's switchboard-kit bolt landed. Its close was refused because a chore of its own was still at ready (`land_refusal`), and that refusal was said on stderr alone, which ops never read. The bolt was held a day until ops ran `crew bolt land` by hand.

Rules this design rests on:

- `plan.21`: a bolt sluice's record shows landed on main is recorded landed by the first crew act that reads it after, on any host, never only by `crew bolt land` by hand; a refused close is said on the row and in the run record until lifted. Its reading of 2026-10-27, with madswan-design, also holds here: sluice changes nothing, `sluice wait <n>` and the submission's state are readable from every host that submits to its branch (sluice statement 26), and a landing's waiter runs `sluice wait` from the background as `teams.5` has an agent wait.
- `teams.5`: an agent waits with `sluice wait <n> --timeout 9m --json` from the background, again while it exits 5.
- `plan.8`: no unit starts on a bolt whose landing is queued. `plan.14`: a landing records the commit main holds. `plan.16`: one procedure, ops's submission on the user's word. `plan.18`: main now is `origin/main` after a fetch.
- `read.1`: what can't be read is refused or leaves things as they were, named. `read.5`: the run record is read from the flywheel's branch, and a host is read over ssh only for its own kits. `state.4`: no view writes on refresh. `code.3`: commands about a team forward to its host. `code.7`: decisions are functions of facts. `code.8`: a change to what crew models updates `board.agent_views` and `status.js` with it. `code.9`: a write answers once it is made, and longer work waits with its own wait.
- `roles.1`, `roles.2`: the landing is ops's act on the user's word, and recording sluice's fact is crew's (see Decision 4).
- `roles.5`: crew builds no mechanism its tools are designed to hold. This change adds no wait of crew's. It reshapes the waiter that already exists and moves the recording into a read, which record 0044 names as crew's part: "a landing known the moment sluice records it is sluice's to tell and crew's to read".

Pages whose area this touches: `plan.md` (`plan.py`), `record.md` (`record.py`), `teams.md` (`plugin/bin/crew`), `briefs.md` (`main-ops.md`), `tests.md` (`tests/`).

## Goals / Non-Goals

**Goals**

- Any host knows a queued landing's submission number from the run record.
- A landing's outcome is recorded once, by whatever crew act reads the bolt first after sluice's record has it out, so no landing depends on one process staying alive.
- A landed bolt is closed by that read. A refused close is said on the bolt's head line and in the run record, retried at each later read, and recorded again only when its words change.
- The landing's background waiter waits as `teams.5` has an agent wait.

**Non-Goals**

- No change to sluice, and no notify of sluice's consumed here.
- No change to how an outcome is judged (`landing_end`, `landing_said`), or to the chain order of `crew bolt submit` across hosts (`submit_order`).
- No reading of sluice from a view's refresh: the board and the rail draw only what the run record holds (`state.4`, `plan.12`).
- No stall or hold reporting (record 0044 outcomes 1 to 3, 5): other units.

## Decisions

### 1. The queued submission is a run-record entry

As soon as `landing_submitted` has a submission number (sluice's id, or the one found for a pull request with `submission_of`), crew writes a `bolt.submit` entry on `bolt/<bolt>`. It carries `Outcome: queued`, `Submission: <n>`, `Head: <TIP>`, `Base: <main before>`, `Repo`, and, for a landing on the user's pane words, `From` and `Chars`. This happens before any wait. `record.py` gains the `Submission` field. The user's pane words are kept on the submitting host at this point (`landing_word_keep`), not at the landing's end, since the end may now be read on another host. `pane_word_of` and `last_submits` treat an entry with `Outcome: queued` as a landing in flight: it is not a landing and not a refusal. Its outcome entry copies `From` and `Chars`, so `pane_word_of` reads the outcome as it reads a landing today.

Considered: reading the number from the landing worktree's git dir on the team's host. Rejected, because a host that doesn't answer would hide it, and the run record is what every host reads (`read.5`).

### 2. One read of a landing, on the team's host, one at a time

`landing_read(fleet, label, bolt)` is exposed as `crew _landing-read <label> <bolt>` and refused on any host but that of the team holding the bolt, as `_land-row` is (`code.3`). Callers on another host forward it there with `crew.on_machine` and `crew.crew_argv`. It holds a flock on `<team state>/landings/<bolt>.lock` for its life. Under the lock:

1. It reads the bolt's last `bolt.submit` and the `bolt.land` entries since it (`partition_entries`).
2. With the last `bolt.submit` queued, it checks for a marker on the team's host, `<team state>/landings/<bolt>.<n>`. If the marker is there, another reader has already recorded this submission's outcome, so it prints the words that reader kept in the marker and goes to step 4.
3. Otherwise it runs `sluice status <n> --json` in the kit's main checkout (a new `SUBMISSION` script). `landing_due(doc)` decides what that means:
   - `standing`, for a state in `STANDING`: nothing is recorded, and it says the landing is still queued.
   - `out` with its exit as `wait` gives it (landed 0, failed 1, conflict 2, withdrawn 4): it runs the end `landing_ended` runs today from `LANDED` onward, with the record's document as `doc` and the verdict from it (`verdict_printed`). That end removes the worktree, reads the mains, judges with `landing_end`, marks the branch, records the outcome `bolt.submit` (with `Outcome: landed` added to a landing, so it is readable by field), or for a landing that did not land drafts the pull request (`landing_unheld`) and hands the landings card (`land_hand`). It writes the marker with its words, then goes on.
   - `unread`: nothing is recorded, and it says why, naming the host (`read.1`).
4. With the bolt's last `bolt.submit` a landing and the plan still holding the bolt, it tries the close (Decision 4).

Every write happens under the lock, and the marker is written on the same host, so two reads cannot both record. This holds even before the first reader's entry reaches the branch. The marker sits in team state, so it goes with the team's state, and it is keyed by the submission's number, so a later submission of the bolt is never mistaken for an earlier one.

The exit-3 path stays in `crew bolt submit`'s own wait (`sluice_failed`, `wait_again`, recorded stopped after `AGAIN` tries). It is the waiter's own handling of sluice failing. A later read that finds the submission out records its outcome, and `last_submits`, which keeps the last entry, then reads that outcome.

### 3. Who reads

- **The waiter.** `SUBMIT`'s detached process becomes a loop: `sluice wait "$id" --timeout 9m --json`, again while it exits 5, then `crew _landing-read <label> <bolt>`, then empty `crew-landing`. For a pull request (`$pull`) it is the same loop on `sluice wait main` from the place, as today. `SUBMIT` takes the label and the crew command to run as two more words. `landing_now` still reads the loop's process id, so `plan.8`'s refusal holds for as long as it waits.
- **`crew bolt submit`'s end.** `landing_ended` keeps its waits and its exit-3 handling. Once a wait returns an outcome, it calls the read on the team's host instead of recording itself, and prints what the read printed. It exits non-zero for a bolt the read says did not land, as now.
- **The team's read.** `reap`, on the team's host, before `rebase_and_tidy`: for each bolt the team holds, it runs the read when `landing_now` finds the landing worktree standing with its waiter not alive, or when every unit and chore of the bolt reads landed and the plan still holds it. This costs nothing for a bolt with neither, so an idle team's read is unchanged (`plan.12`).
- **`crew bolt land`.** `bolt_land` runs the read first, on the team's host, for a held bolt whose last `bolt.submit` is queued, so a hand close of a bolt whose landing was never recorded records it first.

The board and the rail do not read sluice (`state.4`, `plan.12`).

### 4. The close is crew's record of sluice's fact

A read that finds the bolt landed runs `bolt_land`'s code, as `landing_ended` does today, but without `may_write` of the caller. The word to land was the user's, the landing was ops's submission (`roles.1`, `roles.2`, `plan.16`), and the close records what sluice's record and main now say (`plan.21`, accepted after `roles.1`'s table and naming "the first act of crew's that reads the bolt"). The `bolt.land` entry is written `by` main-level ops, the role the close is in the name of (`record.emit`'s `by`, as a card of crew's own is), and its `Why` names the submission and the act that read it. `crew bolt land` by hand keeps `may_write` as it is.

A refused close (`Refusal` from `bolt_land`) is recorded as `record.emit(label, "bolt.land", [f"bolt/{bolt}"], refused=words, by=<ops>)` only when `close_refused_new(entries, bolt, words)` finds the bolt's last refused `bolt.land` since its landing carries other words, or there is none. It is printed on standard error every time. `crew bolt submit`'s "landed and was not closed" line keeps its words, minus "crew bolt land <b> closes it". It now says crew's next read closes it once that is mended.

Considered: leaving the close to ops's `crew bolt land`, with the refusal on the row. Rejected by `plan.21`: the close is never only a hand command.

### 5. The bolt's head line

`board_data` adds to each ledger `landing`: `{"queued": n}` while the bolt's last `bolt.submit` is queued, `{"unclosed": words}` while the bolt has landed and its last `bolt.land` since is refused, else None. It reads this from the run record entries `rail_read` already holds (`landing_of(entries, bolt)`, a decision of facts). `bolt_row` says "landing queued as #<n>", or "landed on main, not closed: <words>" with the attention gutter. The existing "landed" attention's why becomes the refused close's words when there are some, and `ops_view` draws the "landed" attention rows beside host and plan, so main-level ops's band shows it. `status.js` draws the views' rows as text and reads no new key. Its cases and `tests/py/test_board.py`'s pin of the keys it reads follow (`code.8`).

### 6. ops's brief

`main-ops.md` step 3: when the submission says a bolt landed and was not closed, crew's read closes it once what it named is mended, at the team's next read or at `crew bolt land <bolt>`, which ops may run. `tests/t-briefs.sh` is updated if it pins the old words.

## Risks / Trade-offs

- **The waiter reads with crew's code on the team's host.** That host's crew must be one that has `_landing-read`. A waiter started by an older `SUBMIT` makes no read, and the team's read covers it (Decision 3).
- **A submission sluice keeps standing forever.** If `crew bolt submit` is gone and sluice never decides, the bolt reads queued on its head line and nothing records it. That is the truth sluice's record tells, and it is said, not hidden.
- **The card's close with the user's words.** The words are kept on the submitting host. A read on the team's host closes the card through `tidy_after` and `landing_cards_closed` as today. When the words are not on the host that closes it, the card closes naming the pane, the time and the host where they are kept, as `bolt_land` already says. Whether that close should fetch the words from the submitting host is left to the design agent.
- **Stopgap under `roles.5`.** The waiter and its read are crew's until Flume submits a role's landing as a place (`roles.7`). Listing that in `_open.md` is the design agent's (`docs.7`).

## After deploy

None. Every behaviour here is proved by the logic tier, the mod's cases and the end-to-end landing journey on the stub sluice. The first real landing after the release proves nothing a test doesn't.

## Task notes

**1.1** `record.py`: add `Submission` to `%allowed` and `EXTRA`. Case in `tests/py/test_record.py` (or the file that pins `EXTRA`): an entry with `Submission: 412` round-trips.

**1.2** `plan.py` `landing_submitted`: once `f["ID"]` is known (after the pull-request lookup), `record.emit(label, "bolt.submit", [f"bolt/{bolt}"], frm=frm, Outcome="queued", Submission=f["ID"], Head=f["TIP"], Base=before, Repo=name, Chars=…)`. `landing_submitted` takes `label` and `frm`/`excerpt` (from `bolt_submit`). Move `landing_word_keep` from `landing_ended` to here. Decision function `submit_queued(entries, bolt)` → the queued entry or None (last `bolt.submit` with `Outcome` queued). `pane_word_of`, `last_submits`, `refusals`, `stopped_at` and `refused_at` ignore a queued entry as outcome-less. Cases in `tests/py/test_landing.py`.

**1.3** `plan.py` `SUBMIT`: the `nohup` lines become `nohup bash -c 'while sluice wait "$1" --timeout 9m --json >/dev/null 2>&1; rc=$?; [ $rc = 5 ]; do :; done; "${@:4}" _landing-read "$3" "$5"; : > "$2"' …`, or its equivalent, with the pull-request branch looping `sluice wait main` from the place. New words `$9` (label) and `${10}` onward (the crew argv for the host, `crew.crew_argv(fleet, host)`). Exit 0 from the first wait ends the loop. Only exit 5 loops. Contract or end-to-end: the stub sluice logs its argv (`tests/stubs/sluice`), and its `wait` answers 5 for the first `$CREW_TEST_ROOT/sluice-wait-<id>-fives` calls.

**2.1** `plan.py` new `SUBMISSION = r"""cd "$1" || exit 2\nexec sluice status "$2" --json\n"""`; decision `landing_due(code, out)` → `("standing", state)`, `("out", rc, doc)` with rc from `{"landed": "0", "failed": "1", "conflict": "2", "withdrawn": "4"}`, or `("unread", words)` (a non-JSON answer, a non-zero exit, an unknown state, or another schema than `sluice/submission@1`). Logic cases.

**2.2** `plan.py` `landing_read(fleet, label, bolt)` and `landing_read_cmd`: refused off the team's host (as `land_row`), the flock, the marker `team_state(t) / "landings" / f"{bolt}.{n}"` holding the words said, then Decision 2's steps. Factor `landing_ended`'s tail, from `LANDED` to the outcome's `record.emit` and print, into `landing_close_out(fleet, label, t, bolt, p, rc, said, doc, beside)`, used by the read. `p` is rebuilt from the queued entry: `path` = `<kit dir>/places/land-<bolt>`, `TIP` = `Head`, `OLD` and `before` = `Base`, `frm` = `From`. Route `_landing-read` in `plugin/bin/crew` as `_land-row` is routed, and in `plan.py`'s command table. Logic cases for the decision parts. End-to-end in `tests/t-journey-land.sh`.

**2.3** `close_refused_new(entries, bolt, words)` and the close in the read: `bolt_land`'s code with `may_write` skipped and `by` main-level ops (`crew.partition_of(fleet, label)` names it, as `land_hand`'s cards do). On `Refusal`, record if new and print. `landing_ended`'s own close goes, since the read closes. Logic cases for `close_refused_new`.

**3.1** `landing_ended`: after `WAIT`'s non-5 exit, or the exit-3 handling deciding the landing is not stopped, call the read on the team's host (`crew.on_machine(fleet, host, crew.crew_argv(fleet, host, "_landing-read", label, bolt))`, its stdout and stderr passed through) and judge landed from its exit (0 landed, 1 not). Keep the `refused` and `attempted` paths before any submission as they are. `tests/py/test_landing.py`'s cases that drive `landing_ended` follow.

**3.2** `reap`: Decision 3's gate, `landing_now(t, bolt)` = `(path, True, False)` or every unit and chore landed with the bolt in the plan. Then `landing_read` in this process, since `reap` runs on the team's host, with a `Refusal` printed and not raised.

**3.3** `bolt_land`: when the bolt is held and `submit_queued(entries, bolt)` is not None, run the read on the team's host first and re-read the plan after it. If the read closed the bolt, say so and return.

**4.1** `board.py`: `landing_of(entries, bolt)` (a decision of facts), the ledger's `landing` key, `bolt_row`'s words, the "landed" attention's why, and `ops_view`'s attention filter taking "landed". `tests/py/test_board.py`: the views pin, and cases for a queued and an unclosed bolt in a conductor's and ops's view. `plugin/tests/status.test.ts`: a band drawing an unclosed bolt's row.

**5.1** `plugin/roles/main-ops.md` step 3, as Decision 6. `tests/t-briefs.sh` if it checks those words.

**6.1** `tests/t-journey-land.sh` (its `# Reads:` line already names what it starts). Add three journeys: the submitter killed after the queue, the stub's record then landed, the waiter's read recording and closing it; the waiter stopped, and the conductor's next command recording it; and a landed bolt with a chore at ready, its refused `bolt.land` recorded once over two reads, `crew board` showing "landed on main, not closed", then the chore dropped and the next read closing it. Run `tests/moon-tasks` if any test's reads changed, and commit `tests/moon.yml`.
