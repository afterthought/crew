# Design

## Context

See proposal.md, *Why*. Today a batch card's and a long proposal card's reading is started inside `card_built`, once. `card_built` asks `CardActs.session` → `reading_open` → `session_open` for the link. On a `Refusal` it prints one line to standard error and builds the card through `unopened`, which says "Its reading could not be opened on the tailnet." and keeps the reason as `unread`, which `card_posted` and `row_card_change` record as `Unread` on the card's entry (`unread_of`). Every raise of these cards goes through `card_built`:

- a batch's: `crew review --wait` and the rail's sweep, both through `raise_batch` → `row_card_change`;
- a proposal's: its accept (`row_card_post`), its rewrite and a conductor's agreement (`raise_proposal_at` → `row_card_change`), and the rail's sweep (`raise_proposal`).

After the raise, nothing tries again on its own:

- `crew card session batch/<n>` and `proposal/<n>` start the reading when none runs and print its link, but do not change the card, so a card raised without its link keeps standing without it. Only `land_session` changes its card (`relinks`, `RELINKED`).
- `crew card wait batch/<n>`, with the card open and no session, waits on the card alone and says nothing about the missing reading.
- The rail's sweep (`sweep_judged`, `sweep_cards`) reposts a lost card and posts a missing one, but does nothing for a card that stands without its reading.

The landing card got its own fix in `a-landing-card-is-raised-with-its-session-every-time`: two tries at the raise (`landing_opened`), words naming `crew card session land/<bolt>`, and a wait that starts a missing reading (`land_start`). This change does the same for the batch's and the long proposal's cards, and adds a try on the rail's read, which the intent asks for and the landing has not got.

Rules this rests on:

- `briefs.9`: every card that asks the user to read something it cannot hold whole carries its reading's link.
- `briefs.13`: no command on a card for the user to run that an agent can run.
- `briefs.11` and `briefs.16`: crew raises and changes the planner's cards itself, in the planner's name.
- `read.1`: what can't be read is named, never guessed past.
- `record.1`: one entry per act, done or refused. `record.3`: an entry holds crew's own message.
- `code.2`: refusals go through `fail()`. `code.7`: decisions are functions of facts. `code.9`: a command answers within an agent's shell's time; a long wait is the wait command's own.
- `docs.2`, `docs.6`, `docs.7`.

