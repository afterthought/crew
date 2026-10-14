# Design

## Context

Record 0031 (accepted 2026-10-14) rules the whole: six cards of crew's own at fixed points, one open card for a question, one card per thing changed in place, crew closing at the event, one host sign-in; `openspec/explorations/cards/mockups.md` draws each card and `reading.md` has the numbers. This design says how crew does it. It relies on `state.4` (nothing runs: a card is raised by a command, never a watcher), `code.7` (each builder is a function of facts, tested in the logic tier), `code.2` (every refusal a `Refusal`), `read.1` (a card crew cannot read is said, never guessed), `roles.3` (the hook refuses, the brief does not merely say), `code.8` (the agents' views follow), `briefs.9`, `briefs.11`, `briefs.13`, `briefs.15`, `briefs.16`, `plan.14`, `plan.16` as record 0031 amends them, `docs.2`, `docs.6`. It touches the areas of `plan.md`, `teams.md`, `briefs.md`, `record.md` and `tests.md`.

## Goals / Non-Goals

Goals: every card the user sees from crew is one of six forms, built by code, raised and closed at its event; an agent's question keeps every field Pending You offers; nothing waits on an agent remembering a card; the rail is the truth of what is open and whose.

Non-goals: the host's sign-in, the account folders' Claude Code logins and the doctor's row (swancloud's); a card's link to a running environment for a bolt (record 0031 §9, a design of its own); the wake mod itself (the fleet's); any change to what Pending You renders.

## Decisions

### 1. Six builders, functions of facts

`plugin/lib/cards.py` gains one builder per kind, each taking plain facts and returning the arguments of Pending You's `post_request` (title, summary, kind, approve or options or questions, rationale, context, artifacts, urgency, blocking false, idempotency key, session, area), and for a change the arguments of `update_request` with its change note. The facts are read by the caller: the proposal builder takes what `card_model` reads today (the plan and the proposal, the picture drawn as now); the batch builder the batch's units with team and opening paragraph and the session's link; the landing builder the bolt, its units and chores, sluice's verdict and time, main's distance, the batches they were read in; the deploy builder the environment, the head, the landings since the last deploy, the environments before and after, the steps gathered; the step builder the step's words, doer, when, commands and done-when, or the agents' consequences for a held step; the record builder the record's number, title, opening sentences, the user's quoted words and the Markdown. Each is pinned in `tests/py/test_cards.py` by its scenarios; the form cases and `FORMS` go, since no card is checked against a form it was not built from.

The words rule is in the builders: every summary and paragraph is prose cut at whole sentences to Pending You's budget, no code block, no Markdown the user has to read raw; the only artifacts are the proposal's picture (uploaded, as `an-image-on-a-card-is-uploaded` built), the record's Markdown as a `code` artifact of lang `markdown`, and a step's commands in its `action` steps. A path appears only inside a step's command or a deploy's log name.

### 2. Raised by the event's command, under the row's key

The command that makes or reads the event calls the builder and posts through `cards.Bridge`, the `pendingyou mcp --app claude-code` client already built, under the host's sign-in and in the role's name as the session label. Each post's `idempotencyKey` is the row's key, so the same event read twice makes one card:

| Event | Command | Act |
|---|---|---|
| a proposal accepted into the plan | `crew plan propose` | post `proposal/<n>` |
| rewritten | `crew plan propose --replaces <m>` | change the chain's card; the rail's row for `n` carries it |
| a conductor agrees | `crew plan agree` | change ("no longer waits on …") |
| applied, dropped | `crew plan approve`, `crew plan drop` | close with the outcome, or withdraw with the user's reason |
| a batch due | `crew review` | post `batch/<n>` after starting its session |
| the tap, or the session sent | `crew card wait batch/<n>` | print the notes; close |
| a bolt reads proven | the merge's end (`crew unit wait`, `crew chore wait`) and `crew rail` | post `land/<bolt>` |
| the head moves while open | the merge's end | change ("head is now …") |
| landed | `crew bolt land` | close with the merge and the hosts level |
| a defect noted | `crew fix` started on the bolt | withdraw ("held for a fix: …") |
| a deploy offered | `crew ops offer` | post `deploy/<env>`, or change when a newer head is offered |
| the deploy ends or fails | `crew ops record --act end` | close with each step's outcome, or the failed step and its log |
| a step the user's, or held | `crew ops step --state waiting --doer user`, `--held` | post `op/<env>/<n>` |
| done, skipped, done by its agent | `crew ops step --state done\|declined` | close |
| a record proposed, not settled in the pane | `crew record <kit> <n> --proposed` | post `record/<kit>/<n>` |
| revised | `crew record … --proposed` again at a new commit | change |
| accepted, rejected | `crew record … --accepted\|--rejected` | close |
| any approval declined | `crew card read <key>` finds the decline | close with the user's words |

A post or close that Pending You refuses is a `Refusal` in Pending You's words and a `card.post` or `card.close` entry marked refused (`code.2`, as `crew card post` records today); the event itself is not refused: a proposal is in the plan whether its card posted or not, and the rail shows the row with no card and the refusal, so the next rail read posts it. When the host is not signed in, the command says so and goes on.

