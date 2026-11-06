## MODIFIED Requirements

### Requirement: A bolt's land line shows its age and who held its time
Each bolt's line on its kit's landings row SHALL end with the bolt's age since its newest give, the minutes of it each holder held, and who holds it now and since when. It SHALL read them as the board's head line does, by the same rule and from the same read, so the rail and the board never differ for one bolt. A bolt still being built has no line on the rail, but the one that says its conductor was not told of its give, and is read on the board. The rail SHALL raise no card and add no row because of a bolt's age.

#### Scenario: A bolt waiting on the user's yes
- **WHEN** crew's bolt `b`, given to crw-6 five hours ago, has every unit merged, and its kit's landings card has been open for two hours
- **THEN** `b`'s line on the `land/crew` row says `5h 00m` with its shares, the user's `2h 00m` among them, and that the user holds it since the card's post

#### Scenario: The rail and the board agree
- **WHEN** the follower writes the rail's frame and the board's from one read
- **THEN** `b`'s age, shares and holder are the same on the land line and on the board's head line

## ADDED Requirements

### Requirement: A bolt whose conductor was not told of its give is said after the groups
After its groups, `crew rail` SHALL list each bolt a team holds on today's path whose newest refused `bolt.notice` since its newest give has not been followed by a notice that told its conductor or a greeting of it. Each line SHALL give when, the bolt, its partition, the team and crew's words, which say how the conductor is told. It SHALL be no row of the four groups and raise no card.

#### Scenario: A conductor not up
- **WHEN** `crew bolt give swb-2 kept-work` finds swb-2-conductor not up
- **THEN** `crew rail` lists `kept-work (wldn), given to swb-2:` with the words that it is not up and that `crew up swb-2` starts and greets it, under "gives whose conductor was not told:"

#### Scenario: Told since
- **WHEN** `crew up swb-2` then starts swb-2-conductor and greets it
- **THEN** `crew rail` no longer lists `kept-work`

#### Scenario: Dropped
- **WHEN** the planner drops `kept-work` before swb-2-conductor is told
- **THEN** `crew rail` no longer lists `kept-work`
