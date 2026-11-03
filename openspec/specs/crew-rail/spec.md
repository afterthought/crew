# crew-rail Specification

## Purpose
One list of everything that waits on the user, read from the state crew already keeps, so the user can work down it and an answered item leaves it on its own.

## Requirements

### Requirement: The rail lists what waits on the user in four groups
`crew rail [--label L]` SHALL print, from any host, what waits on the user in a partition, or in every partition when no label is given or known. It SHALL group the rows in this order: proposals, batches, land, operations. A verify report SHALL be no row: its findings are fixed in one round with no wait on the user (`teams.17`). Every group heading SHALL be printed, with `none` under a group that has no rows.

#### Scenario: Something waits in two groups
- **WHEN** a proposal is open and a deploy is offered, and nothing else waits
- **THEN** `crew rail --label swancloud` prints the four headings in order, one row under proposals, one under operations, and `none` under batches and land

#### Scenario: Run from another host
- **WHEN** `crew rail --label wldn` runs on a host that holds none of wldn's teams
- **THEN** it prints the same rows as it does on the teams' host

#### Scenario: A unit in verify with its report
- **WHEN** unit `x` is in verify and its report was written after the last commit on `unit/x`
- **THEN** `crew rail` has no row for `x`

### Requirement: Each row has its time, its age and the command that answers it
Each row SHALL name what waits, when it began to wait, how long ago that was, and the command that answers it, written to be pasted into a shell, with every path quoted. Within a group, rows SHALL be ordered oldest first. A row's time SHALL be read from the same state as the row itself, never from a record kept for the rail.

#### Scenario: Two units in review
- **WHEN** unit `a` has been in review since 09:00 and unit `b` since 11:00
- **THEN** `a`'s row comes before `b`'s, and each shows its time and its age

### Requirement: A unit in review is a row with the command that opens its whole change
Each unit whose stage is review SHALL be a row under review, naming its team and host. The row SHALL carry a command that opens the unit's whole change folder in plannotator, and the command that approves it (`crew unit approve <unit> --label <label>`). It SHALL have begun to wait at the time of the last commit on the unit's branch.

#### Scenario: Opened on the team's host
- **WHEN** `crew rail` runs on the host of the unit's team
- **THEN** the row carries `plannotator-tui herdr open <kit>/places/<unit>/openspec/changes/<unit>/`

#### Scenario: Opened from another host
- **WHEN** `crew rail` runs on a host other than the unit's team's host
- **THEN** the row carries `ssh -t <the team host's ssh name> plannotator-tui <the same folder>`

#### Scenario: Construct runs again
- **WHEN** the unit is sent back to construct
- **THEN** the next `crew rail` has no row for it until its change is in review again

### Requirement: Nothing is written to make or clear a row
`crew rail` SHALL read only the plan, the proposals, the kits and the run record, and SHALL write nothing to any of them. Every row SHALL leave the list when the state it was read from records its answer.

#### Scenario: A read leaves no trace
- **WHEN** `crew rail` runs
- **THEN** the flywheel's branch, the kits and the run record are unchanged

### Requirement: A host that does not answer is named
When a team's host does not answer, `crew rail` SHALL print the rows it could read and name that host, saying that its units and bolts may also wait on the user. It SHALL exit zero. When a partition's plan cannot be read, it SHALL name it and exit non-zero.

#### Scenario: The box is asleep
- **WHEN** chuck-herdr-alpha does not answer
- **THEN** `crew rail` still lists the open proposals and the rows of other hosts, and names chuck-herdr-alpha as not answering

### Requirement: A left bolt's land line says it would take main first once ticked
A bolt the user left on its kit's landings card, or stopped in their words to main-level ops, whose forecast against main the run record holds in conflict at its present head, SHALL be said on the kit's land row to be left by the user and to take main first once ticked, naming the files, and SHALL NOT be among the bolts the row's tell lands. A left bolt with no such conflict SHALL read as it does today.

#### Scenario: Left and forecast to conflict
- **WHEN** `z` is left on `land/crew`, reads proven, and the run record holds `z` forecast to conflict with main on `README.md` at its present head
- **THEN** crew's row under land says `z` was left by the user and takes main first once ticked, forecast to conflict with main on `README.md`, and its tell names no `z`

#### Scenario: Ticked
- **WHEN** the user ticks `z` and its take-main fix is told
- **THEN** `z`'s line says it takes main first, until its team's take-main fix moves its head

### Requirement: A bolt's land line shows its age and who held its time
Each bolt's line on its kit's landings row SHALL end with the bolt's age since its newest give, the minutes of it each holder held, and who holds it now and since when. It SHALL read them as the board's head line does, by the same rule and from the same read, so the rail and the board never differ for one bolt. A bolt still being built has no line on the rail and is read on the board. The rail SHALL raise no card and add no row because of a bolt's age.

#### Scenario: A bolt waiting on the user's yes
- **WHEN** crew's bolt `b`, given to crw-6 five hours ago, has every unit merged, and its kit's landings card has been open for two hours
- **THEN** `b`'s line on the `land/crew` row says `5h 00m` with its shares, the user's `2h 00m` among them, and that the user holds it since the card's post

#### Scenario: The rail and the board agree
- **WHEN** the follower writes the rail's frame and the board's from one read
- **THEN** `b`'s age, shares and holder are the same on the land line and on the board's head line

### Requirement: A fix of main waits to land on its kit's row
A fix of the kit's main whose code has delivered and whose submission waits held SHALL be a line of the kit's landings row, `fix main--<name>`, with the first line of its brief, ticked and sent as a bolt is, and naming `crew main fix <kit> <name> --send` as ops's command for it.

