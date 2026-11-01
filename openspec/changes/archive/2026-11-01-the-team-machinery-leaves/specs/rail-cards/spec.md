## ADDED Requirements

### Requirement: A question is asked by three roles in their own name
The planner, main-level ops and the design agent MAY post a card for a question of their own through Pending You's own tools in their session, under an idempotency key of their own that is no row's, shaped as they see fit. The operator agent SHALL post none, the user being in its pane.

#### Scenario: The planner asks
- **WHEN** wldn-planner calls `post_request` with the key `ask/wldn-planner/hold-the-macs` and three options
- **THEN** the call goes through, and the run record has a `card.post` entry on the planner with that key and the card's id

#### Scenario: A question with a words answer
- **WHEN** the design agent's question card asks for the user's words in a `text` question
- **THEN** the call goes through: a question's form is its asker's

### Requirement: crew refuses a question card from any role but the three, or under a row's key
crew SHALL refuse a post, change or close from any role but the three, naming them, and a crew agent's own post, change or close under a row's key or of a row's card, naming the card as crew's; it SHALL refuse nothing else of a question's form. A post's key SHALL be judged by its form alone, with or without `:<n>` or the fill of a short key; a change's or a close's, which carries a request id, by the card this host's run record holds under that id, crew's raises and the agents' own posts alike.

#### Scenario: An agent posts a landing card by hand
- **WHEN** wldn-ops calls `post_request` with the key `land/y`
- **THEN** the call is refused, saying the landing card is crew's and is raised when the bolt reads proven

#### Scenario: An agent posts under a row's key as crew sends it
- **WHEN** wldn-ops calls `post_request` with the key `land/b1_`, or wldn-planner with `batch/7_` or `batch/7:2`
- **THEN** the call is refused, saying the card is crew's

### Requirement: A row forecast to conflict with main takes main first until a fix takes main in
A row whose bolt is forecast to conflict with what the kit's main holds, by the card's forecast or by one the run record holds at the bolt's present head, SHALL be held with no box, saying it takes main first, the files, and that it does until a fix taking main in moves its head. The raise that first finds the conflict at a bolt head and revision of main SHALL record it once, as a `forecast` on the bolt, and SHALL tell no agent and start nothing: a fix taking main in is launched when sluice refuses the bolt's landing for a conflict with main, as "A landing that conflicts with main takes main in by a fix place" has it, or by a fix launched on the bolt by hand. It SHALL NOT be offered to land, and SHALL have a box again once the bolt reads proven at a new head with no conflict forecast. A conflict only with a bolt above it holds nothing. A row whose bolt the user left SHALL NOT be held so: it keeps its box and says it would take main first, as "A row the user left says whether it would take main first" has it.

#### Scenario: Main landed a change the bolt also made
- **WHEN** `y` reads proven and main has landed a change to `openspec/specs/artifact-buckets/spec.md` that `y`'s own archive also changed
- **THEN** `land/crew` holds `y` with no box, saying `y` takes main first, forecast to conflict with main on `openspec/specs/artifact-buckets/spec.md`, until a fix taking main in moves its head; the run record gains one `forecast` on `bolt/y` at `y`'s head and main's revision; and no agent is told

#### Scenario: Raised again at the same heads
- **WHEN** the run record holds `y`'s forecast at `y`'s present head, and the card's own forecast against main could not be made
- **THEN** `y` is still held taking main first, in the recorded files, and nothing more is recorded

#### Scenario: Only a bolt above it
- **WHEN** `z` is forecast to conflict with `y`, the row above it, and with nothing on main
- **THEN** `z` keeps its box, its row naming the conflict with `y`

#### Scenario: The fix merges
- **WHEN** a fix taking main in merges into `y` and `y` reads proven at its new head with no conflict forecast against main
- **THEN** `y` has its box on `land/crew` again

#### Scenario: A bolt the user left
- **WHEN** the user cleared `z` on their send of `land/crew`, and main then lands a change `z` also makes
- **THEN** `z` keeps its box on the card that follows, unticked, and is not held taking main first

## MODIFIED Requirements

### Requirement: A row the user left says whether it would take main first
Each row of a bolt the user left SHALL be forecast against main whenever the card is raised, as every row is, and SHALL keep its box. When its forecast against main finds a conflict, the row SHALL say it would take main first if ticked, on which files and at which revision of main, and that once it is ticked it waits for a fix taking main in, the user's send standing through it; otherwise it SHALL say it lands clean. When the forecast first finds such a conflict at the bolt's head and main's revision while a card waits on the user, crew SHALL change the card in place saying so; the same forecast SHALL NOT change the card again.

