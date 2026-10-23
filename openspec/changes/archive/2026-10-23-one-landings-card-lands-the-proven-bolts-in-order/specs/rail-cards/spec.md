## MODIFIED Requirements

### Requirement: Landing is approved only by holding the button
A kit's landings card SHALL never be landed from a key in Herdr's popup. With one row that can land it SHALL be an `approve` of risk high, not reversible, approved by holding the button in the Pending You app, and SHALL NOT carry the `highStakes` flag, which Pending You refuses on an approval. With two or more it SHALL be a list of boxes carrying `highStakes`, which Pending You takes on a list as the same test as risk high.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landings card of one row in Herdr's popup
- **THEN** Pending You refuses it as high risk, and the bolt does not land

#### Scenario: A list of three bolts
- **WHEN** crew raises `land/crew` with three rows that can land
- **THEN** the card is one list of three boxes with `highStakes` set, and no `approve` block

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a crew card SHALL be acted on by the role whose row it is, woken in its session by the card it adopted, and by no other: the planner applies or rewrites the proposal; main-level ops lands the bolts the user ticked on a kit's landings card, in the card's order, and passes a note naming a defect in a bolt to that bolt's conductor, who starts a fix on it; main-level ops runs the deploy's approval or the step's state; the design agent sets the record's status. crew SHALL then close the card at that act's event.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves the card for proposal 4 on the phone
- **THEN** the planner is woken, runs `crew plan answer` and `crew plan approve 4`, which closes the card with what was applied, and the rail's proposal row is gone

#### Scenario: Changes asked for on a review card
- **WHEN** the user writes a note on a batch's card asking for changes to unit `x`
- **THEN** the planner's wait returns the note, the conductor runs construct again with its words, and no approval is asked

#### Scenario: Landing approved
- **WHEN** the user leaves `a` and `c` ticked on `land/crew`, clears `b`, and sends
- **THEN** swancloud-ops is woken, `crew card read land/crew` prints `a` then `c` and the command that lands them in that order, and no conductor is asked to pass anything on

#### Scenario: A defect noted on a row
- **WHEN** the user's note on `land/crew` names a defect in bolt `b`
- **THEN** swancloud-ops tells `b`'s conductor the note's words, the conductor starts a fix on `b`, and `b`'s row is held for the fix

