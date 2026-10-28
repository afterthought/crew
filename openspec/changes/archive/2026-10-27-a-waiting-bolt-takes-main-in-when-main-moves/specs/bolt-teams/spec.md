## ADDED Requirements

### Requirement: A waiting bolt's conflict with main tells its conductor the take-main fix
When the forecast of a bolt's row on its kit's landings card finds a conflict with what main holds, crew SHALL tell the bolt's conductor, through `crew tell`, the take-main fix to start now, in the words a conductor's wait gives for a conflict with main, and SHALL record the forecast on the bolt with the bolt's head, main's revision and the files. It SHALL be told once for the same bolt head and revision of main, whichever forecast recorded it first.

#### Scenario: Main moves under a waiting bolt
- **WHEN** swc-1 holds `y`, proven and a row of `land/crew`, and main lands a change to `README.md` that `y` also changes, moving GitHub's main to `e4f5a6b`
- **THEN** swc-1-conductor is told `y` is forecast to conflict with main on `README.md`, with `crew fix swc-1 take-main-e4f5a6b "Take main into the bolt: it is forecast to conflict on README.md"`, and a `forecast` on `bolt/y` is recorded with `y`'s head, `main@e4f5a6b` and `README.md`

#### Scenario: Told once
- **WHEN** the card is raised again and neither `y` nor main has moved
- **THEN** swc-1-conductor is told nothing more, and `y` is still held taking main first

#### Scenario: The wait said it first
- **WHEN** a conductor's wait recorded `y`'s forecast against main at the same head and revision of main
- **THEN** the card's raise tells swc-1-conductor nothing of it

#### Scenario: The team holds two bolts
- **WHEN** swc-1 holds `y`, waiting to land, and `x`, which it builds
- **THEN** the fix's command names `--bolt y`

#### Scenario: The conductor cannot be told
- **WHEN** swc-1-conductor's pane does not take the tell
- **THEN** nothing is recorded for the forecast, `y` is still held taking main first, and the next raise tells it again

### Requirement: A wait's forecast conflict with main changes the kit's landings card
When a conductor's wait records a bolt forecast to conflict with what main has landed, and the bolt is a row of its kit's landings card, crew SHALL raise that card again at once, so the row takes main first without waiting for main to move again.

#### Scenario: The wait finds it
- **WHEN** swc-1 holds `y`, a row of `land/crew` with a box, and swc-1-conductor's wait records `y` forecast to conflict with main on `shared.txt`
- **THEN** `land/crew` is raised again on the main level's host, holding `y` taking main first

#### Scenario: A conflict with a queued submission
- **WHEN** the wait forecasts `y` to conflict on `shared.txt` with `#7`, queued on main ahead of it
- **THEN** `land/crew` is not raised for it, and `y` keeps its box
