# A bolt's proof is its verification

## Why

Record 0025 (accepted 2026-10-13): a change is verified by its kit's checks alone, and a bolt's proof is the same checks green at its head. `crew prove` had ops deploy the bolt and work each unit's *Proof in dev* list by hand, a proof nobody could replay, and the landing card asked the user the steps the proof left them. With record 0026 every merge into a bolt is a submission sluice tests before it lands, so the bolt's verification is sluice's verdict on its last landing, and nothing is left to prove by hand.

## What Changes

- **`crew prove` goes**, with ops's proof report, its *Left for the user* and the proof's stage and wait. **BREAKING** for a conductor or ops still running it.
- **The conductor offers the landing once the bolt's verification is green** and every unit and chore has merged; the rail's land row says the verification until it is green and carries no command. The landing card asks only for the landing: a step only the user can do is an after-deploy step on a deploy's card.
- **ops proves and deploys nothing**: it reads why a submission did not land, takes readings and finds what is broken, and tells the conductor what it waits on.
- The conductor's, ops's and main-level ops's briefs, the card hook's landing form, README and CLAUDE.md say so.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: the bolt's proof is its verification; ops's proof stage, its deliverable and its wait go.
- `rail-cards`: the landing card is posted once the verification is green and asks only for the landing; ops's proof steps go.
- `crew-rail`: a bolt is offered for landing only once its verification is green.

## Impact

- `plugin/lib/plan.py` (`prove_cmd`, the proof's stage, owed end and delivery gone; the rail's land row and `crew bolts` read the verification), `plugin/lib/crew.py` (`needs_how`), `plugin/hooks/cards` (the landing form has no steps), `plugin/bin/crew`.
- `plugin/roles/conductor.md`, `ops.md`, `main-ops.md`; README, CLAUDE.md, the skill.
- `tests/py/test_rail.py`, `test_cards.py`, `test_stage_ends.py`, `test_wait.py`, `test_parser.py`; `tests/t-journey-fix.sh`, `tests/t-briefs.sh`.