### Requirement: The landing card is posted once the bolt's verification is green
crew SHALL keep one landings card for each kit with a proven bolt waiting on its main, keyed `land/<kit>`, in the name of the partition's main-level ops, posted on the partition's main host. A bolt SHALL be a row that can land once every unit and chore of it has merged, every unit's latest change has been in a batch whose card the user has answered, sluice's verdict at its head is green and no fix of it is in flight. Rows SHALL be in the plan's order. The card SHALL ask only for the landing.

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` of crew has merged, each unit's latest change has been in a batch the user has answered and sluice is green at `abc1234`, and no other bolt of crew can land
- **THEN** one card keyed `land/crew` is open in swancloud-ops's name, an approve of risk high, naming `y`, its units and chores and the verdict

#### Scenario: Sluice's pull request
- **WHEN** sluice's submission at `y`'s head has pull request #23 on the kit's GitHub
- **THEN** `y`'s row links it, titled as sluice's pull request for `y`'s landing, on the card's face and in its details

#### Scenario: No pull request
- **WHEN** the kit's sluice opens no pull request for a submission
- **THEN** the row carries no link, and says nothing of one

#### Scenario: Two green bolts of one kit
- **WHEN** bolts `y` and `z` of crew both read proven, `y` first in the plan
- **THEN** one card keyed `land/crew` is open in swancloud-ops's name, its rows `y` then `z`, and no card is open under `land/y` or `land/z`

#### Scenario: Bolts of two kits
- **WHEN** bolt `y` of crew and bolt `w` of swancloud both read proven
- **THEN** `land/crew` holds `y`, `land/swancloud` holds `w`, and each is its own card

#### Scenario: A row carries what the bolt's card carried
- **WHEN** bolt `y` of swc-1, holding units `a` and `b` read in batch 7 and chore `c`, reads proven at `abc1234`, sluice green there since 10:02 with pull request #23, main moved two landings since `y` was cut
- **THEN** `y`'s row names swc-1-conductor, `a`, `b` and `c (chore)`, batch 7, `abc1234` green since 10:02, two landings, pull request #23 linked, and `y`'s reading's link

#### Scenario: A second bolt is proven while the card waits
- **WHEN** `land/crew` waits on the user with one row, `y`, and bolt `z` of crew reads proven
- **THEN** the card becomes a list of `y` and `z`, posted following the one it replaces since a card's kind does not change in place, with a change note naming `z`

#### Scenario: A row's head moves while the card waits
- **WHEN** `land/crew` waits on the user as a list of `y` and `z`, and a fix's merge moves `z`'s head to `def5678`
- **THEN** the card is changed in place, its note saying `z`'s head is now `def5678`, and `z`'s row carries its reading and preview of `def5678`

#### Scenario: A yes frees the team for its next bolt
- **WHEN** swc-1's bolt `y` is a row of `land/crew`, and the last unit of swc-1's other bolt `z` merges with sluice green at its head, and `d` is the next planned bolt of swc-1's kit
- **THEN** `y`'s row says a yes frees swc-1 for `d`

#### Scenario: A fix in flight holds the card
- **WHEN** bolt `y` would read proven, but `fix/y/gap`, started on `y`, has neither merged nor been dropped
- **THEN** `y` has no box on `land/crew`, its row on the card's face says it is held for `fix/y/gap`, and it has a box again once the fix has merged and `y` reads proven

#### Scenario: A landing row before the bolt reads proven
- **WHEN** every unit of bolt `y` has merged and one unit's latest change has not been in a batch
- **THEN** the rail's landing row for crew names `y`, saying it lands once that unit has been in a batch, and `y` is no row of `land/crew`

#### Scenario: A landing row while a batch card waits on the user
- **WHEN** every unit of bolt `y` has merged, sluice is green at its head, and batch 7, whose card the user has not answered, holds a unit's latest change
- **THEN** the rail's landing row for crew names `y`, saying it lands once you have answered batch 7, and `y` is no row of `land/crew` until the user has answered batch 7's card

#### Scenario: A defect noted on the card
- **WHEN** the user sends `land/crew` with a note naming a defect in `y`, and `y`'s conductor runs `crew fix` on `y` in the note's words
- **THEN** `y` loses its box and its row says "held for a fix: <the note>", and it has a box again once `y` reads proven again

### Requirement: A landing's card lists the addresses of a preview of its head
When a bolt becomes a row of its kit's landings card in a kit whose sluice policy, as the bolt's head holds it, declares `[preview]`, crew SHALL first ask sluice, on the team's host, for a preview of the bolt's head on the bolt's branch, and SHALL put the row on the card once sluice has named the preview's addresses, without waiting for the preview's stack to come up. The row SHALL list each address under the name the kit's policy gives it, beside its reading's link, and the card SHALL say that a preview lands nothing and that the send is the word to land. A kit whose policy at the head declares no `[preview]` SHALL get no preview. Nothing about a preview SHALL hold, refuse or delay the card or the landing.

#### Scenario: A kit that declares a preview
- **WHEN** bolt `y` reads proven at head `abc1234` in a kit whose policy at `abc1234` declares `[preview]` with addresses `web` and `api`
- **THEN** sluice is asked for a preview of `bolt/y` at `abc1234` on the team's host, and `y`'s row on `land/crew` lists `web` and `api` with the addresses sluice named, saying the preview is coming up and lands nothing

#### Scenario: A kit that declares none
- **WHEN** bolt `y` reads proven in a kit whose policy at its head has no `[preview]` table
- **THEN** sluice is asked for nothing, and `y`'s row carries no preview and no word of one

#### Scenario: Approved without opening the preview
- **WHEN** the user sends `land/crew` with `y` ticked without opening any of its addresses
- **THEN** main-level ops lands `y` as for any ticked row, and nothing waits on the preview

#### Scenario: Asked again with nothing changed
- **WHEN** crew raises `land/crew` again with `y` at the same head, as the rail's sweep does for a card that was lost
- **THEN** sluice gives back the preview crew already asked for, its addresses unchanged, and no second preview is made

### Requirement: A preview that fails is said on the card and holds nothing
A preview sluice refuses, that crew cannot ask for or read, or whose addresses sluice does not name within twenty seconds, SHALL be said on its row with sluice's or crew's reason, and the row SHALL be on the card all the same. A preview whose stack fails to come up after its row listed its addresses SHALL change the card in place, while it waits on the user, to say so on that row with the end of what the preview's command printed, its addresses no longer listed; one whose addresses came too late SHALL change the card in place to list them once it is up. A card the user has answered SHALL be left as it is. None of this SHALL hold the landing.

#### Scenario: The host's sluice has no preview command
- **WHEN** the team's host runs a sluice that refuses `sluice preview` and bolt `y` reads proven
- **THEN** `y`'s row on `land/crew` says the preview could not be asked and why, and lists no addresses

#### Scenario: The stack fails to come up
- **WHEN** `y`'s row lists a preview's addresses and the preview's command then exits non-zero
- **THEN** the card is changed in place with a note that `y`'s preview did not come up, the row says so with the last lines of what the command printed and lists no addresses, and `y` keeps its box

#### Scenario: The host is busy when the card is raised
- **WHEN** sluice waits for room on the team's host and names no preview within twenty seconds of `y`'s row being raised, and the preview later comes up
- **THEN** the row says its preview is not there yet, and the card is then changed in place with a note that `y`'s preview is up, listing its addresses

### Requirement: The preview follows the bolt's head and ends with the card
When a merge moves a bolt's head while it is a row of its kit's landings card, crew SHALL release the preview it asked for at the old head and ask for one at the new head, and the row SHALL list the new preview's addresses. When the bolt leaves the card, landed, held for a fix, or dropped, crew SHALL release its preview on the team's host. A rail read SHALL release, on each host, a preview crew asked for whose bolt is no row of an open landings card. crew SHALL release only a preview it asked for, never one asked for by hand or by another tool.

#### Scenario: The head moves
- **WHEN** a fix's merge moves bolt `y`'s head from `abc1234` to `def5678` while `y` is a row of `land/crew`
- **THEN** `abc1234`'s preview is released, one is asked for at `def5678`, and `y`'s row lists `def5678`'s addresses

#### Scenario: The bolt lands
- **WHEN** `crew bolt land y` closes `y`
- **THEN** the preview of `y`'s head is released on the team's host, and `sluice previews` there no longer lists it

#### Scenario: A fix holds the landing
- **WHEN** a fix started on bolt `y` holds its row
- **THEN** the preview is released, and a new one is asked for when `y` reads proven again at its new head

#### Scenario: A preview crew did not ask for
- **WHEN** a person previewed an earlier revision of `bolt/y` themselves, and `y` later lands
- **THEN** crew releases the preview of the head it asked for, and leaves the person's preview as it is

#### Scenario: A card closed elsewhere
- **WHEN** `land/crew` is closed with no crew command closing it and `y` is no row of an open landings card, and the rail is read
- **THEN** the sweep on `y`'s team's host releases the preview crew asked for, and says so

## ADDED Requirements

### Requirement: A row that can land is a box, ticked as crew proposes
With two to five rows that can land, a landings card SHALL be one list of those rows in order, each ticked as crew proposes, labelled with its place and its bolt, its detail what the row carries, its consequence its forecast; with six or more, lists of five at most, in order, each a question. Clearing a box SHALL leave that bolt waiting. The face SHALL say one send lands the ticked bolts in the order shown and a note may move one.

#### Scenario: Three bolts
- **WHEN** `y`, `z` and `w` of crew read proven in that order
- **THEN** `land/crew` is one list of three ticked boxes, `1. y`, `2. z`, `3. w`, and its summary says the send lands the ticked ones in that order

#### Scenario: Seven bolts
- **WHEN** seven bolts of crew read proven
- **THEN** `land/crew` holds two lists, of four and three, in order, and a change to its rows while it waits withdraws it and posts its new form following it, since Pending You changes no card's questions

### Requirement: The landings card forecasts each row's conflicts
Each row SHALL carry the conflicts crew forecasts when its bolt is merged onto the kit's main and onto each bolt above it on the card, from their merge base, naming the files and the bolt or main each is with, or saying none is forecast. A forecast crew cannot make SHALL be said on its row with why, and SHALL hold nothing. Forecasts SHALL be made again whenever the card is raised or changed.

#### Scenario: Two bolts touch one file
- **WHEN** `y` and `z` of crew are rows in that order, and both change `plugin/lib/plan.py`'s same lines
- **THEN** `z`'s row says it is forecast to conflict with `y` on `plugin/lib/plan.py`, and `y`'s row says no conflict is forecast

#### Scenario: A bolt behind main
- **WHEN** main has landed a change to `README.md` that bolt `y` also changes
- **THEN** `y`'s row says it is forecast to conflict with main on `README.md`

#### Scenario: A bolt branch crew cannot read
- **WHEN** bolt `y` was made before gives went through sluice and its branch is on no host crew can read it from
- **THEN** `y`'s row says its forecast could not be made and why, and `y` keeps its box

### Requirement: A refused landing is held on its row
A bolt whose submission to main sluice refused, or that failed main's checks, SHALL be held on its row at that head, with no box, the row saying sluice's words and that it waits for its team's fix, while the bolts after it go on. It SHALL have a box again once its head moves and it reads proven.

#### Scenario: The second of three is refused
- **WHEN** the user sends `land/crew` with `y`, `z` and `w` ticked, and sluice refuses `z` for a conflict on `plugin/lib/plan.py`
- **THEN** `y` and `w` land, `z` stays on crew's landing row held, saying sluice's words and that it waits for its team's fix, and the next landings card raised carries `z` held with no box

#### Scenario: The fix merges
- **WHEN** `z`'s team's take-main fix merges into `z` and `z` reads proven at its new head
- **THEN** `z` has a box on `land/crew` again

### Requirement: The landings card closes when nothing waits
A landings card the user has answered SHALL be left as it is until every bolt they ticked has landed or been held, then closed naming what landed and where GitHub's main holds it, what was held and why, and what was left; a new card SHALL follow it while rows can land. A send ticking none SHALL close it, landing nothing. With no row that can land, no card SHALL be open, and the next proven bolt SHALL raise one, following nothing.

#### Scenario: Everything ticked lands
- **WHEN** the user sent `land/crew` with `y` and `z` ticked and both land
- **THEN** the card is closed saying `y` and `z` landed and where GitHub's main holds them, and no landings card of crew is open

#### Scenario: One left out
- **WHEN** the user sent `land/crew` with `y` ticked and `z` cleared, and `y` lands
- **THEN** the card is closed saying `y` landed and `z` was left, and a new card follows it with `z` as its one row

#### Scenario: The next proven bolt
- **WHEN** no landings card of crew is open and bolt `w` reads proven
- **THEN** `land/crew` is posted with `w` as its one row, following no card

### Requirement: A bolt's own landing card gives way to its kit's
An open landing card under `land/<bolt>`, in a conductor's name, SHALL be withdrawn by the rail's sweep on the team's host, saying the bolt is now a row of its kit's landings card, and that card SHALL be raised for the bolt. crew SHALL raise no card under `land/<bolt>`. A bolt SHALL NOT be added to the plan under a name that is a kit's of its partition.

#### Scenario: A card from before
- **WHEN** swc-1-conductor holds an open card under `land/y`, raised before this change, and the rail is read on swc-1's host
- **THEN** that card is withdrawn saying `y` is now a row of crew's landings card, and `land/crew` holds `y`

#### Scenario: A bolt named as a kit
- **WHEN** a proposal adds a bolt named `crew` to swancloud's plan, whose teams build the kit crew
- **THEN** its approval is refused, naming the kit, and nothing is written
