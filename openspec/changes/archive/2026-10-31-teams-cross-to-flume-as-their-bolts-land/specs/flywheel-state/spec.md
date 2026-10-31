## ADDED Requirements

### Requirement: crew asks a host's runner for work by requests on the flywheel's branch
crew SHALL write every request for a host's runner as a record of `requests.rec` on the flywheel's branch: a launch of a place, or a retry, drop or priority of one it launched. Each SHALL be numbered once, appended by a crew command in the commit of the plan write that occasions it, checked by `recfix --check` and crew's own rules, and never changed or removed.

#### Scenario: Never renumbered
- **WHEN** `requests.rec` holds requests 1 to 7 and a drop is written
- **THEN** it is request 8, and requests 1 to 7 are as they were

### Requirement: A launch names everything the runner passes to Flume
A launch SHALL name its host, the work it serves, the kit's forge address, its kind, name and base, its stream, priority, intent and recipient, and its brief; it MAY name launches that must land first and a held submission. A retry, drop or priority SHALL name the launch it acts on. crew's rules SHALL refuse a request that lacks what its act needs.

#### Scenario: A launch with no stream
- **WHEN** a give would append a launch with no `Stream`
- **THEN** the write is refused by crew's rules and the branch is unchanged

#### Scenario: A retry of nothing
- **WHEN** a retry would name request 9, which is no launch
- **THEN** the write is refused naming request 9

### Requirement: crew reads each host's runner from that runner's own branch
crew SHALL read a host's runner from `<label>/runner/<host>` of the partition's state repository, fetched with `<label>/main` in one fetch, and SHALL never write it: its `runner.rec` saying a runner serves the partition there, its `answers.rec` where each request stands, and its `places.rec` Flume's status of each place as Flume gave it.

#### Scenario: One fetch
- **WHEN** a command reads the plan and the runners
- **THEN** it fetches the state repository once, `<label>/main` and `<label>/runner/*` together

### Requirement: A runner's branch that can't be read hides only its host's work
A host whose runner branch is missing, or whose files recfix refuses, SHALL hide only that host's work, which reads unknown and is named; every other host's SHALL read as it stands.

#### Scenario: Two hosts, one silent
- **WHEN** `madswan/runner/deneb` holds an answer and a place for request 3, and `madswan/runner/alpha` does not exist
- **THEN** request 3's work reads its stage from deneb's place, and alpha's work reads unknown, naming that no runner branch exists for alpha
