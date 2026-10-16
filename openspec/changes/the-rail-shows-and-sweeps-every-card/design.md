# Design

## Context

Record 0031 makes the rail the truth of what is open and whose; `crew-builds-every-card-from-its-facts` gives crew the act through which it withdraws and posts its own cards. This change makes the rail show every card and its read sweep what nobody will close, and gives each agent its open cards above its prompt. It relies on `state.4` (a view is computed from the files and writes nothing; `crew board` stays one), `read.1` (a card or a session crew cannot judge is kept, and said), `read.3` (a host that does not answer is named), `read.4` (crew withdraws only cards of its own rows and of crew's agents), `code.7`, `code.8` (the agents' views and the mod follow what crew models) and `briefs.16`. It touches the areas of `plan.md` and `tests.md`.

## Goals / Non-Goals

Goals: every open card, a row's, a question's or a record's, shown on the rail with its owner; no card left open whose row or asker is gone; a lost or missing row card posted again by crew; each agent's open cards in its band.

Non-goals: raising any kind's card at its event, which that kind's change does; a question's checks, which `only-crew-raises-a-rows-card` makes.

## Decisions

### 1. The sweep withdraws

On each rail read, crew already ends the sessions of closed cards (`a-cards-session-ends-with-its-card`). It now also, under the host's connection: withdraws a row's card whose row is gone, with the reason ("its proposal was dropped", "its bolt was dropped"); withdraws a question card whose asker herdr no longer lists, naming the asker; and posts again, under its key, an open row's card that reads not found after the host signed in anew, its summary saying the older copy is dead (`a-card-lost-to-its-owner-is-posted-again`'s rule, now crew's act). `crew board` stays a view that writes nothing. The decisions, which cards to withdraw and which to post again from the rows, the record and herdr's listing, are in `tests/py/test_rail.py` `TestSweep`; the acts in `tests/t-cards.sh`.

### 2. A row's card that has none

A row whose card's post Pending You refused, or that no command posted, shows on the rail with no card and the refusal, so the next rail read posts it. The sweep posts it through its kind's raise, the one function of the row its kind's change gives it, which decides whether the kind's point has come: a batch's not before its summary is delivered, a landing's not before the bolt reads proven. A kind whose change has not landed has no raise yet, and its rows are left as they are.

### 3. The rail and the board

`crew rail` prints under every row its card's id and state, and after its groups the open question cards, each with its asker, its title and its age, the open record cards apart as today, and what the sweep did. `board.agent_views` gives each agent its open cards, questions among them, and `status.js` draws them (`code.8`); `tests/py/test_board.py` pins the keys the mod reads. The board's design band reads the `record.<status>` entries `crew record` writes to show proposed records.

## Risks / Trade-offs

- A rail read now posts and withdraws cards, each a round trip to Pending You under the host's sign-in; a host not signed in has the read say so and change nothing, and the next read acts.
- A question's title is not in the run record (`record.3`), so the rail reads it from Pending You at the read; a card it cannot read is listed with its key and asker, saying so.
