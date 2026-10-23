# Proposal

## Why

A decision record becomes accepted only on the user's yes (`briefs.15`). When the user settles a record with the design agent in its pane, the design agent runs `crew record <kit> <number> --proposed --settled-in-pane`, and crew records the yes and raises no card on the agent's word alone. Nothing checks that the user said yes. Record 0031, as amended and accepted on 2026-10-22, says crew records a pane answer only from words it reads in that session's transcript as the user's (`signals.5`), and names `crew record --settled-in-pane` as one of the commands that reads them. The design agent named the gap when it closed the batch work: "`crew record --settled-in-pane` still takes the planner's word on trust rather than reading your words from the transcript, though record 0031's amendment says it should" (signal 2026-10-22-swancloud-planner-968cd584/03). A batch answered in a main-level pane is already recorded this way (`crew card answer`, built in this bolt). This change gives a record settled in the pane the same check.

## What Changes

- `--settled-in-pane` now takes the user's words: `crew record <kit> <number> --proposed --settled-in-pane --excerpt "<the user's yes, as they wrote it>"`. Each of the two flags is refused without the other.
- crew looks for the words in the design agent's own session transcript on this host. It records the record settled in the pane only when it reads them as the user's (`signals.5`). The agent's own words, words another agent passed on with `crew tell`, crew's own messages and a tool's output are each refused with their own reason. So is a transcript crew can't read (`read.1`). Nothing is recorded on a refusal.
- Only the partition's design agent records a record settled in its pane. Any other caller is refused.
- On a refusal, the design agent runs `crew record … --proposed` without the flag, and the user answers on the record's card as usual.
- The run record keeps no words (`record.3`). The `record.proposed` entry still carries `State: settled in the pane`, and now also names the transcript record the words came from and how long they were.
- The design agent's brief says to pass the user's words, and what to do when crew refuses them.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: a record settled in the pane is recorded only from the user's yes, which crew reads in the design agent's own transcript as theirs. Words crew can't read as the user's are refused, and nothing is recorded.

## Impact

- `plugin/lib/plan.py`: `record_status` and its parser take `--excerpt`. A pure refusal reads the caller and the verdict. The verdict half of `pane_answer_refusal` is shared with it. The usage docstring changes.
- `plugin/roles/design.md`: how to run `--settled-in-pane`, and what to do when it is refused.
- Tests: `tests/py/test_cards.py`, `tests/py/test_batch_answer.py` (unchanged words, kept green), `tests/t-cards.sh`, `tests/t-briefs.sh`.
- `README.md`, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew`: the new flag, as `docs.2` asks.

## Touches

```
plugin/lib/plan.py
plugin/roles/design.md
tests/py/test_cards.py
tests/py/test_batch_answer.py
tests/t-cards.sh
tests/t-briefs.sh
README.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
```
