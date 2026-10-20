## ADDED Requirements

### Requirement: A landing's card lists the addresses of a preview of its head
When crew raises a bolt's landing card in a kit whose sluice policy, as the bolt's head holds it, declares `[preview]`, it SHALL first ask sluice, on the team's host, for a preview of the bolt's head on the bolt's branch, and SHALL raise the card once sluice has named the preview's addresses, without waiting for the preview's stack to come up. The card SHALL list each address under the name the kit's policy gives it, beside the reading's link, and SHALL say that the preview is coming up, that it lands nothing, and that approving the card is the word to land. A kit whose policy at the head declares no `[preview]` SHALL get no preview, and its card SHALL be as it would be without this requirement. The approval SHALL stay the word to land: nothing about the preview SHALL hold, refuse or delay the card or the landing.

#### Scenario: A kit that declares a preview
- **WHEN** bolt `y` reads proven at head `abc1234` in a kit whose policy at `abc1234` declares `[preview]` with addresses `web` and `api`
- **THEN** sluice is asked for a preview of `bolt/y` at `abc1234` on the team's host, and `land/y`'s card lists `web` and `api` with the addresses sluice named, says the preview is coming up and lands nothing, and is an approval of risk high as before

#### Scenario: A kit that declares none
- **WHEN** bolt `y` reads proven in a kit whose policy at its head has no `[preview]` table
- **THEN** sluice is asked for nothing, and `land/y`'s card carries no preview and no word of one

#### Scenario: Approved without opening the preview
- **WHEN** the user approves `land/y`'s card without opening any of its addresses
- **THEN** the conductor tells main-level ops to land `y` as before, and nothing waits on the preview

#### Scenario: Asked again with nothing changed
- **WHEN** crew raises `land/y`'s card again at the same head, as the rail's sweep does for a card that was lost
- **THEN** sluice gives back the preview crew already asked for, its addresses unchanged, and no second preview is made

### Requirement: A preview that fails is said on the card and holds nothing
A preview sluice refuses, that crew cannot ask for or read, or whose addresses sluice does not name within twenty seconds, SHALL be said on the landing card with sluice's or crew's reason, and the card SHALL be raised all the same. A preview whose stack fails to come up after the card listed its addresses SHALL change the card in place, while it waits on the user, to say so with the end of what the preview's command printed, its addresses no longer listed; one whose addresses came too late for the card's raise SHALL change the card in place to list them once it is up. A card the user has answered SHALL be left as it is. None of this SHALL hold the landing.

#### Scenario: The host's sluice has no preview command
- **WHEN** the team's host runs a sluice that refuses `sluice preview` and bolt `y` reads proven
- **THEN** `land/y`'s card is raised, saying the preview could not be asked and why, and listing no addresses

#### Scenario: The stack fails to come up
- **WHEN** `land/y`'s card lists a preview's addresses and the preview's command then exits non-zero
- **THEN** the card is changed in place with a note that its preview did not come up, says so with the last lines of what the command printed, lists no addresses, and stays an approval the user may give

#### Scenario: The host is busy when the card is raised
- **WHEN** sluice waits for room on the team's host and names no preview within twenty seconds of `land/y`'s raise, and the preview later comes up
- **THEN** the card is raised saying its preview is not there yet, and is then changed in place with a note that its preview is up, listing its addresses

### Requirement: The preview follows the bolt's head and ends with the card
When a merge moves a bolt's head while its landing card is open, crew SHALL release the preview it asked for at the old head and ask for one at the new head, and the card, changed in place for the head, SHALL list the new preview's addresses. When crew closes the landing card, landed, held for a fix or declined, it SHALL release the bolt's preview on the team's host. A rail read SHALL release, on each host, a preview crew asked for whose landing card is closed or whose row is gone. crew SHALL release only a preview it asked for, never one asked for by hand or by another tool.

#### Scenario: The head moves
- **WHEN** a fix's merge moves bolt `y`'s head from `abc1234` to `def5678` while `land/y`'s card waits on the user
- **THEN** `abc1234`'s preview is released, one is asked for at `def5678`, and the card, changed in place, lists `def5678`'s addresses

#### Scenario: The bolt lands
- **WHEN** `crew bolt land y` closes `land/y`'s card
- **THEN** the preview of `y`'s head is released on the team's host, and `sluice previews` there no longer lists it

#### Scenario: A fix holds the landing
- **WHEN** a fix started on bolt `y` withdraws `land/y`'s card
- **THEN** the preview is released, and a new one is asked for when the card is raised again at the bolt's new head

#### Scenario: A preview crew did not ask for
- **WHEN** a person previewed an earlier revision of `bolt/y` themselves, and `land/y`'s card later closes
- **THEN** crew releases the preview of the head it asked for, and leaves the person's preview as it is

#### Scenario: A card closed elsewhere
- **WHEN** `land/y`'s card is closed with no crew command closing it and its row is gone, and the rail is read
- **THEN** the sweep on the team's host releases the preview crew asked for, and says so
