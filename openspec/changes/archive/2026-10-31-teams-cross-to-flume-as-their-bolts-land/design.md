# Design

## Context

See proposal.md for why. This change is record 0047's move 5 (as amended 2026-10-28 and 2026-10-30) reached a team at a time, as record 0050 parts 2 and 3 have it (`roles.8`), through the runner record 0052 part 3 describes and the user settled on 2026-10-31: a program of its own, `flywheel` from agentplot/flywheel-runner (its record 0001, its rules `core.1`, `core.2`, `core.3`, `core.5`), which keeps the clones and views of the repositories its own configuration names and turns the work crew decides into `flume launch --stream --priority --intent`, carrying Flume's ends and status back to crew as records in crew's state repository. crew reads Flume only through it.

What stands today:

- `crew.load` reads `~/.config/crew/teams.json` version 2 only (`VERSION`), every field required and checked before any is used (`code.5`); a team names `system`, `machine`, `session`, `units` and `repos`, and keeps an unknown field silently.
- `plan.bolt_give` makes `bolt/<bolt>` on GitHub by sluice's `branch create` on the team's host (`BOLT_CREATE`, `plan.19`), refuses while a bolt the team holds is not proven or it holds two (`give_refusal`, `teams.16`), writes `Team` on the bolt, records `bolt.give`, and restarts and greets the conductor and ops (`greet_team`).
- A unit's, chore's or fix's stage is read from its kit on the team's host (`survey`, `gather.py`, `Stages`): its place under `<kit>/places/`, its branch, the bolt holding its change archived (`teams.17`) or a chore's trailer (`plan.11`).
- The rail's landings rows (`rail_rows`, group `land`) and the card sweep raise a kit's landings card from those stages and the bolt's verdict (`kit.verification`); a fix in flight holds the landing (`fixes_in_flight`), a refusal holds it for the team's fix (`held_at`, `landing_held`), and a forecast from the conductor's waits says take main first (`main_conflict`, `teams.21`).
- Flume 0.3.6 on the host runs its own `change@2` (construct, code per task group, verify that archives the change, `on_fail = "code"`), `chore@1` and `fix@1` (code, `on_fail = "code"`), each landing on its base through sluice (`lands = true`, crew's `.config/flume.toml` binding `merge_queue = "sluice"`); a failed or conflicting submission sends the place back to code with sluice's words (flume record 0011, its `core.27`); a launch may hold its submission (`--hold-submission`), and a retry names a stage with words or the submission (`flume retry --stage --words`, `--submission`); a place's priority is the caller's, the highest started first (flume record 0010), its stream the host's (flume record 0020); `flume status --json` gives each place's `stages`, `current`, `tasks`, `submission` (`read`, `submits`, `send_backs`, `verdict`, `waiting`, `held`), `waiting_on`, `stalled`, `holds`, `failures`, `ends`, `phase`, `priority`, `stream` and `intent`.
- agentplot/flywheel-runner holds a scaffold and its first record, no code: its crew implementation, the one part of it that names crew (its `core.2`), is the runner's half of what this change specifies crew's half of.

Area pages this change touches: `core.md` (`state.*`, `roles.*`, `code.5`), `teams.md` (`plugin/lib/crew.py`, `plugin/bin/crew`), `plan.md` (`plugin/lib/plan.py`, and the new `plugin/lib/runner.py`, which writes to the flywheel's branch), `record.md` (`plugin/lib/record.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `tests.md` (`tests/`), `docs.md` (README, the specs).

## Goals / Non-Goals

**Goals:**
- A team moves to Flume on the user's word, one at a time, only once it holds nothing of today's path, so no code converts work in flight (`roles.8`, record 0050 part 3).
- A crossed team's units, chores and fixes run as Flume places through the runner, each kind's stages run by Flume with no conductor's word (record 0047 move 5).
- A failed or conflicting submission of a crossed team's place, and a crossed team's bolt that conflicts with main at its landing, are fixed with sluice's words and no conductor (flume record 0011; `plan.8`).
- A red main of a kit a crossed team builds is fixed by a fix place on main, held for the user's send (record 0047 move 5 as amended 2026-10-30; flume record 0023; `state.3`).
- A crossed team's work is seen on the rail, the board, `crew bolts` and the bands from the runner's records alone.

**Non-Goals:**
- Removing today's path, the conductor, team ops, the dispatcher, slots, the give or the setting once every team has crossed: `the-team-machinery-leaves`.
- The roles as Flume kinds, and waking a role an end is told to: `roles-run-as-flume-kinds`.
- The runner itself, its clones and views, its pull, and its crew implementation: agentplot/flywheel-runner.
- A registry of repositories in crew: there is none; the runner's configuration names what it keeps (the user, 2026-10-31; flywheel-runner `core.5`).
- Converting a team's work in flight from one path to the other.
- A forecast of a crossed team's bolt against main before its landing (Decision 10 says what holds instead).

## Decisions

### 1. The setting is `flume` in `teams.json` version 3: `false`, or the stream its work runs in

Version 3 is version 2 with one field more on every team, `flume`: `false` while the team runs today's path, or the name of the Flume stream its work runs in on its host, a name `code.4` allows, which the host's Flume configuration declares (flume record 0020). The stream is the one fact about the team that only the host's configuration knows and every launch must name (record 0052 part 3: the runner always names `--stream`), so it is the setting itself rather than a second field. crew reads version 3 with `flume` required on every team, refusing a missing field, `true`, an empty string or a name `code.4` refuses, naming the team and the file, and does nothing else with the file (`code.5`). crew reads version 2 as it reads it today: version 2's schema has no setting, so every team in a version-2 file is on today's path, which is what the file says and no default for a field it has. So the release that carries this change runs on every host whichever file swancloud has written, and the swancloud deploy that writes version 3 can come before or after the crew bump that reads it (record 0050 part 2's order, held either way). `the-team-machinery-leaves` drops the version-2 reading with today's path.

### 2. A team's path is today's, due or crossed, from its setting and the bolts it holds

A bolt given to a team whose path is crossed carries the mark `Path: flume` on its Bolt record in the plan, written by that give with `Team`; every other bolt runs today's path. A team's path is a decision of plain facts (`code.7`), `runner.team_path(setting, held)`, `held` being the `Path` of each bolt the plan gives the team:

- **today's**: the setting is `false` and no bolt it holds is marked `flume`;
- **crossed**: the setting names a stream and every bolt it holds is marked `flume`, or it holds none;
- **due**: the setting and a bolt it holds disagree; due to cross while the setting names a stream, due back while it is `false`.

A due team is given no new bolt: `crew bolt give` refuses it, naming each bolt it finishes first and on which path, and crew's tell to the dispatchers that a team is free leaves it out. Its bolts go on as they were given, a today's bolt with its conductor, ops and slots (`teams.*` unchanged for it), a Flume bolt through the runner, until each lands or is dropped. Nothing moves a bolt from one path to the other: a team crosses empty. The mark is intent of the same kind as `Team`, who builds the bolt and how, and says nothing of how far work has got (`state.2`).

### 3. The crossing: a crossed team's standing agents are due an end

The landing or drop that leaves a due team holding no bolt of its old path makes its path its setting's. For a team now crossed, its conductor and ops are due an end, never a restart: crew gives it as `teams.19` gives a due restart, at the agent's next stop once idle with no question open, or by the hand that gives an idle agent its due restart (`crew update`, the console's rail tab), never on a held host. The same holds for a team whose setting is turned on while it holds nothing and its roles are up. Once neither role is up, however they went down, ended at their stops, by a host's hold (`crew hold wait` ends every crew agent there, its pane kept, and the bolt that crosses the team may land meanwhile) or by any other hand, the act that finds them both down closes the crossing: it closes the team's workspaces as `crew close` does, marks it down, frees its slots, records `team.cross` on `team/<team>` with the stream, and tells the partition's dispatchers that are up that the team takes bolts of its kits whenever one is planned. That act is the end of the last role at its stop, or the hand that finds a role due an end already down: the landing's or drop's tidy on the team's host, and `crew go` and `crew update`, which hand each of a crossed team's roles to `crew _renew`. It closes the crossing once: a crossing is recorded while the newest entry on `team/<team>`, of its `team.cross` and the starts of its standing roles, is its `team.cross`, read from the team's host's own run record, where alone the crossing is recorded and where it stands before the branch takes it (`record.2`), as a card's close reads its post. Nothing of it is ended or closed while its host is held; `crew go` closes it. A team due back has no agent to end; once it holds no Flume bolt it is on today's path, and its roles start at its next give or `crew up`, as for any team with none up.

### 4. The exchange with the runner: requests on the flywheel's branch, answers on the runner's own

crew asks a runner for work by records on the flywheel's branch, and the runner answers on a branch of its own, so each branch has one writer's discipline and neither writes the other's.

**`requests.rec`** on `<label>/main`, record set `Request`, numbered from 1 and never renumbered, each record appended by a crew command through `state.1` in the same commit as the plan write that occasions it, recfix-checked with crew's own rules, never changed or removed (as `proposals.rec` is, `plan.4`). Fields:

| Field | Meaning |
|---|---|
| `Request` | its number |
| `Act` | `launch`, `retry`, `drop` or `priority` |
| `Host` | the host whose runner acts on it, as the hosts file names it: the crossed team's `machine` |
| `Work` | the crew object it serves: `unit/<u>`, `chore/<c>`, `fix/<bolt>/<name>`, or `fix/main/<kit>/<name>` (Decision 11) |
| `Repo` | the kit's forge address, `owner/name`, the team's kit as the hosts file's space names it (launch) |
| `Kind` | `change`, `chore` or `fix`, flume's own kinds through crew's `.config/flume.toml` binding (launch) |
| `Name` | the place's name: the unit's or chore's, `<bolt>--<name>` for a fix on a bolt, `main--<name>` for a fix on main (launch) |
| `Base` | `bolt/<bolt>`, or `main` (launch) |
| `Stream`, `Priority`, `Intent`, `Recipient` | the launch's `--stream`, `--priority`, `--intent` (`<label>/<bolt>`, or `<label>/main/<kit>`) and `--recipient` (`<label>/planner`, or `<label>/ops` for a fix on main, `roles.7`) |
| `Hold` | `submission`, for a fix on main (launch) |
| `After` | one per launch request whose place must have landed on its base before this one is launched (launch) |
| `Brief` | the launch's brief, multi-line (launch) |
| `Of` | the launch request a retry, drop or priority acts on |
| `Stage`, `Submission`, `Words` | a retry's `--stage`, `--submission` and `--words` |
| `Date`, `By` | when, and the agent or user whose command wrote it |

**`<label>/runner/<host>`**, one branch per host per partition in the partition's state repository, written by that host's runner alone, pushed without force, and never written by crew (`state.5`: crew's pushes go to `<label>/main` only). It holds three recutils files: `runner.rec`, one record naming the host, the runner's version and when it started serving the partition, so a branch that exists says a runner answers there; `answers.rec`, one record per request it has read, `Request`, `Outcome` (`held` while a launch waits on its `After`, then `launched`; `done`; or `refused`), `Place` (the place's path, once launched), `Words` (Flume's or the runner's own, as given) and `At`; and `places.rec`, one record per place it launched, keyed by its launch's `Request`, with `Place`, `At` and `Status`, Flume's status of that place as `flume status --json <place>` gives it, one line, carried as written (flywheel-runner `core.1`), its last record kept after Flume tidies the place until the work it served has left crew's plan.

crew fetches `<label>/runner/*` in the same fetch as `<label>/main`, into the same cache (`plan.12`: one fetch per command), and reads each host's three files at the tip it fetched. A host's branch that does not exist, or whose files recfix refuses, hides only that host's work, which reads `unknown` and is named (`read.1`, `read.3`); a field crew reads from `Status` is read by facts checked against Flume as it is and guarded where absent (`read.2`).

The runner pulls the flywheel's branch on its own timer (record 0052 part 2), so no host takes an inbound connection (flywheel-runner `core.3`) and crew runs no process for it (`state.4`, `roles.6`). Records are the truth and are pulled; Flume's notice of an end goes to the recipient's address, never to crew (`roles.6`, `roles.7`).

### 5. A crossed team's give launches its bolt whole

`crew bolt give <team> [<bolt>]` to a crossed team checks the kit's policy and makes `bolt/<bolt>` through sluice exactly as today (`give_check`, `BOLT_CREATE`, `plan.19`, `teams.5`), is refused while the team's host is held (`teams.19`) or has no `<label>/runner/<host>` branch (naming it: no runner answers there), and is never refused for the bolts the team already holds (record 0047 move 5 as amended 2026-10-28: capacity is Flume's room per host, never a bolt or a team). Its one plan write sets `Team` and `Path: flume` on the bolt and appends one launch request per unit and chore of the bolt, in the file's order, each with `After` naming the launch requests of the work its `After` names (Decision 7's sequencing). It starts, restarts and greets no agent. It records `bolt.give` as today.

A launch's `Brief` is the work's own words as crew's prompts give them today, less what the stage itself is told, which is the kind's: a unit's `Intent` with its `Source` lines (and an amendment's words, Decision 7), as `stage_prompt` gives construct; a chore's, as `chore_prompt` gives code; a fix's, its words.

**A dependent waits for its After work to land on the bolt.** Flume cuts a place from its base at the launch and takes no other place's work into it, so a unit or chore that builds on another's work is launched only once that work has landed on `bolt/<bolt>`, its place then cut from a bolt that holds it. The runner holds a launch whose `After` names launches until each of their places has landed on its base, answering it `held` meanwhile, and launches it then; that is a fact of Flume's status it already carries, and the decision of the order is crew's, written in the request (flywheel-runner `core.1`). A dependent cut from its After work's branch instead is possible, Flume having no opinion on a base, but its landing would go into that branch ahead of the other's verify, and the other's landing on the bolt would end the dependent's base under it.

### 6. Priority follows the plan's order of bolts

A launch's priority is its bolt's place among the partition's open bolts given to crossed teams, counted from the end of the plan, so the bolt first in the plan has the highest and Flume starts its waiting stages first (flume record 0010); within a bolt every piece has the bolt's priority, and Flume starts equals in the order they came to wait, which is the file's order the give launched them in. Every write that launches or reorders bolts (`crew bolt give`, `crew bolt order`, an approval holding either) recomputes each crossed launch's priority, `runner.priorities(plan, launches)`, and appends a `priority` request for each launched or held place whose priority differs from the last its requests set, so a priority set at a launch is changed after, as record 0047 move 5 has it.

### 7. Plan writes reach a crossed team's places

Each is the write's own act, in its own commit (`plan.3`: an approval applies the same functions as a direct run), decided by `runner.reach(plan, launches, answers, places, op)`:

- a unit or chore added to, or moved into, a crossed team's bolt is launched as the give launches it;
- an approved amendment of a unit whose place is launched is a `retry` of construct with the amendment's words, the place's later stages then running again as Flume runs a kind through (`plan.15`'s outcome, the approval's own act); of a unit whose launch is still held or unanswered, a `drop` of that launch and a new launch whose brief carries the amendment;
- a unit or chore dropped, or a crossed team's bolt dropped, drops each of its launches still standing;
- a dependent whose launch waits on a launch the write drops or launches anew is dropped and launched again naming the new, or none, so no place waits on a launch that will never land; it has not launched, since its After work has not landed;
- a move out of a crossed team's bolt, a split, or a change of `After` on work whose launch is written is refused, naming the work's place and `drop` then `add` as the way on, since a place's base and order are fixed at its launch;
- work with a place on today's path is not moved into a crossed team's bolt, refused naming `drop` then `add`, since nothing moves work in flight from one path to the other (Decision 2);
- work joins no bolt whose landing is queued or that reads proven (`plan.8`), as today.

### 8. A crossed team's work reads its stage from the runner's records

`runner.stage_of(work, launch, answer, place, read)` gives the stage of a crossed team's unit, chore or fix from plain facts: its newest launch not dropped, that launch's answer, its place's record, and whether its host's branch was read. In order: unread host, `unknown`; no launch, `unknown`, naming it; no answer, `launching`; `held`, `waiting` on the work its `After` names; `refused`, `refused` with the words; then from Flume's status: a stage waiting for room, `queued`; a stage begun, its name, code with its ticked tasks of all; stopped short asking, `needs` with the agent's question; sent back after a failed or conflicting submission, its stage with sluice's words; submitted, `submitted` with sluice's number; waiting on its caller past its bound, `waits` with Flume's words; stalled, `stalled`; landed on its base, `merged` on a bolt, `landed` on main; dropped, `dropped`. Once the bolt has landed on main, a merged piece reads `landed`, as today's do. Which of Flume's fields gives each is read against flume 0.3.6's `status --json` and pinned by a fixture of it (`read.2`). `Stages.of` answers this for every piece of a bolt marked `Path: flume`, so `crew bolts`, the rail, the board and every decision that reads a stage read it the same way; the kit is still read for the bolt's head and verdict (`kit.verification`), from GitHub's bolt after a fetch (`plan.19`).

### 9. `crew answer` is the retry that answers a place

`crew answer <work> "<words>"` appends a `retry` of the stage the work's place stopped short on or waits on, with the words, for the planner, the design agent or main-level ops, whoever has the answer (record 0047 move 5: the answer, the planner's, design's or ops's, as a tell or a card, starts it again; flume clause 49). It is refused, naming the place's stage, when the place neither stopped short nor waits on its caller, and when the work is no crossed team's. A card's answer reaches the place the same way: the role that reads it runs `crew answer`. Flume reads no tell, card or pane for an answer (flume record 0008).

### 10. Fixes on a crossed team's bolt

`crew fix <team> <name> "<words>" [--bolt <bolt>]` on a crossed team appends a launch of the fix kind on `bolt/<bolt>`, `--bolt` required while the team holds more than one, named as today's fix is (`fix/<bolt>/<name>`, refused when the name is in use on the bolt), with nothing held: a review note the user marks fix is one (flume record 0011; the planner, reading the batch's notes), as is any repair the planner or ops starts. `--drop` drops it; `--merge` and `--wait` are refused, naming Flume's submission and `crew bolts`. A fix in flight holds the bolt's landing as today's does.

A crossed team's bolt that sluice refuses at its landing for a conflict with main is the bolt's to take main in (`plan.8`): the read of that landing's outcome, ops's `crew bolt submit` or whichever act reads it after (`plan.21`), appends a launch of a fix on `bolt/<bolt>` named `take-main-<main's revision, seven>`, its brief saying to take `origin/main` into the bolt and resolve, with sluice's words of the conflict, unless a fix of that name already stands. The bolt's row says it takes main first; its landing card's approval stands through the fix (record 0031 as amended 2026-10-24), and once the fix lands and sluice is green at the new head, ops submits again on the standing word (`plan.16`). A crossed team's bolt is not forecast against main on any wait, having no conductor; the conflict is met where sluice forms it.

### 11. A red main's fix is a fix place on main

`crew main fix <kit> <name> "<the failure's words>" [--team <team>] [--label L]`, main-level ops's or the user's on reading main's checks red after a landing, appends a launch of the fix kind on `main`, named `main--<name>`, `Work` `fix/main/<kit>/<name>`, its brief the failure's words as the caller has them (sluice's where its gate blamed, the check's own where the checks ran elsewhere: flume record 0023), its submission held (`Hold: submission`), its recipient `<label>/ops`, on the host of the crossed team that builds the kit, `--team` choosing among several and required when they run on different hosts. Where no crossed team builds the kit it is refused, naming `state.3`'s way until then: a bolt of one chore, proposed first among the planned. Once the fix's code has delivered and its submission waits held, the kit's landings row carries it beside the bolts that wait, `fix main--<name>` with the failure's first line, and the user's send of the card is ops's word for it as for any landing: `crew main fix <kit> <name> --send [--excerpt "<the user's words>"]` appends the `retry` of its submission, read and recorded as `crew bolt submit` reads the user's words (`plan.16`, `roles.2`). sluice lands it on main; the runner's record shows it landed; the row leaves. A fix that fails its submission goes back to code with sluice's words as any place does. `--drop` drops it.

### 12. A crossed team's bolt lands by the one procedure

A crossed team's bolt is proven as any is, every piece merged and sluice green at its head, its pieces' stages from Decision 8, so the landings row and card come through the rail's sweep unchanged; main-level ops lands it with `crew bolt submit` on the user's send, from a short-lived worktree on the team's host as today (`plan.16`, `plan.18`), and `crew bolt land` closes it. Its close reads each piece merged from the runner's records where today's reads a change archived or a chore's trailer, a Flume chore's commits carrying no crew trailer (`land_refusal`).

### 13. A crossed team's unit enters a review batch once its change has landed on its bolt

A Flume place's commits live in the runner's clone, which crew does not read, so a crossed unit's change is read for a batch where crew can read it: archived on GitHub's bolt, after a fetch, once its place has merged. It counts toward the partition's batch from that read, named `<unit>:<team>@<the bolt's commit holding it>`, its reading opening its archived folder. Review never holds code (`teams.5`); the bolt's landing waits for its units' batch as today's do.

### 14. The views read the same facts

`crew bolts` (text and JSON), the rail's bolt and landings rows, the board's Construction ledger and `board.agent_views` read every crossed piece's stage from Decision 8 and say each team's path: a due team's head line says what it finishes before it crosses, a crossed team's names its stream and host and has no slots. The planner's band lists the crossed places that wait on an answer, with each question, and ops's band the fixes of main and the take-main fixes in flight; the mod draws both (`code.8`).

### 15. A crossed team runs no standing agent

`crew up`, `rebuild`, `restart`, `resume`, `clear` and `down` of a crossed team, and `crew unit run`, `unit wait`, `unit free`, `chore wait` and `fix --wait` on its work, refuse at once, naming that its work runs in Flume places on its host and that `crew bolts` shows them; `crew status <team>` shows its bolts and places. Nothing of the refusal touches a pane (`teams.2`).

### 16. Who may write a request

A request is written only inside a command the role table already lets its caller run, plus three: `crew answer` (planner, design, main-level ops, the user), `crew fix` on a crossed team (planner, main-level ops, the user) and `crew main fix` with `--send` (main-level ops, the user), each refused for any other caller by `plan.may_write` (`roles.1`); a request's `By` names who ran it. A give is still the dispatcher's or the user's, a landing ops's on the user's word (`roles.2`).

### Rules relied on

`state.1` (every request appended through crew's write, recfix-checked, in the plan write's own commit), `state.3` (a red main's fix as a fix place once Flume's fix kind runs on main), `state.4` and `roles.6` (records pulled, no process of crew's), `state.5` (crew pushes only `<label>/main`), `roles.1` and `roles.2` (Decision 16), `roles.5` (crew holds the order and the readings; Flume the running, sluice the landing), `roles.7` (every place's recipient a role's address), `roles.8` (Decisions 1 to 3), `read.1`, `read.2`, `read.3` (Decisions 4 and 8), `code.2`, `code.4`, `code.7` (every decision in `runner.py` a function of facts), `code.8` (Decision 14), `code.9` (a give answers once its write is made), `plan.2`, `plan.3`, `plan.8`, `plan.16`, `plan.18`, `plan.19`, `plan.21`, `teams.2`, `teams.19`.

### Rules this design departs from, for the design agent to amend

A unit's change edits no page of `docs/architecture/` (`docs.7`, proposed, and the practice since); each departure below is named for the design agent, with the reason, to amend at this change's landing.

- **`code.5`**: crew reads `teams.json` versions 2 and 3 (Decision 1), so the fleet's deploy and crew's bump need no lockstep; the version-2 reading leaves with today's path.
- **`state.2`**: a crossed team's stage is read from the runner's records of Flume's status, not from the kits (Decision 8); the rule's outcome holds, since nothing records by hand how far work has got, and Flume's own state is the stage.
- **`plan.13`, `plan.11`**: a crossed team's dependent is launched once its After work has landed on the bolt, not once that work's construct or a chore's code has delivered (Decision 5), since a Flume place takes no other place's work.
- **`teams.16`**: its one-bolt bound and its room "read from Flume's status" bind a team on today's path; a crossed team holds as many bolts as are given it (record 0047 move 5 as amended 2026-10-28, superseding record 0045's bound when Flume runs).
- **`teams.21`**: a crossed team's bolt is not forecast against main on waits; its conflict with main is met at its landing's submission and its take-main fix launched there (Decision 10).
- **`teams.23`**: a crossed team's stalled place is said on its row from the runner's records and told by Flume to its recipient, the planner's address, not by crew to the operator (flume clause 130).
- **`roles.9`**: no repository is registered in crew; the runner's own configuration names what each host keeps (the user, 2026-10-31; flywheel-runner record 0001 and `core.5`); the rest of record 0052, the runner pulling and launching with `--stream --priority --intent`, stands.
- **`record.md`**: the run record gains the act `team.cross` (Decision 3), a change to the `run-record` spec this change makes as a unit may.
- **`read.5`**: whether a team's crossing is already recorded is read from its host's own run record, not the branch (Decision 3): the crossing is written on that host alone, and an entry the busy branch refused stays off it until the host's next entry (`record.2`), so a read of the branch could record the crossing twice; it is the reading `cards.host_entries` already makes of a card's post, and reads no other host.
- `core.md`'s page table gains `plugin/lib/runner.py` under `plan.md`; `_open.md`'s move 5 says it is built a team at a time by this change and `the-team-machinery-leaves`.

## Dependencies

- **The runner** (agentplot/flywheel-runner, its crew implementation): reads `requests.rec` on each `<label>/main` it serves, answers each request once on `<label>/runner/<host>`, holds a launch for its `After`, runs `flume launch` with every field the request names and `flume retry`, `flume drop` and `flume priority` for the rest in its clone of the repository, carries Flume's status of each place into `places.rec`, and pushes its branch without force as its one writer. Until it runs on a host, crew refuses a give to a crossed team there (Decision 5). Where the runner's design settles another shape for the exchange, this design and its specs are rewritten before code (`docs.3`); crew's half is pinned in the logic tier either way.
- **swancloud**: `teams.json` version 3 with `flume = false` for every team (`lib/crew-teams.nix`); Flume's host configuration declaring each stream a team names; the runner installed and configured for the partition's state repository; and a team's setting turned on in its teams list, one team at a time, on the user's word (`roles.2`, `roles.8`).
- **`roles-run-as-flume-kinds`**: an end Flume tells `<label>/planner` or `<label>/ops` wakes that role. Until it lands, those ends stand untold in Flume, and the planner and ops read them from the rail, the board and their bands (Decision 14); nothing here waits on it.
- **`the-team-machinery-leaves`** depends on this change: it removes today's path, the due path, the setting and the version-2 reading once every team is crossed.
- **Flume** at 0.3.6 or later on the host: `change@2`, `chore@1` and `fix@1` running through (flume record 0011), a fix on any base (flume record 0023), `--hold-submission`, `retry --stage --words` and `--submission`, `priority`, `drop`, and `status --json` with the fields Decision 8 reads.

## Risks / Trade-offs

- **The runner is not built.** Every crossed launch waits on it; the give's refusal on a host with no runner branch keeps a crossed team from taking work nothing will run, and says why.
- **Dependents run one after another.** A dependent's construct waits on its After work's landing rather than its construct (Decision 5); a bolt of long chains takes longer than today's waves. The order is right, and the planner keeps chains short.
- **Ends wake nobody until the roles run as kinds.** A crossed place that stops short waits for a role that reads its band or the board. Flume's stall after five minutes says it on the row (Decision 8).
- **A due team holds its old bolt as long as it lasts.** That is the user's choice of when to turn the setting on; the board says the team is due and what it finishes first.
- **`requests.rec` only grows.** Records are small and few per piece of work; the plan's own files grow the same way.
- **A conflict with main is found at the landing.** One take-main round per conflicting landing, launched at once with sluice's words (Decision 10), where today's forecast may catch it hours earlier.

## Migration Plan

None in code: nothing converts. The order on the fleet: this change lands with every team on today's path (a version-2 file reads as it did); swancloud pins the release and writes version 3 with every team `false`, in either order; the runner is deployed on a host and serves the partition; the user turns one team's setting on; the team is due until its bolt lands, then crossed. A team is moved back by turning its setting off, and is due back until its Flume bolts land.

## After deploy

No step here is a check crew's tiers can hold: each is outside crew's repository or the user's own word.

- **swancloud writes `teams.json` version 3**, `flume = false` for every team, in `lib/crew-teams.nix`, on every host, after or with the bump to this release: swancloud's unit, deployed on the user's word for the bump (record 0050 point 1). Why not code here: swancloud's repository writes the file, crew never does (`code.5`).
- **The runner is deployed** on each host that will run a crossed team, configured for the partition's state repository: flywheel-runner's build and swancloud's install. Why not code here: another repository's program.
- **The user turns a team's setting on**, one team at a time, in swancloud's teams list (`roles.2`, `roles.8`). Why not code here: the move is the user's word.

## Task notes

**1.1** `plugin/lib/crew.py`: `VERSION` becomes the versions crew reads, 2 and 3, and the refusal of any other names both. In `load`, for version 3, each team's `flume` is checked before any team is used: present, and `False` or a string `NAME` matches; `True`, `None`, `""` or any other type refused naming the team and `TEAMS`, saying it is `false` or the name of a Flume stream the host declares. The team's dict gains `flume`: the stream or `False`; a version-2 team gets `False`, said in the docstring as what version 2 means. Cases in `tests/py/test_teams.py`: version 3 with `false` and with a stream; a missing field; `true`; an empty string; a capitalised name; version 2 loads as today with every team off; version 4 refused naming 2 and 3.

**2.1** New `plugin/lib/runner.py`, standard library and crew's own modules only (`code.1`), its docstring saying it is crew's side of the runner's interface (flywheel-runner `core.2`). `team_path(setting, held)`: `setting` the team's `flume`, `held` the list of `Path` values (`"flume"` or `None`) of the bolts the plan gives it; returns `("today"|"crossed"|"due", detail)` where a due detail names whether it is due to cross or back. `path_of(fleet, plan, t)` reads the facts and calls it. Cases in new `tests/py/test_cross.py`: each row of Decision 2, holding none, one, and two of mixed paths.

**2.2** `plugin/lib/plan.py` `HEADER`: the Bolt set's `%allowed` gains `Path` and `%type: Path enum flume`. `plugin/lib/record.py`: `team.cross` among the acts its docstring lists, on `team/<team>`, with the stream in a field the descriptor allows (`State`). Cases: `tests/contract/test_recfix.py` (a plan with `Path: flume` passes recfix, `Path: other` is refused) and `tests/py/test_record.py`.

**2.3** `give_refusal` (or a refusal beside it) refuses a due team, naming each bolt it holds and its path, and says it is given its next bolt once those land; the tell to dispatchers (`tell_dispatchers` and its callers, the bolt-teams "A merge frees the team" path) leaves a due team out. Cases in `tests/py/test_cross.py` and `tests/py/test_bolt_commands.py`.

**2.4** The crossed team's due end: `crew.py` `update_due` / `due_of` read a standing role of a team whose path is crossed as due an end (a reason of its own beside brief, model and plugin); `hold.py` `renew` and `crew _renew` end it, and close the team's workspaces as `crew close` does, rather than restart it; once neither role is up, the act that ended the last records `team.cross` and tells the dispatchers (`tell_dispatchers`). A held host is never touched (`teams.19`). Decisions as plain facts in `runner.py` or `hold.py` (`code.7`): `cross_due(path, up)`, the roles due an end. Cases in `tests/py/test_hold.py` and `tests/py/test_cross.py`; one end-to-end case in new `tests/t-journey-cross.sh` (opening comment and `TESTS` guard per `tests.2`, `# Reads: plugin/hooks/ plugin/roles/`): a due team's bolt lands, its conductor and ops end at their stop, `team.cross` is in the record, `crew up` of it is refused.

**2.5** The refusals of Decision 15, each in the command's entry (`plan.py` `team_cmd`, `unit_run`, `unit_wait`, `unit_free` and the chore's and fix's kin; `plugin/bin/crew` where a team command is pure bash), from `path_of`, before any pane or slot is read. Cases in `tests/py/test_cross.py` for the decision, and `crew up` in `tests/t-journey-cross.sh`.

**2.6** The close of a crossing whose roles are already down (Decision 3): `runner.cross_close(path, up, recorded)`, whether the crossing is due its close, and `runner.cross_recorded(entries, team)`, whether entries hold it (`STARTS`, the acts that start a standing role; a refused act starts nothing), decide it; `hold.crossing_recorded(label, team)` reads this host's day files of the partition newest first until one tells; `hold.close_crossing(fleet, team)`, inside the team's crossing lock (`hold.crossing`), refuses on a held host and does the close, the tail of `cross_end` and `renew`'s branch for a role due an end it finds down; `plan.team_tidy` hands each of a crossed team's roles to `crew _renew` when none is up and the crossing is not recorded. Cases in `tests/py/test_cross.py` for the decisions and `tests/py/test_hold.py` for the close, held, down, recorded and a role still up; in `tests/t-journey-cross.sh`, swb-2 on the same host is due when its host is held and `crew hold wait` ends its roles, its bolt lands with nothing closed, and `crew go` closes it once.

**3.1** `runner.py`: `REQUESTS`, the `requests.rec` header and descriptor (`%rec: Request`, `%key: Request`, `%type: Request int`, `%type: Act enum launch retry drop priority`, `%type: Kind enum change chore fix`, `%type: Of int`, `%type: After int`, `%type: Priority int`, `%mandatory: Request Act Host Work Date By`, `%allowed` as Decision 4's table); `request_refusal(requests, new)`, crew's own rules beyond recfix (`plan.1`): a launch carries `Repo Kind Name Base Stream Priority Intent Recipient Brief`; `Of` names a launch; `After` names launches of the same bolt; a number is the next; a `fix/main/...` launch holds its submission. `plan.write` appends through the change function as plans and proposals are, so the request and the plan write are one commit with one `Crew-Entry` (`plan.2`). Cases in `tests/contract/test_recfix.py` (the descriptor against recfix) and new `tests/py/test_runner.py`.

**3.2** `plan.fetch` (and `plugin/lib/gather.py` only if it reads the state cache) fetches `refs/heads/<label>/runner/*` beside `<label>/main` in its one `git fetch` into crew's cache; `runner.read_runners(repo, label, tips)` reads each host's `runner.rec`, `answers.rec` and `places.rec` at its tip, answering per host either its records or why it was not read (missing branch, recfix refused, a `Status` that is not JSON). A contract case in `tests/contract/test_git.py`: a bare state remote with `madswan/main` and `madswan/runner/deneb`, fetched once, both read; a host with no branch named. Logic cases in `tests/py/test_runner.py` for the parse.

**3.3** `runner.stage_of` per Decision 8, its Flume reads in one place (`flume_facts(status)`), every field guarded (`read.2`). Capture `flume status --json <place>` from flume 0.3.6 for a place at construct, at code with tasks, stopped short asking, sent back after a failed submission, submitted, stalled and landed into `tests/py/flume-0.3.6/` as fixtures, as sluice's are kept, each file saying where and when it was read. Cases in `tests/py/test_runner.py`, one per stage word and the unread and unknown cases.

**4.1** `plan.bolt_give`: from `path_of`, a crossed team skips `give_refusal`'s bound and the restart and greeting; a held host and a missing runner branch for the team's machine refuse before sluice makes the branch. The change function sets `Path: flume` with `Team` and appends the launches from `runner.launches(plan, bolt, team, kit, requests)` (Decision 5's fields and briefs; `After` resolved to the request numbers of the same write). Cases in `tests/py/test_cross.py` (the launches for a bolt of two units, one `After` the other, and a chore); the give in `tests/t-journey-cross.sh` writes `requests.rec` on the bare state remote and starts no agent.

**4.2** `runner.priorities(plan, requests)`: Decision 6's count, and the `priority` requests for each launch whose last priority differs; called from the give and `crew bolt order`'s change function. Cases in `tests/py/test_runner.py`: two bolts given in order, a third added, a reorder sending only what changed.

**4.3** `runner.reach` per Decision 7, called from the change functions of `unit add`, `chore add`, `unit move`, `chore move`, `unit amend`, `unit drop`, `chore drop`, `bolt drop`, `unit split`, `unit after` and `chore after` when the bolt is marked `Path: flume`; a refusal is a `Refusal` from inside the change function, so a proposal holding it is refused whole (`plan.3`). Cases in `tests/py/test_cross.py` and `tests/py/test_amend.py` (an amendment of a launched unit is a retry with its words; of a held one, a drop and a new launch).

**4.4** An approval or `crew bolt new` that plans a bolt of a kit a crossed team builds, held by no team, tells the partition's dispatchers that are up that it can be given (`tell_dispatchers`), as a freed team's does. Cases in `tests/py/test_cross.py`.

**4.5** `plan.bolt_give`'s skip, for a crossed team, of `give_refusal` and of the change function's two-bolt check (Decision 5; `teams.16` binds today's path) reached through the command: in `tests/t-journey-cross.sh`, crossed swb-1, holding `next` with none of its work merged, is given `more` and then `last`, neither refused, each marked `Path: flume`, and no agent starts.

**5.1** `crew answer <work> "<words>"`: `plan.py` command and parser, `plugin/bin/crew` usage; the place's stage from `stage_of`; a `retry` with `Stage` the place's current and `Words`; refused per Decision 9. Cases in `tests/py/test_cross.py`; one case in `tests/t-journey-cross.sh` with a runner record the test writes showing the place stopped short.

**5.2** `plan.fix_cmd` / `fix_run`: a crossed team's fix appends its launch (`Kind: fix`, `Name` `<bolt>--<name>`, nothing held) through `runner.launches`; `--drop` a `drop`; `--merge` and `--wait` refused. `fixes_in_flight` reads a crossed bolt's fixes from its launches and the runner's places. Cases in `tests/py/test_fix.py`.

**5.3** Where a landing's outcome is read (`landing_read` and `landing_said`, `bolt_submit`'s end), a refusal of a crossed team's bolt for a conflict with main (sluice's conflict words, as `held_at` reads them) appends the take-main fix's launch unless one of that name stands; the row says it takes main first. Cases in `tests/py/test_landings.py` and `tests/py/test_landing.py` on sluice 0.56.0's fixtures.

**5.4** `plan.may_write` and its `OPS` table: `answer`, `fix` on a crossed team and `main fix` with `--send` for the callers of Decision 16. Cases in `tests/py/test_plan_roles.py`.

**6.1** `crew main fix <kit> <name> "<words>" [--team <team>] [--label L]`: the crossed team building the kit chosen per Decision 11, refused with `state.3`'s way when none; the launch with `Base: main`, `Name: main--<name>`, `Hold: submission`, `Recipient: <label>/ops`, `Intent: <label>/main/<kit>`; `--drop`. `record.py`'s object types gain `fix/main/<kit>/<name>`. Cases in new `tests/py/test_main_fix.py`; new `tests/t-journey-main-fix.sh` (`# Reads: plugin/roles/`): a fix of main launched, the runner's record showing its code delivered and its submission held, the kit's landings row carrying it, `--send` appending the retry.

**6.2** `rail_rows`' `land` group carries each fix of main whose code has delivered and whose submission waits held, from its launch and the runner's place; `crew main fix --send` with `--excerpt` read as `bolt_submit` reads the user's words (`check_excerpt`, shared, not copied). Cases in `tests/py/test_rail.py`.

**7.1** `Stages.of` answers `stage_of` for every piece of a bolt marked `Path: flume`, the runners' records read once per command beside the plan (`plan.12`); `crew bolts` text and JSON show it with the team's path on the bolt's head line. Cases in `tests/py/test_bolt_commands.py` and `tests/py/test_stages.py`.

**7.2** `proven_facts` and `land_refusal` read a crossed piece's merged from `stage_of`; a chore of a crossed bolt is not asked for its trailer. Cases in `tests/py/test_landing.py`.

**7.3** The batch's count and its units (`batch_due`, the batch's `Units`) take a crossed unit once its stage reads merged, at the commit of GitHub's bolt holding its archive (`kit.main_now`'s fetch for the bolt), and its reading opens the archived folder. Cases in `tests/py/test_batches.py`.

**7.4** `board.py` `bolt_row`, `stage_of` and the Construction ledger, and `agent_views`: a crossed team's line names its stream and host and no slots, a due team's says what it finishes first, the planner's view lists the crossed places waiting on an answer with their questions and ops's the fixes of main and take-main fixes in flight; `plugin/hooks/status.js` draws the new keys. Cases in `tests/py/test_board.py` (the case pinning every key the mod reads, `code.8`) and `tests/py/test_rail.py`; the mod's cases in `plugin/tests/`.

**8.1** `plugin/roles/dispatcher.md`: a due team is given nothing; a crossed team is never full and takes each planned bolt of its kits as the plan orders. `conductor.md`: a due team's conductor builds its bolt to its landing, is given no next bolt and is ended at its stop once it has crossed. `planner.md`: a crossed team's places tell it their ends by its address; `crew answer`; a batch's note marked fix is `crew fix` on a crossed team; amendments and drops reach the places by their approval. `main-ops.md`: a crossed bolt lands by the same procedure; its conflict starts its take-main fix itself; a red main of a kit a crossed team builds is `crew main fix`, and the user's send of its row is `--send`. Each new rule's phrase in `tests/t-briefs.sh` (`tests.6`); `tests/t-roles.sh` where a brief's size or token changes.

**8.2** README's Teams section and the plan's, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header: the setting, a team's path, the crossing, `crew answer`, `crew fix` on a crossed team, `crew main fix`, the refusals, the runner's branches (`docs.2`). `tests/t-docs.sh` holds README's commands to the usage.

**9.1** Run `tests/moon-tasks` and commit `tests/moon.yml`, the two new tests' tasks among them with their `# Reads:` paths and `plugin/lib/runner.py` in the core crew's modules import (`tests.10`); then `tests/suite --affected`.
