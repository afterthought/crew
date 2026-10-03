# Tasks

## 1. Moves

- [ ] 1.1 `moves.rec`'s descriptor becomes the one in design.md (`%key: Id`, the seven-word enum, `Replaces`); the first write under it gives existing records their `Id` in file order, in the same commit. Verify against a fixture branch holding the two `route` moves of 2026-10-03: both keep their fields, gain `Id` 1 and 2, and the file passes `recfix --check`.
- [ ] 1.2 The standing move and "unmoved", as one function used by every reader; crew refuses a second standing move. `crew signal move` takes `join`, requires `--reason`, and applies the target checks of design.md's table (an item open and in the move's lane, a unit or bolt in the plan, a path on its repository's main). Verify one test per move word, and a refusal per unresolved target.
- [ ] 1.3 `crew signal move … --replace "<why>"` and `crew signal revive <id> "<why>"` write a record with `Replaces`; without `--replace` a second move is refused naming the first. Entries `signal.move` and `signal.replace`. Verify a revived signal reads as unmoved, the replaced record is still in the file, and replacing a `join` moves the signal between two items' weights.

## 2. The agenda

- [ ] 2.1 `agenda.rec` with the descriptor in design.md, created by `crew state init` and by the first item on an existing branch; numbers computed inside the write. Verify `recfix --check` and that two items added at once from two hosts get different numbers.
- [ ] 2.2 `crew agenda [--lane] [--all] [--json]`: open items with weight (signals, captures, their sources, the span of event dates) computed from the standing moves and the captures in both homes, and any open proposal naming the item. `crew agenda <n>`: the item, each signal with its assertion, excerpt, grade, source, date and the move's reason, and for a closed item how it closed. Verify with a fixture: an item with a meeting signal from the blueprints remote and an agent's signal from the state, read from a host that holds no team.
- [ ] 2.3 `crew agenda add … --signal <id>...` creates the item and writes each signal's `route` or `join` in one commit; unmoved signals only, or `--replace`; a plan item needs `--repo`. Entry `agenda.add` with the signals in `From`. Verify the commit, and the refusal for a moved signal.
- [ ] 2.4 `crew agenda lane <n> plan|design "<why>"` sets the lane and a note, and when it sends a plan item to design drops any open proposal that adds a unit from it, in the same commit. Verify the proposal is `dropped` with the item named, and that the item's signals now read under the design lane.
- [ ] 2.5 `crew agenda close <n> decided --result <ref>...` and `dropped "<reason>"`: a unit result must carry `Source: agenda/<n>`; a document result `<repo name>:<path>` must be committed at `HEAD` of that repository's main checkout on this host and name `agenda/<n>`, and is recorded as `<owner>/<name>@<sha>:<path>`. Entry `agenda.close`. Verify each check with a scratch checkout, and the refusal when the checkout is not on this host.
- [ ] 2.6 Document the agenda in `README.md` (a section: lanes, the record, the five commands, weight), `plugin/skills/crew/SKILL.md` and the usage header. Verify every command in the README appears in `crew`'s usage.

## 3. Units from items

- [ ] 3.1 `crew unit add … --item <n>`: the item open; lane `plan` inside a proposal, lane `design` and a queue for the design agent; `Source: agenda/<n>` first among the unit's sources; `From: agenda/<n>` on its entry. Verify the design agent's add, and the refusals for a closed item and the wrong lane.
- [ ] 3.2 The gate: an agent's `unit add` with neither `--item` nor an accepted `--signal` is refused, with the design agent's message from design.md. `--signal` is accepted from the planner only in a proposal, for an unmoved signal it captured itself; the approval writes the `route` with `Target: unit/<unit>` as the user's hand; an uncurated signal and a signal on the agenda are refused with their messages. Verify each, and that the user at a shell is unaffected.
- [ ] 3.3 Approval of a proposal with `unit add … --item <n>` for a plan item closes the item as `planned` with the unit as `Result`, in the approval's commit; a dropped proposal leaves the item open. `crew plan proposed <n>` prints the item's subject and its signals with excerpts and grades under the unit. Verify with a fixture item resting on a `verified` excerpt.
- [ ] 3.4 `plugin/roles/construct.md`: a source `agenda/<n>` is read with `crew agenda <n>` and `signals/<id>` with `crew signal show <id>`, and the change's proposal quotes the excerpts. Verify the brief prints with no unfilled token.

## 4. The curator and its batch

