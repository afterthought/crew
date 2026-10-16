# Design

## Context

Record 0031 (accepted 2026-10-14; §5 amended 2026-10-15 from the card trials) rules the whole: six cards of crew's own at fixed points, one open card for a question, one card per thing changed in place, crew closing at the event, one host sign-in; `openspec/explorations/cards/mockups.md` draws each card as the trials settled it and `reading.md` has the numbers. Eight changes build it, in the order *The series* gives; this one builds what every card is made of, the one act that sends it and how its owner hears it, and raises no card at any event. It relies on `state.4` (nothing runs: a card is raised by a command, never a watcher), `code.7` (each builder is a function of facts, tested in the logic tier), `code.2` (every refusal a `Refusal`), `read.1` (a card crew cannot read is said, never guessed), `read.2`, `code.9`, `roles.4` (a card raised outside its owner's turn is told with `crew tell`), `briefs.9`, `briefs.13`, `briefs.16` and `plan.14` as record 0031 amends them, `docs.4` and `docs.6`. It touches the areas of `plan.md` and `tests.md`.

## Goals / Non-Goals

Goals, the series': every card the user sees from crew is one of six forms, built by code, raised and closed at its event; an agent's question keeps every field Pending You offers; nothing waits on an agent remembering a card; the rail is the truth of what is open and whose. This change's: the six forms built by code from facts, in the words the trials settled; one act that posts, changes and closes them; and every card heard by its owner from the moment it is crew's.

Non-goals: the host's sign-in, the account folders' Claude Code logins and the doctor's row (swancloud's); a card's link to a running environment for a bolt (record 0031 §9, a design of its own); the wake mod itself (the fleet's); any change to what Pending You renders; raising any card at its event, which the changes after this one do.

## Decisions

### 1. Six builders, functions of facts

`plugin/lib/cards.py` gains one builder per kind, each taking plain facts and returning the arguments of Pending You's `post_request` (title, summary, kind, approve or options or questions, rationale, context, artifacts, urgency, blocking false, idempotency key, session, area), and for a change the arguments of `update_request` with its change note. The facts are read by the caller: the proposal builder takes what `card_model` reads today (the plan and the proposal, the picture drawn as now); the batch builder the batch's units with team and opening paragraph and the session's link; the landing builder the bolt, its units and chores, sluice's verdict and time, main's distance, the batches they were read in; the deploy builder the environment, the head, the landings since the last deploy, the environments before and after, the steps gathered; the step builder the step's words, doer, when, commands and done-when, or the agents' consequences for a held step; the record builder the record's number, title, opening sentences, the user's quoted words and the Markdown. Each is pinned in `tests/py/test_cards.py` by its scenarios. The proposal builder takes over `card_model`'s drawing, the sections the picture is drawn from and the change as text, as a function of the facts `card_model` reads; `card_model`, `crew plan card` and the card hook's `proposal_form` keep today's card until the series' proposal change raises the card from the builder and its last change removes them.

