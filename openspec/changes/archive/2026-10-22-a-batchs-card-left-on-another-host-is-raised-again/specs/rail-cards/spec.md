## ADDED Requirements

### Requirement: A batch's card the main level's host can't reach is raised again there
A batch's card belongs to the Pending You sign-in of the host it was posted from, and only the main level's host raises and waits on it. When the planner's newest card under a batch's key was posted from another host and no close ends it, or its last close is as lost to the planner on any host, and no newer card of the planner's is under the key, the rail's next read on the main level's host SHALL post the batch's card again there under `batch/<n>`, through the batch's raise, its summary opening with the words that say an older copy was lost and to dismiss it in the app, while the batch still waits on the user; and the rail SHALL take the new card as the row's. crew SHALL neither ask after nor close the older copy from a host whose sign-in does not reach it. A batch that no longer waits SHALL have no card posted again.

#### Scenario: The main level moved to another host
- **WHEN** batch 13's card was posted from mac-studio, the partition's main level now runs on deneb, the user has not answered the batch where crew can read it, and the rail is read on deneb
- **THEN** crew posts batch 13's card again on deneb under `batch/13` in the planner's name, its summary opening "An older copy of this card was lost: dismiss it in the app.", the rail shows the new card's id as the row's, and the read lists the older card as lost and the new one as posted

#### Scenario: Lost to the planner on the host it was posted from
- **WHEN** batch 13's card was recorded lost to the planner on mac-studio, no card was posted under `batch/13` since, and the rail is read on deneb, the main level's host
- **THEN** crew posts batch 13's card on deneb, its summary saying an older copy was lost

#### Scenario: Read on another host
- **WHEN** the rail is read on a host that is not the main level's while batch 13's card is held on mac-studio
- **THEN** that read posts no card for batch 13

#### Scenario: The batch no longer waits
- **WHEN** batch 13's card is held on mac-studio and every unit batch 13 holds has landed
- **THEN** no card of batch 13 is posted on deneb
