## ADDED Requirements

### Requirement: A bolt's land line shows its age and who held its time
Each bolt's line on its kit's landings row SHALL end with the bolt's age since its newest give, the minutes of it each holder held, and who holds it now and since when. It SHALL read them as the board's head line does, by the same rule and from the same read, so the rail and the board never differ for one bolt. A bolt still being built has no line on the rail and is read on the board. The rail SHALL raise no card and add no row because of a bolt's age.

#### Scenario: A bolt waiting on the user's yes
- **WHEN** crew's bolt `b`, given to crw-6 five hours ago, has every unit merged, and its kit's landings card has been open for two hours
- **THEN** `b`'s line on the `land/crew` row says `5h 00m` with its shares, the user's `2h 00m` among them, and that the user holds it since the card's post

#### Scenario: The rail and the board agree
- **WHEN** the follower writes the rail's frame and the board's from one read
- **THEN** `b`'s age, shares and holder are the same on the land line and on the board's head line
