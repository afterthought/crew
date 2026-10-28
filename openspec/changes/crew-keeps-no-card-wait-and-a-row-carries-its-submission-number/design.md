# Design

## Context

See proposal.md for why. This change builds record 0046's parts 2, 4 and 5 for crew (accepted by the user 2026-10-28), under `teams.22` as amended and `teams.24`, read with record 0048's patterns (`roles.6`) and record 0047's wrapper rule (`roles.5`).

What stands on main today:

- `crew card wait <key>` (`plan.card_wait`, `batch_wait`) is a loop with no timeout: a batch's reads Pending You every `CARD_READ` (30 s) and the reading's result file every `CARD_POLL`; a landing's and a long proposal's read the result file. A batch's or landing's wait also starts a reading that is not running (`land_start`, `land_unstarted`, `batch_unstarted`). The planner's brief (step 2 of *Batches*) and the conductor's (*Cards*) start one as a background command; `crew.py`'s `two_bolts_said` tells a restarted conductor to start one.
- A card's tap already wakes its owner through the fleet's wake mod once the owner has adopted the card with `get_request` (rail-cards "An agent never runs Pending You from npm or waits on a hold"). `crew card read <key>` (`card_read`) reads where a card the caller holds stands, and for a kit's landings card prints what to land.
- A reading's decision is plannotator's `result.json` in the key's folder, `~/.local/state/crew/cards/<label>/<key>/` (`CARDS`), read by `card_result`; nothing pushes it.
- Every rail read hands `crew card sweep --label <label>` to each host of the partition (`sweep_sessions`, `code.3`), which ends the sessions of closed cards and gone rows there; the main machine's rail read also runs `sweep_cards`, which closes, withdraws and re-posts cards.
- A merge's submission is made by the merge agent, `sluice submit bolt/<bolt> --no-wait --json` (`merge_command`, `coder.md` *Merging*), and a landing's by `crew bolt submit` through `SUBMIT`, which learns the number (`ID`) and keeps a background `sluice wait` in the landing worktree's `crew-landing` mark. Neither number is on any row: `crew bolts` shows a unit in merge by its stage alone, and the landing's number is recorded only at its end, in `bolt.submit`.
- sluice 0.51.3 on deneb: `sluice overview --json` prints `sluice/overview@1`, whose `branches[]` each hold `submissions[]`, "the submissions still in a chain, as `sluice status <id> --json` prints each" (sluice `crates/sluice-core/src/overview.rs`, `BranchView`): `id`, `branch`, `head`, `state` (`queued`, `waiting`, `testing`, `passed`, `landing`), and `from` (`agent`, `worktree` the branch or `pull/<n>`, `path` where the driver had a worktree, `head` the branch a pull request was opened from; `crates/sluice-seams/src/lib.rs` `Submitter`). Read from agentplot/sluice at cc634f72 and the live overview on deneb, 2026-10-28.

