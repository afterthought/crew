## Context

See proposal.md, *Why*. ADR 0005 as amended 2026-10-11, the point *A card belongs to the host's sign-in*, makes the decision: after the host signs in again, each owner posts its open rows' cards again and says in each new card's summary that the older copy is dead; the dead copies are the user's to dismiss in the app, since no agent can reach them. The same reading established what Pending You does: a card posted under the old connection reads "Not found" under the new one, and a post under the same row key on the new connection makes a new card, since a key's idempotency goes with its connection.

The rules this change rests on: `briefs.11` (a row's card is its owner's, under the row's key; crew refuses a second card for a question already on one), `briefs.13` (a row's card has its row's form), `state.4` (the rail is computed from the record and writes nothing), `read.1` (what crew can't read it does not guess), `roles.4`. The change touches the areas of `briefs.md` (the card discipline in `crew.py`, `main-ops.md`) and `docs.md` (README, the skill), and edits nothing under `docs/` (`docs.7`).

Today:

- `cards_how` in `plugin/lib/crew.py` is the card discipline crew fills into the planner's and the conductors' briefs as `{{CARDS}}`. At its start an owner calls `whoami`, then `list_pending`, and posts a card for any row of its own that has none open. It says never to post again under a key whose card was answered. It says nothing of a card that reads "not found". Main-level ops's operations rows (`deploy/<env>/<sha>`, `op/<env>/<n>`) are carded by `main-ops.md` *Deploying main*, which does not use `{{CARDS}}`.
- `rail_record` in `plugin/lib/plan.py` holds a card open from its `card.post` until a `card.close` of the same card id. A lost card can never be closed: the hook records nothing for a tool call that fails, and `cancel_request` on a lost card fails. So after a re-post the rail shows two open cards on the row's card line, and once the row is gone the dead copy is listed among the open cards with no row, with a tell asking its owner to close what it cannot reach.
- `rail_text` prints a row's card line as `card:   <key>, open, asked by <agent>`, with no card id. An owner started afresh has no id for the card it posted in an earlier session, so it cannot ask Pending You whether that card is still there.

## Goals / Non-Goals

**Goals:** a row whose card is lost to its owner gets one live card again, from the same owner under the same key, saying which copy to answer; the rail shows the live card as the row's.

**Non-Goals:** reaching or closing the dead copy, which no agent can; a card that is no row's (a conductor's own question under `agent/<agent>`, the design agent's records), which the ADR's rule names as rows' cards and this unit leaves alone; preventing the re-sign-in, which is the host's and upstream's; recording a lost card in the run record, which would mean reading Pending You's error text in the hook.

## Decisions

### The words are crew's, said once, in every brief that cards a row

A lost card's handling is one paragraph, `lost_card_how(cmd, label)` in `crew.py`, beside `cards_how`, `signal_how` and `needs_how`. `cards_how` includes it, so the planner and the conductors have it, and the main-level fill gives it to `main-ops.md` as `{{LOST_CARD}}`, at the end of *Deploying main*. The paragraph says:

- what a lost card is: a card of yours that Pending You answers "not found", because the host signed in to Pending You again, while the user may still see it;
- when to check: at your start, and whenever Pending You has you call `whoami` again, ask Pending You with `get_request` for each card the rail's `card:` line shows open under a row of yours, by the id it names; and any Pending You tool that answers "not found" for a card of yours has found a lost one;
- what to do: while its row still waits, post the row's card again under the row's key, in its row's form and with the words it always carries, and put in its summary, right after the link and the bolt, these words: "An older copy of this card is dead: it can no longer be answered, so dismiss it in the app. Answer this one." Its plannotator session is still the row's: `crew card session` gives back the running link. This is the one time you post again under a key you have posted under before;
- a lost card whose row is gone is posted again by nobody, and there is nothing more to do with it.

