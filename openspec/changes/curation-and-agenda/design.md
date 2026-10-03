# Design

## Context

See proposal.md for why. The current state, after the changes this one depends on:

- **Signals.** An agent's capture and signals are files under `signals/<capture>/` on the flywheel's branch (`<label>/main` of its state repository), each signal with a checked excerpt and a grade (`checked-capture`). Meeting and channel signals are in the partition's first blueprints repo's `signals/`, written by the daily pass. crew looks a signal up in the state first, then the blueprints. wldn has 194 signals, 192 with no move, nearly all from meetings.
- **Moves.** `moves.rec` on the flywheel's branch, `%key: Signal`, one move per signal, the enum `attach challenge new-territory answered drop route`. `crew signal move <id> <move>` writes curation's five; `crew unit add --signal` writes `route` with the unit (`state-repository`). Only two moves exist, both `route`, By `wldn-planner`.
- **Briefs.** The design agent's brief has a "Curating signals" section. The conductor's and main-level ops' briefs say to record a finding as a signal "and tell the planner in one line". The planner's says "a signal becomes work only through you, with `--signal`".
- **The plan.** The planner changes it only by a proposal the user approves (`plan-proposals`); each plan command is `checks`, `change`, `after`. The design agent may add a unit to a kit's queue directly.
- **Roles** are agent definitions in `plugin/roles/`, started by `crew-role`; the main level is a herdr workspace `<label>` with `design`, `planner` and `ops` tabs on the host and session the teams file names; `crew main` is forwarded to that host.
- **The run record** has an entry for every act, carried to the flywheel's branch.

The vocabulary and shapes are Flywheel Next's. Its rules this design keeps: a signal is immutable; every signal has exactly one standing move, and only the operator's response replaces one; curation is a bounded session that judges and does not act, reads only its work order, and delivers in one commit; a person writing the same records by hand is curation; a proposed intent's subject is what is unsettled, not the answer, and it rests on at least one signal; weight counts by event date.

## Goals / Non-Goals

**Goals:**
- Every signal is judged, in batches, by a session whose only job is judging.
- What needs the user is a list the user can open, with the evidence on it; what does not goes to the planner, whose proposal the user still approves.
- Every unit and every decision record traces to an item, and every item to words someone said.
- One finding can be followed end to end from the run record.

**Non-Goals:**
- Running curation without being asked. The user starts it; a threshold or cadence waits for the numbers that doing so by hand will show.
- A design session ritual. A session is the user and the design agent talking; crew provides the item and records the close.
- Intents as objects with elaborations, as Flywheel has. An item is settled in a session.
- A finding that blocks the unit it was found in (`blocking-findings`).
- Landing the daily pass through crew (`daily-pass-through-crew`).

## Decisions

### Moves: keyed by number, with a standing move

```
%rec: Move
%key: Id
%type: Id int
%type: Move enum attach challenge join answered route drop revive
%type: Date date
%mandatory: Id Signal Move Date By
%allowed: Id Signal Move Target Reason Date By Replaces
```

The first write under this change rewrites the descriptor and gives the existing records `Id` 1 and 2 in file order, in the same commit. `new-territory` leaves the enum: no record uses it, and `join` is Flywheel's word, so its signals-folder adapter reads every move crew writes.

A signal's **standing move** is its record that no other record's `Replaces` names. A signal is **unmoved** when it has no record or its standing move is `revive`. crew enforces one standing move, since `recfix` no longer can: a write that would give a signal a second is refused unless it carries `Replaces`.

| Move | Target | What follows |
|---|---|---|
| `route` | `agenda/<n>`, a plan item | the planner proposes a unit from the item. (`unit/<unit>` only when written by the approval of a unit proposed with `--signal`.) |
| `join` | `agenda/<n>`, a design item | it is on the design agenda |
| `attach` | `unit/<unit>`, `bolt/<bolt>`, or a path of an open intent | evidence on work already under way; nothing new |
| `challenge` | a path of a standing page: a decision record, a chapter, a spec | weight against that page; nothing new |
| `answered` | a path, `unit/<unit>`, or `<owner>/<name>@<sha>` | nothing; the target is what settled it |
| `drop` | none | nothing |