The words rule is in the builders: every summary and paragraph is prose cut at whole sentences to Pending You's budget, nothing the user has to read as raw Markdown; a list the user scans, units, steps, a change, is an artifact on the card's face, lines of at most forty characters, one thing a line, never a comma run in the summary or the background (the user, 2026-10-15, on the landing card's first version: "it lists units that are hyphenated and long … It needs to be scannable"; "the background only shows when I click the details button and it slides out in a right-hand drawer, it'd be nice if more information could be shown in the card itself"). The artifacts a crew card carries are the proposal's picture (uploaded, as `an-image-on-a-card-is-uploaded` built), inline Markdown as a `code` artifact of lang `markdown` (a record, a proposal's new units, a batch's summary, a deploy's release notes), a text list as a `code` artifact of lang `text`, a link as a `url` artifact, and a step's commands in its `action` steps. Details (`context.background`, `trace`) hold what the user reads only when the face is not enough. A path appears only inside a step's command or a deploy's log name.

Each builder takes the card its card follows, when there is one, and sets Pending You's `follows`, so the chain of one thing reads as one thread on the phone (the user, 2026-10-15: "What is this feature that you used with nesting cards like this? We should use this more"): a deploy's card follows the landing card that put its head on main; a step's card follows the deploy's, and each later step the step before it; a landing raised again after a fix follows the card the defect note held; a deploy of a newer head after a no follows the declined one; a question an asker asks again follows its withdrawn one. A proposal rewritten stays one card changed in place, and follows nothing. Which card a card follows is `follows_of`, a function of the kind, the thing and the run record's card entries, so every change that raises a card asks it the same way.

### 2. One act posts, changes and closes crew's cards

The command that makes or reads an event calls the builder and posts through `cards.Bridge`, the `pendingyou mcp --app claude-code` client already built, under the host's sign-in and in the role's name as the session label. Each post's `idempotencyKey` is the row's key, so the same event read twice makes one card. The act is `plan.py`'s `row_card_post`, `row_card_change` and `row_card_close` (an outcome, or a reason to withdraw), each recording its `card.post`, `card.update` or `card.close` entry on the row's object with the card's id and the key, read from Pending You's own reply, and printing the card's key, its id and the line that adopts it (decision 3).

A post or close that Pending You refuses is a `Refusal` in Pending You's words and a `card.post` or `card.close` entry marked refused (`code.2`, as `crew card post` records today); the event itself is not refused: a proposal is in the plan whether its card posted or not, and the rail shows the row with no card and the refusal. When the host is not signed in, the command says so and goes on. A close that Pending You answers "not found" records the close as lost and goes on; a change that finds its card "not found" posts the card again under its key, its summary saying the older copy is dead.

Each change of the series that raises a kind gives that kind one function, the kind's raise, handed the row: it reads the kind's facts, decides from them whether the kind's point has come, builds the card and calls the act. The raises are `raise_proposal`, `raise_batch`, `raise_land` and `raise_record` in `plan.py`, and `raise_deploy` and `raise_step` in `ops.py`. The event's command and the rail's read both call a kind's raise, so a card is built the same way whoever raises it.

### 3. Hearing

A card crew raises is posted through its bridge in no session, so nothing of the owner's is listening when the user answers. The owner adopts it, from the first card crew raises, so every card is heard from the moment it is crew's:

- **Adoption.** After a post, crew prints `call get_request (requestId req_…, name <role>)`, never `pendingyou hold`. The owner's `get_request` under its own name reads the card the bridge posted on the host's connection, and the fleet's wake mod adopts the card from that call; it then wakes the owner's session, once idle, 20 to 60 seconds after the user's answer.
- **Raised outside the owner's turn**, a landing found on a rail read or the deployer's offer: crew sends the owner that line with `crew tell`. A card the owner's own command raised, a proposal's in the planner's shell, is told to no one.
- **At a fresh start** the owner runs `crew rail`, which names its open cards and their ids, and adopts each the same way, as the briefs already have each owner read the rail's `card:` lines at its start; each card's change writes its owner's words of it into the owner's brief, and the series' last the question discipline.
- **The sweep stays the catch** for a card no owner adopted: the rail names every open card with its owner at each read, and `crew card read <key>` prints a card's state and answer, and closes a declined approval:

| Event | Command | Act |
|---|---|---|
| any approval declined | `crew card read <key>` finds the decline | close with the user's words |

The line is printed by `row_card_post`, and told by it with `crew tell` when the command raising the card is not the owner's, which is a function of the owner and the caller (`code.7`); `card_read` closes a declined approval.

### 4. What each card shows, settled on the phone

Each kind was posted to the user as a real card on 2026-10-15, in the card trials session, and reshaped from what they said; `openspec/explorations/cards/mockups.md` draws each as settled. The builders make these forms:

- **Landing.** The units that land are a text artifact on the face, one a line, under "What lands: N units, M chores"; the summary gives the counts, the batches, sluice's verdict and how far main moved; the rationale says what follows. When sluice's submission has a pull request on GitHub, the card links it as a `url` artifact and among its links ("It would also be nice if the 'Pull request opened in GitHub, created by Sluice' text were a link in here"); a kit whose sluice opens none has no link. Details hold the batches each unit was read in and what a defect note does. Settled: "ok. good enough for now."
- **Deploy.** The face carries the kit's release notes for exactly the environment's range, as git-cliff writes them, per release with each line's scope, as inline Markdown under "What's in it", and the range's after-deploy steps with their doer, the user's, an agent's or held, as a text list under "After the deploy: N steps, K yours"; the summary counts the landings and names which environments go before and after; the landings' subjects are in Details ("when I'm offered a deploy, I want to be able to easily see a summary of what's in it from the release notes … or include a better summary of what will happen after the deploy"; `plan.14` as amended on main 614cd85). Approved on the phone without a note.
- **Step.** The two shapes stand as drawn: a `do` with the commands whole and Done, Skip and Later for the user's step; a choice of when quiet (recommended), now and skip for a held step.
- **Proposal.** The title is the kind and the thing, not a question and not the number: "Plan change to <bolt>: <counts>" ("when it's worded as a question, it's hard to distinguish the different types"; "I don't know that it is worthwhile putting the proposal number in the title since we typically don't follow the proposal numbers"). The summary says in a sentence what the planner proposes and why, from the case. The card is one checkbox list and nothing else to tap: every row of the change is a box set as proposed, a new unit or chore ticked, a dropped one unticked as "Keep <unit>", an amended one unticked as "Keep <unit>'s old intent", each with its intent as its detail; Send applies the change with the boxes as they stand, so leaving a new unit out, keeping a dropped one or an amendment's old words is a tap, and no approve button sits inside the card ("I just don't love how I get the Approve button because when you click it, it doesn't do anything and then you still have to click Send Answers"; "the key would need to be consistency with the checkboxes"; "What if I objected to something being dropped?"). A proposal with no unit rows, a move or an order alone, is a hold-to-approve of low risk. Every new unit has a paragraph on the face as inline Markdown, its intent and a "Direction" line saying where it goes, taken from the proposal's `Do` line and the planner's case, since the card is where the user first meets the unit and confirms its intent before construction ("I need enough information on this card to confirm intent"); a dropped unit's paragraph gives its intent and the drop's why. The picture is crew's own drawer's, drawn at twice the pixel density so it is sharp on a Retina phone (1560 pixels wide, every size doubled: "it's pixelated so I think we have to deal with that 2x issue"), and the change in text stays. A limit of Pending You's: a checkbox card with nothing ticked needs words before it sends, so a proposal of one new unit the user leaves out asks for a note; raised with Pending You, not worked around.
- **Batch.** The title is what the batch is about, drawn from the units' subjects; the body's first line is "N changes to read, nothing to approve" ("I would prefer that a statement like '4 changes to read, nothing to approve' show in the body and that the title summarize what the batch is about"). The reviewer's summary rides the face as inline Markdown, a paragraph per unit with its team, and the one link opens the reading.
- **Record.** A record settled in the pane raises no card; a plain record's card is the hold-to-accept of low risk with the record whole, as record 0031 has it. A record whose decision a rule of the user's made between alternatives is a choice instead, asked once: loosen the rules as drafted and take the other path (recommended when the user's own words point there), accept the record as ruled, or send it back with a note; the face carries the alternatives, the rules that decided and each rule as it would read loosened, as inline Markdown, then the record whole (the user, 2026-10-15: "I want the designer to let me know when there are alternatives, especially if it's choosing one alternative over the other based on my rules. I'd like the opportunity to know which rules were holding it back, whether we should alter those rules, and what those altered rules might look like. That should all be one decision: go with my plan or loosen the rules, and here's what the loosened rules would look like"; on the card: "I like the choices that worked well").
- **Whose name.** Pending You labels a Claude Code session by the name of its latest tool call, so a session that posts under another agent's name takes that agent's answers: crew's own posts go through `pendingyou mcp` as the row's role, in no session, and an asker gives Pending You only its own name, which crew's hook holds it to on every tool (`briefs.17`). A session whose Pending You connection reconnects can come up on a new connection, from which its earlier cards read not found though the host's sign-in never changed (seen in the trials): the sweep's lost-card case covers it, keyed by the row, with no new rule.

### 5. What the card trials hand the builder

The trials' notes the builders take as given, in the recovery session's words:

- Every card follows the one before it (`follows`): a deploy after its landing; a step after its deploy, and each next step after the one before, raised when crew closes the previous; a re-raised landing after the held one; a newer head's deploy after the declined one.
- Each kind of content has its shape: a list you scan is a `code` artifact, lang `text`, lines of at most forty characters; a document's substance is `code`, lang `markdown`; a link is a `url` artifact plus a context link; the details hold only what the face can't.
- The proposal: title "Plan change to <bolt>: <counts>", with no number; one `multi` list where every row is a box set as proposed, new ticked, dropped unticked as "Keep <unit>", amended unticked as "Keep <unit>'s old intent"; groups of at most five rows; a proposal with no unit rows a low-risk approve; a Markdown paragraph for each new or dropped unit; `picture.py` at twice the density, 1560 wide.
- Names: Pending You labels a session by its latest call's name, so crew's own posts go through `pendingyou mcp` as the role, in no session, and an asker gives only its own name. A lost card is re-raised by its row key (the sweep).

### 6. The series

Each change is built and landed on its own, in this order; each names in its proposal's *Touches* the functions it changes. Changes 2 to 5 and 7 follow this one alone and change different functions, so they are built side by side, each rebasing on whatever lands before it; the files they share are the journey `tests/t-cards.sh`, which each adds its own part to, `tests/t-briefs.sh`, which 2 to 5 each add their brief's words to, `tests/py/test_cards.py`, which 3 and 5 each add their own cases to, `tests/moon.yml`, which each regenerates, the opening paragraph of `planner.md`'s *Cards*, whose proposal sentences 2 rewrites and batch sentences 3, and for 4 and 5 the usage header of `plugin/bin/crew`, README and `plugin/skills/crew/SKILL.md`, each its own command's lines.

| # | Change | What it builds | Follows | Functions it changes |
|---|---|---|---|---|
| 1 | `crew-builds-every-card-from-its-facts` | the six builders, the words rule, `follows`, the picture at twice the density, the act, how an owner hears a card | none | `cards.py`: new builders and `follows_of`; `picture.py` `char`, `layout`, `draw`; `plan.py` `card_read`, and new `row_card_post`, `row_card_change`, `row_card_close` |
| 2 | `crew-raises-a-proposals-card` | the proposal's card raised, changed and closed by `crew plan propose`, `--replaces`, `agree`, `approve`, `drop`; Send applying the boxes | 1 | `plan.py` `plan_propose`, `plan_agree`, `plan_approve`, `plan_drop`, `plan_answer`, `card_answer`, `with_answer`, `answered`, `CardReads.open_proposals`, `rail_rows` (the proposal's row); new `proposal_chain`, `proposal_facts`, `raise_proposal`; `planner.md`'s proposal words |
| 3 | `crew-raises-a-batchs-card-with-its-session` | the batch's card and session raised by `crew review --wait`; `crew card wait` and `session` | 1 | `plan.py` `review_wait`, `row_card_post` and `row_card_close` (the session's start and end), `card_session`, `session_refusal`, `card_of`, `card_wait`, `waited`, `end_session`, `batch_folder_write`; new `batch_facts`, `raise_batch`; `planner.md`'s *Batches* and batch words |
| 4 | `crew-raises-the-deploy-and-step-cards` | the deploy's and the step's cards by `crew ops offer`, `record`, `step` | 1 | `ops.py` `rows`, `environments`, `open_keys`, `offer`, `record_cmd`, `step`, `parser`, `args_refusal`; new `deploy_facts`, `raise_deploy`, `raise_step`; `main-ops.md`'s *Deploying main* |
| 5 | `crew-record-raises-a-records-card` | `crew record` and the record's card | 1 | `plan.py` `RECORD_KEY`, `card_refusal` (the design agent's branch), `parser`, `main`; new `record_status`, `record_facts`, `raise_record`; the card hook's `KEYS` (the record's line); `plugin/bin/crew`'s dispatch; `design.md`'s *Decision records* |
| 6 | `crew-raises-a-bolts-landing-card` | the landing's card at the merge's end and the rail's read, withdrawn by `crew fix`, closed by `crew bolt land` | 1, 7; waits on the record of who keeps which folders | `plan.py` `rail_rows` (the landing's row), `unit_wait`, `record_end`, `fix_cmd`, `bolt_land`, `CARD_KEYS` (the landing's key), `card_refusal` (the conductor's branch); new `landing_facts`, `raise_land`; the card hook's `KEYS` (the landing's line); `conductor.md`'s landing words |
| 7 | `the-rail-shows-and-sweeps-every-card` | the rail's card lines, the sweep, the agents' open cards on the board | 1 | `plan.py` `rail_read`, `rail_text`, `record_cards`, `stray_cards`, `sweep_judgment`, `sweep_sessions`; new `sweep_cards`; `board.py` `board_data`, `agent_views` and its five views; `status.js` |
| 8 | `only-crew-raises-a-rows-card` | the hook narrowed to the question, its name check kept whole, the question discipline in the briefs, the old commands removed | 1 to 7 | the card hook (`name_refusal` kept) and `hooks.json`; `plan.py` `card_refusal`, `CardReads`, `card_post`, `card_change`, `card_close`, `plan_card`, `card_model`, `close_card`, `notices`, `lost_rows`, `CARD_KEYS`, `parser`, `main`; `crew.py` `cards_how`, `lost_card_how`; the stage roles', `ops.md`'s, `dispatcher.md`'s and `main-ops.md`'s token; `plugin/bin/crew`; README; the crew skill |