Pages whose areas this touches: `plan.md` (`plan.py`), `record.md` (`record.py`), `briefs.md` (`planner.md`, the crew skill), `teams.md` (`plugin/bin/crew`'s usage), `tests.md`, `docs.md` (README, the spec). `code.8` is not engaged: the new `card.reading` act is one no view draws, and no stage, object or field `board.agent_views` reads changes.

## Goals / Non-Goals

**Goals:**
- A batch card's and a long proposal card's raise tries its reading twice before giving up.
- Such a card without its reading says that crew tries again and names the planner's command.
- Starting the reading by hand, by the batch's wait or by the rail's read changes the card to carry its link.
- Every try keeps its reason in the run record.

**Non-Goals:**
- The landing card. It keeps its own two tries and wait. The rail's read does not try a landing card's reading in this change; that is named for the planner.
- A proposal's wait. The planner reads a proposal's answer from its card, and no `crew card wait proposal/<n>` is in its brief.
- A batch card whose reading was opened and later closed by the user without a decision. That card still has a link to start again with `crew card session`, as today.
- Finding why the original reading failed. It was not kept, and from now on it is.

## Decisions

**1. The raise tries a batch's or a proposal's reading twice.** In `card_built`, for a `batch/<n>` or `proposal/<n>` key whose facts carry neither the link nor `unread`:

- **First try:** `acts.session(label, key, facts)`, as now.
- **On a `Refusal`:** print "card <key>: its reading could not be opened on the tailnet: <why>; crew tries once more" to standard error, and try once more under `READ.fresh()`, so whatever the first read kept is read again.
- **On a second `Refusal`:** build through `unopened` with the second reason, which the entry records as `Unread`, as now.

A landing's key is untouched: `landing_opened` already hands `card_built` its link or its reason. Every raise point listed in *Context* goes through `card_built`, so all of them get the second try.

*Considered:* reading the batch's or the proposal's facts afresh before the second try, as the landing does. Their reading already writes its files afresh on every start (`batch_folder_write` reads each unit's change at its commit from its team's host; the proposal's page is read from the open proposals), so a second start is the fresh read. *Considered:* a pause before the second try. Nothing read says how long, and each start already waits its own `CARD_START`.

**2. The card names who starts it.** For a `batch/` or `proposal/` key, `unopened` says, after the summary's first paragraph: "Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and the planner starts it with crew card session <key>; this card then carries its link." The summary is cut to Pending You's budget as now, and the details open with the reason as now. The printed line names `crew card session <key>` too, as a landing's does. The landing's words are unchanged.

The command is the planner's act, and the user is asked to run nothing (`briefs.13`).

**3. One function tries a reading again and changes its card.** A new `reading_again(fleet, label, key, acts)` does what `crew card session batch/<n>` or `proposal/<n>` does today, and then what `land_session` does for its card:

1. Read the card's facts: a batch's from `batch_facts` (the run record and the summary file), a proposal's from its open proposal as `raise_proposal` reads it.
2. Open its reading with `acts.reading(label, key, facts)`.
3. Record the try (Decision 5): on a `Refusal`, the refusal is recorded and raised again for the caller; on a start anew, it is recorded done; a session given again records nothing, being a read.
4. Change the card the planner holds under the key, when Pending You shows it waiting on the user (`card_waiting`), and when either the session was started anew or the run record shows the card standing without its reading (Decision 6's `reading_unread`, its time left out). The change is the kind's raise with `RELINKED` as its note: `raise_batch(..., note=RELINKED)` and, for a proposal, `raise_proposal` with a new `"relink"` event that `proposal_act` answers with `("change", RELINKED)`. Its `card_built` is handed the running session's link again by `session_open`.

The relink part is shared with `land_session`: its tail (read the card, `relinks`, change it, or say why it is left) moves into a function both call, with the kind's change passed in.

Three callers use `reading_again`:

- `card_session` for `batch/<n>` and `proposal/<n>`, after its own checks (`session_refusal`, `card_row`, `proposal_reads`), printing the link as now. An old batch key, `batch/<n>-<k>`, keeps its path.
- `batch_wait` (Decision 4).
- The rail's sweep (Decision 6), through a new `SweepActs.reading_again`.

*Considered:* the second condition left out, relinking only on a start anew. A sweep whose start worked but whose card change was refused would then give the link again on its next try and never put it on the card.

**4. The batch's wait starts a missing reading.** `batch_wait`, after it reads the card and the session:

- **Card held, no session recorded:** call `reading_again`. The card is changed to carry the link, and the wait waits on both as now.
- **The start refuses:** say once, on standard error, "batch/<n>'s reading could not be opened: <why>; crew card session batch/<n> starts it once that is mended, and the wait goes on for its card", and wait on the card alone. The refusal is recorded by `reading_again`.
- **Otherwise** as now, including the refusal when neither card nor session is there.

The choice is a small function of facts, `batch_unstarted(key, recorded, held, refused=None)` → `("wait", None)`, `("start", None)` or `("card", words)`, with its cases. Unlike the landing's wait, a refused start does not refuse the wait: the batch's card is answered with a tap, so the wait still has something to wait on.

**5. A later try is recorded as `card.reading`.** `reading_again` appends one entry per try that starts or refuses: `card.reading` on the row's object (`cards.row_object(key)`), by the planner, with `Key`, `Card` (the card held, when one is) and, when refused, `Refused` holding crew's message, which may end with plannotator's last line, as `Refused` already carries a tool's words (`record.3`). A session given again appends nothing (`record.1`: a pure read appends nothing). No new field is needed. `record.py`'s comment listing the card acts gains `card.reading`, and README's list of acts names it.

*Considered:* `card.update` with `Unread`. That records a change of the card that was never made. *Considered:* nothing recorded for a refused try. The sweep would then have no fact to wait ten minutes from, and the reason would be lost as the landing's once was.

**6. The rail's sweep tries a reading its card stands without.** A pure `reading_unread(entries, key, card, now)` reads this host's run record for the card:

- a done `card.post` or `card.update` of the card with `Unread`, or a refused `card.reading` under the key, marks it standing without its reading, from that entry's time;
- a done `card.post` or `card.update` of the card without `Unread` clears it;
- refused posts and changes, and done `card.reading` entries, change nothing.

It returns whether the card stands without its reading and its last such entry is `CARD_RETRY` (600) seconds old or more. With `now` left out it returns only whether the card stands without its reading (Decision 3).

`sweep_judged` gains `out["unread"]`: each held card of a `batch/<n>` or `proposal/<n>` row, posted on this host, for which `reading_unread` holds. Those cards are already among the held cards the sweep asks Pending You after. `sweep_cards` then, for each, when Pending You finds it and shows it waiting on the user (`card_waiting`):

- calls `acts.reading_again(label, key)`, recording `did="opened"` with "its reading opened at <link>";
- on a `Refusal`, records `did="left"` with "its reading could not be opened: <why>".

A card Pending You no longer finds is posted again by the held branch as now, whose `card_built` tries twice. The rail lists what was done as it lists every other row of the sweep.

*Considered:* trying on every read with no wait. A cause that lasts, plannotator off the path, would cost up to `CARD_START` on every read of the rail. Ten minutes is how long the sweep already leaves a refused post. *Considered:* reading whether a session serves (`card_recorded` and plannotator's list) instead of the record. That is a tool call inside the decision (`code.7`), and it would also try a reading the user closed on purpose.

**7. Briefs and docs.** `planner.md`'s *Batches* step 2 and its proposal paragraph say:

- a card raised without its reading names `{{TEAM_CMD}} card session <key> --label {{LABEL}}`, which starts it and changes the card to carry its link;
- the batch's wait starts a missing reading itself, and when it can't, says so and waits on the card;
- the rail's read tries it again too.

The crew skill's rows for `crew rail`, `crew card session` and `crew card wait`, the usage in `plugin/bin/crew` and `plan.py`, and README's card-session paragraph and list of acts say the same, together (`docs.2`).

## Risks / Trade-offs

- [A raise now takes up to two of plannotator's starts, about twenty seconds] → `crew review --wait` and a proposal's events already wait on the card's post. A raise whose first start works takes no longer than today.
- [A rail read with a card to try starts plannotator inside `crew rail`, up to `CARD_START` per card] → One try per card per ten minutes, and only for cards whose record shows them without their reading, which should be rare. `code.9`'s two minutes hold for a handful of such cards.
- [A relink from the sweep sends the user a change note] → One note, "Its reading is open again at a new link", the same one a landing's relink sends, and only for a card that had no link.
- [A crew on another host that does not know `card.reading`] → It reads the entry as an act it does not use; nothing parses it but the new code. Every host takes crew's main in the same step (CLAUDE.md, *After landing*).

## After deploy

- The next batch card or long proposal card raised after this lands either carries its reading's link, or its `card.post` entry holds `Unread` and, within the rail's next reads after ten minutes, a `card.reading` entry shows the sweep's try. The doer is swancloud-ops, once such a card is raised, reading the entries with `crew events` or `recsel`. No check in crew's tiers reaches a real plannotator on a loaded host.

## Task notes

**1.1** `card_built` in `plan.py`, Decision 1. The retry is for `batch/` and `proposal/` keys only. Cases in `tests/py/test_cards.py` through `ReadingActs(refusals=[why, None])` (one refusal then a link: two entries in `acts.sessions`, the card carries the link, standard error names the first reason and "crew tries once more") and `ReadingActs(refusals=[a, b])` (the card is built through `unopened` with `b`). Keep `test_a_card_whose_session_could_not_open_is_raised_all_the_same_saying_so` with the new words and two sessions tried. A landing's facts with `link` or `unread` still start nothing.

**1.2** `unopened`'s words and the printed line, Decision 2. Update the batch case's expected summary and standard error. Add a proposal case using the existing long-proposal facts in `tests/py/test_proposal_card.py` (or `test_cards.py`, whichever holds a proposal card with `session`), asserting the summary names `crew card session proposal/<n>` and stays within the budget.

**1.3** `raise_batch` with a first refusal then a link, in `tests/py/test_batches.py` beside `TestCards`: the posted card carries the link and its `card.post` entry has no `Unread`. Monkeypatch what `raise_batch` reads as the existing cases do.

**2.1** `reading_again`, Decision 3, and the shared relink taken out of `land_session`. `raise_batch` gains `note=None` (the default stays "Raised again: crew could not find its earlier copy"). `proposal_act("relink", ...)` returns `("change", RELINKED)` for the planner's own proposal; its case goes in `tests/py/test_proposal_card.py` or wherever `proposal_act`'s cases are. `RELINKED` moves above both if it must.

**2.2** `card_session` for `batch/<n>` and `proposal/<n>` calls `reading_again`, printing its link and the decided line as now. `tests/py/test_cards.py`'s `TestSessions` cases stay green. Add cases through `ReadingActs`: a start anew with the card waiting changes it with `RELINKED` and records a done `card.reading`; a card the user answered is left and says so; a session given again (`started=False`) on a card with a link changes nothing and records nothing; a refusal records `card.reading` with `Refused` and is raised.

**3.1** `batch_unstarted`, Decision 4, with its cases beside `batch_waited`'s in `tests/py/test_cards.py`. Then the wiring in `batch_wait`: once `card` is read and `card_recorded(d)` is None, call `reading_again` through the wait's `acts`; on its `Refusal`, say the words once and go on with `started` falsy; on success, read `card_recorded(d)` again as `started`.

**4.1** `reading_unread`, Decision 6, a pure function beside `refused_lately`, with cases in `tests/py/test_rail.py`'s `TestSweepJudged`: a post with `Unread` twenty minutes ago holds; five minutes ago does not; a later done `card.update` without `Unread` clears it; a refused `card.reading` five minutes after a post with `Unread` restarts the ten minutes; a refused `card.update` changes nothing; `now=None` gives the standing alone.

**4.2** `sweep_judged` gains `unread`, and `sweep_cards` its loop, Decision 6. `SweepActs.reading_again(label, key)` calls `reading_again(self.fleet, label, key, self)`. The stand-in `Acts` in `tests/py/test_rail.py` gains `reading_again`, given a link or a refusal per key, recording its calls. Cases in `TestSweep`: a waiting batch card whose post had `Unread` long ago is tried and listed `opened`; one whose try refuses is listed `left` with why; an answered card and a landing card with `Unread` are not tried; a lost card is posted again through its raise as now. The rail's text of the new `did` follows the existing format; check `TestText`.

**5.1** `record.py`'s comment on the card acts names `card.reading`. If a logic or contract case pins the list of acts, update it.

**6.1** `planner.md`, Decision 7. Check `tests/t-briefs.sh`'s planner lines and keep them green; add a want for the new sentence if the file has one per paragraph there.

**6.2** The crew skill's three rows, the `crew card session|wait|end` and `crew rail` entries of `plugin/bin/crew`'s usage and `plan.py`'s, and README's card-session paragraph and its list of acts, together (`docs.2`). `tests/t-docs.sh` stays green.

**7.1** `tests/t-journey-review.sh`, using the stub plannotator's `refuse-starts` count (`tests/stubs/plannotator`, already there):

- with one refusal set before the batch's raise, `crew review --wait` still starts one session and the card carries its link;
- for a later batch card raised with two refusals set, the card says its reading could not be opened and names `crew card session batch/<n>`, and the run record holds its `card.post` with `Unread`;
- the planner's `crew card wait batch/<n>`, run in the background with the refusals cleared, starts the session, the card's `update_request` carries the new link, and the wait waits. End it as the test ends other waits.

If the test now reads a file it did not, add it to `# Reads:` and run `tests/moon-tasks`, committing `tests/moon.yml`.

**8.1** Run `tests/suite logic`, then `tests/suite t-journey-review t-briefs t-docs t-cards` by name, then `tests/suite --affected` once at the end.
