## MODIFIED Requirements

### Requirement: Landing is approved only by holding the button
A kit's landings card SHALL never be landed from a key in Herdr's popup. With one row, a bolt that can land, it SHALL be an `approve` of risk high, not reversible, approved by holding the button in the Pending You app, and SHALL NOT carry the `highStakes` flag, which Pending You refuses on an approval. With two or more rows, those that can land and those beside them taking main first, it SHALL be a list of boxes carrying `highStakes`, which Pending You takes on a list as the same test as risk high.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landings card of one row in Herdr's popup
- **THEN** Pending You refuses it as high risk, and the bolt does not land

#### Scenario: A list of three bolts
- **WHEN** crew raises `land/crew` with three rows that can land
- **THEN** the card is one list of three boxes with `highStakes` set, and no `approve` block

#### Scenario: One that can land beside one taking main first
- **WHEN** crew raises `land/crew` with `y`, which can land, and `z`, which takes main first
- **THEN** the card is one list of two boxes with `highStakes` set, `y` ticked and `z` unticked

### Requirement: A row that can land is a box, ticked as crew proposes
With two to five rows, a landings card SHALL be one list of those rows in order, each ticked as crew proposes but a row taking main first, which SHALL be unticked, each labelled with its place and its bolt, its detail what the row carries, its consequence its forecast; with six or more, lists of five at most, in order, each a question. Clearing a box SHALL leave that bolt waiting. The face SHALL say one send lands the ticked bolts in the order shown and a note may move one.

#### Scenario: Three bolts
- **WHEN** `y`, `z` and `w` of crew read proven in that order
- **THEN** `land/crew` is one list of three ticked boxes, `1. y`, `2. z`, `3. w`, and its summary says the send lands the ticked ones in that order

#### Scenario: Seven bolts
- **WHEN** seven bolts of crew read proven
- **THEN** `land/crew` holds two lists, of four and three, in order, and a change to its rows while it waits withdraws it and posts its new form following it, since Pending You changes no card's questions

### Requirement: A row forecast to conflict with main takes main first
A row whose bolt is forecast to conflict with what the kit's main holds, by the card's forecast or by one a conductor's wait recorded at the bolt's present head, SHALL take main first, saying so, the files, and that its team takes main in by a fix. It SHALL NOT be ticked or proposed to land while it conflicts: beside a row that can land it SHALL stay on the card as an unticked box, as "A row taking main first changes the card in place" has it, and with none that can land it SHALL be held, no card raised for it. It SHALL be ticked as crew proposes again once the bolt reads proven at a new head with no conflict forecast. A conflict only with a bolt above it holds nothing. A row whose bolt the user left SHALL NOT take main first so: it keeps its box and says it would take main first, as "A row the user left says whether it would take main first" has it.

#### Scenario: Main landed a change the bolt also made
- **WHEN** `x` and `y` read proven, and main has landed a change to `openspec/specs/artifact-buckets/spec.md` that `y`'s own archive also changed
- **THEN** `land/crew` shows `y` unticked, saying `y` takes main first, forecast to conflict with main on `openspec/specs/artifact-buckets/spec.md`, and that its team takes main in by a fix, and `x` ticked

#### Scenario: A wait found it first
- **WHEN** a conductor's wait recorded `y` forecast to conflict with main at `y`'s present head, and the card's own forecast against main could not be made
- **THEN** `y` still takes main first, in the recorded files

#### Scenario: Only a bolt above it
- **WHEN** `z` is forecast to conflict with `y`, the row above it, and with nothing on main
- **THEN** `z` is ticked, its row naming the conflict with `y`

#### Scenario: The fix merges
- **WHEN** `y`'s take-main fix merges and `y` reads proven at its new head with no conflict forecast against main
- **THEN** `y` is ticked on `land/crew` again

#### Scenario: A bolt the user left
- **WHEN** the user cleared `z` on their send of `land/crew`, and main then lands a change `z` also makes
- **THEN** `z` keeps its box on the card that follows, unticked, and does not take main first

### Requirement: A take-main fix holds its row as taking main first
A fix in flight on a bolt whose words begin "Take main into the bolt" SHALL hold the bolt's row as taking main first, never ticked, saying it takes main first and naming the fix and its words; beside a row that can land the row SHALL stay on the card, as "A row taking main first changes the card in place" has it.

#### Scenario: The conductor started the fix
- **WHEN** swc-1-conductor starts `take-main-e4f5a6b` on `y` with "Take main into the bolt: it is forecast to conflict on README.md", and `x` of crew can land
- **THEN** `land/crew` shows `y` unticked, saying it takes main first, `take-main-e4f5a6b` taking main in: "Take main into the bolt: it is forecast to conflict on README.md"

