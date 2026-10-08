> An exploration's plan (2026-10-03): the build order of the findings-to-design changes only; the partition's plan orders every change. Steps 0 to 5 are built; later ADR-driven changes are not listed here.

# Findings to design: the roadmap

Every change that builds `proposal.md`, in build order. Each is an OpenSpec change in this repository, `openspec/changes/<name>/`, with its proposal, specs, design and tasks, written to be built by an agent that has read nothing else. `brief.md` holds the invariants the whole thing answers to.

## The order

| # | Change | Depends on | Usable once it lands |
|---|---|---|---|
| 0 | archive `bolt-teams` | its tasks 7.2 and 7.3 | crew's specs exist in `openspec/specs/` for the changes below to modify |
| 1 | `run-record` | 0 | what happened to a bolt, unit or signal can be read without asking an agent |
| 2 | `state-repository` | 1 | the plan, the moves and the run record live in `crew-state`, a branch per flywheel, and no checkout of the blueprints lags because of crew |
| 3 | `plan-proposals` | 2 | the planner changes nothing in the plan until the user approves it |
| 4 | `unit-amendments` | 3 | a unit already in a bolt can be changed, and comes back to the user's review |
| 5 | `checked-capture` | 2 | a signal carries the words actually said, checked, and the user's asides stay out of the design repository |
| 6 | `curation-and-agenda` | 3, 5 | the flow runs end to end: signals are curated, the agenda exists, both lanes reach the plan |
| 7 | `blocking-findings` | 4, 5, 6 | a finding that blocks its own unit holds the unit until what came of it has merged |
| 8 | `lineage-page` | 1, 2 (richer after 3 and 6) | the flow as one page |
| 9 | `daily-pass-through-crew` | 1, 5 | meeting signals reach git by crew's path and appear in the trace |

Changes 2 to 7 and 9 all change `plugin/lib/plan.py`, and 3 to 7 change the same briefs, so they are built one after another, never side by side. 5 does not depend on 3 or 4 and could be built before them; it is placed after because the user's approval of plan changes is the more pressing gap. 8 can be built any time after 2.

Each change's delta specs are written against the specs as they will stand once the changes before it are archived. So a change is archived when it has landed and been proven, before the next is archived. `openspec validate <name>` passes for all nine today, and notes for most that a MODIFIED delta cannot be archived until its target spec exists; that is this ordering, not a defect.

The user reviews every change in full, in plannotator, before it is built. Reviewing them in this order means each is read with the ones it rests on already settled.

## How the changes follow the proposal's steps

The steps the user reviewed became these changes:

| Step as reviewed | Change |
|---|---|
| the run record and `crew trace` | `run-record` |
| the state repository | `state-repository`, which also takes "the other partitions": every partition's state moves in its rollout, because crew cannot read some plans from the blueprints and others from the state |
| the checked capture | `checked-capture` |
| curation and the agenda; the two lanes' ends | `curation-and-agenda` for curation, the agenda and both lanes' ends; `plan-proposals` for the user's approval of the planner's changes, split out and moved earlier because it stands without curation |
| bolts | the conductor's agreement is in `plan-proposals`; changing a unit in flight is `unit-amendments`; the hold is `blocking-findings` |
| the lineage page | `lineage-page` |
| the daily pass through crew | `daily-pass-through-crew` |

Two things the steps named are not changes. They are at the end of this document.

## 0. Archive `bolt-teams`

- **Open tasks.** 7.2: `crew main up` for each partition and `crew operator up` in each operator session, verified by each agent being listed in its workspace. 7.3: move swb-1: plan its first bolt with the planner, `crew bolt give swb-1`, `crew up swb-1` on the box, verified by `crew bolts` showing the bolt active on `chuck-herdr-alpha`. `plan/wldn` already shows `smoke` held by swb-1 and `smoke-2` by swb-2, so 7.3 may need only its verification and its tick.
- **Then** `openspec archive bolt-teams`, which creates `openspec/specs/` for `agent-models`, `bolt-plan`, `bolt-teams`, `crew-sites`, `main-level` and `operator-agent`.
- **The user decides** that the bolt model is proven enough to archive.
- **Proof:** `openspec list --specs` lists the six capabilities.