#### Scenario: A fix of main waits beside a bolt
- **WHEN** `main--a-test-reads-its-fixture`'s code has delivered and its submission waits held
- **THEN** crew's landings row has a line `fix main--a-test-reads-its-fixture` with the failure's first line, and names its `--send` command

### Requirement: A bolt whose every unit has merged and that has not landed is a row of its kit's
Each kit with a bolt in flight whose units have all merged and not all landed SHALL be one row under land, keyed `land/<kit>`, naming the partition's main-level ops and, in the plan's order, each such bolt with what it waits on. A bolt not yet proven SHALL say what it waits on: the verification as it reads, the units due a batch, the batches waiting on the user's answer, a fix in flight, a landing sluice rejected at its head for the bolt's own content, said as rejected with the bolt open for work, or that it takes main first, forecast at its present head to conflict with what main holds. A bolt whose landing the run record has queued, or landing again, SHALL say so with its number and that no work joins it until sluice decides, and SHALL be none of the bolts that can land (bolt-teams "A landing queued holds its bolt's work"). A bolt that can land whose last landing at its head sluice or its host stopped SHALL say, beside that it can land, what stopped it and that main-level ops submits it again once that is cleared. Once a bolt can land, the row SHALL carry `crew tell <label>-ops "Land <bolts that can land, in order>."`. The row SHALL have begun to wait at the time of the earliest last commit among its bolts' branches.

#### Scenario: The last unit merges
- **WHEN** the last unit of crew's bolt `b` merges into `bolt/b` through sluice, every unit's change has been in a batch the user has answered, and the landing's verdict is `passed`
- **THEN** crew's row under land names `b` and `swancloud-ops`, saying `b` waits to land, with the tell that lands it

#### Scenario: Two bolts of one kit
- **WHEN** crew's bolts `b` and `c` can both land, `b` first in the plan
- **THEN** there is one row, `land/crew`, naming `b` then `c`, its tell naming both in that order

#### Scenario: A verification that is not green
- **WHEN** every unit of bolt `b` has merged and been in a batch the user has answered, and `bolt/b`'s head is no landing of sluice's
- **THEN** `b`'s line says it lands once its verification is green and what the verification is now, and the row's tell leaves `b` out

#### Scenario: A batch that waits on the user
- **WHEN** every unit of bolt `b` has merged, its verification is green, and batches 8 and 9, whose cards the user has not answered, hold its units' latest changes
- **THEN** `b`'s line says it lands once you have answered batches 8 and 9, and the row carries no tell when no other bolt can land

#### Scenario: A refused landing
- **WHEN** sluice refused `b`'s landing at its head for a conflict
- **THEN** `b`'s line says its landing was rejected at that head and the bolt is open for work, and, in sluice's words, that it lands again once a fix moves its head

#### Scenario: A landing queued
- **WHEN** the run record has `b`'s landing queued on main as #412 with no outcome
- **THEN** `b`'s line says its landing is queued as #412 and that no unit, chore or fix joins it until sluice decides, and the row's tell leaves `b` out

#### Scenario: Landing again
- **WHEN** `b`, rejected as #412, is queued again as #415
- **THEN** `b`'s line says it is landing again as #415, after #412 was rejected, and the row's tell leaves `b` out

#### Scenario: A bolt taking main first
- **WHEN** `b` reads proven and the run record holds a `forecast` on `bolt/b` at `b`'s present head naming a conflict with main on `README.md` and no submission queued on main
- **THEN** `b`'s line says it takes main first, forecast to conflict with main on `README.md`, until a fix taking main in moves its head, and the row's tell leaves `b` out

#### Scenario: A conflict forecast at an older head
- **WHEN** the run record's `forecast` on `bolt/b` naming a conflict with main is at a head `b` has since moved from
- **THEN** that forecast holds nothing on `b`'s line

#### Scenario: A stopped landing
- **WHEN** `b`'s last landing at its head did not land because sluice itself failed
- **THEN** `b`'s line says it can land, that sluice itself failed at that head, in sluice's words, and that `swancloud-ops` submits it again once that is cleared, and the row's tell names `b`

#### Scenario: It lands
- **WHEN** the bolt is landed and closed in the plan
- **THEN** the next `crew rail` names it on no row

### Requirement: An open proposal is a row until the user approves or drops it
Each open proposal on the flywheel's branch SHALL be a row under proposals. The row SHALL name the command that prints it (`crew plan proposed <n> --label <label>`), the command that opens it in plannotator for the user to read and annotate (`crew plan proposed <n> --label <label> --open`), and the command that approves it (`crew plan approve <n> --label <label>`). It SHALL have begun to wait at its `plan.propose` entry in the run record, or at its `Opened` date when no entry is found.

#### Scenario: An open proposal
- **WHEN** proposal 3 is open and touches a bolt in flight
- **THEN** its row names no agreement it needs and carries `crew plan proposed 3 --label wldn`, `crew plan proposed 3 --label wldn --open` and `crew plan approve 3 --label wldn`

#### Scenario: Approved
- **WHEN** proposal 3 is approved
- **THEN** the next `crew rail` has no row for it

### Requirement: A started bolt waits to land on its kit's row
A started bolt SHALL wait to land on its kit's landings row on the same terms as any bolt, every unit and chore merged and sluice green at its head, its pieces' stages read from the runner's records; its line SHALL name the host its work runs on, as the runner that took it reported, and no team or slot.

#### Scenario: A started bolt proven
- **WHEN** started `x` has `a`, `b` and `c` merged by the runner's records, deneb's runner having taken them, and sluice green at its head
- **THEN** the rail shows crew's landings row with `x`, on deneb, can land
