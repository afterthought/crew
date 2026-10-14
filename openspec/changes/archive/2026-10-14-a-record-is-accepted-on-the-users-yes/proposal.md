## Why

The design agent wrote decision record 0016 and committed it as accepted on its own reading, and the user found out afterwards: "I don't think the design agent really consulted me. I think it just added the ADR so I think this is one part of the process we should tweak. I think the design agent should get approval and present ADR changes to me before locking them in" (2026-10-11). The rule now says a record is proposed until the user says yes (`briefs.15`), but the design agent's brief still has it record and commit a decision as settled, and crew's card hook refuses any card the design agent posts, so it couldn't ask on a card even if its brief told it to.

## What Changes

- The design agent's brief gains a section on decision records: every record it writes, and every amendment to one, is committed as proposed and put to the user on one Pending You card in the record's own words. It becomes accepted only on the user's yes, and the record says so, with the date and anything the user added in their own words. Where the user settled something in their own words while talking the design through, the record quotes those words as the user's decision, and the card says which part that is.
- Until the yes, a rule drawn from the record is written marked as proposed, and no unit is queued from it. A note asking for changes means the record is revised, still proposed, and put on a new card. A no means the record is marked rejected, in the user's words, and the rules drawn from it come out.
- The record's card is the one card the design agent posts. It goes under a key of its own, `record/<kit>/<number>/<commit>`, where the commit is the one that proposed the record or the amendment, so each new version of a record gets a new card.
- crew's card hook lets the design agent post under that key, for a kit its partition builds, and nobody else. It checks the card is an approval of low risk with no options or steps, and records the card in the run record with its key.
- `crew rail` lists the open record cards under a heading of their own, with who asked and when, and stops listing them as cards whose row is gone.
- README, the crew skill and the usage header of `crew rail` say the same.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: the design agent puts every record it writes or amends to the user, and a record is accepted only on their yes.
- `rail-cards`: the design agent's record key, the record card's form, how it is recorded, and where the rail shows it.

## Impact

- `plugin/roles/design.md`: the decision-record section and its card discipline.
- `plugin/lib/plan.py`: `card_refusal` (the record key) and the rail's text (open record cards apart).
- `plugin/hooks/cards`: the record key's object and form.
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header of `plugin/bin/crew`.
- Tests: `t-cards.sh`, `t-rail.sh`, `t-briefs.sh`. No test is added or removed and none reads a new file, so `tests/moon.yml` is unchanged.
- Nothing changes in Pending You, the rail's rows, or the form of any row's card.

## Touches

```
plugin/roles/design.md
plugin/lib/plan.py
plugin/hooks/cards
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/t-cards.sh
tests/t-rail.sh
tests/t-briefs.sh
```
