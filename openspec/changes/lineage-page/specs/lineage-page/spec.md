# Spec Delta

## Purpose

Draws a flywheel's signals, agenda items, proposals, units and bolts with the links between them, from the run record, on one page a person can open without asking an agent, as a view that can be replaced without changing what crew records.

## ADDED Requirements

### Requirement: One command writes one self-contained page
`crew page <label> [--out <file>] [--since <time>]` SHALL write a single HTML file holding its own data, style and script, which opens from disk with no network and no server. By default it SHALL be written under `~/.local/state/crew/<label>/` on the host where the command runs, and the command SHALL print its path. The page SHALL never be written to a repository.

#### Scenario: Made on a Mac
- **WHEN** `crew page wldn` runs on mac-studio
- **THEN** it prints the path of an HTML file there, which opens in a browser with the network off

#### Scenario: Nothing recorded yet
- **WHEN** the flywheel's run record is empty
- **THEN** the page is written and says nothing has been recorded

### Requirement: The page draws what led to what
The page SHALL show the flywheel's signals, agenda items, proposals, units and bolts as columns in that order, each object once, with a line for every link between two objects. Selecting an object SHALL mark everything it came from and everything that came from it. An object with no link SHALL still be shown.

#### Scenario: From a signal to a bolt
- **WHEN** a signal was routed to a plan item, a proposal added a unit from the item to a bolt, and the bolt landed
- **THEN** the page shows the signal, the item, the proposal, the unit and the bolt joined in a line, and selecting the signal marks all five

#### Scenario: An unmoved signal
- **WHEN** a signal has only its capture's entry
- **THEN** it is shown in the signals column with no line

### Requirement: The page's objects and links come from the run record alone
Which objects exist, how they are linked and in what order things happened SHALL be read only from the run record's entries, by the same walk `crew trace` makes. Labels that describe an object, such as a signal's assertion, an item's subject, a unit's intent or a bolt's goal, MAY be read from the flywheel's state. For every object, the history the page shows SHALL be the entries `crew trace` prints for it.

#### Scenario: The page and the trace agree
- **WHEN** an object's history on the page is compared with `crew trace` for that object
- **THEN** they hold the same entries in the same order

#### Scenario: Another view
- **WHEN** a different view is built later
- **THEN** it reads the same entries, and nothing crew records has to change for it

### Requirement: Each object opens to its history
Selecting an object SHALL list its entries in time order: the time, the act, who asked, the host, the commit, a refusal's reason, and the session to open for the detail, as text that can be copied. A timeline beneath the columns SHALL show when the flywheel's entries happened, and selecting an object SHALL mark its entries there.

#### Scenario: Who approved a unit
- **WHEN** the user selects a unit
- **THEN** its entries include the approval, with who ran it, on which host, and that agent's session to open

### Requirement: The page says what it was made from
The page SHALL state the time it was made, the commit of the flywheel's branch it read, and any host whose uncarried entries it could not read. It SHALL NOT change after it is written; running the command again writes it anew.

#### Scenario: A host was asleep
- **WHEN** the page is made while a Mac holding uncarried entries does not answer
- **THEN** the page is complete as far as that host had carried, and names the host