### 7. Where each part of `every-crew-card-is-raised-at-its-point` lands

The series replaces that change whole. Its parts land by these rules: a requirement lands whole in the change after whose landing all of it holds, so no change's spec says more than its code does (`docs.4`); a card's form holds once this change's builder makes it, whichever later change raises the card, so a form lands here; a requirement that also says which command raises, changes or closes a card, or what its owner does with it by its brief, lands with that card's change, which rewrites that owner's brief in the same change; how an owner hears a card lands here, so every card is heard from the moment it is crew's; one that speaks of several kinds' events at once lands in change 8, after which all of it holds. The two requirements over 500 characters are split, each part stating one behavior, and so is one whose last sentence holds only once change 8 removes a command. Changes are numbered as in *The series*.

**Requirements**, 69, in the order the change's deltas held them:

| # | Capability | Requirement | Delta | Change |
|---|---|---|---|---|
| 1 | `rail-cards` | crew raises a row's card at its event | added | 8 |
| 2 | `rail-cards` | A raised card is adopted by its owner | added | 1 |
| 3 | `rail-cards` | A row's card is changed in place when its thing changes | added | 8 |
| 4 | `rail-cards` | A card is closed by crew at the event that ends it | added | 8 |
| 5 | `rail-cards` | A question is asked by four roles in their own name | added | 8 |
| 6 | `rail-cards` | crew refuses a question card from any other role or under a row's key | added | 8 |
| 7 | `rail-cards` | A question whose asker is gone is withdrawn | added | 7 |
| 8 | `rail-cards` | A deploy's card is a high approval | added | 1, as "A deploy's card is a high approval"; 4, as "A deploy's card carries the kit's release notes and steps as the deployer hands them" |
| 9 | `rail-cards` | A step's card is the user's do | added | 4 |
| 10 | `rail-cards` | A held step's card is a choice of when | added | 4 |
| 11 | `rail-cards` | Each rail row has a card key | modified | 8 |
| 12 | `rail-cards` | A card says whose it is and where it belongs | modified | 1 |
| 13 | `rail-cards` | A card carries what the user would read and the row's answers | modified | 3 |
| 14 | `rail-cards` | Landing is approved only by holding the button | modified | 1 |
| 15 | `rail-cards` | An answer wakes the owner, which acts on the user's word | modified | 8 |
| 16 | `rail-cards` | An agent never runs Pending You from npm or waits on a hold | modified | 1 |
| 17 | `rail-cards` | A crew agent's card acts are in the run record | modified | 8 |
| 18 | `rail-cards` | The rail shows each row's card | modified | 7 |
| 19 | `rail-cards` | The rail names an open card whose row is gone | modified | 7 |
| 20 | `rail-cards` | A card's words are the document's own | modified | 1 |
| 21 | `rail-cards` | The check refuses what it cannot read, and only for crew's sessions | modified | 8 |
| 22 | `rail-cards` | crew's card commands refuse what they cannot do, in the words that say why | modified | 1 |
| 23 | `rail-cards` | The landing card is posted once the bolt's verification is green | modified | 6 |
| 24 | `rail-cards` | A batch's card is a notice naming every unit | modified | 3 |
| 25 | `rail-cards` | A batch's card names every unit and links its session | modified | 1 |
| 26 | `rail-cards` | No card of crew's asks a question in words | modified | 1 |
| 27 | `rail-cards` | A card's picture is uploaded | modified | 1 |
| 28 | `rail-cards` | A card's document is inline Markdown | modified | 1 |
| 29 | `rail-cards` | A row's card lost to its owner is posted again | modified | 7 |
| 30 | `rail-cards` | The design agent posts a record's card under its record key | modified | 8 |
| 31 | `rail-cards` | A record key is checked against the teams file alone | modified | 5 |
| 32 | `rail-cards` | A record card's acts are recorded on the record | modified | 5 |
| 33 | `rail-cards` | A record's card is an approval | modified | 5 |
| 34 | `rail-cards` | The rail lists open record cards apart | modified | 5 |
| 35 | `rail-cards` | The owner of a row posts its card | removed | 8 |
| 36 | `rail-cards` | A review's card is an approval with a note | removed | 1 |
| 37 | `rail-cards` | A proposal's card is an approval | removed | 2 |
| 38 | `rail-cards` | A landing's card is a high-stakes approval | removed | 1 |
| 39 | `rail-cards` | No row's card takes another kind | removed | 8 |
| 40 | `rail-cards` | crew refuses a row's card in another form | removed | 8 |
| 41 | `rail-cards` | crew refuses a change that takes a row's card out of its form | removed | 8 |
| 42 | `rail-cards` | crew refuses a batch card in another form | removed | 8 |
| 43 | `rail-cards` | crew checks only a row's card in a crew session | removed | 8 |
| 44 | `rail-cards` | crew refuses a crew agent's card under any key but a row's of its own | removed | 8 |
| 45 | `rail-cards` | crew refuses a crew agent's area under any key but the kit's | removed | 1 |
| 46 | `rail-cards` | A crew agent's card is posted through crew | removed | 8 |
| 47 | `rail-cards` | A crew agent's card is changed, closed and read through crew | removed | 8 |
| 48 | `rail-cards` | crew names the card a change ends | removed | 8 |
| 49 | `rail-cards` | A row's card is closed when the row's key changes | removed | 8 |
| 50 | `rail-cards` | A card's link and bolt come first | removed | 3 |
| 51 | `rail-cards` | No card carries a path | removed | 1 |
| 52 | `rail-cards` | An owner checks its rows' cards when its sign-in may have changed | removed | 7 |
| 53 | `card-sessions` | A session is started for a card's row by its key | modified | 3 |
| 54 | `card-sessions` | A session is started only where its link can be answered | modified | 3 |
| 55 | `card-sessions` | The session's decision reaches the owner as the card's answer | modified | 3 |
| 56 | `card-sessions` | The session ends when its card closes | modified | 3 |
| 57 | `review-batches` | crew raises a batch's one card | added | 3 |
| 58 | `review-batches` | A batch card is read and answered in Pending You | modified | 3 |
| 59 | `review-batches` | The planner posts a batch as one card | removed | 3 |
| 60 | `main-level` | A record's status is recorded through crew, and its card raised when it was not settled in the pane | added | 5, as "A record's status is recorded through crew", "A record's card is raised unless it was settled in the pane" and "A record's card is closed with its accepted or rejected status" |
| 61 | `main-level` | A deploy and every operation are approved and recorded through crew | modified | 4 |
| 62 | `main-level` | A decision record is accepted only on the user's yes | modified | 5 |
| 63 | `main-level` | A record the user does not accept is revised or rejected | modified | 5 |
| 64 | `main-level` | The user's own words are their decision | modified | 5 |
| 65 | `plan-proposals` | A proposal is put before the user whole | modified | 2 |
| 66 | `plan-proposals` | A proposal is dropped with a reason, or replaced | modified | 2 |
| 67 | `plan-proposals` | A proposal's card is drawn from the plan and the proposal | modified | 1, but for its last sentence; 8, that sentence, as "A proposal's card has no command of its own" |
| 68 | `plan-proposals` | The change reads as text on a phone | modified | 1 |
| 69 | `plan-proposals` | The card's questions are the approval and the new units | modified | 2 |

