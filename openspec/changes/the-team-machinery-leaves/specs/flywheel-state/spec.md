## ADDED Requirements

### Requirement: A kit's work is taken by a runner whose configuration names its repository
crew SHALL record a kit's work against its repository and look up no kit's host: a runner whose configuration names the repository takes it, under a lease and while its host's stream has room, and launches it there, in the stream its host's Flume configuration maps the repository to. crew SHALL read a launched piece's stage from the runner whose answers hold its launch, launching while none does; where two runners hold it, or none crew read holds it and a runner could not be read, the piece SHALL read unknown, naming them. Where crew must act on or say where a bolt's work runs, its landing, its reads of the bolt and its kit, its reading and preview, the sweep after a landing or a drop, its site row and its ledger's host and stream, it SHALL read what the runner reported for the work it took: the host whose runner took the newest of the bolt's launches taken, and the kit's folder there and the stream its work runs in as Flume's status of that runner's place names them; while no runner has taken any of the bolt's own work, where the runner that took its kit's newest work taken reported the kit. A bolt or kit no runner has reported, or whose newest launch two runners took, SHALL be named as unread, nothing of it landed, and every other bolt read as it stands.

#### Scenario: The runner that took the work
- **WHEN** deneb's runner answers launch 1 of crew's unit `a` on `bolt/x` and carries Flume's status of its place, naming its repository `/w/crew` and its stream `madswan`
- **THEN** `a`'s stage is read from deneb's records, and `x` is read and landed on deneb in `/w/crew`, its ledger saying deneb and `madswan`

#### Scenario: A bolt none of whose own work is taken
- **WHEN** `x` is started and no runner has taken its launches, and deneb's runner took crew's work on another bolt, its place naming `/w/crew`
- **THEN** `x` is read and landed on deneb in `/w/crew`

#### Scenario: Taken by two runners
- **WHEN** deneb's and chuck-herdr-alpha's runners both answer launch 1
- **THEN** its piece reads unknown naming both, and crew can't tell where `x` runs, landing nothing of it

#### Scenario: No runner has reported the kit
- **WHEN** no runner has taken any launch of crew's work
- **THEN** a landing of `x` is refused naming that no runner has reported taking its work, and a piece of it reads launching

### Requirement: What comes before a runner takes a kit's work is done on the main-level host
What crew does on a kit before any runner has taken the work in hand, a start's `sluice branch create` and its read of the kit's policy and its host's sluice, a new unit's or chore's name checked against the kit's main, a bolt never started landed by its close alone, the design agent's records and a proposal's records read in the kit, the board's explorations on the kit's main, and the main level's folders of the partition's kits, SHALL be done in the checkout the partition's main-level host keeps of the kit, as that host's spaces in the hosts file keep it, by its forge address or, for a kit the plan names by its name alone, by that name; it SHALL be refused, naming the host and the kit, where that host keeps none, or keeps two repositories by the kit's name, and nothing SHALL be asked of a runner for it.

#### Scenario: A kit's first bolt is started
- **WHEN** `crew bolt start x` runs for crew's first bolt, no runner has taken any of crew's work, and deneb, madswan's main-level host, keeps `afterthought/crew` at `/d/madswan/crew/main`
- **THEN** sluice makes `bolt/x` from main in `/d/madswan/crew/main` on deneb, the policy there is read, and the start goes on as any start

#### Scenario: A kit the main-level host keeps no checkout of
- **WHEN** `crew bolt start x` runs and deneb's spaces keep no checkout of crew
- **THEN** it is refused naming deneb and crew, the plan is unchanged and no branch is made

#### Scenario: A unit's name and a record
- **WHEN** the planner adds unit `a` to crew and the design agent runs `crew record crew 53 --proposed`
- **THEN** `a`'s name is checked against crew's main, and record 0053 read, in `/d/madswan/crew/main` on deneb

#### Scenario: The main level's kit folders
- **WHEN** madswan's plan names crew and sluice, deneb keeps both and a role of madswan's main level starts there
- **THEN** it may reach deneb's checkouts of crew and sluice, and a kit its plan names that deneb keeps none of is left out

## RENAMED Requirements

- FROM: `### Requirement: A runner's branch that can't be read hides only its host's work`
- TO: `### Requirement: A runner's branch that can't be read hides only the work no runner crew read has taken`

## MODIFIED Requirements

### Requirement: A launch names everything the runner passes to Flume
A launch of a kit's work SHALL name the work it serves, its repository as the plan names it, its kind, name and base, its priority, intent and recipient, and its brief, and SHALL name no host or stream, a runner whose configuration names its repository taking it, in the stream its host's Flume configuration maps the repository to; a launch of a role's work SHALL also name the host and stream its role runs in. A launch MAY name launches that must land first and a held submission. A retry, drop or priority SHALL name the launch it acts on and no host. crew's rules SHALL refuse a request that lacks what its act needs or names what its act does not take.

#### Scenario: A launch with no stream
- **WHEN** a bolt's start appends a launch of a kit's work naming no `Stream`
- **THEN** it is appended, a runner whose configuration names the kit's repository giving its stream

#### Scenario: A kit's launch naming a host
- **WHEN** a bolt's start would append a launch naming a `Host` or a `Stream`
- **THEN** the write is refused by crew's rules and the branch is unchanged

#### Scenario: A retry of nothing
- **WHEN** a retry would name request 9, which is no launch
- **THEN** the write is refused naming request 9

### Requirement: A runner's branch that can't be read hides only the work no runner crew read has taken
A host whose runner branch recfix refuses, or crew can't read, SHALL hide only the work no runner crew read has taken, which reads unknown, naming that runner; work a runner crew read has taken SHALL read as it stands. A host with no runner branch is no runner, and hides nothing.

#### Scenario: Two hosts, one silent
- **WHEN** `madswan/runner/deneb` holds an answer and a place for request 3, and `madswan/runner/alpha` can't be read
- **THEN** request 3's work reads its stage from deneb's place, and work deneb has not taken reads unknown, naming alpha's runner
