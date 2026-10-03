# Findings to design: a proposal

For the user's review. It answers `brief.md`, beside it, in the brief's order. The build is laid out in `roadmap.md`, beside it, and specified change by change in `openspec/changes/`.

## The flow

```
 notice                 curate, on the user's word      two lanes
 ──────                 ──────────────────────────      ─────────
 an agent, the user,    a curator, started for          route ─► plan item ───► the planner proposes a plan change ─► the user approves ─► the plan
 a meeting, a channel   one batch, gives every     ┌──►
        │               unmoved signal one move ───┤    join ──► design item ─► the user and the design agent,
        ▼                        ▲                 └──►                         in a session: decision record, units
 capture + signal ───────────────┘                      attach · challenge · answered · drop: recorded, lead nowhere
 (verbatim excerpt, checked)

 a finding that blocks its own unit: the conductor asks the user. A small change amends the unit; a big one takes the path above while the unit waits.
 every crew command above, and every one that moves a bolt or a unit, adds an entry to the run record
```

1. **Whoever notices something runs `crew signal`**, with the words that show it. crew looks for those words in the agent's own Claude transcript and records how well it could check them. The agent tells nobody and carries on.
2. **Nothing more happens until curation**, which starts on the user's word. A curator, started for one batch, reads the unmoved signals against the design as it stands and delivers every move in one commit. Signals that should lead somewhere are grouped into **agenda items**, each in the plan lane or the design lane.
3. **A plan item goes to the planner, which proposes a change to the plan**: the unit, its intent and where it goes, which may be the queue, a new bolt or an existing one. Every change the planner makes to the plan is a proposal, and the plan changes when the user approves it.
4. **A design item waits for the user.** The user and the design agent settle it in a session, and the decision record and the units it produces cite the item.
5. **A finding that blocks the unit it was found in** is the conductor's question to the user. A small change amends the unit. A big one becomes a signal like any other, and the unit cannot merge until what came of it has.
6. **Every crew command that moves work adds an entry to the run record.** `crew trace <signal|unit|bolt>` prints what happened to it, in order, from those entries alone.

The words are Flywheel Next's: capture, signal, kind, move (attach, challenge, join, answered, route, drop), curation, weight, proposal, run record, state repository. A **flywheel** here is one partition's loop, named by its label (`wldn`). Section 5 says where crew is simpler.

## 1. The invariants, and what makes each true

### Captures and signals

| # | Mechanism |
|---|---|
| 1 | For an agent, a source event is **one record its session received**: a message the user typed, or one tool's output. `crew signal` asks herdr for the calling agent's Claude session (as `crew status` does today), finds the record that holds the excerpt, and writes `capture.md` with the host, session id, record id and time, the agent, and the team, bolt and unit it was working in. It copies that record to `~/.local/state/crew/<flywheel>/raw/` on the host, outside git. A second signal from the same record joins the same capture, so capturing twice yields one. Meetings and channels keep the daily pass in the blueprints repo. |
| 2 | `--excerpt` is mandatory. crew looks for it in the session's transcript and records a grade on the capture: `verified`, `found` or `unverified`. It refuses the signal only when it can read the transcript and the words are not in it, which is the paraphrase case. Section 3 gives the grades and why a change in the transcript's format lowers a grade and never blocks a capture. When the user runs `crew signal` at a shell, the text is its own excerpt, as Flywheel's capture box is. |
| 3 | `crew signal` is the only thing a noticing agent does about a finding outside its own unit. The briefs lose "and tell the planner in one line". Every signal, from a meeting or from a conductor, then waits unmoved for the same curation. |
| 4 | The banked record and the transcript stay on the host. `capture.md` names them as `<host>:<path>`, so anyone who can reach the host reads the source again. Only the excerpt enters git: in the flywheel's state for an agent's capture, in the blueprints for a meeting's. The run record carries no text anyone typed. |
| 5 | No crew command edits a signal. A move is appended to the flywheel's `moves.rec` and never changed. A signal's standing move is its latest, and crew accepts a second move for a signal only as the user's replacement: `crew signal move <id> <move> --replace "<why>"`, or `crew signal revive <id> "<why>"`, which leaves the signal unmoved for the next batch. The new record names the one it replaces. |

### Curation and the two lanes

| # | Mechanism |
|---|---|
| 6 | `crew curate <flywheel>`, run on the user's word, fixes the batch (every signal with no standing move at that tip), writes a work order and starts a curator session for it. `crew curate deliver <file>` accepts the delivery only when every signal of the batch has exactly one move, and writes all of them in one commit. A signal that arrives during the run waits for the next batch. |
| 7 | `route` targets a **plan** item and `join` a **design** item; both are records in `agenda.rec`, created by the same delivery. `attach`, `challenge`, `answered` and `drop` lead nowhere and name what they rest on. The curator's test for `route` is the brief's: the planner could write the unit's intent with no decision only the user can make. When in doubt, `join`. |
| 8 | **The planner changes the plan only by a proposal the user approves** (`crew plan propose`, `crew plan approve`). A unit an agent adds names where it came from: `--item <n>`, an open plan item or a design item being decided; or, for the planner alone, `--signal <id>`, a signal it captured itself from what the user told it, whose `route` move the approval writes as the user's hand. The design agent queues the units of a session directly, with `--item`, and the planner places them by proposal. crew refuses an agent's `crew unit add` that names neither. The user at a shell writes the plan freely. |
| 9 | The planner words the intent, and the user judges it twice. `crew plan proposed <n>` prints the proposal: the planner's case, and each change with the intent beside the excerpts it rests on and where the unit would go. The user approves it, drops it, or sends an item to design (`crew agenda lane <n> design "<the decision it needs>"`, which the planner also runs when it finds an intent needs one). The second judgment is the review of the unit's OpenSpec change. crew cannot detect a design decision in a sentence; it puts the sentence beside the words it came from before anything is built. |