**Tasks**, 16 in 9 groups:

| Task | What it builds | Change, task |
|---|---|---|
| 1.1 | the six builders | 1, 1.1 |
| 1.2 | the words rule and `follows` | 1, 1.2 |
| 1.3 | the proposal's checkbox list and the picture at twice the density | 1, 1.3 |
| 2.1 | the proposal's card at `propose`, `--replaces`, `agree`, `approve`, `drop` | 2, 1.1 |
| 2.2 | the batch's card at `crew review --wait`, closed by `crew card wait` | 3, 1.1 |
| 2.3 | the landing's card at the merge's end and the rail's read | 6, 1.1 |
| 2.4 | the deploy's and the step's cards at `crew ops offer`, `record`, `step` | 4, 1.1 |
| 2.5 | `crew record` | 5, 1.1 |
| 2.6 | `crew card read` and the line every post prints | 1, 3.1 |
| 3.1 | the hook narrowed | 8, 1.1 |
| 4.1 | the sweep | 7, 2.1 |
| 5.1 | the sessions of a batch and a long proposal | 3, 2.1 |
| 6.1 | the briefs | each owner's words of its card with that card's change: the planner's proposal words 2, 1.3; its batch words 3, 1.2; main-level ops's 4, 1.3; the design agent's 5, 1.3; the conductor's 6, 1.2; the question discipline, `lost_card_how` and the stage roles' words 8, 2.1 |
| 7.1 | the rail's card lines and the board | 7, 1.1 |
| 8.1 | the old commands removed, the docs | 8, 3.1 |
| 9.1 | `tests/t-cards.sh` and the suite | 1, 4.1 |

