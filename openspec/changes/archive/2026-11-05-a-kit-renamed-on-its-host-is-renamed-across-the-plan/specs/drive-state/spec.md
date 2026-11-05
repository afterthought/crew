## MODIFIED Requirements

### Requirement: crew reads each host's runner from that runner's own branch
crew SHALL read a host's runner from `<label>/runner/<host>` of the partition's state repository, fetched with `<label>/main` in one fetch, and SHALL never write it. The branch holds four files:
- `runner.rec` says a runner serves the partition there;
- `answers.rec` says where each request stands;
- `places.rec` holds Flume's status of each place, as Flume gave it;
- `repositories.rec` holds each repository the runner keeps on its host, by its forge address with the folder of its clone.

A `repositories.rec` that recfix refuses, or that holds a record with no address or one address twice, SHALL make that host's runner unreadable, as the other files do. A branch with no `repositories.rec` SHALL be read as a runner that reports no repositories.

#### Scenario: One fetch
- **WHEN** a command reads the plan and the runners
- **THEN** it fetches the state repository once, `<label>/main` and `<label>/runner/*` together

#### Scenario: The repositories a runner keeps
- **WHEN** `madswan/runner/deneb` holds a `repositories.rec` naming `agentplot/boomdrive-cloud` at `/r/boomdrive-cloud`
- **THEN** crew reads that deneb's runner keeps `agentplot/boomdrive-cloud` in `/r/boomdrive-cloud`

#### Scenario: A runner that reports no repositories
- **WHEN** `madswan/runner/deneb` holds no `repositories.rec`
- **THEN** deneb's runner is read as before, reporting no repositories

#### Scenario: A repositories file crew can't read
- **WHEN** deneb's `repositories.rec` names `agentplot/boomdrive-cloud` twice
- **THEN** deneb's runner can't be read, naming the file, and only the work no runner crew read has taken reads unknown

### Requirement: A kit's work is taken by a runner whose configuration names its repository
crew SHALL record a kit's work against its repository and look up no kit's host. A runner whose configuration names the repository takes the work, under a lease and while its host's stream has room, and launches it there, in the stream its host's Flume configuration maps the repository to.

crew SHALL read a launched piece's stage from the runner whose answers hold its launch, and read it as launching while none does. Where two runners hold it, or none crew read holds it and a runner could not be read, the piece SHALL read unknown, naming them.

Where crew must act on or say where a bolt's work runs, it SHALL read what the runner reported for the work it took. This covers the bolt's landing, its reads of the bolt and its kit, its reading and preview, the sweep after a landing or a drop, its site row, and its ledger's host and stream.
- The host is the one whose runner took the newest of the bolt's launches taken. While no runner has taken any of the bolt's own work, it is the host whose runner took its kit's newest work taken.
- The kit's folder there is the one that runner's `repositories.rec` names for the repository of the kit's name now. Where that runner reports no repositories, it is the folder Flume's status of its newest place names.
- The stream is the one Flume's status of that runner's place names.

The kit SHALL be named as unread, nothing of it landed and every other bolt read as it stands, in each of these cases:
- a runner that reports its repositories names none for the kit's name now. The refusal names the host, the repositories it keeps and `crew kit rename`;
- no runner has reported the bolt or the kit;
- the runner that took it reports two repositories by the kit's name, and the plan names the kit by its name alone;
- two runners took the bolt's newest launch.

#### Scenario: The runner that took the work
- **WHEN** deneb's runner answers launch 1 of crew's unit `a` on `bolt/x` and carries Flume's status of its place, naming its repository `/w/crew` and its stream `madswan`, and reports no repositories
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

#### Scenario: A kit renamed under its place
- **WHEN** deneb's runner carries request 1's place, Flume's status naming its repository `/r/flywheel-cloud`, its `repositories.rec` names `agentplot/boomdrive-cloud` at `/r/boomdrive-cloud`, and the bolt's kit reads `boomdrive-cloud`
- **THEN** the bolt is read and landed on deneb in `/r/boomdrive-cloud`

#### Scenario: A runner that does not keep the kit
- **WHEN** deneb's `repositories.rec` names only `agentplot/boomdrive-cloud`, and the bolt's kit reads `flywheel-cloud`, with no rename
- **THEN** its landing is refused naming deneb, `flywheel-cloud`, the repositories deneb's runner keeps and `crew kit rename`, and nothing is landed

### Requirement: What comes before a runner takes a kit's work is done on the main-level host
Some of what crew does on a kit comes before any runner has taken the work in hand:
- a start's `sluice branch create`, and its read of the kit's policy and its host's sluice;
- a new unit's or chore's name, checked against the kit's main;
- a bolt never started, landed by its close alone;
- the design agent's records, and a proposal's records, read in the kit;
- the board's explorations on the kit's main;
- the main level's folders of the partition's kits.

That work SHALL be done in the checkout the partition's main-level host keeps of the kit, as that host's spaces in the hosts file keep it, found by the kit's forge address or, for a kit the plan names by its name alone, by that name. Nothing SHALL be asked of a runner for it. It SHALL be refused, naming the host and the kit, where that host keeps none or keeps two repositories by the kit's name. A refusal for a kit the host keeps none of SHALL also name `crew kit rename <kit> <new>` as the way on for a kit renamed on its host.

#### Scenario: A kit's first bolt is started
- **WHEN** `crew bolt start x` runs for crew's first bolt, no runner has taken any of crew's work, and deneb, madswan's main-level host, keeps `afterthought/crew` at `/d/madswan/crew/main`
- **THEN** sluice makes `bolt/x` from main in `/d/madswan/crew/main` on deneb, the policy there is read, and the start goes on as any start

#### Scenario: A kit the main-level host keeps no checkout of
- **WHEN** `crew bolt start x` runs and deneb's spaces keep no checkout of crew
- **THEN** it is refused naming deneb and crew, the plan is unchanged and no branch is made

#### Scenario: A kit renamed on its host before the plan
- **WHEN** deneb's spaces keep `agentplot/timber` and nothing by `tailrace`, and `crew bolt start x` runs for a bolt whose `Repo` is `tailrace`, with no rename
- **THEN** it is refused naming deneb, `tailrace` and `crew kit rename tailrace <new>`, and nothing is made

#### Scenario: A unit's name and a record
- **WHEN** the planner adds unit `a` to crew and the design agent runs `crew record crew 53 --proposed`
- **THEN** `a`'s name is checked against crew's main, and record 0053 read, in `/d/madswan/crew/main` on deneb

#### Scenario: The main level's kit folders
- **WHEN** madswan's plan names crew and sluice, deneb keeps both and a role of madswan's main level starts there
- **THEN** it may reach deneb's checkouts of crew and sluice, and a kit its plan names that deneb keeps none of is left out