### Design sessions

| # | Mechanism |
|---|---|
| 10 | `crew agenda` lists the open items from any host: number, lane, kind (a proposed intent or a question), subject, weight (how many signals, from how many sources, over what span of event dates), and any unit an item holds up. `crew agenda <n>` shows one item with its signals, their excerpts and each excerpt's grade. Nothing is kept by hand: the list is `agenda.rec`, and signals and weight are read from `moves.rec` and the captures. |
| 11 | A session needs no machinery. The user goes to the design agent's pane and names items, or asks for the agenda. The design agent reads only those items with `crew agenda <n>`. |
| 12 | `crew agenda close <n> decided --result <ref>...` closes an item. crew checks that each result exists and cites it: a decision record or intent whose text names `agenda/<n>`, or a unit queued with `--item <n>`, which carries `Source: agenda/<n>`. The planner places those units by proposal. `crew agenda close <n> dropped "<reason>"` is the other ending. |
| 13 | Curation is not in the design agent's brief. It never reads the unmoved signals; it reads the items the user takes up. |

### Plan and bolts

| # | Mechanism |
|---|---|
| 14 | `Goal` is mandatory on a bolt today. What keeps a bolt to it: a conductor's finding outside its unit is a signal and nothing else, and whether new work is a new bolt, a unit in an existing bolt, or queued is a proposal the user reads and approves, with the bolt's goal beside the unit. |
| 15 | A proposal that touches a bolt a team holds needs that bolt's conductor to agree before the user can approve it. crew tells the conductor when the proposal is written; the conductor runs `crew plan agree <n>`, or tells the planner why not. Agreement is then a recorded act. |

**Changing a unit already in the plan** has two forms, and both end in the user's review of the unit's change.

- **What the unit builds stays, and how it builds it changes.** The conductor runs construct again with the user's words (`crew unit run <unit> construct "<the user's words>"`), at any stage before the unit has merged. crew marks the unit amended, and code, verify and merge wait until the user has approved the unit again.
- **What the unit builds changes.** That is a change to its intent, so it is the planner's proposal (`unit amend <unit> "<new intent>"`). Approval rewrites the intent. For a unit in flight, crew marks it amended and tells its conductor, who runs construct again; the unit comes back to review.

**A finding that blocks the unit it was found in** does not wait for curation.

- The conductor asks the user, in its pane, in the words of whoever raised it.
- **A small change amends the unit**, by the first form above. Nothing is added to the plan, so nothing is curated.
- **A big change, or a design question only the user can answer**, goes out: the conductor runs `crew signal ... --blocks <unit>`. crew marks the unit held (`Hold: signals/<id>` in `plan.rec`), in the commit that writes the signal, and refuses its merge while the hold stands. The signal reaches an item by curation, or at once by the user's hand (`crew agenda add`, run on the user's word).
- The hold ends in the same commit as whatever settles the signal. A move that leads nowhere, or an item closed with **a direct answer from design** and no unit, lifts it; crew tells the conductor the result, and the conductor amends the unit with it. An item that yields **a new unit** turns the hold into `After: <that unit>` when an approved proposal puts the unit into the bolt, and crew refuses to merge a unit whose `After` units have not merged.

### Seeing what happened

| # | Mechanism |
|---|---|
| 16 | Every crew command that moves work appends one entry to the run record: who (agent, Claude session, host), what, to what, when, on which host, and the commit it wrote. Shared-record writes pass through two functions in `plan.py` (`write` and `land`), so two hooks cover capture, curation, routing and every bolt and unit write. Stages, approval, tell, greet and restart are recorded where `plugin/bin/crew` runs them. A refusal is an entry too. |
| 17 | The entry is appended to `~/.local/state/crew/<flywheel>/runs/<host>/<date>.rec` on the host where the command ran: a file on disk, never rewritten. `crew events` reads every host of the flywheel, one ssh call each, as `crew bolts` reads the kits. Each host's file is also carried to the same path in the state repository, so a host that is asleep or rebuilt loses nothing. |
| 18 | Each entry names the objects it acted on (`On`) and the objects it came from (`From`). `crew trace <object>` follows those links in both directions and prints the chain in time order. |
| 19 | `crew trace`, `crew events` and the lineage page are pure functions of the entries. Any other view reads the same files (section 4). |
| 20 | Each entry carries the session, its host and the time. `zoe <session>` on that host opens the transcript, and the time finds the place in it, for as long as Claude Code keeps the transcript. |