Tasks the series adds, each where a part above needs one of its own: 1's 2.1, the act, which decision 2 below has and which 2.1 to 2.6 each used; 2's 1.2, Send applying the boxes as they stand, which requirement 69 says and no task built; 4's 1.2 and 5's 1.2, the docs of each change's command (`docs.2`), which 8.1 held for all; 7's 1.2, the board's design band showing the records proposed, which decision 3's sentence on it says; 7's 2.2, a row's card that has none posted by the rail's next read, which decision 2's paragraph on refusals says; and in changes 2 to 8, a last task for the suite, as 9.1 is change 1's.

**Design**, by decision and part:

| Part | Change |
|---|---|
| Context; Goals / Non-Goals | 1 |
| 1. Six builders, its three paragraphs | 1; its clause that the form cases and `FORMS` go is decision 4's, in 8 |
| 2. Raised by the event's command: its first paragraph | 1 |
| 2: the table's proposal rows (accepted, rewritten, agreed, applied or dropped) | 2 |
| 2: the table's batch rows | 3 |
| 2: the table's landing rows | 6 |
| 2: the table's deploy and step rows | 4 |
| 2: the table's record rows | 5 |
| 2: the table's row for a declined approval | 1 |
| 2: its paragraph on refusals | 1; its clause that the next rail read posts a row's card that has none, 7 |
| 2: its paragraph on when a bolt reads proven | 6 |
| 3. `crew record` | 5; its sentence on the board's design band, 7 |
| 4. The hook, narrowed to three checks and a record | 8 |
| 5. The sweep withdraws | 7 |
| 6. Hearing, as settled from the hearing probe of 2026-10-16 | 1; its sentence on `crew card wait` for a batch, 3 |
| 7. Sessions | 3 |
| 8. The briefs | each owner's *Cards* words with its card's change: `conductor.md`'s 6, `planner.md`'s proposal words and `Do` lines 2 and batch words 3, `main-ops.md`'s 4, `design.md`'s and its rule-decided choice 5; `cards_how`, `lost_card_how`, the stage roles and `operator.md` 8 |
| 9. The rail and the board | 7 |
| 10. What each card shows: its opening and its landing, deploy, step, proposal, batch, record and whose-name bullets | 1; the landing's "not in this change", 6; the deploy's `crew ops offer` flags and files, 4; the step's one card at a time, 4; the batch's session, 3; the record's `crew record --alternatives` and the design agent's brief, 5 |
| 10: the question's bullet | 8 |
| Risks / Trade-offs | 1 |
| After deploy 1, the host's sign-in | 1 |
| After deploy 2, the standing agents restarted | 8; and in each of 2 to 6, the role whose brief it changes |

