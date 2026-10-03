# Tasks

## 1. The hold

- [ ] 1.1 Add `Hold` to the Unit schema's `%allowed`. `crew signal … --blocks <unit>`: the unit is in a bolt and not merged; the caller is the user or an agent of the team holding that bolt; the capture gains `blocks: <unit>`; the capture, the signal and `Hold: signals/<id>` are one commit; entry `unit.hold`. Verify the commit, a second hold on the same unit, and the refusals for a merged unit and for another team's unit.
- [ ] 1.2 `run_check` refuses merge for a held unit with the message of design.md, saying whether the signal is uncurated or on which item, and leaves a refused entry; construct, code and verify still start. `crew bolts` prints `held` and `--json` carries `holds`. Verify in a scratch kit.

## 2. Ending a hold

- [ ] 2.1 `settle`, called inside every write that changes a signal's standing move or an item's state: a standing `attach`, `challenge`, `answered` or `drop`, an item `dropped`, or an item `decided` with no unit result, removes the hold in that same commit; `route`, `join` and `revive` leave it. The conductor is told what settled it. Entry `unit.release` naming the signal. Verify one test per row of design.md's table: a delivery, a hand move, a replacement, `agenda close dropped`, `agenda close decided` with a decision record alone, and with a unit.
- [ ] 2.2 `crew unit release <unit> "<why>"` as `checks`, `change`, `after`: removes every hold, never an `After`; direct for the user and for the unit's conductor; the planner's only in a proposal, where it is an accepted command. Verify each caller, and that a unit with no hold is refused.

## 3. From hold to dependency

- [ ] 3.1 Inside `unit add` and `unit move`: when a unit sourced from `agenda/<n>` enters bolt `B`, each unit of `B` held by a signal of item `n` loses that hold and gains `After: <the unit>`, in the same commit; entry `unit.after` naming the signal and the unit. Verify through an approved proposal that adds the unit, and through one that moves a unit the design agent had queued.
- [ ] 3.2 `run_check` refuses merge while an `After` unit has not merged, naming it; a unit not yet started is `waiting` as before. Verify a unit in code that gains a dependency can run code and verify and cannot merge until the other has, and that the cycle check refuses a proposal making the new unit depend on the held one.
- [ ] 3.3 A proposal that adds or moves a unit sourced from an item holding `H` to anywhere but `H`'s bolt is refused at propose and at approve, unless an earlier command of it releases `H`. `crew plan proposed <n>` says the held unit will come after the new one. Verify the refusal, the release form, and the page.

## 4. Showing it

- [ ] 4.1 `crew agenda` and `crew agenda <n>` print `holds unit <H> (<bolt>, <team>)` for an item with a blocking signal whose unit has not merged; the curator's work order marks blocking signals in `order.md`. Verify with a fixture.
- [ ] 4.2 Document blocking findings in `README.md` (under signals: `--blocks`, what a hold stops, how it ends, `crew unit release`), `plugin/skills/crew/SKILL.md` and the usage header. Verify every command in the README appears in `crew`'s usage.

## 5. Briefs

- [ ] 5.1 `conductor.md`: the section "A finding that blocks a unit" as design.md gives it. `curator.md`, `planner.md`, `design.md`: an item that holds a unit. Verify each prints for its fixture with no unfilled token.

## 6. Proof on real work

- [ ] 6.1 Pull on every host and restart wldn's agents. While a unit is in code, raise with its conductor something small that changes how it is built. Verify the conductor asks you, amends the unit by running construct again, and records no signal.
- [ ] 6.2 On another unit in flight, tell the conductor a question is one for design. Verify `crew signal … --blocks` is one commit with the hold; `crew bolts` shows the unit held; its merge is refused; and you were told it is held.
- [ ] 6.3 Have the question put on the agenda by your word, and settle it with the design agent by a direct answer. Verify the close lifts the hold in its own commit, the conductor is told the decision record, and it amends the unit with it.
- [ ] 6.4 Repeat with a finding whose answer is a new unit: the design session queues it, the planner proposes it into the held unit's bolt, the conductor agrees and you approve. Verify the held unit comes `After` the new one, cannot merge before it, and merges after; and that `crew trace unit/<held unit>` shows the whole detour in order.
