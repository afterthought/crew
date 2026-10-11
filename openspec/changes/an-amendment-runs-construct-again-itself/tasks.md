# Tasks

## 1. The amendment starts construct itself

- [x] 1.1 Applying `unit amend` to a unit with a worktree in a held bolt, directly or in an approval, runs `crew unit run <unit> construct` on the team's host in the applier's name and tells the conductor that construct runs again or why it did not start (design.md, Decisions 1 and 4; Task notes 1.1). Verify `tests/suite t-amend-intent` ends with "0 failed".
- [x] 1.2 `run_check` starts construct on a unit marked `proposal/<n>` or `intent` for any caller, sends the amendment's words read from the mark (the proposal's case included), and names the card of the row the unit held before its amendment (design.md, Decisions 2 to 4; Task notes 1.2). Verify `tests/suite t-amend t-amend-intent` ends with "0 failed".
- [x] 1.3 `crew plan proposed <n>` says of an amendment "On approval: construct runs again at once in <team>'s slot, and the unit returns to your review." (design.md, Decision 6). Verify `tests/suite t-amend-intent` ends with "0 failed".

## 2. A conductor brought back starts amended units

- [x] 2.1 The greeting of `crew up`, `rebuild`, `restart` and `revive` opens with the line `plan _amended <team>` prints, and `crew resume` sends that line as a `[crew]` notice when it is not empty (design.md, Decision 5; Task notes 2.1). Verify `tests/suite t-greet t-revive t-resume` ends with "0 failed".
- [x] 2.2 `conductor.md` says crew starts an approved amendment's construct and tells it, and that any unit `crew bolts` shows as `amended` gets its construct run; `tests/t-briefs.sh` pins those phrases in place of "When crew tells you a unit's intent was amended, run construct again" (design.md, Decision 5). Verify `tests/suite t-briefs` ends with "0 failed".

## 3. Docs

- [ ] 3.1 README (the amendment paragraph and the role table's conductor row), `plugin/skills/crew/SKILL.md`'s `crew resume` row, the usage header of `plugin/bin/crew` and the `crew unit amend` line of `plan.py`'s usage say that an amendment starts construct itself and a conductor brought back is told which units wait amended (`docs.2`). Verify `tests/suite t-docs` ends with "0 failed".
- [ ] 3.2 `plan.15`'s details in `docs/architecture/plan.md` drop "not built: `_open.md`", and `_open.md` no longer lists `plan.15`. Verify `tests/suite --affected` ends with "0 failed".

## 4. Proof on real work

- [ ] 4.1 Work design.md's *Proof on real work* once the bolt has landed and every host has pulled.
