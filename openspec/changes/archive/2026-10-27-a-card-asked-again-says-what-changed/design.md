# Design

## Context

crew raises its six cards itself (record 0031 §1, `briefs.11`, `briefs.13`) and keeps one card per thing, changed in place while it waits (§3). Once the user has answered a card, Pending You no longer changes it, so when its thing changes again crew acks it and posts a new card that follows it (`row_card_change`, `cards.revision`). Other raises post a card following an answered one too: a kit's landings card after a send that left bolts (`raise_landings`, `landings_step`), a deploy after the user declined the last one, a step after its deploy or the step before (`cards.follows_of`). Pending You shows a follow-on on top of its thread with the earlier cards folded below it, each with its answer (Pending You's guide, *Follow up with a new card*, read 2026-10-23), but the new card's own face says nothing of that answer, so the user reads it as the same card again.

Record 0031 as amended 2026-10-24, accepted on the user's card (req_a8f1924055614766b729), rules the second of its three changes for this unit: every card that follows one the user answered says first that they answered the earlier one, when and with what, and what changed since; a follow-on that cannot say what changed is not posted, the earlier answer standing. Its first change, a landing's approval standing through taking main in, is `a-landings-approval-stands-through-taking-main-in`, beside this unit in the bolt; it decides whether a landing asks again, and this unit decides what any card asked again says. Its third, an amendment's card titled by the amendment, is a chore. `plan.19`'s details carry the first change's clause for landings and nothing this unit changes.

What crew holds today, read on main at 6159160:

- The run record keeps a card's post (`card.post`, with `At`, `Card`, `Key`, `By`, and a landing's or deploy's `Head`), its changes, and its close (`card.close`, `State` closed, withdrawn, declined or lost, and crew's `Outcome`). It keeps nothing of what the user answered, and no entry may hold their typed words (`record.3`).
- Pending You's `get_request` gives an answered card's `answer` (`approved`, `choiceIds`, `answers`, `done`, `failedStep`, `handled`, `note`, `text`, as `cards.answer_lines` reads them). Neither its tool description nor its guide names a time for the answer, so crew's times come from its own run record.
- `card_posted` is the one act every post of crew's six cards passes through, `row_card_change`'s new versions and follow-ons among them.

Rules this rests on: `code.7` (each decision a function of plain facts), `record.3` (no typed text in an entry), `read.1` (what crew can't read is said, never guessed), `roles.3` (a check in crew rather than words in a brief), `briefs.13` (one card per thing; prose that wraps), `state.4` (the rail computed from the record), `code.8` (the agents' views follow what crew models). Pages whose area this touches: `plan.md` (`plan.py`), `record.md` (`record.py`'s field list), `briefs.md` (the cards' forms).

## Goals / Non-Goals

**Goals:**

- Every card crew posts that follows a card the user answered opens with what they answered, when, and what changed since.
- A follow-on with nothing changed is not posted, and the earlier answer stands; nothing re-raises it until something has changed.
- The rule lives in the act every post passes through, so no raise can post a bare repeat.

**Non-Goals:**

- When a landing asks again after its head moves: `a-landings-approval-stands-through-taking-main-in`.
- An amendment's card title: the chore `an-amendments-card-is-titled-by-the-amendment`.
- An agent's own question card, which its asker shapes through Pending You's tools (record 0031 §2).
- A card raised afresh for a new thing under a key whose last card closed at the event that ended it: the next proven bolt's landings card after nothing waited (Rows 0), the next deploy offer after a deploy ended. Each follows nothing today (`follows_of`) and asks a new question.

## Decisions

### 1. The answer is recorded at the close, in crew's words

When crew closes a card the user answered (an ack of an answered card in `card_closed` and `row_card_change`; a close as answered in a pane; a card picked up or resolved in Pending You whose reply still carries the answer), the close's entry carries `Answer`, made by a decision in `cards.py` from `get_request`'s reply and, for a kit's landings card, the bolts its rows offered (its recorded `Heads`): "approved", "declined", "ticked y and z, left w", "picked quiet", "done", "said step 2 did not work", "said you will handle it yourself", "answered in swancloud-ops's pane", each with ", with a note" when they wrote one. Option ids are named by what they name: `land:<bolt>` and `add:<unit>` by the bolt or unit, `unticked` as "left it out", others as they are. These are names crew minted, never the user's words (`record.3`); the note's words reach the follow-on only through Pending You's own thread.

Alternative weighed: reading the earlier card again with `get_request` when the follow-on is posted. A card acked or picked up no longer has its turn with the agent, and what `get_request` gives of its answer then is unread; recording at the close reads it while crew already holds the reply, once.

### 2. When: the times the run record holds