### Where I would change an invariant

- **3, a reading.** I take "deciding what it means" to be curation. The noticing agent still writes the signal's one-sentence assertion beside the checked excerpt, because it is the only reader that holds the source. Capture-only, with a reader writing the signals later, is the first alternative in section 7.
- **5, reworded**: "A signal never changes. A move is append-only, and each signal has one standing move; only the user replaces it, with a new record that names the one it replaces." Flywheel has the same rule, and without it a wrong move could never be put right.
- **8, two edges.** Amending a unit's change in flight is not reaching the plan, so it needs no curation. And every unit an agent adds names an item, the design agent's included: a design talk the user starts unprompted becomes an item by the user's hand first (the design agent captures the user's words and runs `crew agenda add --lane design --signal <id>`), so every unit traces to words someone said.
- **15, widened.** The user approves every change the planner makes to the plan, a bolt in flight or not, because where work goes is the judgment agents get wrong: a new bolt, a unit in an existing bolt, or a change to a unit already there.
- **16, "ending a stage".** crew cannot watch an agent finish. A stage's end is recorded when `crew unit wait <unit>` returns (it wraps the `herdr agent wait` the conductor already runs), with the stage crew then reads from the kit and the unit branch's head. If the conductor never waits, the next crew command that reads the team records the end and marks it observed late.

## 2. Who does each step

| Step | Who | Standing or per batch | Host |
|---|---|---|---|
| Capture a finding or an aside | any agent crew started: conductor, ops, a stage agent, design agent, planner, main-level ops, operator agent | standing; one command | the agent's own host, where its transcript is |
| Capture the user's own note | the user, `crew signal` at a shell | — | any |
| Capture and read meetings and channels | the daily pass (`signals/bin/sweep`, the `signal-capture` skill) | a job, daily | the Mac that runs it today |
| Start curation | the user's word, carried by any agent or typed at a shell: `crew curate <flywheel>` | — | forwarded to the main level's host, as `crew main` is |
| Curate | **the curator**, a new role (`plugin/roles/curator.md`, Fable 5.1 at high effort) | started for one batch, gone when it has delivered | the main level's host and session, as a `curator` tab of the `<label>` workspace |
| Propose a change to the plan | the planner: `crew plan propose` | standing | main level |
| Agree a proposal that touches a bolt in flight | that bolt's conductor: `crew plan agree` | standing | the team's host |
| Approve a proposal | the user: `crew plan approve`, typed or run by an agent on the user's word, as `crew unit approve` is | — | any |
| Design item to decision | the user and the design agent | standing agent, short session | main level |
| A finding that blocks its unit | the conductor asks the user; amends the unit, or captures with `--blocks` | standing | the team's host |
| Write the run record | crew, inside every command | — | wherever the command runs |
| Gather and show it | `crew events`, `crew trace`, the lineage page | on demand, or a tab that follows | any host |

**Curation is its own pass, not the design agent's.** Four reasons:

1. Invariant 13. A batch is dozens of signals read against the books and the decision records. In the design agent's context it would crowd out the user's design work and be carried into every later conversation.
2. Curation is better stateless. Flywheel's curator has a bounded job and reads only its work order. A fresh session judges each batch against the design as it stands today, not as a long-lived agent remembers it.
3. The curator decides which lane a signal takes. That judgment should not sit with the planner, which would then both admit work and place it (what happened on 2026-10-03), nor with the design agent, whose attention the user is steering in the moment.
4. A bounded session with one validated delivery can be killed and started again with nothing half-written.

The work order is a directory `crew curate` writes on the main level's host: the batch's signal and capture files exported from crew's git cache at the tip (so a lagging checkout does not matter), the open agenda items, the plan's bolts with their goals and its units with their intents, where the standing claims are, and the delivery format. The curator reads the design itself in the main checkouts, read-only. When the delivery lands, crew tells the planner which plan items are waiting. Nobody is interrupted for design items; they are on the agenda.

Curation starts only when the user asks for it. That is enough to prime the flywheel, and running it by hand is what will show the threshold and cadence an automatic trigger should have.

## 3. The records

### Where each lives

| Record | Home | Why there |
|---|---|---|
| Capture and signal from an agent's session, or the user's own note | **the state repository**, `signals/` on the flywheel's branch | The user's words to an agent stay out of the design repository, and a capture, its hold and its entry are one commit. |
| Capture and signal from a meeting or a channel | the flywheel's first blueprints repo, `signals/` on main | Where the daily pass writes them, and where Flywheel Next keeps them. |
| Raw record, transcript | the capturing host, outside git | Invariant 4. |
| Move, agenda item, proposal, plan | the state repository, on the flywheel's branch | One flywheel's judgment and intent, rewritten often, and no part of the design. |
| Run record | the host's disk, carried to the state repository | Written with no network; central once carried. |

crew then keeps nothing of its own in a blueprints repo: no plan branch, no moves, no agenda, no agent's signals, no run record. The one thing it writes there is the daily pass's captures, which it lands on the pass's behalf (`crew signal land`). A signal's id is the same wherever it lives, and crew looks for it on the flywheel's branch first and in the blueprints after.

