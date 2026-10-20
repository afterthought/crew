## ADDED Requirements

### Requirement: A card follows only a card in its owner's name
A card crew posts SHALL follow only a card the run record shows posted in the same owner's name, since Pending You takes `follows` only to a card of the asker's own. When the card its thing would follow is another owner's, it SHALL follow nothing and be posted all the same. A deploy's card SHALL never follow a landing's card; the landings it carries are named on its face.

#### Scenario: A deploy of the head a landing left
- **WHEN** swc-2-conductor's landing card for `the-box-works-in-wldn-prod` is closed, its landing left swancloud's main at `ddcf2cb`, and the deployer offers deneb `ddcf2cb`
- **THEN** crew posts deneb's deploy card in swancloud-ops's name under `deploy/deneb`'s key, following no card, and its face names the landings it carries, the-box-works-in-wldn-prod's among them

#### Scenario: Five environments offered that head
- **WHEN** the deployer offers deneb, mac-studio, macbook-pro, chuck-herdr-alpha and swancloud-srv `ddcf2cb`, as it did from 23:54Z on 2026-10-19
- **THEN** none of the five posts follows swc-2-conductor's card, and none is refused as another agent's

#### Scenario: A newer head after the user declined
- **WHEN** the user declined srv's deploy card `req_d1` and the deployer offers srv a newer head
- **THEN** the new card follows `req_d1`

#### Scenario: A deploy after one that ran
- **WHEN** srv's last deploy card closed with its deploy's outcome and the deployer offers srv a newer head
- **THEN** the new card follows nothing

#### Scenario: A step after its deploy
- **WHEN** swancloud-ops's deploy card for srv was posted and the deploy's first step for the user waits
- **THEN** the step's card follows that deploy card, as before

#### Scenario: A landing raised again on a team that did not post the last one
- **WHEN** bolt b7's last landing card was withdrawn in swb-1-conductor's name and b7 is now held by swb-2, whose conductor raises it again
- **THEN** the new card follows nothing

### Requirement: A row's card that Pending You refused is owed until it posts
A post of a row's card that Pending You refuses SHALL be recorded as a `card.post` on the row's object, under the row's key, in its owner's name, marked refused in Pending You's words, and SHALL refuse nothing of the event it was raised for. The row SHALL stay on the rail, owing its card, with no card open and those words on its card line, until a later post of it is made: by the event raising it again, a deploy's by the next offer of its commit, or by the rail's sweep.

#### Scenario: Pending You refuses a deploy card
- **WHEN** Pending You refuses deneb's deploy card
- **THEN** the run record has a `card.post` on `env/deneb` under `deploy/deneb`, in swancloud-ops's name, marked refused with Pending You's words, `crew rail` shows deneb's row with no card open and those words, and the offer stands

#### Scenario: The next offer of that commit
- **WHEN** deneb's card for `ddcf2cb` was refused and the deployer offers deneb `ddcf2cb` again
- **THEN** crew posts the card, and the rail's card line for `deploy/deneb` names it open, swancloud-ops's

## MODIFIED Requirements

### Requirement: A card's words are the document's own
A crew card's words SHALL be prose the phone wraps, in short paragraphs, cut at whole sentences to Pending You's budget, with nothing the user has to read as raw Markdown; where a card speaks for a document, a proposal's case, a unit's opening paragraph, a record's opening sentences, it SHALL use the document's own words, never reworded. A list the user scans, the units that land, a deploy's steps, a proposal's change, SHALL be an artifact on the card's face, one thing a line and no line over forty characters, never a comma run in the summary or the background; the background SHALL hold only what is read when the face is not enough. A path SHALL appear only inside a step's command or a deploy's log name.

#### Scenario: Six units on a landing card
- **WHEN** crew raises the landing card of a bolt of six units
- **THEN** the six names are a text artifact on the face, one a line, and the background names none of them

#### Scenario: A card follows the card its thing follows
- **WHEN** crew raises the card of srv's first step for the user after swancloud-ops's deploy card for srv
- **THEN** the step's card follows that deploy card, and the phone shows it in that card's thread

#### Scenario: A review card
- **WHEN** unit `x`'s change is read in batch 3
- **THEN** the batch's card carries `x`'s reviewer paragraph in the reviewer's words, and no card carries `x`'s Why alone

#### Scenario: A verify card
- **WHEN** a unit's verify saves a report that raised two warnings
- **THEN** no card carries it: a verify report waits on no one, and its findings are fixed in one round

#### Scenario: A change too long for the summary
- **WHEN** a batch's paragraphs run past what the summary holds
- **THEN** the summary ends at the last whole sentence that fits, and the background holds every paragraph

#### Scenario: A proposal card
- **WHEN** crew raises the card for proposal 4
- **THEN** its title, summary, background, questions and artifacts are built from the plan and the proposal, the case and each change in the proposal's words

#### Scenario: A batch card's summary
- **WHEN** crew raises batch 7's card for four units
- **THEN** each unit's paragraph is the reviewer's opening paragraph as prose in its summary and details, with no code block in its words, the reviewer's summary rides its face as inline Markdown, and the card wraps on the phone

### Requirement: A deploy's card is a high approval
A deploy's card SHALL be an `approve` of risk high, not reversible, because irreversible, naming the environment and the commit; its summary SHALL count the landings since the environment's last deploy and name the environments before and after it, and its details SHALL hold the landings' subjects. It SHALL follow its environment's last deploy card when the user declined that card, and otherwise no card.

#### Scenario: Three landings since srv's last deploy
- **WHEN** the deployer offers srv `c882cff` with git-cliff's notes for `6aed25c..c882cff` and two steps, and srv runs `6aed25c`
- **THEN** the card's approve block has risk high and reversible false, its summary counts three landings and says the box follows on its own and mac-studio is offered after srv, its face holds the notes as handed and the two steps with their doers, and its details name landings #16, #17 and #18

#### Scenario: A head a landing card put on main
- **WHEN** crew raises srv's deploy card for a head that landing #24's card put on main
- **THEN** the card follows no card, and its details name landing #24