- [ ] 4.1 `plugin/roles/curator.md` (`claude-fable-5-1`, `high`) with the brief of design.md; `crew-role` and the brief builder know the role; the teams file's `roles.curator` override applies. Verify the launch arguments for the `wldn` fixture, with and without an override, and that the brief prints with no unfilled token.
- [ ] 4.2 `crew curate <label> [--only <capture>...]`, forwarded to the main level's host: refuses a running curator; fixes the batch at the two commits; writes the work order (`order.md`, `signals/`, `agenda.md`, `plan.md`, `batch.rec`); opens the `curator` tab in the `<label>` workspace, starts the role and prompts it. Entry `curate.start`. Verify with the stubs: the work order's files for a batch spanning both homes, `--only`, the refusal while a curator is up, and "nothing to curate".
- [ ] 4.3 The curator's tab is closed by the next `crew curate` or `crew main` command once its batch is delivered and its agent is not working; `crew main status` lists a running curator. Verify with the stub `herdr`.

## 5. The delivery

- [ ] 5.1 `crew curate deliver <file>`: the checks of design.md (the caller; the batch covered exactly; each signal still unmoved, naming any moved by hand; targets, lanes, reasons, an item for every local name and a move for every item); one write of every move and item; the `delivered` marker; a second run writes nothing. Verify with fixtures: an accepted delivery is one commit; a missing signal, an extra signal, an unresolved target, an item with no move and a missing reason are each refused with nothing written.
- [ ] 5.2 Entries `curate.deliver`, one `signal.move` per move and one `agenda.add` per item, sharing the commit; the planner is told the open plan items, and nobody is told of design items. Verify `crew trace signals/<id>` for a routed signal shows capture, move and item, and the stub `herdr` shows one prompt, to the planner.

## 6. Briefs

- [ ] 6.1 `conductor.md`, `ops.md`, `main-ops.md`: a finding outside the bolt or unit is recorded with `crew signal` and nobody is told. `design.md`: "Curating signals" replaced by "The agenda" as design.md describes. `planner.md`: plan items become `unit add --item` in proposals; the intent adds nothing the item's signals and the standing design do not say; `crew agenda lane` for an intent that needs a decision; the user's direct word is captured and proposed with `--signal`. `operator.md`: the agenda and proposals among what waits on the user; `crew curate` and hand moves only on the user's word. Verify every brief prints for its fixture with no unfilled token, and that none tells an agent to tell the planner about a finding.

## 7. Outside crew

- [ ] 7.1 The blueprints repos' `signals/README.md` (willdan-blueprints first), as a reviewed commit: the six moves with `join` in place of `new-territory`; the two lanes and the agenda; that moves and items live on the flywheel's branch of the state repository and are written only through crew; that curation is a curator started with `crew curate`, on the user's word; that a decision record cites its agenda item and that item's signals. The `signal-capture` skill's sentence about "five curation moves" follows. Verify the README's move table matches `moves.rec`'s enum.
- [ ] 7.2 A decision for the user: when to curate wldn's 192 unmoved meeting signals, as one batch or by capture with `--only`. It is an operation, not part of this change's proof.

## 8. Proof on real work

- [ ] 8.1 Pull on every host and restart wldn's main level, conductors and operator agents. In a conductor's pane on the box, say one thing about work outside its bolt that is plainly plan-ready and one that raises a design question, and let it also record a finding from a tool's output. Verify three signals on `wldn/main`, each with a checked excerpt, and that the conductor told no agent.
- [ ] 8.2 Tell the operator agent to curate, scoped to those captures. Verify `crew curate wldn --only …` starts the curator, its delivery is one commit, the plan-ready signal is routed to a plan item and the question joined to a design item, each move with a reason, and only the planner was told.
- [ ] 8.3 Verify the planner writes a proposal with `unit add … --item <n>`; that its page shows your words under the intent; and that on your approval the unit, the closed proposal and the item `planned` are one commit.
- [ ] 8.4 In the design agent's pane, take up the design item. Verify it reads `crew agenda <n>` and not the unmoved signals, records the decision citing `agenda/<n>`, queues a unit with `--item <n>`, and closes the item; and that the planner then proposes that unit's placement.
- [ ] 8.5 Run `crew trace signals/<id>` for each of the two signals on mac-studio. Verify each prints the whole chain (capture, move, item, proposal and approval or session close, unit), every line naming an agent, a host, a session and a time, with no agent asked. Then revive the third signal and replace one move, and verify both show in its trace.