### The state repository

Flywheel Next gives each instance, which its surfaces call a flywheel, three kinds of repository, each with one owner. The blueprints are the design, written by people and sessions. The built repositories are their owners'. The **state repository** (`<instance>/flywheel-state`) is the machinery's alone: one record file per object on `main`, the run record at `runs/<host>/<date>.rec`, every write a commit that carries its reason, and leases and heartbeats on branches of their own so that `main`'s history stays the audit record. One instance has one state repository, and a host runs several instances with nothing crossing between them.

crew's interim version keeps that shape and puts several flywheels in one repository:

- **One state repository per organisation, named `crew-state`**: `WilldanGroup/crew-state` for wldn. A partition names it in the teams file (`state`), beside its `blueprints`.
- **One branch per flywheel, `<flywheel>/main`**: an orphan line that holds that flywheel's files and no one else's.

  ```
  wldn/main
    plan.rec                  bolts and units
    proposals.rec             the planner's proposals
    agenda.rec                items
    moves.rec                 moves
    signals/<capture>/        captures and signals from agents' sessions
    runs/<host>/<date>.rec    the run record
  ```

- **Written only through crew**, by the path the plan uses today: fetch the branch, apply the write to the tip, check it with `recfix` and crew's rules, push without force, apply again when someone pushed first. Nothing is merged.
- **One commit may change several files.** A curator's delivery writes its moves and its items together; an approval changes the plan and closes the proposal and its items; a blocking signal and the hold it places land together. No reader sees one without the other. Each commit's message names its run-record entry.

**How flywheels stay separate.** A branch per flywheel gives each its own history, which is that flywheel's audit record and nobody else's. No flywheel's push can be refused because another wrote, crew's cache fetches one ref, and nothing in one flywheel's files names another's. Two people working for one client are two partitions: each has its own label, main level, teams and branch. They share the blueprints, with its meeting signals, and the kits. They keep separate moves, agendas, proposals, plans and run records, so each curates the same evidence in their own way.

**What a branch cannot do is hide.** GitHub grants read access per repository, so everyone who can read the state repository reads every flywheel in it, which is accepted. A flywheel that must one day be private gets a state repository of its own: push its branch there as `main`, history intact. That repository is then laid out as Flywheel Next's is, one instance to one state repository with `main` as the shared line. So the branch namespace is the interim, and the move to Flywheel's layout is one push per flywheel.

**Getting there.** `plan/<label>` holds only `plan.rec`, so pushing it to the state repository as `<label>/main` carries the plan with its history. `moves.rec` goes over with its records.

crew differs from Flywheel's layout in four ways: one file per record set, not one per object, because crew applies a write to the new tip again where Flywheel rebases a one-file commit; no leases or heartbeats, because no engine holds anything; moves beside the plan, where Flywheel keeps them in the blueprints with the signals, because two flywheels may share one blueprints repo and a move is one flywheel's judgment; and an agent's signals in the state, where Flywheel puts every signal in the blueprints.

### What crew reads of a transcript

crew reads the transcript to check an excerpt and to copy the record that holds it. It leans on the format as little as it can.

| Grade | When | What the capture records |
|---|---|---|
| `verified` | the excerpt is in a record the session received | the record's id and time, and who asserted it: the user, a tool, or another agent |
| `found` | the excerpt is in the session's file, but crew cannot tell what kind of record holds it | the line, banked |
| `unverified` | herdr names no session, the file is missing, its lines are not JSON, or crew cannot find its own command in it | the reason |
| refused | crew finds its own command in the file, and the excerpt nowhere else | nothing is written |

- Only `verified` knows anything of Claude Code's format, and it knows one fact: a top-level `type` of `user` marks a record the session received. `found` and the refusal need only that each line is JSON; crew searches every string in it, whatever its place.
- The refusal has a canary. The command that is running is in the transcript, so if crew cannot find it there, crew cannot read this transcript, and the capture is written `unverified`. A change of format therefore lowers the grade. It cannot refuse a true excerpt, and it cannot stop a capture.
- Nothing downstream is gated on the grade. It is shown beside the excerpt wherever the excerpt is shown, and the curator weighs it.
- `crew tell` marks what it sends (`[crew tell from <agent>]`), so words another agent sent are not taken for the user's.

This is a much narrower dependency than writing transcripts for another tool to read (section 4). Writing means getting right, and keeping right, every field someone else's parser interprets. The check reads one fact, falls back to none, and says which it did. crew reads the same files already, for the context use and compactions `crew status` shows.

### Shapes

**Capture**: `signals/<event date>-<agent>-<record id, first 8>/capture.md`.

```markdown
---
capture: 2026-10-05-swb-2-conductor-9f2c1a7e
source: crew-session
key: session/3f0c2d1e-…/9f2c1a7e-…
captured_by: swb-2-conductor
host: chuck-herdr-alpha
session: 3f0c2d1e-…
record: 9f2c1a7e-…
at: 2026-10-05T14:21:07Z
excerpt: verified
asserted_by: user
where: team swb-2, bolt smoke-2, unit cfn-lint-treefmt
blocks: cfn-lint-treefmt          # only with --blocks
raw: chuck-herdr-alpha:~/.local/state/crew/wldn/raw/2026-10-05-swb-2-conductor-9f2c1a7e.jsonl
event_date: 2026-10-05
imported: 2026-10-05
status: read
signals: 1
---
```

