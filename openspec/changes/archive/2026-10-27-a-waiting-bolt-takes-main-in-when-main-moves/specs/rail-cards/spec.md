## MODIFIED Requirements

### Requirement: The landings card forecasts each row's conflicts
Each row SHALL carry the conflicts crew forecasts when its bolt is merged onto the kit's main and onto each bolt above it on the card, from their merge base, naming the files and the bolt or main each is with, or saying none is forecast. A forecast crew cannot make SHALL be said on its row with why, and SHALL hold nothing. Forecasts SHALL be made again whenever the card is raised or changed, and whenever the kit's main moves while the card is open, against GitHub's main after a fetch and each bolt where it lives.

#### Scenario: Two bolts touch one file
- **WHEN** `y` and `z` of crew are rows in that order, and both change `plugin/lib/plan.py`'s same lines
- **THEN** `z`'s row says it is forecast to conflict with `y` on `plugin/lib/plan.py`, and `y`'s row says no conflict is forecast

#### Scenario: A bolt behind main
- **WHEN** main has landed a change to `README.md` that bolt `y` also changes
- **THEN** `y`'s row says it takes main first, forecast to conflict with main on `README.md`

#### Scenario: A bolt branch crew cannot read
- **WHEN** bolt `y` was made before gives went through sluice and its branch is on no host crew can read it from
- **THEN** `y`'s row says its forecast could not be made and why, and `y` keeps its box

#### Scenario: Main moves under an open card
- **WHEN** `land/crew` is open with `y` as a row forecast against main at `a1b2c3d`, and the rail is read on the main level's host once crew's checkout of the kit reads GitHub's main, as last fetched, at `e4f5a6b`
- **THEN** crew raises `land/crew` again, fetching GitHub's main and forecasting `y` against `e4f5a6b`

#### Scenario: Main has not moved
- **WHEN** `land/crew` is open with its rows forecast against `a1b2c3d`, and the rail is read with GitHub's main still at `a1b2c3d`
- **THEN** the read raises no landings card and fetches nothing for it

## ADDED Requirements

### Requirement: A row forecast to conflict with main takes main first
A row whose bolt is forecast to conflict with what the kit's main holds, by the card's forecast or by one a conductor's wait recorded at the bolt's present head, SHALL be held with no box, saying it takes main first, the files, and that its team takes main in by a fix. It SHALL NOT be offered to land, and SHALL have a box again once the bolt reads proven at a new head with no conflict forecast. A conflict only with a bolt above it holds nothing.

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

### Requirement: A take-main fix holds its row as taking main first
A fix in flight on a bolt whose words begin "Take main into the bolt" SHALL hold the bolt's row with no box, saying it takes main first and naming the fix and its words.

#### Scenario: The conductor started the fix
- **WHEN** swc-1-conductor starts `take-main-e4f5a6b` on `y` with "Take main into the bolt: it is forecast to conflict on README.md"
- **THEN** `land/crew` holds `y`, saying it takes main first, `take-main-e4f5a6b` taking main in: "Take main into the bolt: it is forecast to conflict on README.md"

### Requirement: A row taking main first changes the card in place
When a row comes to take main first while its card waits on the user, crew SHALL change the card in place saying which bolt takes main first and why, as for any row held, following it instead only when the card's form must change; a card left with no row that can land SHALL be withdrawn saying why.

#### Scenario: One of two
- **WHEN** `land/crew` waits with `y` and `z` as boxes, and main moves so that `z` is forecast to conflict with it
- **THEN** the card is followed by one with `y` as its one box and `z` held taking main first, since a list of two becomes an approval of one

#### Scenario: One of three
- **WHEN** `land/crew` waits with `y`, `z` and `w` as boxes, and main moves so that `w` is forecast to conflict with it
- **THEN** the card is changed in place, its change note saying `w` takes main first and why, `y` and `z` still ticked

### Requirement: A send stands for a ticked bolt taking main in
When the user has sent a landings card with a bolt ticked, and that bolt then takes main first, by a forecast or a take-main fix in flight, crew SHALL keep the send standing for it: the card SHALL be left, and SHALL NOT be closed counting that bolt as held, while it takes main in.

#### Scenario: Ticked, then forecast to conflict
- **WHEN** the user sent `land/crew` with `y` ticked, and before ops submits it main moves so that `y` is forecast to conflict with it
- **THEN** `land/crew` is left as it is, its send still standing for `y`, and `y`'s conductor is told the take-main fix

#### Scenario: Ticked beside one that lands
- **WHEN** the user sent `land/crew` with `y` and `z` ticked, `z` lands, and `y` takes main first
- **THEN** `land/crew` is left as it is while `y` takes main in, and is not closed saying `y` was held
