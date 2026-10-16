# Design

## Context

Record 0031 rules that crew raises six cards and an agent asks the seventh; the series' earlier changes raise each of the six at its event. This change, the series' last, ends the old path: the hook narrowed to the question, the briefs rewritten to the record, the commands agents built cards with removed, and how an owner hears a card crew raised. It relies on `roles.3` (the hook refuses, the brief does not merely say), `briefs.11`, `briefs.13`, `briefs.15` and `briefs.16` as record 0031 amends them, `briefs.17` (a call in another agent's name refused on every tool), `plan.16` (the conductor's tell to main-level ops on the landing's yes), `tests.6` (every brief's rule pinned by `tests/t-briefs.sh`), `docs.2`, `code.2`, `read.1` and `state.4`. It touches the areas of `briefs.md`, `teams.md`, `plan.md`, `tests.md` and `docs.md`.

## Goals / Non-Goals

Goals: no agent writes, posts or closes a row's card; an agent's question keeps every field Pending You offers; each role's brief says what crew raises for it and how it hears; nothing of the old path left to drift.

Non-goals: raising any card, which the earlier changes do; the wake mod itself (the fleet's).

## Decisions

### 1. The hook, narrowed to three checks and a record

`plugin/hooks/cards --before` runs on every Pending You tool in a crew session, and first refuses a call in another agent's name (`briefs.17`), which this change keeps as it stands. On `post_request`, `update_request`, `cancel_request`, `ack_answer` and `create_area` it then refuses when the agent's role is not a conductor, the planner, main-level ops or the design agent, naming the chain of command; when the `idempotencyKey` or the request id is a row's key or card (crew's own); and when `create_area`'s key is not `create-area:<owner>/<kit>`. Everything else passes. The after-hook records `card.post`, `card.update` and `card.close` with the card's id and the agent's key, on the agent's own object, and when the reply gives no id records the act as unread, which the rail lists. `KEYS`, `FORMS`, `form_check`, `form_refusal` and `proposal_form` go, with the form cases in `tests/py/test_cards.py`, since no card is checked against a form it was not built from. The decision of who may post is `plan.card_refusal`, a function of the role, the key and the rows, in `tests/py/test_cards.py` `TestKeys`.

The name check stays whole: `name_refusal` keeps running first in `refusal`, apart from the key and role checks, with its cases in `TestNames`, and `hooks.json`'s matcher stays `mcp__.*[Pp]ending.*[Yy]ou.*__.*`, so the hook runs before every Pending You tool, not only the five a card is posted, changed or closed with. An asker gives Pending You only its own name, which crew's hook holds it to on every tool.

### 2. Hearing

A card crew raises is posted through its bridge in no session, so nothing of the owner's is listening when the user answers. The owner adopts it:

- **Adoption.** After a post, crew prints `call get_request (requestId req_…, name <role>)`, never `pendingyou hold`. The owner's `get_request` under its own name reads the card the bridge posted on the host's connection, and the fleet's wake mod adopts the card from that call; it then wakes the owner's session, once idle, 20 to 60 seconds after the user's answer.
- **Raised outside the owner's turn**, a landing found on a rail read or the deployer's offer: crew sends the owner that line with `crew tell`. A card the owner's own command raised, a proposal's in the planner's shell, is told to no one.
- **At a fresh start** the owner runs `crew rail`, which names its open cards and their ids, and adopts each the same way.
- **The sweep stays the catch** for a card no owner adopted: the rail names every open card with its owner at each read, and `crew card read <key>` prints a card's state and answer, and closes a declined approval:

| Event | Command | Act |
|---|---|---|
| any approval declined | `crew card read <key>` finds the decline | close with the user's words |

The line is printed by `row_card_post`, and told by it when the command raising the card is not the owner's; the briefs say to call it.

### 3. The briefs