### Requirement: A row taking main first changes the card in place
While any row of a kit's landings card can land, each row taking main first, forecast to conflict with main or with only take-main fixes in flight, SHALL stay on the card as a box, unticked, its detail saying it takes main first and why, its consequence that ticked it lands once its team has taken main in and sluice has proven it, the user's send standing through it; a row taking main first that an earlier send still lands SHALL be held with no box. The card's form SHALL be read from every row it shows. When a row comes to take main first while its card waits on the user, or comes back from it, crew SHALL change the card in place saying so, and SHALL NOT withdraw it and post it again: a bolt taking main in keeps the card's rows and so its form. crew SHALL follow the card instead only when its form must change, as when a second bolt joins a card of one row, since Pending You changes no card's kind in place and takes no list of fewer than two boxes. A card left with no row that can land SHALL be withdrawn saying why. A row the card showed taking main first that the user leaves unticked on their send SHALL NOT be a bolt they left: once it can land, a card asks for it, ticked as crew proposes.

#### Scenario: One of two
- **WHEN** `land/crew` waits with `y` and `z` as ticked boxes, and main moves so that `z` is forecast to conflict with it
- **THEN** the card is changed in place, its change note saying `z` takes main first and why, `y` still ticked and `z` unticked, saying why

#### Scenario: One of three
- **WHEN** `land/crew` waits with `y`, `z` and `w` as boxes, and main moves so that `w` is forecast to conflict with it
- **THEN** the card is changed in place, its change note saying `w` takes main first and why, `y` and `z` still ticked and `w` unticked

#### Scenario: Back from taking main in
- **WHEN** `land/crew` waits with `y` ticked and `z` unticked taking main first, and `z`'s take-main fix merges and `z` reads proven at `def5678`
- **THEN** the card is changed in place, its change note saying `z`'s head is now `def5678` and `z` can land again, both ticked

#### Scenario: Taking main in and back, one card
- **WHEN** `land/crew` waits with `y` and `z`, main moves under `z`, `z`'s take-main fix runs and merges, and main moves under `z` again, as switchboard-kit's identity-and-access did beside a-deploy-row on 2026-11-06
- **THEN** one card is open throughout, posted once and changed in place at each move, and none is withdrawn and posted again

#### Scenario: Joining a card of one
- **WHEN** `land/crew` waits with `y` alone, and `z`, proven, is forecast to conflict with main
- **THEN** the card is followed by a list of `y` ticked and `z` unticked, taking main first, since a card of one row is an approval

#### Scenario: Unticked on the send
- **WHEN** the user sends `land/crew` with `y` ticked and `z`, shown taking main first, unticked, and `z` then reads proven
- **THEN** `z` is not left: the close names no bolt left, and the card that follows asks for `z` ticked

#### Scenario: Nothing else can land
- **WHEN** `y` lands from `land/crew` and `z` still takes main first
- **THEN** no landings card of crew is open until `z` can land

### Requirement: A send stands for a ticked bolt taking main in
When the user has sent a landings card with a bolt ticked, and that bolt then takes main first, by a forecast or a take-main fix in flight, or they ticked it while its row took main first, crew SHALL keep the send standing for it: the card SHALL be left, and SHALL NOT be closed counting that bolt as held, while it takes main in. `crew card read land/<kit>` SHALL leave such a bolt out of the submit it prints only while the bolt still stands at the head the card showed or the run record holds a conflict at its head now, read where the bolt lives; once its take-main fix has moved it, its own work unchanged, the read SHALL give it to land on that send.

#### Scenario: Ticked, then forecast to conflict
- **WHEN** the user sent `land/crew` with `y` ticked, and before ops submits it main moves so that `y` is forecast to conflict with it
- **THEN** `land/crew` is left as it is, its send still standing for `y`, and `y`'s conductor is told the take-main fix

#### Scenario: Ticked beside one that lands
- **WHEN** the user sent `land/crew` with `y` and `z` ticked, `z` lands, and `y` takes main first
- **THEN** `land/crew` is left as it is while `y` takes main in, and is not closed saying `y` was held

#### Scenario: Ticked while taking main in
- **WHEN** the user sends `land/crew` with `y` ticked and `z`, shown taking main first, ticked too
- **THEN** `y` lands, the card is left while `z` takes main in, and `z` lands on that send once it reads proven, its own work unchanged

#### Scenario: Read after the take-main fix
- **WHEN** the run record holds `z` forecast to conflict with main at `abc1234`, the head the card showed, the user ticked `z`, and `z`'s take-main fix has moved it to `def5678`, with no conflict recorded there
- **THEN** `crew card read land/crew` gives `z` to land beside the other ticked bolts, in the card's order
