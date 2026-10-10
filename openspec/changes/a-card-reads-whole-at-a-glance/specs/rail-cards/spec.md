# Spec Delta

## ADDED Requirements

### Requirement: A card's words are the document's own
A card a crew agent posts for a rail row SHALL say what the user decides from in the words of the document it asks the user to read, cut by whole sentences and never reworded: a review card the change's Why and the lead sentence of each What Changes item; a proposal card the proposal's case and each change in a line, as `crew plan proposed <n>` words them; a verify card each finding in a line, with what the conductor would do about it.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the review card for unit `x` of bolt `y`
- **THEN** the card's background holds `x`'s Why and one line per What Changes item, in the proposal's words

#### Scenario: A verify card
- **WHEN** a conductor posts the card for a verify report that raised two warnings
- **THEN** the card's background holds one line for each warning, saying what it found and what the conductor would do about it

#### Scenario: A change too long for the summary
- **WHEN** a unit's Why runs past what the summary holds after the link and the bolt
- **THEN** the summary ends at the last whole sentence that fits, and the background holds the whole Why

### Requirement: A card's link and bolt come first
A card's summary SHALL begin with the link to its row's plannotator session, then name the bolt, within Pending You's 400 characters, and its background SHALL begin with the same link. The link SHALL be the card's entry in its links and SHALL NOT be carried as an attached artifact. A landing card, which has nothing to read, SHALL name its bolt and carry no link.

#### Scenario: A review card's opening
- **WHEN** swb-1-conductor posts the review card for unit `x` of bolt `y`, whose session's link is `http://mac-studio.ts.swancloud.net:19432`
- **THEN** the card's summary begins with that link and names bolt `y`, its background begins with the link, its links hold it labelled "Read and annotate it in plannotator", and it has no artifact

### Requirement: No card carries a path
A card a crew agent posts SHALL carry no path of a file, a folder or a report: none in its title, summary, background, trace, files touched, links or artifacts.

#### Scenario: A review card's change folder
- **WHEN** a conductor posts the review card for a unit whose change is at `~/Code/kit/places/x/openspec/changes/x/`
- **THEN** that path is nowhere on the card, its files touched is empty, and the change is reached through the session's link