## 1. `run-record`

- **What it is.** Every crew command that moves work appends an entry (who, session, act, objects, commit) to a recutils file on its host. `crew events` gathers them over ssh; `crew trace <object>` prints one object's history; `crew unit wait` records a stage's end; a `flow` tab in the operator workspace follows the record.
- **Outside crew.** Optional: swancloud adds zoetrope (`zoe`) and its herdr plugin to each host, to open the session an entry names.
- **The user reviews** the change. Nothing to decide.
- **Proof.** One unit of swb-2's bolt taken through a stage and approved; `crew trace unit/<unit>` on mac-studio shows it, each line naming an agent, a host and a session; a tell's text is in no run-record file.

## 2. `state-repository`

- **What it is.** `crew state init`; each partition names a `state` repository; its flywheel's plan, moves and run record are files on `<label>/main` there; one write may change several files in one commit; the run record is carried with every write.
- **Outside crew.**
  - GitHub, with the user's go: create `WilldanGroup/crew-state` and `afterthought/crew-state`, private and empty; afterwards delete `plan/wldn`, `plan/madswan` and `plan/swancloud` from the blueprints repos.
  - swancloud: `state` for every partition in `lib/crew-teams.nix`, carried in the teams file published to each host (`lib/herdr-published.nix`); the box's GitHub token helper must reach the state repositories.
  - Each blueprints repo: `signals/README.md` says moves and the plan live in the state; `signals/moves.rec` and its `.gitattributes` line go.
- **The user decides** that `afterthought/crew-state` holds both `madswan` and `swancloud`, and when every team is idle for the move.
- **Proof.** `git log` of `wldn/main` reaches the plan's first commit of 2026-10-02; `crew bolts` shows the same bolts and stages as before, from both hosts; a plan write from each host is one commit with a `Crew-Entry` trailer; a clone of the branch reads with `recsel`.
- **Rollout note.** Every host pulls crew together. A crew from before this change still writes `plan/<label>`.

## 3. `plan-proposals`

- **What it is.** The planner's direct plan writes are refused. A proposal is its case and the plan commands it would run; `crew plan proposed <n>` prints it for the user, with each unit's intent beside the goal of the bolt it would join; a conductor whose bolt it touches runs `crew plan agree`; `crew plan approve` applies it in one commit. Other agents write the plan only within their own job.
- **Outside crew.** Nothing.
- **The user reviews** the change, and from then on approves every proposal.
- **Proof.** wldn's planner asked to place the queued units writes a proposal and not the plan; a proposal touching a held bolt cannot be approved before its conductor agrees; an approval is one commit; a replaced proposal shows in `crew trace proposal/<n>`.

## 4. `unit-amendments`

- **What it is.** Construct can be run again on a unit at any stage before merge; the unit is marked amended, code, verify and merge wait, and `crew unit approve` clears the mark. `crew unit amend`, inside a proposal, changes a unit's intent, and for a unit in flight hands it to its conductor to run construct again.
- **Outside crew.** Nothing.
- **The user reviews** the change.
- **Proof.** A unit in code amended on the user's word returns to review and cannot be coded until approved again; an intent amended by an approved proposal reaches the conductor, who runs construct again unprompted by the user.

## 5. `checked-capture`

- **What it is.** `crew signal` requires the excerpt, looks for it in the agent's transcript, and grades it `verified`, `found` or `unverified`; it refuses only a paraphrase. A capture is one record the session received, with its host, session, time and where the agent was working; the record is banked on the host. An agent's signals are written to the flywheel's branch. `crew signal show`; `crew tell` marks what it sends.
- **Outside crew.** The blueprints repos' `signals/README.md` says where an agent's signals live and documents the capture fields crew writes.
- **The user reviews** the change.
- **Proof.** An aside to a conductor is recorded with the user's exact words, `verified`, on `wldn/main`, with willdan-blueprints untouched; a finding "in its own words" is refused; the raw record on the box is the one transcript line.
- **First task is a probe**: whether the running `crew signal` command is already in the transcript when crew reads it. The design's canary depends on it, and gives the fallback if it is not.

## 6. `curation-and-agenda`

