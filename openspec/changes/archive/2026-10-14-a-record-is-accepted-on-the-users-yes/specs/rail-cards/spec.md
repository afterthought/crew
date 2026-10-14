## ADDED Requirements

### Requirement: The design agent posts a record's card under its record key
Besides the row keys, crew SHALL let the partition's design agent post a card under `record/<kit>/<number>/<commit>`, where `<kit>` is the name of a kit one of its partition's teams builds, `<number>` the record's four digits and `<commit>` the seven hex digits of the commit that proposed the record or the amendment. No other crew agent SHALL post under a record key. A record key with a kit that is not its partition's, or in any other shape, SHALL be refused naming the record key's form.

#### Scenario: The design agent posts a record's card
- **WHEN** wldn-design posts a card keyed `record/atlas-kit/0021/abc1234`, and atlas-kit is built by one of wldn's teams
- **THEN** the call goes through, and the run record has a `card.post` entry on `record/atlas-kit/0021` with that key

#### Scenario: A kit outside the partition
- **WHEN** wldn-design posts a card keyed `record/flywheel-next/0003/abc1234`, and no team of wldn builds flywheel-next
- **THEN** the call is refused before it reaches Pending You, naming `record/<kit>/<number>/<commit>` and wldn's kits

#### Scenario: Another agent posts under a record key
- **WHEN** wldn-planner or a conductor posts a card keyed `record/atlas-kit/0021/abc1234`
- **THEN** the call is refused as before, naming the keys that are its own

#### Scenario: The design agent posts under any other key
- **WHEN** wldn-design posts a card keyed `proposal/1`
- **THEN** the call is refused, naming `record/<kit>/<number>/<commit>` as the one key the design agent posts under

### Requirement: A record key is checked against the teams file alone
crew's check of a card under a record key SHALL read nothing beyond the teams file.

#### Scenario: Checked with the plan unread
- **WHEN** wldn-design posts a card keyed `record/atlas-kit/0021/abc1234` while wldn's plan can't be read
- **THEN** the call goes through on the teams file alone

### Requirement: A record card's acts are recorded on the record
A record card's acts SHALL be recorded in the run record on `record/<kit>/<number>` with the card's key in `Key`, and closing one SHALL end no plannotator session.

#### Scenario: A record's card closed
- **WHEN** wldn-design closes its card keyed `record/atlas-kit/0021/abc1234` once the user said yes
- **THEN** the run record has a `card.close` entry on `record/atlas-kit/0021` with that key, and no plannotator session is ended

### Requirement: A record's card is an approval
A card under a record key SHALL be an approval, kind `approve`, whose approve block is of low risk and reversible, with no options and no steps. crew SHALL refuse a record card in another form, or a change that takes it out of that form, before Pending You sees it, naming the form.

#### Scenario: A record card as a choice
- **WHEN** wldn-design posts a card keyed `record/atlas-kit/0021/abc1234` of kind `choice`
- **THEN** the call is refused, naming the record card's form

#### Scenario: A record card marked high risk
- **WHEN** wldn-design posts a record card whose approve block has risk `high`
- **THEN** the call is refused, naming the record card's form

### Requirement: The rail lists open record cards apart
After its groups, `crew rail` SHALL list each open card under a record key under a heading of its own, with its key, who asked it and when, and SHALL NOT list it among the open cards whose row is gone.

#### Scenario: A record waiting on the user
- **WHEN** wldn-design's card `record/atlas-kit/0021/abc1234` is open
- **THEN** `crew rail` lists it under the record heading, asked by wldn-design, and not among the cards whose row is gone

#### Scenario: A record answered
- **WHEN** that card has been closed
- **THEN** `crew rail` no longer lists it
