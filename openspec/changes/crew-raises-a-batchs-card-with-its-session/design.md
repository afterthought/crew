# Design

## Context

Record 0031 and `crew-builds-every-card-from-its-facts` give a batch's card its form and the act that sends it; this change raises it when the batch's summary is delivered, starts its reading session with it, and closes both when the user is done. It relies on `briefs.9` (a card that cannot hold its document links a plannotator session crew starts), `briefs.12` (the batch, due across the partition), `briefs.13`, `state.4`, `read.1` (a session crew cannot judge is kept, and said), `read.4` (crew ends only what it started), `code.7` and `code.9`. It touches the areas of `plan.md`, `briefs.md` and `tests.md`.

## Goals / Non-Goals

Goals: one card per batch, raised by crew with its one session when the summary is there; a session that stays running while the card is open, ends when crew closes the card, and opens over the tailnet.

Non-goals: the batch's form, which `crew-builds-every-card-from-its-facts` builds; the sweep's end of a session whose card closed elsewhere, which stands as `a-cards-session-ends-with-its-card` built it.

## Decisions

### 1. Raised when the summary is delivered

| Event | Command | Act |
|---|---|---|
| a batch's summary delivered | `crew review --wait`, when the reviewer's file is there | start the batch's session, post `batch/<n>` |
| the tap, or the session sent | `crew card wait batch/<n>` | print the notes; close |

`raise_batch`, the batch's raise, reads `batch_facts`, each unit of the batch with its team and its opening paragraph from the reviewer's summary, and the units' subjects for the title, and calls the act; it finds the batch's point not come while the reviewer's summary is not there, so a rail read before then raises nothing. `crew card wait <key>` keeps its session wait for a batch and closes the batch's card on the tap or the session's send.

### 2. Sessions

crew starts a plannotator session only for a batch (on the batch's folder, the summary whole and every change as one review) and for a proposal of more than fifteen new units, when it raises the card, and puts the link in the card's words first and among its links. `crew card session <key>` prints a running session's link again and refuses a key of any other kind. The session ends when crew closes the card, and on the sweep. Both are in the act: `row_card_post` starts the session of those two kinds before it builds the card, so the link is a fact the builder is handed, and `row_card_close` ends the key's session after the close, so a proposal's raise in `crew-raises-a-proposals-card` gets its session without changing a function of its own.

### 3. What the user holds the card to

What the user holds this card to is the session: "it stays running, it closes when it's supposed to once we're done, it's accessible", which `card-sessions` pins; access over the tailnet "has been opening pretty reliably" (the user, 2026-10-15). The card trials' note for the builder, in the recovery session's words: the batch's title comes from the units' subjects; the summary opens "N changes to read, nothing to approve"; the reviewer's summary goes on the face as Markdown; the plannotator session behind it must "1. stay running 2. close when it's supposed to once we're done 3. be accessible".

### 4. The planner's brief

`planner.md`'s *Batches* says crew starts the batch's session and raises its card when the reviewer's summary is delivered and `crew review --wait` returns; that the planner adopts the card with the line the wait prints; and that it reads the notes with `crew card wait batch/<n>` and sends each unit's to its conductor word for word, as today. It starts no session for a batch and posts and closes no batch card. `tests/t-briefs.sh` pins the words (`tests.6`).

## Risks / Trade-offs

- A session started inside the act adds plannotator's start to `crew review --wait`, which already waits on the reviewer and takes a timeout (`code.9`).

## After deploy

1. The planner of each partition restarted at a quiet moment, by the dispatcher, since a brief loads at a fresh start and no check can make a running agent reread it; the environments are the two hosts.