- **What it is.** The curator role (Fable 5.1, high effort) and `crew curate`, on the user's word, with its work order and one-commit delivery. Flywheel's six moves, each with a reason. Agenda items in two lanes; `crew agenda` with weight; `add`, `lane`, `close`. Units name their item with `--item`; a plan item becomes a unit inside a proposal; a design item is closed with the decision records and units that cite it. A noticing agent captures and tells nobody. The user replaces or revives a move.
- **Outside crew.** The blueprints repos' `signals/README.md`: `join` in place of `new-territory`, the lanes, where moves and items live, how curation runs. The `signal-capture` skill's sentence about curation's moves follows.
- **The user reviews** the change, and decides when to run the backlog batch (below).
- **Proof, which proves the flow.** A conductor captures a plan-ready aside, a design question and a tool finding. The user says to curate those captures. The curator routes one and joins another, in one commit, and only the planner is told. The planner proposes a unit from the plan item, with the user's words on the proposal's page, and the approval closes the item. The user and the design agent settle the design item, with a decision record and a queued unit that cite it. `crew trace` of each signal prints the whole chain, with no agent asked.

## 7. `blocking-findings`

- **What it is.** The conductor asks the user about a finding that blocks a unit; a small change amends the unit. A large one, or a question for design, is `crew signal … --blocks <unit>`, which holds the unit from merging. The hold lifts with a direct answer, or becomes `After` the new unit when that unit enters the bolt; `After` is checked at merge. `crew unit release` on the user's word.
- **Outside crew.** Nothing.
- **The user reviews** the change.
- **Proof.** A small finding is amended with no signal; a held unit's merge is refused; a direct answer from design lifts the hold and the conductor amends the unit; a finding answered by a new unit makes the held unit wait for it, and the trace shows the detour.

## 8. `lineage-page`

- **What it is.** `crew page <label>` writes one self-contained HTML file: signals, items, proposals, units and bolts in columns with their links, a timeline, and each object's history. Links come from the run record alone, by the walk `crew trace` uses.
- **Outside crew.** Nothing.
- **The user reviews** the change, and may want to see the page's layout before it is built.
- **Proof.** After the flow's proof, the page shows each signal's line through to its unit; a unit's history on the page is what `crew trace` prints; a page made with the box unreachable names the box.

## 9. `daily-pass-through-crew`

- **What it is.** `crew signal land <capture-dir>` checks a capture directory and writes it to the blueprints repo's main by crew's path, leaving `capture` entries. A landed signal is never changed.
- **Outside crew.** willdan-blueprints, as one reviewed commit: `signals/.work/` in `.gitignore`; the `signal-capture` skill writes there; `signals/bin/sweep` lands each capture and pulls, and commits nothing itself; the README. The Mac that runs the launchd job needs `crew` on the job's `PATH`.
- **The user decides, before it is built,** whether meeting signals stay in the blueprints or follow an agent's signals to the state repository (`proposal.md`, section 8). The change is written for the blueprints; the other answer changes where `crew signal land` writes and nothing else.
- **Proof.** A morning's pass lands by crew's commits with a clean checkout afterwards; a meeting signal's trace begins with its capture.

## Not changes

- **The backlog batch.** wldn has 192 unmoved meeting signals. Curating them is `crew curate wldn`, once or capture by capture with `--only`, after change 6 has been proven on fresh signals. The user chooses when. Most should land as `answered`.
- **An automatic trigger for curation.** Curation runs on the user's word. A threshold and a cadence are not specified, because running it by hand is what will show the numbers: how many signals wait each time, how old the oldest is, and what share lands as `answered`. When the user wants it, it is a small change to `curation`: `crew curate --if-due`, called by the daily pass.

## Not settled

- **Where meeting signals live** (decides the target of change 9).
- **The state repository for madswan and swancloud**: `afterthought/crew-state` is assumed in change 2.
- **swancloud's side** is named from the user's description (`lib/crew-teams.nix`, `lib/herdr-published.nix`); swancloud was not read for this work, so its own change for the `state` field is still to be written there.
- **Whether the running command is in the transcript when `crew signal` reads it**: change 5's first task finds out.
- **Which Mac runs the daily pass**: change 9's rollout names it.