**Signal**: `signals/<capture>/NN-<slug>.md`, the shape the blueprints' `signals/README.md` gives, the excerpt always present.

```markdown
---
signal: 2026-10-05-swb-2-conductor-9f2c1a7e/01-cfn-nag-templates
kind: ask
who: user
subject: [cloudformation, security]
---

The user wants a security check on Switchboard's CloudFormation templates beside cfn-lint's validity check.

> "<the user's words, verbatim>" — 14:21:07Z
```

**Move**: `moves.rec`. The six words are Flywheel's, so `join` stands where `signals/README.md` says `new-territory`; no record uses that word yet. `revive` is the user's "unmoved again". A `route` or `join` targets `agenda/<n>`.

```
%rec: Move
%key: Id
%type: Id int
%type: Move enum attach challenge join answered route drop revive
%type: Date date
%mandatory: Id Signal Move Date By
%allowed: Id Signal Move Target Reason Date By Replaces
```

**Agenda item**: `agenda.rec`. Items are never removed and numbers never reused, so a citation always resolves.

```
%rec: Item
%key: Item
%type: Item int
%type: Lane enum plan design
%type: Kind enum intent question
%type: State enum open planned decided dropped
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

A design item's subject says what is unsettled, never the answer (Flywheel's rule for an intent proposal). A plan item's subject says what was asked for, in the asserter's terms. An item's signals are not stored on it: they are the standing moves that target it. `State`, `Closed`, `Result` and `Lane` are the only fields crew rewrites; the branch's history and the run record keep what they were.

**Proposal**: `proposals.rec`. A proposal is the planner's case and the plan commands it would run, in order. Approval runs them as one commit. Proposals are never removed.

```
%rec: Proposal
%key: Proposal
%type: Proposal int
%type: State enum open approved dropped
%mandatory: Proposal Case Do State Opened By
%allowed: Proposal Case Do Agreed State Opened By Closed Reason Replaces