Area pages this change touches: `teams.md` (`plugin/lib/crew.py`), `plan.md` (`plan.py`, `gather.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `tests.md` (`tests/`), `docs.md` (README, the specs).

## Goals / Non-Goals

**Goals:**
- No process of crew's waits on a card or a reading (`teams.24`; record 0046 part 1).
- Every decision the user makes on a card or a reading reaches its owner at least once, and is acted on exactly once (`roles.6`).
- Every standing merge and landing shows its number on its bolt's row from the read after the submit, whoever made it (`teams.22`; record 0046 part 2).

**Non-Goals:**
- Any change to `crew unit wait`, `crew chore wait`, `crew fix --wait`, `crew review --wait` or the landing's own background `sluice wait`: ending them with their session is the sibling chore `a-wait-ends-with-the-session-that-started-it`; replacing the stage wait is Flume's (record 0047 move 3).
- A start-time reconnect hook or greeting list (record 0046 part 3: none is built in crew).
- Acting on sluice's push of an outcome into the submitter's session (sluice record 0068, not yet on the hosts); this change only puts the number where a session finds it.
- When a refresh reads anything at all: the sibling unit `a-rail-refresh-after-no-change-reads-nothing`.

## Decisions

### 1. `crew card wait` is removed, and refuses at once

The subcommand stays in the parser only to refuse, naming `crew card read <key>`, so an agent still carrying an old brief, or an old background command after a restart, learns what replaced it in one line and leaves nothing running (`code.2`). `card_wait`, `batch_wait`, `land_start`, `land_unstarted`, `batch_unstarted`, `CARD_POLL` and `CARD_READ` go. Alternative: drop the subcommand from the parser, which argparse refuses with a usage line naming none of what replaced it.

### 2. The owner's act is `crew card read <key>`

Record 0046 part 4 says an answer is read at the owner's act. The owner is already woken by the wake mod for a tap, and already runs `crew card read` for a landings card; one command for every card key is what the briefs can name (`briefs.11`, `briefs.12`). It gains three key kinds, each a decision of plain facts (`code.7`) over the card as `get_request` gives it and the reading's result:

- `batch/<n>`, the planner on the main level's host: what `batch_waited` decides today from the card and the reading together, now read once; a pane answer (`pane_answered`) said with whose pane; the card closed with the outcome (`row_card_close`), crew's own `batch.close` when no card closed (`batch_read_close`), the session ended. A card Pending You has lost is recorded lost (`card_lost`) and the reading still read. Nothing decided: it says the batch waits on the user.
- `land/<bolt>`, the bolt's conductor on the team's host, who holds no card under that key: the reading's decision alone, worded as `land_waited` words it, then set aside (`reading_decided`), the card untouched; it names `crew card session land/<bolt>` to open the reading again.
- `proposal/<n>` with a reading: the card's answer as today and, after it, the reading's decision (`waited`), a decided reading set aside.

Alternative: a new command per kind, or the decision printed by `crew card session`. Rejected: three commands for one act, and `card session` starts readings, which the intent keeps it to.

### 3. The rail's refresh tells a sent reading's owner once

A reading's send has no push of its own: plannotator writes `result.json` and nothing else. Record 0046 part 4 has crew read it at the rail's refresh. `crew card sweep`, which every rail read and follower refresh already runs on each host of the partition, finds each reading on its host whose result is approved or annotated and that carries no told mark, and tells its owner with `crew tell` (`roles.4`): the key, that the user sent it, and `crew card read <key>`, holding none of the user's words (`roles.6`: a nudge names the record). The mark, `told.json` beside `result.json`, is written only once the tell goes through; a tell refused because the owner is not up (`teams.11`) leaves it untold for the next refresh, so delivery is at least once. `crew card read` sets the result aside, so a read before any refresh leaves nothing to tell. A reading closed undecided is told nothing: there is nothing to act on, and `crew card session` starts it anew.

Alternative: a background process per reading watching its file. Rejected: that is the wait this change removes (`teams.24`). Alternative: the refresh records and acts on every send itself. Rejected for sends with words, Decision 4.

### 4. A batch is recorded read at the planner's read, and a wordless send also at the refresh

Today the wait records the batch read the moment the user sends, and prints the notes for the planner to pass on at once. With no wait, recording a send with notes at the refresh would let a bolt land (`review-batches` "A bolt lands only once every unit's latest change has been in a batch the user has answered") before the planner has passed the notes on, if the planner is down. So a send with annotations is recorded read only by `crew card read batch/<n>`, which prints the notes in the same act; a reading approved with no annotations, which has no words to pass on, is recorded read by the refresh too, its card closed "Read; no notes" and its session ended, whichever comes first. A tap on the card is read only at the planner's act: the wake mod already delivers it, and the refresh reads no Pending You card for it, which would cost a bridge call on every refresh.

### 5. A reading starts at its card's raise, by `crew card session`, and by the rail's retry

Nothing new: the two waits that also started readings go (Decision 1). The rail's retry of a card standing without its reading (card-sessions "The rail's read tries a reading its card stands without") stays as it is. A landing's reading the conductor read and set aside is opened again by the conductor's `crew card session land/<bolt>`, which changes the card to carry the new link (card-sessions "A landing's session follows the bolt's head").

### 6. A submission's number is read from sluice's queue on the team's host

The gather (`gather.py`), which already reads each kit on each host, runs `sluice overview --json` once in the kit's main checkout when the host holds a bolt of that kit, and returns each standing submission as `{id, branch, head, state, worktree, pull_head}`, guarding every field (`read.2`). The decision that maps them to rows is a function in `plan.py` (`code.7`): on `bolt/<bolt>`, a submission from `unit/<u>`, `chore/<c>` or `fix/<bolt>/<f>` is that line's; on `main`, one from `bolt/<bolt>`, or from `pull/<n>` whose `from.head` is `bolt/<bolt>`, is the bolt's landing. Its state is said in `STANDING`'s words. `crew bolts` (text and JSON), the board's ledger and `board.agent_views`, and the mod (`status.js`) carry it (`code.8`). sluice not on the host, failing, or printing another schema leaves every row of that kit's bolts on the host saying its submissions can't be read and why, never "none" (`read.1`).

Alternatives: a run-record entry at the submit. Rejected: a merge's submit is the merge agent's own `sluice submit`, which no crew command sees, and a record of crew's would repeat what sluice's queue already holds (`state.2`, `roles.5`; `teams.24`: every wait recorded where its subject lives, sluice's queue among them). Matching by `from.path`: rejected, since a pull request's submission has no path and the branch names already say whose work it is.

### 7. `crew bolt submit` waits again on a landing standing at the bolt's head

`landing_submitted` first reads the bolt's landing from the same overview read on the team's host. Standing at the head it would submit, crew hands `SUBMIT` that submission's number and tip, its existing wait-again words (seventh and eighth), so nothing is submitted, the worktree is made again if gone, the `crew-landing` mark is set, and `landing_ended` reads and records the end as for any landing (`plan.16`). Standing at another head, it says so and submits as before; sluice's resubmission from the landing worktree replaces it. This is how main-level ops picks a landing up from the row after its session ended; its brief says to run `crew bolt submit` again in that case.

### Rules relied on

`teams.22`, `teams.24`, `roles.4`, `roles.5`, `roles.6`, `state.2`, `state.4` (the sweep, not the board, writes; nothing is kept but the told mark beside crew's own result file), `read.1`, `read.2`, `code.1` (`gather.py` stays standard library), `code.2`, `code.7`, `code.8`, `code.9` (`crew card read` answers at once), `plan.16`, `briefs.11`, `briefs.12`, `docs.2`, `tests.10`, `tests.11`. No rule is departed from.

## Risks / Trade-offs

- [The planner is down when the user sends a batch's reading with notes] → The batch stays a row and holds its bolts' landings until the planner reads it; the refresh tells it once it is up. Slower than today's wait, never lost.
- [No follower runs on the reading's host] → The rail read on the main machine reaches every host with `crew card sweep`, as it does to end sessions; a host no rail read reaches is told nothing until one does, and the owner's own `crew card read` still reads it.
- [One more process per kit per gather] → `sluice overview` reads sluice's files once per kit with a held bolt on the host; the sibling refresh unit decides when a gather runs at all.
- [A standing submission whose `from.worktree` names no line of the plan, a hand submission] → It is shown on no line, and changes nothing.
- [Overlap with the sibling unit and chore] → Both touch `plan.py`, and the unit `board.py` and `gather.py`; crew names the overlap and forecasts conflicts, and the later merge takes the earlier's work.

## Migration Plan

The briefs change in the same change, so every conductor and planner is due a restart once it reaches its host (`teams.19`), and comes back told to read cards rather than wait. A `crew card wait` still running from before the landing ends with its session or when its host's crew is restarted; started again, it refuses. Nothing is rolled back but by reverting the change.

## After deploy

None: every behaviour here is proven by the logic, end-to-end and mod tiers in the coder's worktree, and nothing waits on a live host.

## Task notes

**1.1** `plan.py`: replace `card_wait` with a refusal naming `crew card read <key>`; delete `batch_wait`, `land_start`, `land_unstarted`, `batch_unstarted`, `CARD_POLL`, `CARD_READ`; keep `batch_waited`, `read_outcome`, `waited`, `land_waited`, `reading_decided`, `batch_read_close`, `pane_said`, which the read reuses. Drop the "crew card wait gives the decision" lines in `card_session`, `land_session` and `session_open`'s docstring for "crew card read <key> gives it". The parser's `card wait` stays for the refusal. Cases in `tests/py/test_card_commands.py`: the refusal, no process left.

**1.2** `plan.py` `card_read`: route `batch/<n>`, `land/<bolt>` and a reading `proposal/<n>` through a new decision, `reading_read(key, got, decided, answered)` returning what to print, what to close with and whether to record `batch.close`, and thin acts around it (`code.7`). `land/<bolt>` checks the caller is the bolt's conductor on the team's host (`session_refusal`), holds no card. Move `test_cards.py`'s `batch_waited` cases to the read; new cases in `tests/py/test_cards.py` and `tests/py/test_landings.py` for each key kind, decided and not, a lost card, a pane answer, and the refused close (review-batches scenarios).

**1.3** `plan.py` `card_sweep` on each host: a decision `readings_due(folders)` over each key folder under `CARDS/<label>` (`session.json`, `result.json`, `told.json`) giving the readings to tell and the wordless batch sends to record; acts: `crew.tell` to the owner (the planner for `batch/` and `proposal/`, the bolt's conductor for `land/`), `told.json` written after a tell that went through, and for a wordless batch send the close and `batch.close` as the read does. Its lines join the sweep's printed list. Cases in `tests/py/test_card_commands.py` (told once, untold on a failed tell, nothing for a dismissed reading, nothing after a read) and `tests/t-journey-review.sh` (the batch path end to end on stub herdr).

**1.4** `crew.py` `two_bolts_said` and its case in `tests/py/test_teams.py`: the waiting bolt as a row of its kit's landings card, crew telling the conductor when its reading is sent, `crew card read land/<bolt>`; no `crew card wait`. `hold.py` `crew_wait`'s docstring drops `crew card wait`, and `tests/py/test_hold.py` keeps its case as a command the regex still reads as crew's.

**2.1** `gather.py`: per kit main on a host holding a bolt of it, `sluice overview --json` with a timeout, returned as `submissions: [...]` or `submissions_error: "<why>"` in the kit's read; standard library only (`code.1`). A fixture of sluice 0.51.3's overview with standing submissions under `tests/py/` beside the 0.36.4 ones, from the sluice tests' shape (`overview_shows_every_branch_at_a_glance`).

**2.2** `plan.py`: `submission_rows(submissions, bolt, lines)` mapping as Decision 6; `bolts_data` gives each unit, chore and fix a `submission` ({id, state} or None) and the bolt a `landing` and `submissions_error`; `bolts_text` prints `#<id> <state>` after the stage and `landing #<id> <state>` on the head line. Cases in a new `tests/py/test_bolt_submissions.py`, beside `bolts_text`'s cases in `tests/py/test_chores.py`.

**2.3** `board.py` `ledger_rows`, `bolt_row` and `agent_views`: carry and draw the same fields; `plugin/hooks/status.js` draws them; `tests/py/test_board.py`'s case pinning every key the mod reads gains them; a case in `plugin/tests/status.test.ts` drawing a ledger with a merge and a landing standing.

**2.4** `plan.py` `landing_submitted`: read the bolt's landing from the overview on the team's host before submitting; standing at the head to submit, hand `SUBMIT` the number and tip; at another head, say it. A decision `landing_standing(submissions, bolt, head)`; cases in `tests/py/test_landing.py`; `tests/t-journey-land.sh` drives a second `crew bolt submit` with the stub sluice's overview (`$CREW_TEST_ROOT/sluice-overview.json`) holding the submission queued.

**3.1** Briefs: `planner.md` *Batches* steps 2 to 4 (woken by the card, or told by crew that the reading was sent, run `crew card read batch/<n>`; no background wait); `conductor.md` *Cards* (told when the bolt's reading is sent, `crew card read land/<bolt>`; no wait) and its restart words (the bands show each merge's number; a merge stage's agent waits on its own); `main-ops.md` (after a restart, a landing the row shows standing is picked up with `crew bolt submit <bolt>` again). `tests/t-briefs.sh` wants the new words and refuses `card wait`.

**3.2** `README.md`, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header together (`docs.2`): `card wait` gone, `card read` for every card key, the row's submission numbers, `crew bolt submit` picking a standing landing up. `tests/t-docs.sh` checks the skill names `crew card read <key>` and not `crew card wait <key>`. `tests/t-cards.sh` and `tests/t-journey-land.sh` lose their `crew card wait` runs for the read.

**3.3** `tests/moon-tasks` and `tests/moon.yml` after any test's reads change (`tests.10`), then `tests/suite --affected`.
