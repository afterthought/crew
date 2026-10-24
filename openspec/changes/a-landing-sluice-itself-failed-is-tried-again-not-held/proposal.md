# A landing sluice itself failed is tried again, not held

## Why

Today every landing that does not land holds its bolt on the landings card "until its team's fix moves its head", whatever stopped it. On 2026-10-23 and 24 in wldn, two bolts were held so when nothing of theirs was at fault: the box's Dagger engine did not answer, so main's checks never ran, and sluice failed releasing a place it still held for a worktree that was gone ("could not release …, whose worktree no longer exists"). No fix of the team's can clear either, so the bolts sat with no box, and the user's approval was spent on a refusal that was never the bolt's (wldn signal 2026-10-24-wldn-ops-2dd52ecd/01; `plan.16` as read 2026-10-24, in `plan.18`'s details). Record 0031 holds a refused landing on its row for the team's fix; that hold is for a fault in the bolt, and only for that.

## What Changes

- **crew tells the bolt's refusals from everything else.** When a landing does not land, crew reads sluice's own record of the landing's submission. It is the bolt's only when that record has the submission in conflict, or blamed for a check that ran and failed (or was cut off by its time limit). Everything else is a stop, not the bolt's: sluice itself failing (exit 3), a submission sluice refused or answered with no record of a conflict or a failed check, a place sluice holds, checks the host could not run, a withdrawal, and a landing crew can't tell the outcome of.
- **A stop holds nothing.** crew records it with the head submitted and what stopped it, and no refusal. The bolt's row on the kit's landings card keeps its box and the approval it has: an answered card is left as it is, its send still standing for the bolt, and `crew card read` names the bolt with what stopped it and the command that lands it.
- **The row says what stopped it and what comes next.** The landings card's row and the rail's line say what stopped the landing at that head, that it was nothing of the bolt's, and that main-level ops submits it again once that is cleared.
- **Ops submits it again with no new word.** `crew bolt submit`'s words for a stop tell ops so, and main-ops's brief says it: report what stopped it as a finding outside any bolt, and once it is cleared submit the bolt again on the word that stands.
- **The bolt's own refusals are held as before.** A conflict or a failed check holds the bolt's row for its team's fix, as record 0031 has it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a refused landing is held on its row only when the refusal is the bolt's; a landing sluice or its host stopped keeps its box, saying what stopped it.
- `crew-rail`: a bolt's line under land says a stopped landing beside "can land", and the tell names it.
- `bolt-teams`: `crew bolt submit` says whether a landing that did not land was the bolt's, from sluice's record of the submission, and records a stop with no refusal.
- `main-level`: main-level ops submits a stopped bolt again on the word that stands, once what stopped it is cleared.

## Impact

- `plugin/lib/plan.py`: `wait_outcome` and `landing_said` read whether the outcome is the bolt's from sluice's record; `landing_ended` records a stop with `Why`, `Head` and `Outcome: stopped`; a new reader of stops beside `refusals`; `landing_rows`, the rail's land line, `landings_step`'s outcome words and `card_read` carry the stop.
- `plugin/lib/cards.py`: a row's paragraph and box detail say the stop.
- `plugin/roles/main-ops.md`: step 2 of *Landing a bolt*.
- README's `crew bolt submit` paragraph, the crew skill's landing row and `plugin/bin/crew`'s usage header for `crew bolt submit` (`docs.2`).
- `tests/py/test_landing.py`, `tests/py/test_landings.py`, `tests/py/test_rail.py`, `tests/py/test_cards.py`, a fixture of sluice 0.36.4's failed submission records under `tests/py/sluice-0.36.4/`, `tests/t-journey-land.sh` and the stub sluice and wt-submit, `tests/moon.yml`.
- Nothing outside the standard library is imported (`code.1`); nothing is pushed (`state.5`).

## Touches

```
plugin/lib/plan.py
plugin/lib/cards.py
plugin/roles/main-ops.md
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/py/test_landing.py
tests/py/test_landings.py
tests/py/test_rail.py
tests/py/test_cards.py
tests/py/sluice-0.36.4/*
tests/t-journey-land.sh
tests/stubs/sluice
tests/stubs/wt-submit
tests/moon.yml
```
