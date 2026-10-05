# Tasks

## 1. The mark and the stage

- [x] 1.1 Add `Amended` to the Unit schema's `%allowed` in `plan.py`'s header, and have `crew state init` and every plan write keep an existing branch's descriptor in step with it. Verify `recfix --check` passes on a plan holding a unit with `Amended: proposal/4`, and that a plan from before the change still reads.
- [x] 1.2 `Stages.of`: after `landed` and `merged`, a marked unit reads `amended` for `proposal/<n>` or `intent`, `construct` while the unit branch's head equals a marked sha, and `review` once it differs; unmarked units read as today. Verify with a fixture kit: a unit with ticked tasks and each of the three mark states, and an unmarked unit at every existing stage.
- [x] 1.3 `crew bolts` prints `amended`, and `--json` carries it. Document the stage in `README.md`'s plan section. Verify with the fixture.

## 2. Construct again

- [x] 2.1 `run_check` for construct accepts `ready`, `construct`, `review`, `amended`, `approved`, `code` and `verify`, refuses `merged` and `landed`, and at `approved`, `code`, `verify` or `amended` sets `Amended: <unit head>` in the plan before the stage starts; the conductor's role allows this write for a unit of its own bolt. When the mark was `proposal/<n>` or `intent`, the prompt carries the sentence that the intent was amended. Verify in a scratch kit: construct on a unit in code marks it and starts a fresh agent with the user's words; on a merged unit it is refused.
- [x] 2.2 Code, verify and merge are refused while the mark is set, with the two messages in design.md, each leaving a `Refused` entry. Verify each.
- [x] 2.3 `crew unit approve` at `review` on a marked unit writes the approval commit and clears the mark in one plan write; run again after a failed plan write it only clears the mark; at `amended` it is refused. Verify the stage after approval is `code` with ticked tasks and `approved` without.
- [ ] 2.4 `plugin/roles/construct.md`: revising an existing change, for the user's words or for an amended intent. `plugin/roles/conductor.md`: amending a unit after approval, the re-review, and what to do when crew says an intent was amended. Verify both print for the `swb-1` fixture with no unfilled token.

## 3. Amending an intent

- [ ] 3.1 `crew unit amend <unit> "<new intent>"` as `checks`, `change` and `after`: refused for a merged or landed unit; `Intent` replaced; a unit with a worktree marked `proposal/<n>` in an approval or `intent` for the user; its conductor told. The planner's direct run is refused naming `crew plan propose`; the user's is written. Entry `unit.amend`. Verify each case, and that a queued unit is not marked.
- [ ] 3.2 A proposal may hold `unit amend`; it touches the unit's bolt, so a held bolt's conductor is told and must agree. `crew plan proposed <n>` prints the amendment as before and after with the unit's bolt, team and stage and what approval sets in motion. Verify with a fixture proposal amending a unit in code: the page, the refusal of approval before agreement, and after approval the new intent, the mark and the tell.
- [ ] 3.3 `plugin/roles/planner.md`: a change to what an existing unit builds is `unit amend` in a proposal, with the case saying why the unit changes and is not replaced. Document `crew unit amend` and amending a unit in flight in `README.md`, `plugin/skills/crew/SKILL.md` and the usage header. Verify every command in the README appears in `crew`'s usage.

## 4. Proof on real work

- [ ] 4.1 Pull on every host and restart wldn's planner and conductors. On a unit of a bolt in flight that is approved or in code, tell its conductor a change you want in how it is built. Verify the conductor runs construct again, `crew bolts` shows the unit in `construct` and then `review`, `crew unit run <unit> code` is refused until you approve, and after `crew unit approve` the unit carries on from its tasks.
- [ ] 4.2 Ask the planner to change what a unit in flight builds. Verify it writes a proposal with `unit amend`, its page shows both intents, the bolt's conductor agrees, and on your approval the unit reads `amended`, its conductor runs construct again unprompted by you, and the unit comes back to your review. `crew trace unit/<unit>` shows the proposal, the agreement, the approval, the amend, the construct and the second approval, in order.
