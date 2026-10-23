# A card left on another host is raised again

## Why

A Pending You card can be reached only from the host whose sign-in posted it. When the partition's main level moved from mac-studio to deneb, the batch cards it had posted on mac-studio could be answered, read or closed by nobody on deneb, and crew did not raise them again because its run record still showed each one open. The bolt's earlier unit fixed that for batches alone: on the main level's host, the rail's next read now posts a batch's card again when its owner's newest copy was posted from another host, or was lost to it, its summary saying the older copy is dead.

Every other card crew raises can be stranded the same way: a proposal's, a decision record's, a bolt's landing, a deploy's and an after-deploy step's. The rules hold all six cards to one form and one path (`briefs.11`, `briefs.13`, record 0031 §1), and the design agent named proposal cards as stranded the same way while reading the batch's unit (signal 2026-10-22-swancloud-planner-968cd584/02). Today the sweep leaves those as they are: the card stays open in the run record forever, the row shows it as asked, and the user's answer on it reaches nobody.

## What Changes

- At the rail's next read on the host where a card's owner runs, every row's card that host's sign-in can't reach, its owner's newest copy under the row's key posted from another host and never closed, or recorded lost to the owner on any host, is posted again under the row's key through its kind's raise, its summary opening with the words that say an older copy was lost and to dismiss it in the app. This is what a batch's card already gets, now for a proposal's, a landing's, a deploy's and a step's too. The older copy is never asked after or closed from a host that can't reach it, and a raise that finds its row no longer waits posts nothing.
- A landing's owner is the conductor of the team holding the bolt, so its card is raised again on that team's host, where its conductor's cards are; every other card's owner runs on the main level's host.
- A decision record's card, which has no rail row, is raised again the same way on the main level's host while its record is still proposed and was not settled in the pane: crew reads the record on the kit's main as `crew record --proposed` does and posts it again in the design agent's name. A record whose card offered alternatives can't be rebuilt there, since crew keeps no copy of the alternatives file; the read says so, naming the `crew record` command the design agent runs, and that command then posts the card saying the older copy is dead.
- `crew record --proposed` records whether the card it raised offered alternatives, a fact with no words, so a later read can tell.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a card its owner's host can't reach is raised again there, for every card crew raises, not only a batch's; a decision record's card is raised again from its record on the kit's main.

## Impact

- `plugin/lib/plan.py`: `sweep_judged` puts every kind's row in `again`, and a record still proposed whose card is stranded; `sweep_cards` raises them; `raise_proposal`, `raise_proposal_at` and `raise_land` post with the dead-copy summary when handed an older copy; a new record raise for the sweep, sharing `record_status`'s read of the record; `record_status` records the alternatives fact and posts with the dead-copy summary when an older copy is stranded.
- `plugin/lib/ops.py`: `raise_deploy` and `raise_step` post with the dead-copy summary when handed an older copy.
- README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header: the rail's sweep, `crew record` (`docs.2`).
- Tests: `tests/py/test_rail.py`, `tests/py/test_cards.py`, `tests/py/test_ops.py`, `tests/t-cards.sh`.

## Touches

```
plugin/lib/plan.py
plugin/lib/ops.py
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/py/test_rail.py
tests/py/test_cards.py
tests/py/test_ops.py
tests/t-cards.sh
```