Proposal: 3
Case: Two findings from swb-2 are both about checking CloudFormation templates. smoke-2 is close to landing and
+ its goal is the bolt loop, so they start a bolt of their own.
Do: bolt new cfn-checks "Switchboard's CloudFormation templates are checked for security as well as validity" --repo switchboard-kit
Do: unit add cfn-nag-security-check "Switchboard's CloudFormation templates get a security check beside cfn-lint's validity check" --item 8 --bolt cfn-checks
Do: unit move retire-suite-cfn-lint cfn-checks
State: open
Opened: 2026-10-06
By: wldn-planner
```

**Plan**: `plan.rec` as today, with two marks a unit may carry: `Amended` (its change was written again and waits for the user's review) and `Hold` (the signal that blocks its merge).

**Curator's delivery**: one recutils file of `Move` records and new `Item` records, the items under local names that crew replaces with numbers. Delivering it again writes nothing.

**Run-record entry**: section 4.

### Commands, new or changed

```
crew state init <flywheel>
crew signal <slug> "<what it asserts>" --excerpt "<verbatim>" [--kind K] [--subject a,b] [--blocks <unit>]
crew signal show <id>
crew signal move <id> <move> [--target T] [--reason R] [--replace "<why>"]
crew signal revive <id> "<why>"
crew signal land <capture-dir>
crew curate <flywheel> [--only <capture>...]
crew curate deliver <file>
crew agenda [<n>] [--lane plan|design] [--json]
crew agenda add "<subject>" --lane plan|design --signal <id>... [--kind intent|question] [--repo <kit>]
crew agenda lane <n> design "<the decision it needs>"
crew agenda close <n> decided --result <ref>... | dropped "<reason>"
crew plan propose <file> [--replaces <n>]      crew plan proposed [<n>]
crew plan agree <n>      crew plan approve <n>      crew plan drop <n> "<reason>"
crew unit add <unit> "<intent>" --item <n>|--signal <id> ...
crew unit amend <unit> "<new intent>"          (in a proposal)
crew unit release <unit> "<why>"               crew unit wait <unit>
crew events [--about <object>] [--since T] [--follow] [--push] [--json]
crew trace <signals/id|agenda/n|proposal/n|unit/u|bolt/b>
crew page <flywheel>
```

`crew agenda add`, `crew signal move` and `crew signal revive` are the user's hand: Flywheel counts a person writing curation's records as curation.

## 4. How events are seen

### The entry

```
Id: 20261006T140210Z-chuck-herdr-alpha-48213-1
At: 2026-10-06T14:02:10Z
Host: chuck-herdr-alpha
By: wldn-planner
Session: chuck-herdr-alpha:7be1…
Act: plan.propose
On: proposal/3
On: unit/cfn-nag-security-check
On: bolt/cfn-checks
From: agenda/8
Commit: WilldanGroup/crew-state@4119bf25
Why: plan(proposal 3): propose a new bolt cfn-checks with 2 units
```

- The format and the path are Flywheel's run record: recutils, `runs/<host>/<date>.rec`. recutils is already on every host, so the record can be read with `recsel` and nothing else: `recsel -e "On = 'unit/cfn-nag-security-check'" runs/*/*.rec`.
- `Host` is where crew ran; `By` is who asked, and `Session` the host and Claude session herdr reports for that agent at that moment. When crew forwards a command over ssh it carries the session as it carries `CREW_AGENT` today. For the user at a shell, `By` is `<user>@<host>` and there is no session.
- `On` and `From` hold typed names: `signals/`, `agenda/`, `proposal/`, `unit/`, `bolt/`, `queue/`, `team/`, `agent/`, `stage/<unit>/<stage>`.
- `Why` is the subject crew itself composes. A `tell` entry records sender, recipient and length, never the text; the text is in both transcripts.
- `Refused`, when present, holds crew's reason. A refused write is otherwise invisible, and it is often the interesting line.

| `Act` | Recorded by |
|---|---|
| `capture` | `crew signal`, `crew signal land` |
| `curate.start`, `curate.deliver`, `signal.move` (one per move, sharing the delivery's commit), `signal.replace` | `crew curate`, `crew signal move`, `crew signal revive` |
| `agenda.add`, `agenda.lane`, `agenda.close` | the delivery, `crew agenda …` |
| `plan.propose`, `plan.agree`, `plan.approve`, `plan.drop` | `crew plan …` |
| `unit.add`, `.amend`, `.split`, `.order`, `.after`, `.move`, `.hold`, `.release`, `.drop`, `.approve` | `crew unit …`, an approval, `crew signal --blocks`, and whatever settles a hold |
| `bolt.new`, `.order`, `.give`, `.drop`, `.land` | `crew bolt …`, an approval |
| `stage.start`, `stage.end`, `fix.start`, `fix.merge` | `crew unit run`, `crew unit wait`, `crew fix` |
| `tell`, `greet`, `agent.start`, `.restart`, `.resume`, `.clear`, `.stop`, `team.up`, `.down`, `.rebuild`, `.close` | `crew tell` and the team and main-level commands |

### Where it is written, and how it is gathered

Written: one append to the host's own `runs/<host>/<date>.rec`, after the command has done its work, so the entry can name the commit. No network, no lock, and a failed append never fails the command it describes.

Carried: every write crew makes to the flywheel's branch also brings `runs/<host>/` on the branch up to what that host has recorded. One file per host means two hosts never write the same file. An entry for a command that wrote no commit (a tell, a stage start) rides with the host's next write, or with `crew events --push`.

Gathered: `crew events` reads the branch, then asks each host it can reach for the entries it has not yet carried, one ssh call each. A host that does not answer is named, as `crew bolts` names one, and the view is complete up to that host's last push. `--follow` holds a `tail -F` open on each host.

### Views

| View | What it shows | Cost | Judgment |
|---|---|---|---|
| **`crew trace`, `crew events --follow`** (text) | Trace: one object's chain, signal to item to proposal to unit to bolt to landing, each line with who, when, commit and the `zoe` session to open. Follow: the flywheel's entries as they happen, in a `flow` tab of the operator workspace the user can leave open. | Small; Python in crew. | **First.** It answers invariant 18 as asked, by object, and it is the reference any richer view is checked against, as `zoe inspect` is for zoetrope. |
| **The lineage page** (`crew page`) | Signals, items, units and bolts as columns with the links between them, a timeline under them, and each node opening its entries. One self-contained HTML file generated from the run record. | Moderate; no service. | **Second.** It draws the thing invariant 18 asks about. |
| **zoetrope, unchanged, on Claude transcripts** | The detail behind one entry: that agent's session, scrubbed to the entry's time. Its herdr plugin already opens the focused pane's session. | Install only. | **Use from the first step**, for invariant 20. This is the job it was built for. |
| **A zoetrope provider for the run record** | A live graph whose nodes are crew's agents, with a team or bolt as a group and each crew command as a tool chip, over zoetrope's scrubbable timeline. | A Rust provider directory (wire model, discovery, stream, golden fixtures), upstream or in a fork, and a line-per-entry export, since zoetrope tails JSON lines. | **Not planned.** zoetrope draws agents, "not messages". It would show who is working and who told whom. It would not show what a signal led to, because work objects are not nodes in its model. |
| **Entries written as Claude-format transcripts** | The same graph, with zoetrope unchanged. | A generator in crew, and its upkeep. | **No.** It counterfeits a format zoetrope's own README calls undocumented and liable to change, so crew would track both Claude Code's format and zoetrope's reading of it. The mapping is false in the particulars zoetrope trusts: crew commands posing as tool calls, standing agents as subagents with spawn acks, and liveness rules that mark an agent idle after two minutes. It still would not show lineage. |

An OpenTelemetry trace viewer and Datasette would both read these entries too. Each wants a service running, which crew has none of, so neither is proposed.

## 5. Against Flywheel Next

| Flywheel Next | crew, in this proposal | |
|---|---|---|
| A capture is one keyed source event with a pointer to raw material outside version control; twice yields one | The same. An agent's source event is one record of its session; raw is banked on the host | same |
| Enumerators run unattended; a capture-reader session reads a capture into signals | The daily pass does both for meetings. For an agent's capture the capturer writes the signal and crew checks the excerpt | simpler: no reader for a one-record source |
| A session's finding is a signal of kind ask whose assertion is a document's path and whose excerpt is empty, pinned at a revision | A finding is a signal with a checked excerpt; there is no finding document and no pin | differs, because invariant 2 requires an excerpt |
| A signal: capture, kind of five, asserter, tags, assertion, excerpt with position, claims; immutable | The same | same |
| Six moves, one standing per signal; only the operator's response replaces one | The same six words; one standing; `--replace` and `revive` are the user's | same |
| Curation: a bounded session, charged by cadence, threshold or the operator's word; never opens an intent; one commit; a person by hand is also curation | The curator, per batch, on the user's word alone; one commit; `crew agenda add` and `crew signal move` are the hand | same, less the automatic triggers |
| `join` makes or grows a proposed intent, shown with its weight, one decision per proposal | `join` makes or grows a design item, shown with its weight | same shape |
| The planner writes one proposal, the case for a batch and its units; nothing is created until the operator approves it | The planner writes a proposal, its case and the plan commands it would run; the plan changes when the user approves it | same shape |
| A finding about the session's own bolt is a proposal on that thread, not a signal | A finding that blocks its own unit is the conductor's question to the user, and a small change amends the unit | same shape |
| An intent is worked by typed elaborations, one awaiting approval at a time | A design item is settled in a session with the design agent | simpler: no intent object, no elaboration types |
| The rail: decisions derived from active states, each with a number never reused | `crew agenda` and `crew plan proposed`: read from `agenda.rec`, `moves.rec` and `proposals.rec`; numbers never reused | simpler |
| One state repository per instance, the machinery's alone; `main` the shared line; one file per object; leases on branches of their own | One state repository per organisation, written only through crew; one branch per flywheel; one file per record set; no leases | interim: a flywheel's branch pushed as `main` of its own repository is Flywheel's layout |
| Captures, signals and moves in the blueprints, under the machinery's prefix | Meeting captures and signals in the blueprints' `signals/`; an agent's captures and signals, and every move, in the flywheel's state | differs: a move is one flywheel's judgment, and the user's words to an agent stay out of the design repository |
| The run record at `runs/<host>/<date>.rec`; every write a commit that carries its reason and evidence; refusals recorded | The same path and format; one entry per command, naming the commit when there is one; refusals recorded. Entries reach git with the host's next write, not one commit each | close: half of crew's acts (a tell, a stage start, a restart) write no commit of their own |
| The status view is central and readable with nothing running | `crew bolts` for state; the run record on the flywheel's branch, readable with `recsel` from a clone | partial |
| The tick, leases, host declarations, claims and verdicts, chores | None. Agents run crew's commands | not built |

What running crew this way would show about Flywheel's model:

1. **What the operator's yes on a plan proposal is worth, and on which part.** Count how often an approval changes anything, and what: an intent reworded, a unit put in a different bolt, a new bolt turned into a unit of an existing one, an item sent to design. That says where a planner's judgment needs a person and where the rail carries a decision it could do without.
2. **What threshold and cadence should be.** crew curates only when asked. How many signals are waiting each time, how old the oldest is, and what share lands as `answered`, are the numbers Flywheel leaves to the manifest.
3. **Where "small" ends.** How often a blocking finding amended in place should have gone to design, how long holds last, and how often a hold ends in a direct answer and how often in a new unit. That tests Flywheel's rule that a finding on its own thread never becomes a signal.
4. **Whether an excerpt on a session's finding earns its cost.** Flywheel leaves it empty and points at a document. See how often the curator can judge from the excerpt and assertion alone, and how often it goes back to the raw record.
5. **How often a move has to be replaced.** That says how much of Flywheel's revive and split machinery real work uses.
6. **Whether weight is what the user chooses by.** Which agenda items get taken up first, against their signal counts, sources and span.
7. **What the run record must carry.** Whether the questions the user asks are by object or by actor, and how much of "what happened" lives in acts that are not writes. Flywheel records writes; crew will show what a write-only record would miss.
8. **Whether a curator apart from the design session loses anything.** The design agent meets an item knowing only its subject and signals. If sessions keep reopening what the curator already read, Flywheel's hand-off from curation to elaboration needs more than the proposal.
9. **Where signals and moves belong, and how much isolation a flywheel needs.** Whether signals in two homes cost the curator anything, whether two flywheels on one blueprints repo move the same meeting signal differently, and whether a branch is enough separation in practice or each flywheel ends up wanting its own repository, which is Flywheel's rule.

## 6. Steps

Nine OpenSpec changes in crew, built in this order after `bolt-teams` is archived. `roadmap.md` gives each one's dependencies, what it needs outside crew, what the user decides, and how it is proven.

1. **`run-record`**: the run record, `crew events` and `crew trace`, and the `flow` tab that follows them. It changes no record and no rule, and from that day what happens to a bolt, a unit or a signal can be read without asking an agent.
2. **`state-repository`**: `crew state init`; every partition's plan and moves go to its branch of its organisation's `crew-state`, with their history; each write carries the host's run record with it.
3. **`plan-proposals`**: the planner changes the plan only by a proposal the user approves, with the conductor's recorded agreement for a bolt in flight.
4. **`unit-amendments`**: a unit in flight goes back through construct and the user's review, on the conductor's word for its change and by an approved proposal for its intent.
5. **`checked-capture`**: `crew signal` requires the excerpt, grades it, writes the capture with its provenance on the flywheel's branch and banks the record.
6. **`curation-and-agenda`**, which proves the flow: the curator, `crew curate` and its delivery, the agenda with both lanes' ends, the replacement of a move, and the briefs.

   The proof is one run. A conductor captures an aside from the user and a finding from a tool's output. The user says "curate now". The curator routes one and joins the other. The planner proposes a unit from the first and where it goes, and the user approves it. The user and the design agent settle the second, and a decision record and a unit cite the item. Then `crew trace` on each signal prints the whole chain, each line naming a session and a time, with no agent asked. `--only` matters because wldn has 192 unmoved signals from meetings (194 in 15 captures, two moved); the proof should not be their first curation.
7. **`blocking-findings`**: `--blocks`, the hold, `After` checked at merge, and the conductor's brief for a finding that blocks its unit.
8. **`lineage-page`**: `crew page`.
9. **`daily-pass-through-crew`**: the daily pass lands its captures by crew's path, so they leave entries.

Two things in the roadmap are not changes: the first full batch over wldn's 192 meeting signals, which is one `crew curate` when the user chooses; and an automatic trigger for curation, which waits for the numbers that running it by hand will show.

## 7. Alternatives considered

- **Capture only, and a reader writes the signals later**, as Flywheel does for a transcript. It is the stricter reading of invariant 3. Set aside for agent sources: the raw record is on the capturing host, so a reader elsewhere needs a way to fetch it, and each finding would cost a second session to restate one sentence. Worth revisiting for a long exchange with the user, where one capture holds many signals.
- **Refuse any excerpt crew cannot verify.** Simpler to state, and it would turn a change in Claude Code's transcript format into a day with no captures.
- **Trust the agent's excerpt, with no check.** The paraphrase problem is that the agent's words stand in for the user's; only a look at the transcript closes it.
- **The design agent curates**, as its brief says today. Against invariant 13, and for the reasons in section 2.
- **The planner curates.** It would admit work and place it, with nobody between a finding and the queue. That is 2026-10-03.
- **The curator adds the unit itself.** One step fewer, but Flywheel's curator judges and does not act, and the planner would stop being the only agent that shapes the plan.
- **A proposal as prose the planner writes, applied by the planner after a yes.** What the user approved and what was then run could differ. A proposal that is the commands themselves is applied by crew, exactly as read.
- **Approval applies each change of a proposal as its own commit.** A refusal halfway would leave the plan half-changed, with a bolt created and its units not in it.
- **Items and outcomes as two append-only record sets**, with a lane change as a new item pointing at the old. Purer, and three record sets to read where one does. `agenda.rec` is state, like `plan.rec`; history is the branch's and the run record's.
- **The agenda as GitHub issues, or as a page the design agent keeps.** The first leaves the path crew writes by, and Flywheel's git-only profile never reads issues. The second is kept by hand.
- **A state repository per flywheel from the first day**, Flywheel's exact layout. A repository to create and grant for every partition, and a second one the day a second person joins a client. The branch namespace gives the same files and the same history, and becomes this by one push.
- **One branch for every flywheel, a directory each.** Every flywheel's pushes would contend for one ref, their histories would interleave, and taking one out later means rewriting history.
- **State on branches of the blueprints repo**, as `plan/<label>` is today. It puts the machinery's frequent writes and its branches in the design repository, and ties a flywheel's state to one blueprints repo when a partition may have two.
- **Every signal in the blueprints**, Flywheel's placement. The user's asides to agents would sit in the client's design repository, a blocking signal and its hold would be two commits in two repositories, and crew would go on writing to the design repository's main while people work in it.
- **Each run-record entry as its own commit**, Flywheel's way. A push for every tell and every stage start is slow, and an entry cannot name the commit that carries it. Entries are written on the host and carried with its next write.
- **No log: a tool reconstructs events from transcripts and git logs.** It automates what an agent does by hand today, on a transcript format nobody documents and files Claude Code cleans up.
- **A Claude Code hook that logs every `crew` command.** A hook sees a command string. crew knows the act, the objects and the commit.

## 8. Open questions

1. **Where meeting signals live.** An agent's signals are in the flywheel's state; a meeting's stay in the blueprints' `signals/`, where the daily pass writes them and decision records already cite them. The curator reads both. Should the daily pass follow, so that every signal has one home and crew never writes to a blueprints repo at all? `daily-pass-through-crew` is written for the blueprints and would change if so.
2. **The state repository for madswan and swancloud.** `afterthought/crew-state` is proposed for both, as branches `madswan/main` and `swancloud/main`. madswan's work also reaches agentplot's blueprints and kits; one flywheel has one state repository, so its agentplot work would be planned in afterthought's.
