## MODIFIED Requirements

### Requirement: Entries can be followed as they are written
`crew events --follow` SHALL print each entry of the partition as it reaches the partition's branch, one line per entry, until it is interrupted. It SHALL read the branch as this host's cache holds it, read it again only when the cache's tip moves, and read again only the run-record files whose content changed. The branch SHALL be fetched once a minute, never faster: by the host's follower for a partition it follows, else by the follow itself. It SHALL ask no host for entries.

#### Scenario: Following a bolt team
- **WHEN** `crew events --follow --label wldn` is running and a conductor starts a stage on the box
- **THEN** that entry's line appears once its commit is on `wldn/main` and this host has fetched it, within a minute, without the command being run again

#### Scenario: A host is asleep
- **WHEN** `crew events --follow --label wldn` starts while macbook-pro does not answer
- **THEN** it follows the branch as before, and starts nothing on macbook-pro

#### Scenario: Nothing moves
- **WHEN** `crew events --follow --label wldn` runs on a host where no follower follows wldn, and nothing reaches wldn's branch
- **THEN** it fetches the branch once a minute and starts no other process

#### Scenario: The host's follower fetches
- **WHEN** `crew events --follow --label wldn` runs on mac-studio while mac-studio's follower follows wldn
- **THEN** the follow fetches nothing itself, and prints each entry once the follower's fetch, or a write on mac-studio, has moved the cache
