## MODIFIED Requirements

### Requirement: A row forecast to conflict with main takes main first
A row whose bolt is forecast to conflict with what the kit's main holds, by the card's forecast or by one a conductor's wait recorded at the bolt's present head, SHALL be held with no box, saying it takes main first, the files, and that its team takes main in by a fix. It SHALL NOT be offered to land, and SHALL have a box again once the bolt reads proven at a new head with no conflict forecast. A conflict only with a bolt above it holds nothing. A row whose bolt the user left SHALL NOT be held so: it keeps its box and says it would take main first, as "A row the user left says whether it would take main first" has it.

#### Scenario: Main landed a change the bolt also made
- **WHEN** `y` reads proven and main has landed a change to `openspec/specs/artifact-buckets/spec.md` that `y`'s own archive also changed
- **THEN** `land/crew` holds `y` with no box, saying `y` takes main first, forecast to conflict with main on `openspec/specs/artifact-buckets/spec.md`, and that its team takes main in by a fix

#### Scenario: A wait found it first
- **WHEN** a conductor's wait recorded `y` forecast to conflict with main at `y`'s present head, and the card's own forecast against main could not be made
- **THEN** `y` is still held taking main first, in the recorded files

#### Scenario: Only a bolt above it
- **WHEN** `z` is forecast to conflict with `y`, the row above it, and with nothing on main
- **THEN** `z` keeps its box, its row naming the conflict with `y`

#### Scenario: The fix merges
- **WHEN** `y`'s take-main fix merges and `y` reads proven at its new head with no conflict forecast against main
- **THEN** `y` has its box on `land/crew` again

#### Scenario: A bolt the user left
- **WHEN** the user cleared `z` on their send of `land/crew`, and main then lands a change `z` also makes
- **THEN** `z` keeps its box on the card that follows, unticked, and is not held taking main first

## ADDED Requirements

### Requirement: A bolt the user left stays left until they tick it
A bolt SHALL be left when the user cleared it on their send of its kit's landings card, or when main-level ops recorded the user's words in its pane stopping its landing. It SHALL stay left, shown unticked on each card that follows, until the user ticks it on a later send or ops lands it on the user's words, or until its head moves. crew SHALL move no left bolt's head: it starts no take-main fix for it while it is left.

#### Scenario: Cleared on a send
- **WHEN** the user sends `land/swancloud` with `x` ticked and `builds-reach-the-phone` cleared
- **THEN** `builds-reach-the-phone` is left, and the card that follows shows it unticked

#### Scenario: Left again
- **WHEN** the user sends the card that follows with `builds-reach-the-phone` cleared again
- **THEN** it stays left, unticked on the next card

#### Scenario: Main moves under it many times
- **WHEN** main moves five times while `builds-reach-the-phone` is left, each move conflicting with it
- **THEN** no take-main fix is started for it, its head stays where it was, and it stays left on the card, asked for no more than any other row

#### Scenario: Its head moves
- **WHEN** a fix its conductor started for a defect merges into a left bolt and it reads proven at the new head
- **THEN** it is no longer left, and the card asks for it as a row at its new head

### Requirement: A row the user left says whether it would take main first
Each row of a bolt the user left SHALL be forecast against main whenever the card is raised, as every row is, and SHALL keep its box. When its forecast against main finds a conflict, the row SHALL say it would take main first if ticked, on which files and at which revision of main, and that its team takes main in by a fix once it is ticked, the user's send standing through it; otherwise it SHALL say it lands clean. When the forecast first finds such a conflict at the bolt's head and main's revision while a card waits on the user, crew SHALL change the card in place saying so; the same forecast SHALL NOT change the card again.

#### Scenario: Left, and main conflicts with it
- **WHEN** `z` is left on `land/crew`, waiting on the user, and main moves to `e4f5a6b`, landing a change to `README.md` that `z` also makes
- **THEN** `land/crew` is changed in place, its note saying `z`, which they left, would take main first, forecast to conflict with main on `README.md` at `e4f5a6b`; `z` keeps its box, its row saying it would take main first once ticked; and nothing is told to `z`'s conductor

#### Scenario: Raised again at the same heads
- **WHEN** the card is raised again and neither `z` nor main has moved
- **THEN** the card is not changed for it

#### Scenario: Left and clean
- **WHEN** `z` is left and its forecast against main finds no conflict
- **THEN** its row says no conflict is forecast

### Requirement: Ticking a left bolt that conflicts with main starts its take-main fix
When the user ticks a bolt they had left on a send of its kit's landings card, crew SHALL act on the send when ops reads it: a forecast conflict with what main has landed SHALL hold the bolt's row as taking main first, its conductor SHALL be told the take-main fix then, once, and the user's send SHALL stand for it through the fix. The bolts the read of the send gives ops to land SHALL leave it out, saying it takes main first and that the send stands for it.

#### Scenario: Ticked after being left
- **WHEN** `z` was left on `land/crew` and forecast to conflict with main on `README.md`, and the user sends the card with `z` ticked
- **THEN** `crew card read land/crew` holds `z` taking main first, swc-1-conductor is told `crew fix swc-1 take-main-e4f5a6b "Take main into the bolt: it is forecast to conflict on README.md"`, and the read leaves `z` out of the command that lands, saying it takes main first and that the user's send stands for it

#### Scenario: The fix merges
- **WHEN** `z`'s take-main fix merges and `z` reads proven at its new head
- **THEN** `z` lands on that same send, with nothing asked

#### Scenario: Ticked and clean
- **WHEN** `z` was left, its forecast against main finds no conflict, and the user ticks it
- **THEN** the read gives `z` to land in the command, as any ticked bolt

### Requirement: A bolt stopped in ops's pane is shown as left
A bolt whose landing main-level ops recorded the user's words stopping SHALL be shown on its kit's landings card unticked, as a bolt the user left, at the head it had when the stop was recorded, and SHALL be treated as left until the user ticks it on a send or ops lands it on their words.

#### Scenario: Stopped, then the card is raised
- **WHEN** ops records the user's words stopping `z`'s landing, and `land/crew` is raised
- **THEN** `z`'s row is unticked, the card's note says `z` was stopped on the user's words, and no take-main fix is started for it

#### Scenario: Ticked after a stop
- **WHEN** the user then ticks `z` on a send of `land/crew`
- **THEN** `z` is no longer left, and lands on that send or takes main first as any ticked bolt