`crew.py` `cards_how` becomes the question discipline every one of the four roles carries: the chain of command, Pending You's test for what is the user's, the fields a good question gives (options with a recommendation, a fallback when not blocking, what was tried), the key of its own (`ask/<agent>/<slug>`), how it hears, and that crew's six cards are crew's. `lost_card_how` goes. `conductor.md` *Cards* says crew raises the landing card and what the conductor does on its answer (the tell to ops on a yes; a fix on a defect note); `planner.md` says crew raises proposals' and batches' cards, how it reads a batch's notes (`crew card wait`) and gathers a proposal's answers (`crew plan answer`, as built); `main-ops.md` says crew raises the deploy's and the step's cards and how it adopts one; `design.md` says `crew record`; `coder.md` and the other stage roles say a question goes to the conductor by `crew needs`; `operator.md` is unchanged. `tests/t-briefs.sh` pins the words (`tests.6`).

`design.md` also says a record whose decision a rule of the user's made between alternatives names them, the rules that decided and each rule loosened, in a file `crew record --alternatives` takes, never settled silently; and `planner.md` says the planner's `Do` lines carry each new unit's direction for its card.

A question's card is as drawn, the asker's own: "I think the last question card looks fine" (the user, 2026-10-15, in the card trials).

### 4. The old path goes

`crew plan card` and `crew card post|change|close` are removed from `plugin/bin/crew`, its usage header, README and `plugin/skills/crew/SKILL.md`, with `card_model`, which only they and the hook's proposal form read; `crew card read|wait|session|end` stay. crew no longer names a card for its owner to close when a write ends a row (`close_card`, `notices`, `lost_rows`): it closes the card itself at the event. `CARD_KEYS` keeps only the rows' keys as the series made them, the verify report's and the head-keyed forms gone.

## Alternatives considered for hearing

From the recovery session's probe of Pending You 0.28.0 and 0.35.1, 2026-10-16 (`hearing-probe/finding.md` in the session's scratchpad; `PY` is the 0.28.0 store package, `mod` the fleet's wake mod):

- **`pendingyou hold <id>` in the owner's session.** The wake mod answers `hold` only for a session that already has a Pending You server on record from an earlier named call (`mod/wake.js:240`, `register.js:440`); otherwise the CLI's `hold` runs for real, keyed by request id with no name or session, and in the foreground blocks the agent for up to four hours (`PY/dist/hold.js:80,95-100`, `args.js:3`). The owner's own `get_request` gets the same adoption with nothing that can block (`mod/wake.js:278-284`), and records the server and name as it does.
- **`pendingyou watch` as a service on each host**, telling each answer's owner. It marks every answer on the host handed in the shared `state.json` (`PY/dist/watch.js:71,79`), which every session's per-message pickup reads and skips (`pickup.js:248`), so it would hide other sessions' answers from them.
- **A wake webhook per role** (`set_wake_webhook`): ids only, stored per name on the connection; it needs Tailscale Funnel, a receiver and a secret on every host, and the secrets are the user's to write.
- **Polling `list_pending`** from crew: a new bridge and MCP session for every poll, and still a watcher, which `state.4` rules out.

## Risks / Trade-offs

- An answer wakes its owner only once the owner has adopted the card and its session is idle: the mod checks an adopted card every 20 seconds, every 60 once it has been quiet for 30 minutes (`mod/wake.js:5-7`, `register.js:141-147`), and forgets one unchanged for seven days or across a new session id (`wake.js:11,369`, `register.js:33,368`). A card adopted by no one, or forgotten, is the rail's to show and the owner's to read at its breakpoints and fresh start.
- An agent may ask more questions than it did when every card was refused but a row's; volume comes down by mechanism, one card per thing changed in place, crew closing at the event, four voices each its own, and never by telling agents not to ask (record 0031, *Decision drivers*).

## After deploy

1. The standing agents of each partition restarted at a quiet moment, by the dispatcher, since a brief loads at a fresh start and no check can make a running agent reread it; the environments are the two hosts.
