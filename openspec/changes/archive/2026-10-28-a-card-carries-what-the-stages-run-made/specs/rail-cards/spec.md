# Spec Delta

## ADDED Requirements

### Requirement: A landing row carries what brings its bolt's preview up
Where the kit's policy at a bolt's head declares `[preview]`, the bolt's row on its kit's landings card SHALL carry what brings the preview up, the bolt's branch and its head, and SHALL say that the preview comes up only when the user asks for it on the card and goes when they are done. Where the policy declares none, the row SHALL say "no preview". crew SHALL ask sluice for nothing when it posts or changes the row.

#### Scenario: A kit that declares a preview
- **WHEN** bolt `y` reads proven at head `abc1234` in a kit whose policy at `abc1234` declares `[preview]`
- **THEN** `y`'s row on `land/crew` names `bolt/y` at `abc1234` as what brings its preview up, says to write on the card to bring it up, and sluice on the team's host lists no preview of `abc1234`

#### Scenario: A kit that declares none
- **WHEN** bolt `y` reads proven in a kit whose policy at its head has no `[preview]` table
- **THEN** `y`'s row says "no preview", and sluice is asked for nothing

#### Scenario: The policy can't be read
- **WHEN** the kit's policy at `y`'s head can't be read on the team's host
- **THEN** `y`'s row says its preview can't be told and why, and `y` keeps its box

#### Scenario: Approved without a preview
- **WHEN** the user sends `land/crew` with `y` ticked and never asked for its preview
- **THEN** main-level ops lands `y` as for any ticked row, and no preview of `y` was made

### Requirement: The user asks for a preview by writing on the card
A card that carries a thing that must run SHALL say, in its words, that the user brings it up by writing on the card naming it, and puts it away by writing that they are done. The card's owner, woken by the user's words, SHALL run `crew card preview <key> <thing>` to bring it up and `crew card preview <key> <thing> --done` to release it, `<thing>` a landings row's bolt or a batch line's `<unit>/<name>`. No card SHALL ask the user to run a command.

#### Scenario: The user asks on the landings card
- **WHEN** the user writes "bring up y's preview" on `land/crew` while it waits on them
- **THEN** swancloud-ops is woken, runs `crew card preview land/crew y`, and the card stays open waiting on the user's send

#### Scenario: A thing the card does not carry
- **WHEN** `crew card preview land/crew w` is run and `w` is no row of `land/crew`
- **THEN** crew refuses, naming the rows that carry a preview, and asks sluice for nothing

#### Scenario: Asked by anyone but the owner
- **WHEN** a conductor runs `crew card preview land/crew y`
- **THEN** crew refuses, naming swancloud-ops as the card's owner

### Requirement: A preview asked for from a card is brought up through sluice and listed while it is up
`crew card preview` SHALL bring the thing up with `sluice preview <branch> <revision>` on the host where its kit's work is, as the row or line names them, and SHALL change the card in place listing each address sluice names, under the name sluice gives it, while the preview is up. Asked again while one is up or coming up at the same revision, crew SHALL give it back and make no second.

#### Scenario: Brought up
- **WHEN** swancloud-ops runs `crew card preview land/crew y` with `y`'s row at `abc1234`, and the kit's policy names addresses `web` and `api`
- **THEN** sluice is asked for a preview of `bolt/y` at `abc1234` on `y`'s team's host, and `land/crew` is changed in place, its note saying `y`'s preview is up, `y`'s row listing `web` and `api` with sluice's addresses and saying a preview lands nothing

#### Scenario: Asked twice
- **WHEN** `crew card preview land/crew y` is run again while `y`'s preview of `abc1234` is up
- **THEN** sluice gives back the same preview, and `y`'s row lists the same addresses

### Requirement: A preview is released on the user's done and when its card or row ends
crew SHALL release a preview it brought up from a card when the owner runs `--done` on the user's word, when the card closes, when the bolt lands, is held for a fix or is dropped, and when the row or line that carries it leaves the card; and the card, while it waits, SHALL say it was released. A rail read SHALL release, on each host, a preview crew brought up whose card is closed or whose row is gone. crew SHALL release only a preview it asked for.

#### Scenario: The user is done
- **WHEN** the user writes "done with y's preview" on `land/crew` and swancloud-ops runs `crew card preview land/crew y --done`
- **THEN** `y`'s preview is released on the team's host, and `y`'s row again names `bolt/y` at its head and says to write on the card to bring it up

#### Scenario: The bolt lands with its preview up
- **WHEN** `crew bolt land y` closes `y` while its preview is up
- **THEN** the preview is released on the team's host, and `sluice previews` there no longer lists it

#### Scenario: A fix holds the landing
- **WHEN** a fix started on bolt `y` holds its row while its preview is up
- **THEN** the preview is released, and none is asked when `y` reads proven again

#### Scenario: A preview crew did not ask for
- **WHEN** a person previewed an earlier revision of `bolt/y` themselves, and `y` later lands
- **THEN** crew releases only the preview it brought up, and leaves the person's preview as it is

#### Scenario: A card closed elsewhere
- **WHEN** `land/crew` is closed with no crew command closing it while `y`'s preview is up, and the rail is read
- **THEN** the sweep on `y`'s team's host releases the preview, and says so

### Requirement: A moved head releases the preview of the old one and asks for none
When a merge moves a bolt's head while it is a row of its kit's landings card, crew SHALL change the row in place to name the new head as what brings the preview up, SHALL release a preview it brought up at the old head, and SHALL say so on the row; it SHALL ask for no preview at the new head until the user asks again.