**The card trials' seven notes to the builder** (the recovery session's plan, 1.3):

| Note | Change |
|---|---|
| 1. Every card follows the one before it | 1 |
| 2. Each kind of content has its shape | 1 |
| 3. The proposal's form and its picture | 1 |
| 4. `crew ops offer <env> <sha> [--notes <file>] [--steps <file>]` | 4 |
| 5. `crew record <kit> <n> --proposed --alternatives <file>` | 5 |
| 6. The batch's form and its session | 3 |
| 7. Names | 1 |

**Counts**:

| Change | Requirements whole | Parts of a split one | Requirements in its deltas | Tasks of the change | Tasks added |
|---|---|---|---|---|---|
| 1 | 15 | 8, 67 | 17 | 1.1, 1.2, 1.3, 2.6, 9.1 | 1 |
| 2 | 4 | | 4 | 2.1, part of 6.1 | 2 |
| 3 | 10 | | 10 | 2.2, 5.1, part of 6.1 | 1 |
| 4 | 3 | 8 | 4 | 2.4, part of 6.1 | 2 |
| 5 | 7 | 60 | 10 | 2.5, part of 6.1 | 2 |
| 6 | 1 | | 1 | 2.3, part of 6.1 | 1 |
| 7 | 5 | | 5 | 4.1, 7.1 | 3 |
| 8 | 21 | 67 | 23 | 3.1, part of 6.1, 8.1 | 1 |
| | 66 | 3 | 74 | 16 | 13 |

