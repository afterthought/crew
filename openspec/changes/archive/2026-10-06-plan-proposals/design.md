# Design

## Context

See proposal.md for why. The current state, after `bolt-teams`, `run-record` and `state-repository`:

- A flywheel's plan is `plan.rec` on `<label>/main` of its state repository. Every write is `plan.py`'s `write(fleet, label, change, subject)`: fetch the tip, run `change` on the state there, check, commit, push without force, run again on a refused push. A write may replace several files in one commit.
- Each plan command (`bolt_new`, `unit_add`, `unit_move`, …) is a function that does its own checks first (some read the kits on a team's host: a unit's stage, whether a name is free), then calls `write` with a closure, then runs what follows the write (freeing a slot, a rebase's undo, telling conductors and dispatchers).
- crew knows who is calling: `CREW_AGENT` is the agent's name (`<label>-planner`, `<label>-design`, `<team>-conductor`, `<label>-dispatch-<host>`, `<label>-ops`, `<team>-ops`, `<team>-unit-<n>`, `<label>-operator-<host>`), unset for the user at a shell.
- The briefs already say who writes what: the planner is "the only agent that creates bolts, puts units into bolts, and splits, orders or moves units between bolts"; the conductor narrows, orders and sets dependencies within its bolt; the design agent queues. Nothing in the code enforces it.
- The planner's brief has it agree a change to a bolt in flight with the conductor by `crew tell` and wait for an answer. The agreement lives in two transcripts.
- At a unit's review, the conductor opens the change in plannotator beside its pane (bolt-teams task 8.3).

## Goals / Non-Goals

**Goals:**
- What the user approves is exactly what is applied: the proposal holds the commands themselves.
- An approval is atomic: all of a proposal's changes, or none.
- The conductor's agreement and the user's approval are recorded acts.
- The user can read a proposal without knowing crew's command grammar.

**Non-Goals:**
- Changing a unit's intent or sending a unit in flight back to construct. `unit-amendments` adds `unit amend` to what a proposal can hold.
- Proposals from curation's plan items. `curation-and-agenda` adds `--item`.
- A proposal for the conductor's own writes, the design agent's queuing, a dispatcher's give or a landing. Those stay direct.
- Checking that it was the user who said yes. crew records who ran the approval and in which session, where the user's words are; the rule that an agent never approves on its own judgment is the briefs', as it is for `crew unit approve`.

## Decisions

### The record

`proposals.rec` on the flywheel's branch:

```
%rec: Proposal
%key: Proposal
%type: Proposal int
%type: State enum open approved dropped
%type: Opened,Closed date
%mandatory: Proposal Case Do State Opened By
%allowed: Proposal Case Do Agreed State Opened By Closed Reason Replaces

Proposal: 3
Case: Two findings from swb-2 are both about checking CloudFormation templates. smoke-2 is close to landing and
+ its goal is the bolt loop, so they start a bolt of their own.
Do: bolt new cfn-checks "Switchboard's CloudFormation templates are checked for security as well as validity" --repo switchboard-kit
Do: unit add cfn-nag-security-check "Switchboard's CloudFormation templates get a security check beside cfn-lint's validity check" --signal 2026-10-06-wldn-planner/01-cfn-nag-templates --bolt cfn-checks
Do: unit move retire-suite-cfn-lint cfn-checks
State: open
Opened: 2026-10-06
By: wldn-planner
```

`Do` repeats, in order. `Agreed` repeats, one team each. A number is one more than the highest in the file, computed inside the write so a replay recomputes it. `state init` creates the file with its descriptor on branches made after this change; on an existing branch the first proposal creates it.

The file the planner hands `crew plan propose` is one recutils record with `Case` and `Do` fields and nothing else. A `Do` is a plan command as it would be typed, without the leading `crew`, parsed with `shlex` and then with crew's own argument parser, so a proposal's grammar is the command line's and cannot drift from it.

*Alternatives:* marks on the plan's own records (a `Proposed` field on a unit). Rejected: it cannot express a move or a drop without a second copy of the record, and a half-approved set would be visible in the plan. A proposal written as prose and applied by the planner after a yes was rejected because what was approved and what was run could differ.

### Each plan command becomes three parts

Every plan command is refactored, without changing what it does when run directly, into:

1. `checks(fleet, args, plan)`: the refusals that read the kits or the plan (the unit's stage, the name free in the kit, the bolt in the same repo);
2. `change(w)`: the closure that edits the plan (and, for `--signal`, appends the move), as today;
3. `after(fleet, args, result)`: what follows the push (free a slot, tell conductors and dispatchers, print).

`unit move` has a fourth, `prepare`, with an `undo`: the rebase of a unit that has a worktree.

Run directly, a command is `checks`, `prepare`, `write(change)`, `after`, as today. The three new callers reuse the parts:

- **propose** runs each `Do`'s `checks` and `change` in order on a copy of the plan at the tip, and discards the copy. A command later in the list sees what earlier ones did (a unit added to a bolt the proposal creates). Stage checks read the kits once per host for the whole proposal. Nothing is prepared and nothing pushed but the Proposal record.
- **approve** runs, inside one `write`: every `Do`'s `checks` and `change` in order on the plan at the tip, then sets the proposal `approved` with `Closed`. Before the push it runs each `prepare` in order; if a later `prepare` or the checks of a replay fail, it runs the `undo`s in reverse and refuses. After the push it runs each `after` in order.
- **proposed** runs nothing; it prints.

`name_free` (a unit's name against the kit's changes) needs the kit's host. If the host does not answer, propose and approve are refused as the direct command is.

### Who may write what directly

One function, called at the top of every plan-writing command when `CREW_AGENT` is set, decides from the agent's name and the teams file:

| Caller | Writes directly | Otherwise |
|---|---|---|
| the user (no `CREW_AGENT`) | everything | |
| `<label>-planner` | `plan propose`, `plan drop` (its own proposals) | refused: "the planner changes the plan through a proposal: crew plan propose" |
| `<team>-conductor` | `unit split`, `unit order`, `unit after` on units of the bolt its team holds; `plan agree` | refused: "tell <label>-planner" |
| `<label>-design` | `unit add … --repo <kit>` (the queue, never `--bolt`) | refused, the same way |
| `<label>-dispatch-<host>` | `bolt give` | refused |
| `<label>-ops` (main level) | `bolt land` | refused |
| any other agent | nothing | refused |

`crew unit approve` and `crew plan approve` are open to any caller; they are the user's acts, run by the user or on the user's word. `crew plan drop` is open to the planner for its own proposals and to any caller acting on the user's word.

A command inside an approval is exempt from the table: the approval is the authority.

*Alternative:* leave the rule in the briefs. Rejected: the rule was in the planner's brief on 2026-10-03, and the mechanism is a few lines.

### Which bolts a proposal touches

A `Do` touches: the bolt named by `unit add --bolt`; the bolt a unit leaves and the bolt it joins in `unit move`; the bolt of the unit in `unit split`, `unit order`, `unit after` and `unit drop`; the bolt of `bolt order` and `bolt drop`. `bolt new` touches none. A touched bolt that has a `Team` at the tip is in flight.

At propose, crew tells each such team's conductor: "Proposal 4 would change your bolt <bolt>: <the commands that touch it>. Read it with `crew plan proposed 4`. Agree with `crew plan agree 4`, or tell <planner> why not." A conductor that is not up is reported, and the proposal is still written.

`crew plan agree <n>` checks the caller is the conductor of a team holding a touched bolt (or the user, who may agree for any), appends `Agreed: <team>`, and tells the planner. Approval computes the touched, held bolts again at the tip, so a bolt given to a team after the proposal was written needs that team's agreement too.

The user's approval does not override a missing agreement. The user who wants a change over a conductor's objection writes the plan at a shell, which is always open.

### How a proposal reads

`crew plan proposed <n>` prints markdown, so the planner can show it in its pane or open it in plannotator beside the pane as a conductor does with a unit's change:

```
# Proposal 3 — open, by wldn-planner, 2026-10-06

Two findings from swb-2 are both about checking CloudFormation templates. …

## Changes

1. **New bolt `cfn-checks`** in switchboard-kit
   Goal: Switchboard's CloudFormation templates are checked for security as well as validity

2. **New unit `cfn-nag-security-check`** in bolt `cfn-checks` (new in this proposal)
   Intent: Switchboard's CloudFormation templates get a security check beside cfn-lint's validity check
   From: signals/2026-10-06-wldn-planner/01-cfn-nag-templates — "<its assertion>"

3. **Move unit `retire-suite-cfn-lint`** from the queue to bolt `cfn-checks`
   Intent: <the unit's intent, as it stands>

## Waiting on

The user: `crew plan approve 3`, or `crew plan drop 3 "<reason>"`.
```

A unit joining an existing bolt shows that bolt's goal and its team under the unit, which is the comparison the user is approving. A signal source shows the signal's assertion and, where the signal has one, its excerpt. The bare `crew plan proposed` lists open proposals one per line with what each waits on: named conductors, then the user.

### The planner's brief

The planner's brief is rewritten around this: decide, write the proposal file (the case first: why these units, why this bolt or a new one), run `crew plan propose`, show the user `crew plan proposed <n>`, and wait. It runs `crew plan approve <n>` only when the user says so in its pane, and `crew plan propose --replaces <n>` when the user wants it changed. It no longer tells a conductor to agree; crew does. The operator agent's brief lists open proposals among what waits on the user.

### Entries

`plan.propose`, `plan.agree`, `plan.approve` and `plan.drop` each name `proposal/<n>` and every bolt and unit the proposal's commands name. An approval also emits the entry each command would emit run directly (`bolt.new`, `unit.add`, …), with `From: proposal/<n>` and the approval's commit. `crew trace` follows `proposal/` names like any object.

### What must not break

- Every plan command run by the user at a shell behaves as it does today.
- A conductor's split, order and dependency writes on its own bolt, the design agent's queuing, `bolt give` and `bolt land` are unchanged.
- A conductor still hears the subject of a write to its bolt; an approval's subject is `plan(proposal <n>): approve: <a summary of its changes>`.
- `crew unit add --signal` still writes the unit and its `route` move in one commit; inside a proposal, that commit is the approval's.

## Risks / Trade-offs

- [The plan moves between propose and approve] → approval checks again at the tip and refuses, naming the command. The planner replaces the proposal.
- [A proposal waits on a conductor that is down] → `crew plan proposed` names it; the dispatcher starts the team, or the user writes the plan directly.
- [An agent approves without the user's word] → the same exposure as `crew unit approve` today. The entry names the session, and the operator agent lists what was approved since the user last asked.
- [The refactor of every plan command breaks one] → the existing `bolt-plan` tests run unchanged against the direct commands before any proposal test is written.
- [The role table refuses something an agent legitimately did] → the table is the briefs' rules as written; the first days' refusals show in the run record as `Refused` entries.

## Migration Plan

Pull on every host and restart each partition's planner, design agent, conductors and operator agents so they have the new briefs. A planner started before the pull finds its direct writes refused with a message that names the new command. There is nothing to migrate in the state: `proposals.rec` appears with the first proposal. Rollback is reverting the commit; open proposals stay in the file, unread.