The landing's point needs one rule: a bolt reads proven when every unit and chore has merged, every unit's latest change has been in a batch, and the bolt's head carries a green `Sluice-Result` (record 0025). The merge's end and the rail read both read it (`plan.py`'s landing row already does); whichever runs first posts, the other finds the card by its key in the run record and does nothing.

### 3. `crew record`

New: `crew record <kit> <number> --proposed|--accepted|--rejected [--settled-in-pane]`, run by the design agent in its worktree at each turn of a record's status. It records `record.<status>` in the run record with the kit, the number and the commit, and with `--proposed` raises the record's card unless `--settled-in-pane` is given, which records the user's yes as given in the pane and raises nothing. `--accepted` and `--rejected` close the card with the commit. The board's design band reads these entries to show proposed records. The record's status is read from the file at the commit; a mismatch (`--accepted` on a file still `proposed`) is refused.

### 4. The hook, narrowed to three checks and a record

`plugin/hooks/cards --before` runs on `post_request`, `update_request`, `cancel_request`, `ack_answer` and `create_area` in a crew session. It refuses when the agent's role is not a conductor, the planner, main-level ops or the design agent, naming the chain of command; when the `idempotencyKey` or the request id is a row's key or card (crew's own); and when `create_area`'s key is not `create-area:<owner>/<kit>`. Everything else passes. The after-hook records `card.post`, `card.update` and `card.close` with the card's id and the agent's key, on the agent's own object, and when the reply gives no id records the act as unread, which the rail lists. `KEYS`, `FORMS`, `form_check`, `form_refusal` and `proposal_form` go. The decision of who may post is `plan.card_refusal`, a function of the role, the key and the rows, in `tests/py/test_cards.py` `TestKeys`.

### 5. The sweep withdraws

On each rail read, crew already ends the sessions of closed cards (`a-cards-session-ends-with-its-card`). It now also, under the host's connection: withdraws a row's card whose row is gone, with the reason ("its proposal was dropped", "its bolt was dropped"); withdraws a question card whose asker herdr no longer lists, naming the asker; and posts again, under its key, an open row's card that reads not found after the host signed in anew, its summary saying the older copy is dead (`a-card-lost-to-its-owner-is-posted-again`'s rule, now crew's act). `crew board` stays a view that writes nothing. The decisions, which cards to withdraw and which to post again from the rows, the record and herdr's listing, are in `tests/py/test_rail.py` `TestSweep`; the acts in `tests/t-cards.sh`.

### 6. Hearing

A post prints `card req_… posted; run: pendingyou hold req_…` so the owner's session adopts it; the fleet's wake mod answers `hold` itself and learns the card. For the deployer's offer, which runs under launchd, `crew ops offer` tells main-level ops the same line through `crew tell`. At a fresh start an owner runs `crew rail`, which names its open cards and their ids, and adopts each. `crew card read <key>` prints a card's state and answer, and closes a declined approval (decision 2). `crew card wait <key>` keeps its session wait for a batch and closes the batch's card on the tap or the session's send.

### 7. Sessions

crew starts a plannotator session only for a batch (on the batch's folder, the summary whole and every change as one review) and for a proposal of more than fifteen new units, when it raises the card, and puts the link in the card's words first and among its links. `crew card session <key>` prints a running session's link again and refuses a key of any other kind. The session ends when crew closes the card, and on the sweep.

### 8. The briefs

`crew.py` `cards_how` becomes the question discipline every one of the four roles carries: the chain of command, Pending You's test for what is the user's, the fields a good question gives (options with a recommendation, a fallback when not blocking, what was tried), the key of its own (`ask/<agent>/<slug>`), how it hears, and that crew's six cards are crew's. `lost_card_how` goes. `conductor.md` *Cards* says crew raises the landing card and what the conductor does on its answer (the tell to ops on a yes; a fix on a defect note); `planner.md` says crew raises proposals' and batches' cards, how it reads a batch's notes (`crew card wait`) and gathers a proposal's answers (`crew plan answer`, as built); `main-ops.md` says crew raises the deploy's and the step's cards and how it adopts one; `design.md` says `crew record`; `coder.md` and the other stage roles say a question goes to the conductor by `crew needs`; `operator.md` is unchanged. `tests/t-briefs.sh` pins the words (`tests.6`).

### 9. The rail and the board

`crew rail` prints a fifth group, questions, each open question card with its asker, its title and its age, and under every row its card's id and state; after the groups it lists what the sweep did. `board.agent_views` gives each agent its open cards, questions among them, and `status.js` draws them (`code.8`); `tests/py/test_board.py` pins the keys the mod reads.

## Risks / Trade-offs

- Two paths to Pending You, crew's and the sessions', which must share the host's sign-in to see each other's cards. The record settles the sign-in; this change refuses nothing when it is absent but says so on every post and on the rail.
- A card raised by a command an agent runs in its shell adds Pending You's round trip to that command; `code.9` holds, since the Bridge's call is one short MCP session and the command answers once the commit is made and the post attempted.
- Pending You's tool schema is read at each connection; a field it renames breaks a builder loudly (`read.2`), which is better than today's silent drift.

## After deploy

1. The host's Pending You sign-in: `pendingyou-signin` on mac-studio and on chuck-herdr-alpha, by the user, since the device code is approved on their phone and no check can do it; the environments are the two hosts.
2. The standing agents of each partition restarted at a quiet moment, by the dispatcher, since a brief loads at a fresh start and no check can make a running agent reread it; the environments are the two hosts.
