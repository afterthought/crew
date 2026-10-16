# Design

## Context

Record 0031 makes the rail the truth of what is open and whose; `crew-builds-every-card-from-its-facts` gives crew the act through which it withdraws and posts its own cards. This change makes the rail show every card and its read sweep what nobody will close, and gives each agent its open cards above its prompt. It relies on `state.4` (a view is computed from the files and writes nothing; `crew board` stays one), `read.1` (a card or a session crew cannot judge is kept, and said), `read.3` (a host that does not answer is named), `read.4` (crew withdraws only cards of its own rows and of crew's agents), `briefs.17` (crew claims no agent's name where it need not), `code.7`, `code.8` (the agents' views and the mod follow what crew models) and `briefs.16`. It touches the areas of `plan.md`, `tests.md` and `docs.md`.

## Goals / Non-Goals

Goals: every open card, a row's, a question's or a record's, shown on the rail with its owner; no card left open whose row or asker is gone; a lost or missing row card posted again by crew; each agent's open cards in its band.

Non-goals: raising any kind's card at its event, which that kind's change does; a question's checks, which `only-crew-raises-a-rows-card` makes.

## Decisions

### 1. The sweep acts on its host's cards, under its sign-in

Each host has its own Pending You sign-in, and a card posted under one reads "not found" under another, so a rail read sweeps only the cards posted on the host it runs on; a card of another host whose row is gone is listed with the host whose rail read closes it. On each rail read, `crew rail` and each refresh of the rail tab, crew already ends the sessions of closed cards (`a-cards-session-ends-with-its-card`). It now also sweeps, in `plan.py`'s `sweep_cards`, from a judgment that is a function of the rows, the run record and the cards, `sweep_judged`:

- a row's card whose row is gone is closed through the act's `row_card_close`, in its owner's name: with the event's outcome when the run record holds the event that ended the row ("its proposal was applied", "its bolt landed"), else withdrawn with why ("its proposal was dropped", "its bolt was dropped"), as `row_gone` reads it;
- a question whose asker herdr no longer lists, read from one listing of the asker's session, is withdrawn in the asker's name, which no session holds any longer: "<asker> ended; ask again if it still matters";
- an open row's card that reads not found is posted again under its key through its kind's raise (decision 2), its summary saying the older copy is dead (`a-card-lost-to-its-owner-is-posted-again`'s rule, now crew's act); one of a kind with no raise yet is recorded lost, for its owner to post again as its brief says until the series' last change; a lost card whose row is gone is recorded lost and posted again by nobody.

Before it acts, the sweep asks Pending You once, through one bridge, after every card it judges: in crew's own name, `crew`, never an agent's, so no agent's answers move to it (`briefs.17`). Pending You refuses crew another assistant's card in that assistant's words, and answers "not found" only for a card this host's sign-in no longer reaches, which is all the sweep asks. A host not signed in, or a bridge that fails, changes nothing and is said; so is a partition whose run record did not answer on its branch, on this host or on its main level's host, where its cards and rows are written. A land card of a bolt whose team's host did not answer is left, since whether its row is gone can't be told. A post or close Pending You refused is tried again only once it is ten minutes old (`CARD_RETRY`), so a refusal that stands is not tried, and recorded, at the rail tab's pace of thirty seconds. `crew board` sweeps nothing. The decisions are in `tests/py/test_rail.py` `TestSweepJudged`, the acts on a stand-in for Pending You, herdr and the raises in `TestSweep`, and their wiring through the stubs in `tests/t-cards.sh`.

### 2. A row's card that has none

A row whose card's post Pending You refused, or that no command posted, shows on the rail with no card and the refusal's words, so the next rail read posts it. The sweep posts it through its kind's raise, the one function of the row its kind's change gives it, which decides whether the kind's point has come: a batch's not before its summary is delivered, a landing's not before the bolt reads proven. The sweep calls it as `raise_<kind>(fleet, row, acts=None)`, looked up by name from the row key's first part, `plan.raise_proposal`, `plan.raise_batch`, `plan.raise_land`, `ops.raise_deploy` and `ops.raise_step`, handing it the rail's row and the act's `CardActs`; the raise reads its facts from the row's label and key, and posts through `row_card_change`, which posts a card the owner holds none of and posts again, saying the older copy is dead, one Pending You no longer finds. It returns the card's id, or None when the point has not come. A raise is called only on the host where the row's owner runs, the planner and main-level ops on the partition's main machine and a conductor on its team's, and only for a key in record 0031's form; a kind whose change has not landed has no raise yet, and its rows are left as they are.

### 3. The rail and the board

`crew rail` prints under every row its card's key and whether a card is open, whose and its id, or, with none open, the words of the refusal of its last post; and after its groups the open questions, each with its asker, its title as Pending You gave it to the sweep, and its age, a question it could not read listed with its key and asker, saying so; the open record cards apart as today; any open card whose row is gone with the host whose read closes it; and what the sweep did, each card closed, withdrawn, recorded lost or posted, and each partition it could not sweep, with why. A card is a row's, a decision record's or a question by its key (`card_kind`). The rail reads every run-record entry it gathered once, `rail_record` handing them to the sweep and the board, so a read still gathers each host's record once (`plan.12`).

`board.board_data` lists each partition's open cards, with whose each is and what it is, and the decision records proposed and not yet accepted or rejected, read from the `record.<status>` entries `crew record` writes on `record/<kit>/<number>`. `board.agent_views` gives each agent its open cards, questions among them, as `cards` beside `views` in the views file, and `status.js` draws them above the agent's view (`code.8`); the design agent's view shows each record proposed, with its card, or that the user settled it in the pane. `tests/py/test_board.py` pins the keys the mod reads, and `plugin/tests/status.test.ts` that the cards are drawn above the view.

## Risks / Trade-offs

- A rail read now asks Pending You after each card on its host, one bridge each read, and posts and withdraws cards, each a round trip under the host's sign-in; a host not signed in has the read say so and change nothing, and the next read acts.
- A question's title is not in the run record (`record.3`), so the rail reads it from Pending You at the read, in crew's own name. Pending You's guide says it refuses one assistant's card to another on a shared sign-in, so the title reads as Pending You's refusal until crew may read it without claiming the asker's name: the question is listed with its key, asker and age, saying so.
- A post or close crew makes in an owner's name moves that owner's label in Pending You to crew's bridge until the owner's next call, as the act does for every card of crew's; the sweep does so only when it closes a card or posts one, never to ask after one.