The opening names when the earlier card was posted and by when crew recorded the answer: the `At` of its last post and of its close, in UTC as the record writes them ("posted 2026-10-23 13:10 UTC, by 14:02 UTC"). "By" because the close can come after the answer: crew acks an answered card at the event that ends it. If Pending You's reply gives the answer's own time, a later change can say it exactly; nothing here assumes it does.

### 3. One opening, put on by the act

A decision `cards.answered_opening(earlier, since)` makes the paragraph: "You answered the card before this one, posted <time>, by <time>: <answer>. Since then: <sentences>." earlier is the answered card as the run record holds it (its post, its close, its `Answer`, or none, which reads "crew holds no record of what you answered"). `card_posted` finds the card a post comes after, `cards.answered_before(entries, follows, key, owner)`: the card its `follows` names when the run record shows it closed `closed` or `declined`; else, when the owner's newest act under the row's key is a withheld follow-on (Decision 5), the card that one names. With one found, it puts the opening first in the summary (cut again at whole sentences by `cards.prose`) and first in the details, and sets `follows` to that card when the builder set none. Builders stay as they are; the act holds the rule (`roles.3`).

### 4. What changed is the event's, handed in as sentences

Each raise that can post a follow-on of an answered card hands `since`, a list of sentences, to `row_card_change` or `card_posted`:

- A record revised (`raise_record`): its change note, "Revised at <sha>: <subject>".
- A proposal rewritten (`raise_proposal_at`, event replace): `cards.proposal_since(old, new)`, from the replaced proposal's commands and case and the new one's: each unit or chore it adds that the old did not, each the old added that it no longer does, each whose intent it words otherwise, each it newly drops or no longer drops, other commands changed counted, and "its case is rewritten" when the case differs. The same commands and case give nothing.
- A deploy (`ops.raise_deploy`): `cards.deploy_since(earlier head, head)`, "The offer is now <head>, where you answered on <earlier>", nothing when the heads are one. The earlier head is the followed card's recorded `Head`, or `head_anew`'s approved head.
- A step (`ops.raise_step`): following its deploy's card, "the deploy of <to> to <env> ended, and this is its step <n>"; following a step's card, "step <m> is behind you, and this is step <n>"; recorded again with another doer while answered, its change note.
- A kit's landings card (`raise_landings`): the outcome `landings_step` already writes for the close, what landed and where, what their send still lands, what was held and why, what was left, what reads proven or moved since; for a post following the kit's last card (`follows_of`), `landings_since(earlier Heads, rows now)`: each bolt that joins, each head that moved, each bolt they left that still waits.
- Any other follow-on of an answered card in `row_card_change` (its "ended" path, a kind changed after the answer): its change note.

A bolt the user left unticked counts as said: record 0031's amendment keeps it shown again so they can tick it later ("that is how i can choose to land it later", their note on req_518093a519084ad5bfdb), and the card says it waits because they left it. A send ticking nothing is then a card whose rows all say so.

### 5. Nothing changed: not posted, recorded, and left alone by the sweep

