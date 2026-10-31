## ADDED Requirements

### Requirement: A kit's work runs on the host whose runner keeps it with a stream
crew SHALL read from each host's `runner.rec` the repositories its runner keeps for the partition, each with its folders on the host and, where its work runs there, its Flume stream, and SHALL take a kit's host, its folders there and its work's stream from those records alone: the one host whose runner keeps the kit with a stream, or, where several do, the partition's main-level host when it is one of them. A kit kept with a stream on several hosts, none of them the main level's, or on none, SHALL be named as unread with the hosts found, nothing of it launched or landed, and every other kit read as it stands. A host whose runner keeps the kit as a view alone SHALL be no host for its work, and a `runner.rec` that names no repositories SHALL be read as keeping none, and named.

#### Scenario: One host keeps the kit with a stream
- **WHEN** deneb's runner alone keeps crew with the stream `madswan`
- **THEN** crew's work is launched on deneb in `madswan`, and crew is read and landed on deneb at the folders its runner names

#### Scenario: Two hosts, the main level's among them
- **WHEN** deneb's and mac-studio's runners both keep crew with a stream, and madswan's main level runs on mac-studio
- **THEN** crew's host is mac-studio

#### Scenario: Two hosts, neither the main level's
- **WHEN** deneb's and chuck-herdr-alpha's runners both keep crew with a stream, and madswan's main level runs on mac-studio
- **THEN** crew is named unread with deneb and chuck-herdr-alpha, nothing of crew's is launched or landed, and every other kit reads as it stands

#### Scenario: A view alone
- **WHEN** mac-studio's runner keeps crew as a view alone and no other runner keeps it
- **THEN** crew is named unread, no host keeping it with a stream

## MODIFIED Requirements

### Requirement: A launch names everything the runner passes to Flume
A launch SHALL name its host, the work it serves, the kit's forge address, its kind, name and base, its stream, priority, intent and recipient, and its brief; it MAY name launches that must land first and a held submission. A retry, drop or priority SHALL name the launch it acts on. crew's rules SHALL refuse a request that lacks what its act needs.

#### Scenario: A launch with no stream
- **WHEN** a bolt's start would append a launch with no `Stream`
- **THEN** the write is refused by crew's rules and the branch is unchanged

#### Scenario: A retry of nothing
- **WHEN** a retry would name request 9, which is no launch
- **THEN** the write is refused naming request 9