Every move carries `Reason`. A path target is `<path>` in the first blueprints repo or `<owner>/<name>:<path>`, and must exist on that repository's main; a unit or bolt must be in the plan; an item must be open and in the move's lane. `challenge` moves are not gathered into items: a curator that thinks a challenged page should be reopened `join`s the signal to a design item that says so.

**Replacement.** `crew signal move <id> <move> … --replace "<why>"` writes a new record with `Replaces: <Id of the standing move>` and `Reason` holding the why; `crew signal revive <id> "<why>"` writes `Move: revive` the same way. Both are the user's, run by the user or on the user's word. Nothing is rewritten. An item whose last signal is moved away stays open with no weight until someone closes it.

### The agenda

`agenda.rec` on the flywheel's branch:

```
%rec: Item
%key: Item
%type: Item int
%type: Lane enum plan design
%type: Kind enum intent question
%type: State enum open planned decided dropped
%type: Opened,Closed date
%mandatory: Item Lane Subject State Opened By
%allowed: Item Lane Kind Repo Subject State Opened By Closed Result Note

Item: 7
Lane: design
Kind: question
Repo: switchboard-kit
Subject: How agents find out what nixpkgs and treefmt-nix offer before choosing a tool for the dev shell.
State: open
Opened: 2026-10-06
By: wldn-curator
```

- `Kind` is for design items: `intent` (something to work out and probably build) or `question` (something to answer). `Repo` is the kit; a plan item must have one, since the planner needs it.
- `Result` repeats: `unit/<unit>`, or `<owner>/<name>@<sha>:<path>`. `Note` repeats: a lane change's reason, a drop's reason.
- crew rewrites only `Lane`, `State`, `Closed`, `Result` and `Note`. An item is state, like a unit; what it was is in the branch's history and the run record.
- A number is one more than the highest, computed inside the write.

Signals and weight are computed on reading: the signals whose standing move targets `agenda/<n>`; their captures (each signal's capture file, in either home) for the count of captures, their `source` values and the span of `event_date`. `crew agenda` prints one line per open item:

```
 7  design  question  switchboard-kit  3 signals, 2 captures (wispr-flow, crew-session), 09-29 to 10-03
    How agents find out what nixpkgs and treefmt-nix offer before choosing a tool for the dev shell.
```

`crew agenda <n>` prints the item, then each signal as `crew signal show` does in short (id, kind, who, assertion, the excerpt and its grade, capture source and date) with the move's reason, then any open proposal naming the item, then for a closed item its state, date and results.

### Hand-written curation

- `crew agenda add "<subject>" --lane plan|design --signal <id>... [--kind …] [--repo <kit>]` creates the item and writes each signal's `route` or `join` in one commit. Each signal must be unmoved, or the command carries `--replace "<why>"` for all of them.
- `crew signal move` keeps its form, takes `join` where it took `new-territory`, requires `--reason` for every move, and applies the target checks above.

These are for the user: typed at a shell, or run by an agent on the user's word. The briefs say so; the run record shows who ran each.

### Lanes and closing

- `crew agenda lane <n> plan|design "<why>"`: the item must be open. It sets `Lane`, adds `Note: to <lane>: <why>`, and when it moves a plan item to design, sets any open proposal with a `unit add --item <n>` to `dropped` with the reason "item <n> was sent to design", in the same commit. The moves that target the item are not rewritten: a `route` whose item is now in the design lane is read as a join, because the lane is the item's.
- `crew agenda close <n> decided --result <ref>...`: at least one result. A unit result must be in the plan with `Source: agenda/<n>`. A document result is given as `<repo name>:<path>`; crew finds that repository's main checkout on the host it runs on (the design agent's host), requires the file to be committed at `HEAD` with `agenda/<n>` in its text, and records `<owner>/<name>@<sha>:<path>`. A checkout that is not on this host is a refusal that says where to run it. The design agent pushes only on the user's word, so crew reads the local commit and not GitHub.
- `crew agenda close <n> dropped "<reason>"` closes with a `Note`.
- A plan item closes as `planned` when an approval applies a unit added from it, with the unit as `Result`; a later unit from the same item adds a `Result`.

### A unit names its item

`crew unit add` gains `--item <n>`. Its `checks`: the item is open; in a proposal (the planner) its lane is `plan`; run directly by the design agent its lane is `design` and the unit goes to a queue (`--repo`). Its `change`: `Source: agenda/<n>` is the unit's first source; in an approval, for a plan item, the item becomes `planned` with the result, in the approval's commit.