Change 8's delta also holds one requirement of its own, "A crew agent's Pending You call names only the agent itself", the spec of `briefs.17`, whose check landed on main on 2026-10-16 and which that change keeps whole while it narrows the key and form checks. The 152 scenarios land each with its requirement; the two split requirements' scenarios each with the part whose behavior it shows. Two requirements are mended as they land: the landing card's "A note naming a defect…" sentence, which had run into its *No pull request* scenario, is in the requirement's text; and the landing card's close, in requirement 4's *A bolt landed*, is the landing's outcome in the words change 6 gives it, which wait on the record of who keeps which folders.

## Alternatives considered for hearing

From the recovery session's probe of Pending You 0.28.0 and 0.35.1, 2026-10-16 (`hearing-probe/finding.md` in the session's scratchpad; `PY` is the 0.28.0 store package, `mod` the fleet's wake mod):

- **`pendingyou hold <id>` in the owner's session.** The wake mod answers `hold` only for a session that already has a Pending You server on record from an earlier named call (`mod/wake.js:240`, `register.js:440`); otherwise the CLI's `hold` runs for real, keyed by request id with no name or session, and in the foreground blocks the agent for up to four hours (`PY/dist/hold.js:80,95-100`, `args.js:3`). The owner's own `get_request` gets the same adoption with nothing that can block (`mod/wake.js:278-284`), and records the server and name as it does.
- **`pendingyou watch` as a service on each host**, telling each answer's owner. It marks every answer on the host handed in the shared `state.json` (`PY/dist/watch.js:71,79`), which every session's per-message pickup reads and skips (`pickup.js:248`), so it would hide other sessions' answers from them.
- **A wake webhook per role** (`set_wake_webhook`): ids only, stored per name on the connection; it needs Tailscale Funnel, a receiver and a secret on every host, and the secrets are the user's to write.
- **Polling `list_pending`** from crew: a new bridge and MCP session for every poll, and still a watcher, which `state.4` rules out.

## Risks / Trade-offs

- An answer wakes its owner only once the owner has adopted the card and its session is idle: the mod checks an adopted card every 20 seconds, every 60 once it has been quiet for 30 minutes (`mod/wake.js:5-7`, `register.js:141-147`), and forgets one unchanged for seven days or across a new session id (`wake.js:11,369`, `register.js:33,368`). A card adopted by no one, or forgotten, is the rail's to show and the owner's to read at its breakpoints and fresh start.

- Two paths to Pending You, crew's and the sessions', which must share the host's sign-in to see each other's cards. The record settles the sign-in; crew refuses nothing when it is absent but says so on every post and on the rail.
- A card raised by a command an agent runs in its shell adds Pending You's round trip to that command; `code.9` holds, since the Bridge's call is one short MCP session and the command answers once the commit is made and the post attempted.
- Pending You's tool schema is read at each connection; a field it renames breaks a builder loudly (`read.2`), which is better than today's silent drift.

## After deploy

1. The host's Pending You sign-in: `pendingyou-signin` on mac-studio and on chuck-herdr-alpha, by the user, since the device code is approved on their phone and no check can do it; the environments are the two hosts.