`card_posted`, with an answered card found and `since` empty or not given, posts nothing. It records a `card.post` on the row's object under the row's key in the owner's name, `Refused` in crew's words ("Not posted: nothing has changed since the user answered <card> by <time>, so their answer stands"), `Card` the answered card and `State: stands`, prints the same on standard error, and returns None, refusing nothing of the event (as a refused post already does, rail-cards "A row's card that Pending You refused is owed until it posts"). The rail's card line and the board's marker already show the last refused post's words (`last_refusal`, `board.marker`), so the views change nothing (`code.8`). The sweep's rows with no card (`sweep_judged`'s none) leave a row whose newest post under its key is a `stands`, so a rail read does not try it again and again; an event that raises it with something changed posts it, following the answered card. A raise that gives nothing changed, such as a conductor's agreement on a proposal whose card is withheld, is recorded withheld again, once per event.

Alternative weighed: posting the follow-on anyway with "nothing has changed" in its opening. The record rules it out: a card with nothing new is the repeat the user reported.

### 6. Where the in-memory close carries the answer

`row_card_change` builds the entries its follow-on posts against (`closed`) by adding the close it just made; that close carries the same `State`, `At` and `Answer` it records, so the follow-on's opening reads the answer it just closed. `raise_landings` reads the run record afresh for its follow-ons, as it does today.

## Risks / Trade-offs

- Two units of this bolt edit the landing paths of `plan.py` and `cards.py`: `a-landings-approval-stands-through-taking-main-in` changes when a landing asks again; this changes what it says. The merge settles the overlap; the opening is put on by `card_posted`, which the other unit does not change.
- A summary near Pending You's budget loses its last sentences to the opening; the details keep everything.
- A close from before this change carries no `Answer`; its follow-ons say crew holds no record of what was answered, as `read.1` asks, until those cards age out.

## After deploy

None: every behaviour here is crew's own decisions and acts, proved in the logic tier with Pending You stubbed, and nothing waits on a host.

## Task notes

**1.1** `plugin/lib/record.py` `EXTRA` gains `Answer`. `plugin/lib/cards.py`: `answer_said(got, offered=())`, the answer in crew's words from a `get_request` reply (Decision 1): reads the same fields as `answer_lines`, picked ids from `choiceIds` and from each `answers` entry, `offered` the ids the card offered so the ones not picked are named left (a kit's landings card's rows as `land:<bolt>`); returns None when the reply holds no answer. Cases in `tests/py/test_cards.py`: an approval, a decline with a note (no note words in the result), a landings send ticking `land:y` of `land:y`, `land:z` with a note ("ticked y, left z, with a note"), a choice `quiet`, a lone unit's `unticked`, a do with `done`, a failed step, handled, an empty answer.

**1.2** `plugin/lib/plan.py`: `card_closed` passes `Answer` on its `card.close` entry when the reply it read was answered (`cards.answer_said`), "answered in <owner>'s pane" when it closes as answered there (`here`); `row_card_change`'s follow and ended paths the same on the close they emit, and on the `closed` entries they post against, with `State` and `At` (Decision 6); `followed_closed` when the reply it reads still carries an answer. `raise_landings` hands `row_card_close` the offered rows (its `card_heads`) so the answer names what was left. Cases in `tests/py/test_card_commands.py` with the stub bridge: an answered card's close records `Answer`; a waiting card's withdrawal records none; a pane close records the pane.

**2.1** `cards.answered_before(entries, follows, key, owner)` and `cards.answered_opening(earlier, since)` (Decisions 3 and 5): earlier as `{card, posted, answered, answer}` from the run record, oldest first, the card the post follows closed `closed` or `declined`, else the card a newest `stands` post under the key names; the opening's words as Decision 3 gives them, times as `YYYY-MM-DD HH:MM UTC` with the date left off the second time when it is the same day; None from the opening when since is empty. Cases in `tests/py/test_cards.py`: a follow of an answered card; a follow of a withdrawn card (none found); a key whose newest post is a `stands` and no `follows`; no recorded `Answer`; since empty.

**2.2** `card_posted(acts, label, owner, b, where, entries=None, since=None)`: before the bridge opens, `answered_before`; with one found, the opening first in the card's summary and details, `follows` set when unset, or, with no opening, the `stands` record and print and return None (Decision 5). `row_card_change` takes `since` and passes it on its posts. Cases in `tests/py/test_card_commands.py`: a follow-on posted with its opening and `follows`; one with nothing changed recorded `stands` and not posted, Pending You never called; a later post with since following the stood card; a post following no answered card unchanged.

**2.3** `sweep_judged`'s `none` leaves a row whose newest `card.post` under its key is `State: stands` (Decision 5). Case in `tests/py/test_cards.py` or the sweep's existing cases: a proposal row whose card was withheld is not in `none`.

**3.1** `raise_record` passes `since=[note]`. `raise_proposal_at` passes, on replace, `cards.proposal_since` of the replaced proposal's `Do` lines parsed (`do_args`) and `Case` against the new one's (Decision 4), its other events none. `cards.proposal_since(old_argvs, old_case, new_argvs, new_case)` cases in `tests/py/test_proposal_card.py`: a unit added and one no longer added; an intent reworded; a drop added; a case rewritten alone; the same commands and case giving []. A proposal rewrite after an answered card posts with the opening, and with nothing changed is withheld, in `tests/py/test_proposal_life.py`.

**3.2** `plugin/lib/ops.py`: `raise_deploy` passes `cards.deploy_since(earlier, head)`, earlier the followed card's recorded `Head` (`cards.head_asked`) or `head_anew`'s `approved`; `raise_step` passes the step's sentences (Decision 4), from the followed card's key, `deploy/<env>` or `op/<env>/<m>`, and its change note when its kind changed after an answer. Cases in `tests/py/test_ops.py`: a deploy offered again at a newer head after a decline opens saying so; at the declined head with the same files, withheld; a step following its deploy's card opens with the deploy's answer and its place.

**3.3** `raise_landings` passes its outcome as `since` on its follow and close-then-post paths, and on its post path `landings_since(earlier Heads, rows)`, a decision in `plan.py` beside `landings_step` (Decision 4). Cases in `tests/py/test_landings.py`: a send ticking `y` and leaving `z`, `y` landed, the follow-on opens with "ticked y, left z" and says `y` landed and `z` waits; a send ticking none; a post following the kit's last card after a bolt joined.

**4.1** The run of the affected tests.
