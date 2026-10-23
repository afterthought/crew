## ADDED Requirements

### Requirement: A proposal rests only on accepted records
Before a proposal is written, crew SHALL read every decision record named as a source by each bolt the proposal creates and each unit or chore it makes new to a bolt or the queue (one it adds, or moves into a bolt). Each record SHALL be read on its kit's main as GitHub holds it now. When any is not accepted there, the proposal SHALL be refused, naming each such unit or bolt, the record's number and kit, and what main holds, and nothing SHALL be written and no card raised.

#### Scenario: A unit names a proposed record
- **WHEN** the planner proposes `bolt new a-team-of-one-slot-lands-its-bolt … --repo crew` and `unit add a-bolts-unblocker-is-built-whatever-slots-its-team-has … --bolt a-team-of-one-slot-lands-its-bolt --source docs/adr/0033-a-unit-waiting-to-merge-yields-its-slot-to-the-work-it-waits-on.md`, and crew's main holds record 0033 with `status: proposed`
- **THEN** the proposal is refused, naming that unit, record 0033 of crew and that main holds it proposed; no proposal is written and no card is raised

#### Scenario: A record the user rejected
- **WHEN** a new unit's source names a record its kit's main holds with `status: rejected`
- **THEN** the proposal is refused, naming the record and that main holds it rejected

#### Scenario: An accepted record with an amendment still proposed
- **WHEN** a new unit's source names a record whose file on main says `status: accepted` and holds an amendment marked "Status: proposed"
- **THEN** the proposal is refused, naming the record and that main holds it accepted with an amendment still marked proposed

#### Scenario: A record main does not hold yet
- **WHEN** a new unit's source names `docs/adr/0040`, and its kit's main has no file numbered 0040 in `docs/adr/`
- **THEN** the proposal is refused, naming record 0040 and that main holds no such record

#### Scenario: A new bolt's source
- **WHEN** a proposal's `bolt new` names a proposed record with `--source`
- **THEN** the proposal is refused, naming the bolt and the record

#### Scenario: A queued unit moved into a bolt
- **WHEN** a proposal moves a queued unit into a bolt, and the unit's sources in the plan name a proposed record
- **THEN** the proposal is refused, naming the unit and the record

#### Scenario: Every record accepted
- **WHEN** every record the proposal's new bolts and units name is accepted on its kit's main, with no amendment marked proposed
- **THEN** the proposal is written and its card raised, as without records

#### Scenario: A record of another repository
- **WHEN** a new unit of crew names `agentplot/sluice:docs/adr/0022` as a source
- **THEN** record 0022 is read on agentplot/sluice's main, not crew's, and judged the same way

#### Scenario: A kit's main that cannot be read
- **WHEN** a new unit names a record, and its kit's main cannot be fetched from GitHub
- **THEN** the proposal is refused, naming the repository and why it could not be read, and nothing is written

#### Scenario: Work the proposal does not make new
- **WHEN** a proposal only reorders, amends or drops units already in a bolt, whose sources name a proposed record
- **THEN** no record is read for them, and the proposal is written

### Requirement: A record is named in a source by its path
crew SHALL take a source to name a decision record wherever it holds `docs/adr/<four digits>`, with or without the rest of the record's file name. A record named so SHALL be the kit's of the bolt or unit that names it, unless `<owner>/<name>:` or `<owner>/<name>` and a space comes right before it, when it SHALL be that repository's. One source MAY name several records. A record named only in words, such as "record 0026", SHALL NOT be read.

#### Scenario: A source holding several records and other pages
- **WHEN** a source reads `docs/adr/0029 (accepted 2026-10-14); docs/architecture/core.md read.5`
- **THEN** crew reads record 0029 of the unit's kit, and nothing else of that source

#### Scenario: A record named in words
- **WHEN** a source reads `record 0026 point 4`
- **THEN** crew reads no record for it
