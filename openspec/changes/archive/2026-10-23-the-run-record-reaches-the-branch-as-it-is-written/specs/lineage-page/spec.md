## MODIFIED Requirements

### Requirement: The page says what it was made from
The page SHALL state the time it was made and the commit of the flywheel's branch it read, its run record read from that commit alone. It SHALL NOT change after it is written; running the command again writes it anew. When the flywheel's branch cannot be read, the command SHALL write no page and SHALL say which branch it could not read.

#### Scenario: A host was asleep
- **WHEN** the page is made while a Mac that wrote entries of the partition does not answer
- **THEN** the page holds every entry the branch holds, the Mac's among them, and names no host for its run record

#### Scenario: The branch cannot be read
- **WHEN** `crew page wldn` runs while the state repository cannot be fetched
- **THEN** no page is written, an earlier page is left as it was, and the command names `wldn/main` as what it could not read
