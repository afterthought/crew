## RENAMED Requirements

- FROM: `### Requirement: A batch's card the main level's host can't reach is raised again there`
- TO: `### Requirement: A row's card its owner's host can't reach is raised again there`

## MODIFIED Requirements

### Requirement: A row's card its owner's host can't reach is raised again there
A card belongs to the Pending You sign-in of the host it was posted from, and each row's card is raised and waited on only where its owner runs: a proposal's, a batch's, a deploy's and a step's on the partition's main level's host, a landing's on the host of the team holding the bolt. When the owner's newest card under a row's key was posted from another host and no close ends it, or its last close is as lost to the owner on any host, and no newer card of the owner's is under the key, the rail's next read on the owner's host SHALL post the row's card again there under the row's key, through its kind's raise, its summary opening with the words that say an older copy was lost and to dismiss it in the app, while the row still waits on its card; and the rail SHALL take the new card as the row's. crew SHALL neither ask after nor close the older copy from a host whose sign-in does not reach it. A row that no longer waits SHALL have no card posted again, and the read SHALL say its raise posted none.

#### Scenario: The main level moved to another host
- **WHEN** batch 13's card was posted from mac-studio, the partition's main level now runs on deneb, the user has not answered the batch where crew can read it, and the rail is read on deneb
- **THEN** crew posts batch 13's card again on deneb under `batch/13` in the planner's name, its summary opening "An older copy of this card was lost: dismiss it in the app.", the rail shows the new card's id as the row's, and the read lists the older card as lost and the new one as posted

#### Scenario: A proposal's card left on the host the main level left
- **WHEN** proposal 13's card was posted from mac-studio in the planner's name, proposal 13 is still open, the main level now runs on deneb, and the rail is read on deneb
- **THEN** crew posts proposal 13's card again on deneb under `proposal/13`, in its form, its summary opening with the words that say an older copy was lost, and the rail shows the new card's id as the row's

#### Scenario: A deploy's and a step's card left behind
- **WHEN** `deploy/dev`'s card, or `op/dev/2`'s, was posted from mac-studio in main-level ops's name, the offer or the step still waits on the user among the operations recorded on deneb, and the rail is read on deneb
- **THEN** crew posts that card again on deneb in main-level ops's name, saying an older copy was lost

#### Scenario: A landing's card left on the host its team left
- **WHEN** bolt `y`'s landing card was posted from mac-studio in its conductor's name, the team holding `y` now runs on deneb, the bolt still reads proven, and the rail is read on deneb
- **THEN** crew posts the landing card again on deneb under `land/y`, an approval of risk high, saying an older copy was lost

#### Scenario: Lost to the planner on the host it was posted from
- **WHEN** batch 13's card was recorded lost to the planner on mac-studio, no card was posted under `batch/13` since, and the rail is read on deneb, the main level's host
- **THEN** crew posts batch 13's card on deneb, its summary saying an older copy was lost

#### Scenario: Read on another host
- **WHEN** the rail is read on a host where the row's owner does not run while its card is held on mac-studio
- **THEN** that read posts no card for the row

#### Scenario: The batch no longer waits
- **WHEN** batch 13's card is held on mac-studio and every unit batch 13 holds has landed
- **THEN** no card of batch 13 is posted on deneb

#### Scenario: The proposal no longer waits
- **WHEN** proposal 13's card is held on mac-studio and proposal 13 was approved since
- **THEN** no card of proposal 13 is posted on deneb

## ADDED Requirements

### Requirement: A record's card its owner's host can't reach is raised again there
A decision record's card has no rail row and is raised in the design agent's name on the main level's host. When the design agent's newest card under a record's key was posted from another host and no close ends it, or was lost to it on any host, no newer card of the design agent's is under the key, and the record's last status crew recorded is proposed and not settled in the pane, the rail's next read on the main level's host SHALL post the record's card again there under `record/<kit>/<number>`, built from the record as the kit's main holds it, its summary opening with the words that say an older copy was lost.

#### Scenario: A record's card left on the host the main level left
- **WHEN** record 21 in atlas-kit was raised from mac-studio with no alternatives, is still proposed, the main level now runs on deneb, and the rail is read on deneb
- **THEN** crew posts record 21's card again on deneb under `record/atlas-kit/0021` in wldn-design's name, built from the record on atlas-kit's main, its summary opening with the words that say an older copy was lost, and the rail lists the new card under the decision records

#### Scenario: A record settled since
- **WHEN** record 21's card is held on mac-studio and `crew record atlas-kit 21 --accepted` was recorded since
- **THEN** no card of record 21 is posted on deneb

### Requirement: A record raised with alternatives is raised again by its command
`crew record --proposed` SHALL record on its `record.proposed` entry whether the card it raised offered alternatives, keeping none of the file's words. A stranded record card raised with alternatives SHALL NOT be posted again by the rail's read, since crew keeps no copy of the alternatives file: the read SHALL say so, naming `crew record <kit> <number> --proposed --alternatives <file>` for the design agent; and `crew record --proposed`, run while its record's card is stranded so, SHALL post the card saying an older copy was lost.

#### Scenario: A record raised with alternatives
- **WHEN** record 32's card was raised from mac-studio with `--alternatives`, the main level now runs on deneb, and the rail is read on deneb
- **THEN** no card is posted, and the read names `crew record switchboard-kit 32 --proposed --alternatives <file>` for wldn-design

#### Scenario: The command raises it
- **WHEN** wldn-design then runs `crew record switchboard-kit 32 --proposed --alternatives alternatives.md` on deneb
- **THEN** the card is posted on deneb as a choice, its summary opening with the words that say an older copy was lost