Fixed words rather than the agent's own: the user sees two cards with the same title, and the same short sentence on each live copy, in every partition, is what tells them apart at a glance. They go after the link and the bolt, because the spec already fixes the summary's opening (*A card's link and bolt come first*); the document's opening sentences then fit in what is left of the 400 characters, as they do now.

Considered: a crew command that finds the lost cards for the agent, which would need crew to call Pending You, and ADR 0005 rules that crew carries no Pending You client of its own; `list_pending` alone at the start, which lists only the new connection's cards and cannot tell a lost card from one never posted, and whose entries are not known to carry the key.

### The rail names the open card's id

A row's card line becomes `card:   <key>, open, asked by <agent> (<card id>)`. The id is the `Card` the hook already records. That is how an owner started afresh finds the card it must check. The board's markers are unchanged.

### A newer post under a key, by the same owner, replaces the older

In `rail_record`, a `card.post` with a `Key`, read in the record's order, drops from the open cards any earlier open card of the same partition with the same `Key` and the same `By` and another card id. The newer card is the row's, and the older is taken as lost. Within one sign-in, Pending You gives the same card back for the same key, so the hook records the same id and nothing is dropped. Two ids under one key from one owner happen only when the first was lost to it. So the rule judges nothing it cannot read (`read.1`), and needs no new entry or field. It applies to the rail's card lines, its open cards with no row, the board's markers and the card sweep's view of which keys have a card open, all of which read `rail_record`'s cards.

Same owner only: a card under a key by another agent is not this owner's to judge, and `briefs.11` already refuses a row's card under another owner's key.

Considered: a `card.lost` entry written by the hook when a close answers "not found", which would read Pending You's error text, a fact not yet read against the tool (`read.2`), and would still leave a lost card that nobody tried to close shown as open.

## Risks / Trade-offs

- [The owner posts again under a key whose card is still live, by mistake] → Pending You gives the same card back within one sign-in, so the record holds one id and nothing changes.
- [A lost card whose row is gone stays among the open cards with no row for up to 14 days, with a tell its owner cannot act on] → the owner's brief says there is nothing to do with it. Crew can't tell it is lost without reading Pending You. Named for the design agent in the change's report.
- [The user answers the dead copy] → its answer reaches nobody, and the live copy says to dismiss the dead one. The ADR leaves the dead copies to the user.

## Proof in dev

Nothing to work in dev. A lost card comes only from a new Pending You sign-in on the host, and the ADR rules that the host's sign-in is not redone while a card is open, so it is not staged. The tests prove the rail's part and the briefs' words. The first real re-sign-in after the landing shows the rest: each owner's rows get a second card whose summary names the older copy as dead, and the rail shows one open card per row.

## Task notes

### 1.1

`lost_card_how(cmd, label)` in `crew.py`, beside `needs_how`, returning the paragraph *The words are crew's* gives, with the quoted sentence exactly as written there. `cards_how` includes it as a paragraph of its own after the paragraph that ends "The kits: …". Rewrite its "Never post again under a key whose card was answered" sentence so it still holds and points at the lost card as the one exception: an answered card is found, a lost one is not. Add `"LOST_CARD": lost_card_how(cmd, label)` to the main-level fill's tokens, and `{{LOST_CARD}}` as the last paragraph of `main-ops.md` *Deploying main*, after the bullets. Main-level ops's rows are its operations rows, so in its copy "a row of yours" reads the same; check the filled brief reads whole.

### 1.2

In `tests/t-briefs.sh`, `cards_say` gains the paragraph's phrases: "reads \"not found\"", "whenever Pending You has you call `whoami` again", the quoted sentence whole, "under the row's key", and "posted again by nobody". The main-level ops brief's test gains the quoted sentence. Run `tests/suite t-briefs`.

### 2.1

In `rail_record`, on a `card.post` with a `Card` and a `Key`, before `posted.setdefault`, drop each entry of `posted` with the same `key`, the same `by` and another `card`. Keep the existing rule that a post older than `CARD_DAYS` is not read. In `rail_text`, the open card's line ends ` (<card>)`. Update `rail_record`'s and `rail_text`'s docstrings to say so.

### 2.2

In `tests/t-rail.sh`: the lines that assert `open, asked by` with `eq` gain the id; one `has` asserts the id on a line, for example `proposal/1, open, asked by wldn-planner (req_prop-1)`. Add a case: the planner's `req_prop-1` under `proposal/1` left open, then `req_prop-2` posted under `proposal/1` by the same planner: the row's line names `req_prop-2`, `req_prop-1` is on no line, and no "open cards with no row" lists it; then once proposal 1 is approved, only `req_prop-2` is listed with no row. Add a case where another agent's card under the same key does not replace it, written as the hook would record it. Run `tests/suite t-rail t-board t-card-sweep`.

### 3.1

README, the rail paragraph under Pending You: a row's card line names the open card's id, a newer card posted under a row's key by its owner is the row's card and the older is taken as lost; and one sentence on a lost card: a card that reads "not found" to its owner, after the host signs in to Pending You again, is posted again under its row's key, its summary saying the older copy is dead and this one is the one to answer, and the dead copy is the user's to dismiss in the app. The crew skill's row "see whether a rail row's card is open, or a card has no row" says it shows the open card's id. `crew`'s usage header is unchanged: it says only that the rail shows each row's card. Run `tests/suite t-docs`, then `tests/suite --affected`.
