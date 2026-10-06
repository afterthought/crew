# Tasks

## 1. Plan commands in three parts

- [x] 1.1 Refactor each plan command in `plan.py` (`bolt new|order|drop`, `unit add|move|split|order|after|drop`) into its `checks`, its `change` and its `after`, with `prepare` and `undo` for `unit move`'s rebase, keeping what each does when run directly. Verify the existing `bolt-plan` tests pass unchanged.
- [x] 1.2 A helper that applies a list of commands to a copy of the plan in order, running each one's `checks` and `change`, and reports the first refusal with its command. Verify with a test that a unit added to a bolt created earlier in the list passes, and a unit added to an unknown bolt is reported with its command.

## 2. Writing a proposal

- [x] 2.1 `proposals.rec` with the descriptor in design.md, created by `crew state init` on new branches and by the first proposal on an existing one. Verify `recfix --check` passes on the file after one proposal.
- [x] 2.2 `crew plan propose <file> [--replaces <n>]`: the file is one record with `Case` and `Do` fields; each `Do` is parsed with `shlex` and crew's argument parser; only the nine commands are accepted; the list is checked with the helper of 1.2; the proposal is written `open` with the next number, recomputed on a replay; `--replaces` drops the named open proposal in the same commit. Only the partition's planner and the user may run it. Verify: a valid proposal leaves the plan unchanged; `bolt give` in a `Do` is refused; a refused command writes nothing; a conductor's `plan propose` is refused; a replaced proposal is `dropped` and its successor names it.
- [x] 2.3 On writing, tell the conductor of each touched bolt a team holds, with the commands that touch its bolt and how to agree; a conductor that is not up is reported and the proposal still written. Verify with the stub `herdr`.
- [x] 2.4 Entries: `plan.propose` naming `proposal/<n>` and every bolt and unit its commands name. Verify the entry and that it holds neither the case nor an intent.

- [x] 2.5 `--unblocks <bolt>` on `unit add` and `unit move` inside a proposal: the named bolt must be held by a team, and the unit must go into that bolt ahead of the units that wait on it; the check refuses the proposal otherwise, naming the bolt. Verify a unit marked `--unblocks` and placed in the queue or a new bolt is refused, and one placed in the held bolt passes.

## 3. Reading proposals

- [x] 3.1 `crew plan proposed [--label L] [--json]` lists open proposals with number, writer, date, the case's first line and what each waits on. `crew plan proposed <n>` prints the markdown in design.md: the case; each change in plain words; a new unit's intent with its sources (a signal's assertion and excerpt where it has one) and the goal and team of the bolt it would join, and the bolt it unblocks when it carries `--unblocks`; a move's bolts and goals; a drop's reason; the agreements given and missing. Verify against a fixture proposal with one of each change, from a host that holds no team.
- [x] 3.2 Document proposals in `README.md` (a "Proposals" section under the plan: the record, the five commands, who may write what directly), `plugin/skills/crew/SKILL.md` and the usage header. Verify every command in the README appears in `crew`'s usage.

## 4. Agreement

- [x] 4.1 `crew plan agree <n>`: the caller is the conductor of a team holding a bolt the proposal touches, or the user; it appends `Agreed: <team>`, tells the planner, and emits `plan.agree`. Verify: the touched bolt's conductor agrees; another team's conductor is refused; agreeing twice changes nothing.

## 5. Approval and dropping

- [x] 5.1 `crew plan approve <n>`: inside one write, every command's `checks` and `change` in order at the tip, then the proposal `approved` with `Closed`; `prepare` steps before the push with `undo` in reverse on any failure; `after` steps once the push lands. Verify: a three-command proposal is one commit holding the plan change and the closed proposal; a command that no longer applies refuses the approval and leaves both files unchanged; a conflicting rebase is undone and nothing is written; a `--signal` unit's `route` move is in the same commit.
- [x] 5.2 Approval is refused while a touched bolt held by a team has no `Agreed`, naming the conductor, computed at the tip. Verify with a bolt given to a team after the proposal was written.
- [x] 5.3 Entries: `plan.approve` naming the proposal and its objects, and one entry per applied command as that command emits when run directly, each with `From: proposal/<n>` and the approval's commit. The conductors of touched bolts hear the approval's subject, and dispatchers a new bolt. Verify `crew trace unit/<unit>` for a unit an approval added shows the proposal, the agreement, the approval and the add.
- [x] 5.4 `crew plan drop <n> "<reason>"` closes an open proposal as `dropped` with the reason, tells the planner when someone else ran it, and emits `plan.drop`. Verify the plan is unchanged and a dropped proposal cannot be approved.

## 6. Who may write the plan directly

- [x] 6.1 The role check of design.md's table at the top of every plan-writing command when `CREW_AGENT` is set; commands inside an approval are exempt. Verify one test per row: the planner's direct `unit add` and `bolt new` are refused naming `crew plan propose`; a conductor's split on its own bolt is written and on another bolt refused; a conductor's `unit add --bolt` is refused; the design agent's `--repo` add is written and its `--bolt` add refused; `bolt give` by a dispatcher and `bolt land` by main-level ops still work; a unit-slot agent's write is refused; the user's writes are untouched. Each refusal leaves a `Refused` entry.

## 7. Briefs

- [x] 7.1 `plugin/roles/planner.md`: the plan table becomes the proposal file and `crew plan propose`; the case says why these units and why this bolt, a new bolt, or the queue; show the user `crew plan proposed <n>`, in the pane or in plannotator beside it; approve only on the user's word in this pane; `--replaces` when the user wants it changed; no direct writes; no telling a conductor to agree. Verify the brief prints for the `wldn` fixture with no unfilled token and names no direct plan write.
- [x] 7.2 `plugin/roles/conductor.md`: a proposal that touches the bolt arrives from crew; read it, agree with `crew plan agree <n>` or tell the planner why not; adding a unit is the planner's proposal, never the conductor's write. `plugin/roles/design.md`: units are queued with `--repo`, never placed. `plugin/roles/operator.md`: open proposals (`crew plan proposed`) are among what waits on the user, and the operator runs `crew plan approve` only on the user's word. Verify each prints with no unfilled token.

## 8. Proof on real work

- [ ] 8.1 Pull on every host and restart wldn's main level, its conductors and the operator agents. Ask wldn's planner to place the units waiting in switchboard-kit's queue. Verify it writes a proposal and not the plan: `crew bolts` is unchanged, `crew plan proposed` lists it, and its page shows each unit's intent with the goal of the bolt it would join or the new bolt's goal.
- [ ] 8.2 Have the planner propose a unit for a bolt a team holds. Verify that team's conductor is told, that `crew plan approve` is refused naming it until it runs `crew plan agree`, and that after the user says yes the approval is one commit on `wldn/main` holding the plan change and the closed proposal.
- [x] 8.3 Ask for a different placement of one proposal. Verify the planner replaces it (`--replaces`), the first is `dropped`, and `crew trace proposal/<n>` shows both, each line naming the planner's session and a time.