#### Scenario: The head moves with a preview up
- **WHEN** a fix's merge moves bolt `y`'s head from `abc1234` to `def5678` while `y`'s preview of `abc1234` is up
- **THEN** `abc1234`'s preview is released, `y`'s row names `bolt/y` at `def5678` and says its preview of `abc1234` was released as the head moved, and sluice lists no preview of `def5678`

### Requirement: A batch's card carries what each unit's stages recorded as made
A batch's card SHALL carry, under each unit, every line its stages recorded as made, named by the stage that recorded it, each with its name, what it is and its address or its branch and revision, exactly as the run wrote them. crew SHALL make, check and rewrite none of it. A unit whose stages recorded nothing SHALL carry no such line and no word of one.

#### Scenario: A spike recorded by a code stage
- **WHEN** unit `a`'s code stage recorded `{"name": "spike", "kind": "page", "address": "https://example.test/spike"}` and `a` is in batch 7
- **THEN** batch 7's card names, under `a`, the code stage's `spike`, a page, at `https://example.test/spike`, as written

#### Scenario: A thing that must run
- **WHEN** unit `a`'s code stage recorded `{"name": "demo", "kind": "preview", "branch": "bolt/y", "revision": "abc1234"}`
- **THEN** batch 7's card names under `a` the `demo` preview, brought up from `bolt/y` at `abc1234`, says to write on the card to bring it up, and lists no address

#### Scenario: A line crew cannot read as a made thing
- **WHEN** a line of `a`'s is not a JSON object naming a name and what it is
- **THEN** the card carries the line's text as written, saying crew could not read it as a made thing, and the card is raised all the same

#### Scenario: Nothing recorded
- **WHEN** no stage of unit `b` recorded anything as made
- **THEN** batch 7's card says nothing of made things under `b`

### Requirement: A batch's card changes in place as lines are added
When a stage of a unit in a batch whose card waits on the user records a line its card does not yet carry, crew SHALL change that card in place, its note naming the unit and the line's name. A card the user has answered SHALL be left as it is.

#### Scenario: A line added while the card waits
- **WHEN** batch 7's card waits on the user and unit `a`'s code stage, still running, records a page `notes`
- **THEN** batch 7's card is changed in place with a note that `a` recorded `notes`, and carries it under `a`

#### Scenario: A line added after the user answered
- **WHEN** the user has answered batch 7's card and `a`'s stage records another line
- **THEN** batch 7's card is left as it is

### Requirement: A card about a landed revision carries its commit and no preview
A card about a revision that has landed, a deploy's card and the close of a landings card's row that landed, SHALL carry the commit it landed as, and SHALL carry no preview and no word of bringing one up.

#### Scenario: A deploy's card
- **WHEN** main's head `9f8e7d6` is offered to `prod`
- **THEN** `deploy/prod`'s card names `9f8e7d6`, and carries no preview, no branch to bring one up and no word of one

#### Scenario: A landed row
- **WHEN** `y` lands on GitHub's main as `1a2b3c4` and its card closes
- **THEN** the close names `1a2b3c4` as the commit it landed as, and says nothing of a preview

## MODIFIED Requirements

### Requirement: A preview that fails is said on the card and holds nothing
A preview sluice refuses, that crew cannot ask for or read, or whose addresses sluice does not name within twenty seconds of the ask, SHALL be said on its row or line with sluice's or crew's reason, the card changed in place while it waits on the user. A preview whose stack fails to come up after its addresses were listed SHALL change the card in place to say so with the end of what the preview's command printed, its addresses no longer listed; one whose addresses came too late SHALL change the card in place to list them once it is up. A card the user has answered SHALL be left as it is. None of this SHALL hold the landing.

#### Scenario: The host's sluice has no preview command
- **WHEN** swancloud-ops runs `crew card preview land/crew y` and the team's host runs a sluice that refuses `sluice preview`
- **THEN** `land/crew` is changed in place, `y`'s row saying its preview could not be brought up and why, listing no addresses, and `y` keeps its box

#### Scenario: A line naming a branch sluice does not land
- **WHEN** the planner runs `crew card preview batch/7 a/demo` for a line naming `unit/a` at `abc1234`, and sluice refuses since no `[branches]` table names `unit/a`
- **THEN** batch 7's card is changed in place, saying under `a` that `demo` could not be brought up, in sluice's words

#### Scenario: The stack fails to come up
- **WHEN** `y`'s row lists a preview's addresses and the preview's command then exits non-zero
- **THEN** the card is changed in place with a note that `y`'s preview did not come up, the row says so with the last lines of what the command printed and lists no addresses, and `y` keeps its box

#### Scenario: The host is busy when the card is raised
- **WHEN** sluice waits for room on the team's host and names no preview within twenty seconds of the ask, and the preview later comes up
- **THEN** the row says its preview is not there yet, and the card is then changed in place with a note that `y`'s preview is up, listing its addresses

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
- **THEN** the card is changed in place, its note saying `z`'s head is now `def5678`, and `z`'s row carries its reading of `def5678` and, where the kit's policy names a preview, `bolt/z` at `def5678` as what brings it up

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

## REMOVED Requirements

### Requirement: A landing's card lists the addresses of a preview of its head
**Reason**: Record 0043 (accepted 2026-10-28) and flume record 0007: a preview held from the row's post may sit for days as a loose server; the row now carries what brings it up, and it comes up only on the user's ask.
**Migration**: "A landing row carries what brings its bolt's preview up" and "A preview asked for from a card is brought up through sluice and listed while it is up".

### Requirement: The preview follows the bolt's head and ends with the card
**Reason**: Record 0043: a moved head no longer asks for a new preview, and a preview is released on the user's done as well as when its card or row ends.
**Migration**: "A preview is released on the user's done and when its card or row ends" and "A moved head releases the preview of the old one and asks for none".