The role table of `plan-proposals` gains the gate: an agent's `unit add` with neither `--item` nor an accepted `--signal` is refused. For the design agent the message is "a unit names the agenda item it came from (--item <n>); for something the user raised here, record it with crew signal and add an item with crew agenda add". `--signal` is accepted from the planner only inside a proposal, for a signal whose capture names the planner as `captured_by` and that is unmoved; the approval writes its `route` with `Target: unit/<unit>`, `Reason: the user told the planner directly`, `By` whoever ran the approval. A signal with no move is refused as "not yet curated", one routed or joined as "on the agenda as item <n>: use --item <n>".

The construct stage is given the unit's sources as today. `construct.md` gains: a source `agenda/<n>` is read with `crew agenda <n>` and a source `signals/<id>` with `crew signal show <id>`; the change's proposal quotes the excerpts it rests on. The proposal page (`crew plan proposed <n>`) prints, under a unit added from an item, the item's subject and its signals with excerpts and grades.

### The curator

`plugin/roles/curator.md`: `model: claude-fable-5-1`, `effort: high`. Its brief, in substance:

- The job is one batch: every signal in the work order gets exactly one move, with a reason a stranger could weigh. Nothing outside the work order is acted on.
- Read before judging: the signal, its excerpt and grade (an `unverified` excerpt is the agent's claim and weighs less), and for a challenge or an answer the page itself, in the main checkouts, read-only.
- The test for the lanes: `route` when the planner could write a unit's intent from the signal with no decision only the user can make, and say which kit; `join` when it raises a design question, a tradeoff or something to investigate; when in doubt, `join`. `attach` when the plan already holds it; `answered` when a decision since settles it, naming the record; `drop` for noise or a duplicate, with the reason, naming the signal it duplicates.
- Check the open items first: a signal that fits one joins it. Several signals about one thing make one item. A design item's subject says what is unsettled, never the answer; a plan item's says what was asked for, in the asserter's terms.
- Judge, do not act: write the delivery file and run `crew curate deliver`. Change no design, no plan, no code. An idea of its own is a `crew signal`.
- When the delivery is accepted, say in two lines what the batch held and stop.

### `crew curate`

`crew curate <label> [--only <capture>...]` is forwarded to the main level's host, like `crew main`.

1. Refuse when the label's curator is up (its pane has an agent), naming its batch.
2. Fetch the flywheel's branch and the first blueprints repo's main. The batch is every unmoved signal at those two commits, narrowed by `--only`. Empty: say so and stop.
3. Write the work order to `~/.local/state/crew/<label>/curate/<batch>/`, the batch id being `<UTC date>-<n>`:
   - `order.md`: the job in a paragraph, the batch's signals listed by id, the paths below, the checkouts to read the design in (the main level's blueprints and kit checkouts, and that each repository's CLAUDE.md says where its design is written), the delivery's format with an example, and the command to deliver;
   - `signals/<capture>/…`: each batch signal and its capture, exported from crew's git caches at the fixed commits, from either home;
   - `agenda.md`: `crew agenda --all`'s open items, each with its signals;
   - `plan.md`: each bolt with its goal and team, each unit with its intent and stage, and the queue;
   - `batch.rec`: the batch id, the two commits and the signal ids, which `deliver` checks against.
4. Open a `curator` tab in the `<label>` workspace, start the role there in the first blueprints repo's main checkout, and prompt it: "Curate batch <batch>: read <dir>/order.md."
5. Entry `curate.start`, `On: batch/<batch>`.

`crew main status` lists the curator when it is up. Any `crew curate` or `crew main` command closes the tab of a curator whose batch is delivered and whose agent is not working. A curator that dies leaves an undelivered batch directory; the next `crew curate` starts a new batch and ignores it.

### The delivery

The curator writes one recutils file:

```
%rec: Item

Item: a
Lane: plan
Repo: switchboard-kit
Subject: A security check on Switchboard's CloudFormation templates, beside cfn-lint's validity check.

%rec: Move

Signal: 2026-10-05-swb-2-conductor-9f2c1a7e/01-cfn-nag-templates
Move: route
Target: a
Reason: The user asked for it in so many words, and it names the tool; nothing in it is a choice only the user can make.

Signal: 2026-09-29-vpp-standup/04-package-lookup
Move: join
Target: agenda/7
Reason: The same question item 7 already holds, from a second source.
```

A `Target` is a local item name from the file, `agenda/<n>` for an open item, or another target of the table above. `crew curate deliver <file>` (run by the curator, or by the user for a delivery written by hand) checks, at the tip:

- the caller is the label's curator with an undelivered batch, or the user with `--batch <id>`;
- the moves' signals are exactly the batch's, each still unmoved; a signal moved by hand since the batch was fixed is named, and the curator leaves it out and delivers again, which the check then allows;
- every move's target resolves and its lane matches, every move has a reason, every new item has a move, a plan item has a `Repo`;
- then one `write`: the moves with their `Id`s, the items with their numbers (local names replaced), `Date` and `By`.

The commit's subject is `curate(<batch>): <m> moves, <i> items (<curator>)`. Entries: `curate.deliver` (`On: batch/<batch>`), one `signal.move` per move (`On: signals/<id>` and the target), one `agenda.add` per item (`On: agenda/<n>`, `From:` its signals). Afterwards crew writes `delivered` with the commit into the batch directory, and tells the planner the plan items that are open: "[crew] Curation <batch> left plan items 8, 9 for you: crew agenda --lane plan." A second delivery finds `delivered` and writes nothing.

### Briefs

- `conductor.md`, `ops.md`, `main-ops.md`: a finding outside the bolt or the unit is `crew signal`, and that is all. "Tell the planner" goes. What is theirs to tell the planner about stays: a conductor still tells it what building showed about its own bolt's units.
- `design.md`: the "Curating signals" section is replaced by "The agenda": when the user names items or asks for the agenda, read them with `crew agenda`; settle each with the user; record the decision where the repository's CLAUDE.md says, citing `agenda/<n>` and its signals; queue what needs building with `--item <n>`; close the item. When the user starts on something new, record their words and add an item first. A conductor's question the design does not answer and only the user can: say so to the conductor, who asks the user.
- `planner.md`: plan items arrive from curation (`crew agenda --lane plan`); each becomes a `unit add … --item <n>` in a proposal whose intent says what must be true and adds nothing the item's signals and the standing design do not say; an intent that needs a choice goes to the design lane with `crew agenda lane`; what the user says directly is recorded with `crew signal` and proposed with `--signal`.
- `operator.md`: the agenda and proposals among what waits on the user; `crew curate` on the user's word; a signal moved by hand only on the user's word.
- `construct.md`: reading an item and its signals.

### What must not break

- Signals and captures are never rewritten; the two `route` moves of 2026-10-03 keep their content and gain an `Id`.
- The daily pass is untouched; its signals are curated where they lie.
- The user at a shell can still add any unit and move any signal.
- A proposal with no `--item` in it (a move, a new bolt, a drop) behaves as in `plan-proposals`.

## Risks / Trade-offs

- [The first batch on wldn is 192 meeting signals] → `--only` scopes the proof; the backlog is a batch the user starts when they choose, and most of it should land as `answered`.
- [The curator routes what the user would have wanted to decide] → the planner's proposal still needs the user's approval, with the excerpts on its page, and both the planner and the user can send an item to design.
- [A curator holds a large batch in context] → the work order is files it reads as needed; a batch can be split with `--only`.
- [An agent moves a signal by hand without the user] → the same exposure as approvals; the entry names the session.
- [`agenda close` cannot see an unpushed decision record from another host] → it runs where the design agent works, which is where the commit is.
- [Weight is slow to compute over many items] → one fetch of each home and file reads from crew's cache; no host is contacted.

## Migration Plan

1. Pull on every host. The first move or delivery re-keys `moves.rec`; `agenda.rec` appears with the first item.
2. Restart every standing agent, since most briefs change. Until a conductor is restarted it still tells the planner about findings; the planner's new brief has it answer that findings are curated.
3. The blueprints' `signals/README.md` is edited (an outside task).

Rollback: revert crew's commit. `moves.rec` keeps its `Id` key, which the older crew cannot read; restoring the older crew therefore also means restoring the descriptor by hand, so roll forward where possible.