#### Scenario: Left, and main conflicts with it
- **WHEN** `z` is left on `land/crew`, waiting on the user, and main moves to `e4f5a6b`, landing a change to `README.md` that `z` also makes
- **THEN** `land/crew` is changed in place, its note saying `z`, which they left, would take main first, forecast to conflict with main on `README.md` at `e4f5a6b`; `z` keeps its box, its row saying it would take main first once ticked; and no agent is told

#### Scenario: Raised again at the same heads
- **WHEN** the card is raised again and neither `z` nor main has moved
- **THEN** the card is not changed for it

#### Scenario: Left and clean
- **WHEN** `z` is left and its forecast against main finds no conflict
- **THEN** its row says no conflict is forecast

### Requirement: A refused landing is held on its row
A bolt whose landing sluice refused for its own content, its submission in conflict or blamed for a check that ran and failed, SHALL be held on its row at that head, with no box, the row saying its landing was rejected and the bolt is open for work, sluice's words, and that it waits for a fix on the bolt, while the bolts after it go on. Once its head moves and it reads proven, it SHALL land on the user's send that ticked it when that send still stands for its work, and SHALL otherwise have a box again. A landing that did not land for any other cause SHALL NOT hold its row. No row SHALL name a team.

#### Scenario: The second of three is refused
- **WHEN** the user sends `land/crew` with `y`, `z` and `w` ticked, and sluice refuses `z` for a conflict on `plugin/lib/plan.py`
- **THEN** `y` and `w` land, `z` stays on crew's landing row held with no box, saying its landing was rejected and the bolt is open for work, with sluice's words, and that it waits for a fix on the bolt, and the next landings card raised carries `z` held with no box

#### Scenario: A check fails
- **WHEN** sluice blames `z`'s landing for `tests:logic`, which ran and failed
- **THEN** `z` is held on its row with no box, saying its landing was rejected and the bolt is open for work, with sluice's words, and that it waits for a fix on the bolt

#### Scenario: The fix merges
- **WHEN** a fix taking main in, launched on `z`, merges into `z` and `z` reads proven at its new head, its own work unchanged since the user's send
- **THEN** `z` has no box on any landings card and lands on that send

#### Scenario: A fix that changes the bolt's work merges
- **WHEN** `z` was refused for a failed check, and a fix on `z` commits a change and merges, and `z` reads proven at its new head
- **THEN** `z` has a box on `land/crew` again, its note naming the fix's commit

#### Scenario: A bolt the user left
- **WHEN** the user cleared `z` on their send of `land/crew`, and main then lands a change `z` also makes
- **THEN** `z` keeps its box on the card that follows, unticked, and is not held taking main first

## REMOVED Requirements

### Requirement: The conductor's tell to the operator agents is for what has no card
**Reason**: Record 0047 move 5, record 0050 part 3: no conductor, and no operator agents of a team to tell.
**Migration**: A question with no card goes to the partition's operator by `crew send` or `crew tell`, as any role's.

### Requirement: A take-main fix holds its row as taking main first
**Reason**: Record 0047 move 5, record 0050 part 3: no team's take-main fix; a landing's conflict with main is answered as the crossed path answers it.
**Migration**: The crossed path's fix of a bolt (`teams-cross-to-flume-as-their-bolts-land`).

### Requirement: Ticking a left bolt that conflicts with main starts its take-main fix
**Reason**: Record 0047 move 5, record 0050 part 3: no team's take-main fix is started by a tick.
**Migration**: The crossed path's fix of a bolt (`teams-cross-to-flume-as-their-bolts-land`).

### Requirement: A question is asked by four roles in their own name
**Reason**: Record 0047 move 5: the conductor is no longer among those who ask, and no stage agent, team ops or dispatcher of crew's is left to refuse (`briefs.11`).
**Migration**: "A question is asked by three roles in their own name", added by this change.

### Requirement: crew refuses a question card from any other role or under a row's key
**Reason**: Record 0047 move 5: no stage agent of crew's asks its conductor, and no conductor posts.
**Migration**: "crew refuses a question card from any role but the three, or under a row's key", added by this change.

### Requirement: A row forecast to conflict with main takes main first
**Reason**: Record 0047 move 5: no conductor's wait records a forecast and no team takes main in; the landings card's raise records the forecast and tells no one (Task notes 2.2).
**Migration**: "A row forecast to conflict with main takes main first until a fix takes main in", added by this change.
