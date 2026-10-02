# Spec Delta

## Purpose

Above a partition's bolt teams: a design agent that elaborates on main, a planner across the bolts, a dispatcher on each host that runs them, and ops that lands them. Signals are what reaches them from outside.

## ADDED Requirements

### Requirement: Partitions are declared in the teams file
`teams.json` SHALL list each partition with a main level. Each entry gives the partition's label (`wldn`, `madswan`, `swancloud`), its swancloud name, its blueprints repos, and the machine and session its main level runs in. The first blueprints repo listed SHALL be the one the partition's signals and elaboration go to by default.

#### Scenario: clients/willdan
- **WHEN** `teams.json` lists `wldn` as `clients/willdan` with willdan-blueprints, running on the box in `wldn-3`
- **THEN** `crew main up wldn` starts its main level in `wldn-3` on the box

### Requirement: The main level is one herdr workspace
`crew main up <label>` SHALL open a herdr workspace named `<label>` in the main level's session. It SHALL hold a `design` tab with the design agent, a `planner` tab with the planner, and an `ops` tab with the main-level ops, and start each. It SHALL then start a dispatcher on every host where the partition's teams run.

#### Scenario: The main level comes up
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-design`, `wldn-planner` and `wldn-ops` start in the `wldn` workspace, and `wldn-dispatch-chuck-herdr-alpha` starts on the box

### Requirement: The design agent elaborates on main
The design agent SHALL keep the partition's design true on main: the books, specs and constitution in its blueprints repos and kits, the decision records, and the curation of signals with the moves `attach`, `challenge`, `new-territory`, `answered` and `drop`, each written only through `crew signal move`. It SHALL answer a conductor's design question. Work its elaboration calls for SHALL be queued as units, never put into a bolt by the design agent.

#### Scenario: Elaboration produces work
- **WHEN** the design agent records a decision that needs building
- **THEN** it queues a unit whose source is the decision's page, and tells the planner

### Requirement: The planner plans across bolts
The planner SHALL be the only agent that creates bolts, puts units into bolts, and splits, orders or moves them between bolts. It SHALL route signals to work, and agree a change to an active bolt with that bolt's conductor before writing it. It SHALL NOT start units or drive a team.

#### Scenario: A finding mid-bolt
- **WHEN** swb-1's conductor reports that a unit needs work outside the bolt's goal
- **THEN** the planner queues that work or adds it to another bolt, and swb-1's bolt keeps its goal

### Requirement: A dispatcher allocates each host's work
A dispatcher SHALL run on each host where the partition's teams run, in a herdr workspace `<label> dispatch`. It runs in the main level's session if that is on the host, otherwise in the session of the host's first team by name. It SHALL give that host's teams their bolts, start and stop them, and watch their health and their accounts' use. It SHALL NOT change a bolt's content or drive a unit.

#### Scenario: Two hosts
- **WHEN** the partition's teams run on the box and on mac-studio
- **THEN** each host has its own dispatcher, and asking either one about allocation answers for its host only

### Requirement: Main-level ops lands bolts and deploys main
The main-level ops SHALL merge a proven bolt into main on the user's word, deploy main, and run `crew bolt land`. A failure after landing SHALL be a fix on main.

#### Scenario: Landing
- **WHEN** the user tells the planner that swb-1's bolt may land
- **THEN** the main-level ops merges it, deploys main, and the plan no longer holds the bolt

### Requirement: Signals reach the plan only through a route
Signals SHALL stay in the partition's first blueprints repo, in the signals model its `signals/README.md` gives. A bolt's agents SHALL record a finding outside their bolt as a signal there with `crew signal`. A signal SHALL become work only through a `route` move written by `crew unit add --signal`.

#### Scenario: A finding from a bolt
- **WHEN** ops on swb-1 finds a defect in a shared service the bolt does not own
- **THEN** it records a signal in willdan-blueprints, and the planner decides whether to route it

### Requirement: Every move is written through crew and never merged
Every move SHALL be appended to `signals/moves.rec` through crew: `route` by `crew unit add --signal`, and `attach`, `challenge`, `new-territory`, `answered` and `drop` by `crew signal move <id> <move>`. Each SHALL be fetched over https, applied to the tip of the repo's main, checked with `recfix --check`, committed by its own path alone, and pushed without force, applied again to the new tip when the push is refused. A signal SHALL have one move; a second is refused. `signals/moves.rec merge=union` SHALL stay in `.gitattributes`, only as a fallback for a hand edit.

#### Scenario: Moves from two hosts
- **WHEN** a route is written on the box while curation writes a drop on mac-studio, both through crew
- **THEN** both moves are in `moves.rec`, one after the other, nothing is merged, and the file passes `recfix --check`

#### Scenario: A signal moved twice
- **WHEN** `crew signal move` names a signal that already has its move
- **THEN** it is refused, naming the move it has

### Requirement: Any agent crew starts is reached by name
`crew tell <agent> "<text>"` SHALL prompt any agent crew starts, by its name alone, in the host and session where it runs. An agent that is not up SHALL be reported and the command SHALL fail, with nothing sent.

#### Scenario: A conductor asks the design agent
- **WHEN** swb-1's conductor on the box runs `crew tell wldn-design "<question>"`
- **THEN** the design agent in `wldn-3` receives the question
