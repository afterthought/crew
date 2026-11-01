## ADDED Requirements

### Requirement: Construction shows a crossed team's bolts from the runner's records
The Construction lane SHALL show each bolt a crossed team holds as a ledger of its units, chores and fixes with the stages the runner's records give, its head line naming the team's stream and host and no slots; a due team's head line SHALL say it is due to cross, or due back, and name what it finishes first. The board's JSON SHALL give each team its path and, for a crossed team, its stream.

#### Scenario: A crossed team's ledger
- **WHEN** crossed crw-4 holds `x`, `a` at `code 3/7` and `b` waiting on `a`
- **THEN** the board's Construction lane shows `x` on deneb in stream `madswan`, `a` at code 3/7 and `b` waiting on `a`, and no slot line

#### Scenario: A due team
- **WHEN** crw-5 is due to cross while it builds `y`
- **THEN** its head line says crw-5 is due to cross once `y` lands

### Requirement: The planner's and ops's bands show what a crossed team's places wait on them for
`board.agent_views` SHALL give the planner's band each crossed place that stopped short asking or waits on its caller, with its question or Flume's words, and main-level ops's band each fix of main and each take-main fix in flight with its stage; crew's mod SHALL draw both above the agent's prompt.

#### Scenario: A question in the planner's band
- **WHEN** `a`'s construct stopped short asking "Which partition's rail?"
- **THEN** madswan-planner's view lists `a` with that question, and the mod draws it

#### Scenario: A fix of main in ops's band
- **WHEN** `main--a-test-reads-its-fixture` is in code
- **THEN** madswan-ops's view lists it at code, and the mod draws it
