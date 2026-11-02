## ADDED Requirements

### Requirement: A red main's fix is a fix place on main where a crossed team builds the kit
`crew main fix <kit> <name> "<the failure's words>"`, main-level ops's or the user's on reading the kit's main red after a landing, SHALL append a launch of the fix kind on `main`, named `main--<name>`, its brief the failure's words, its submission held and its recipient `<label>/ops`, on the host of the crossed team that builds the kit, `--team` choosing among several and required when they run on different hosts. `--drop` SHALL drop it.

#### Scenario: Main red after a landing
- **WHEN** crew's main fails its checks after a landing, crw-4 is crossed and builds crew, and ops runs `crew main fix crew a-test-reads-its-fixture "<the check's words>"`
- **THEN** `requests.rec` gains a launch of `fix` named `main--a-test-reads-its-fixture` on `main`, its submission held, recipient `madswan/ops`, on deneb

### Requirement: A red main's fix stays a bolt of one chore where no crossed team builds the kit
Where no crossed team builds the kit, `crew main fix` SHALL be refused, naming a bolt of one chore, proposed first among the planned, as the way.

#### Scenario: No crossed team builds the kit
- **WHEN** no crossed team builds switchboard-kit and ops runs `crew main fix switchboard-kit gate-word "<words>"`
- **THEN** it is refused, naming a bolt of one chore proposed first among the planned

### Requirement: A fix of main lands on the user's send
Once a fix of main's code has delivered and its submission waits held, the kit's landings row SHALL carry it; `crew main fix <kit> <name> --send`, ops's on the user's send and read as a landing's words are, SHALL append the retry of its submission, and nothing else SHALL submit it.

#### Scenario: The user's send
- **WHEN** the runner's record shows `main--a-test-reads-its-fixture`'s code delivered and its submission held, and the user sends the kit's landings card with it ticked
- **THEN** ops's `crew main fix crew a-test-reads-its-fixture --send` appends a retry of its submission
