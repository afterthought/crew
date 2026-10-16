# A card the user answered is followed by its new version

## Why

crew changes its own card in place when the card's thing changes (record 0031 §3): a record revised after the user's note, a proposal rewritten after a note, a landing whose head moved. Pending You changes a card only while it waits on the user. Its guide, read 2026-10-16 (pendingyou.com/skill.md, "Follow up with a new card"), says: "`update_request` works only while the question waits on them. Once they've answered, post a new card that `follows` it", and "Use one `idempotencyKey` per question". A revision after the user's note is always a revision of an answered card. So `row_card_change` was refused, the refusal recorded, and the user never saw the new version. A row's card raised again after its last card closed, such as a landing raised after a defect held it, was posted under the same key, and Pending You gave the closed card back.

## What Changes

- `row_card_change`: while the card waits on the user, it is changed in place, as before. Once the user has answered it, crew acks it with the change note as its outcome. It then posts the new version as a new card that follows it, in the same owner's name. The run record keeps the close of the answered card and the post of the new one, both under the row's key.
- Every card crew posts under a row's key after a card of the owner's under that key closed takes the key with its revision, `<key>:<n>`, as its idempotency key. A card still open under the key keeps its own key, so posting it again gives it back. This covers an answered card followed by its new version, a declined landing raised again, and a lost card posted again. The run record and the rail know the card by the row's key alone.
- `crew card read` and the act find the latest card under the row's key, as they already do: the newest one posted there that no close has closed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a card the user answered is followed by its new version, and a card posted after a closed one under the same key takes the key with its revision.
- `main-level`: a record revised after the user's note goes on a new card that follows the one they answered. A record revised while its card waits still changes that card in place.

## Impact

Follows `crew-record-raises-a-records-card`, landed, whose revision after a note it makes reach the user; the design agent's brief, README and crew's usage say so. The rest of record 0031's series rebases onto it: `crew-raises-a-proposals-card` changes a card after the user's note, and `crew-raises-a-bolts-landing-card` raises a landing again after a defect held it.

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
tests/py/test_card_commands.py
tests/py/test_cards.py
tests/t-cards.sh
plugin/roles/design.md
tests/t-briefs.sh
README.md
plugin/bin/crew
```

`cards.py` gains `revision` and `post_key`. `plan.py` changes `card_posted` and `row_card_change`, gains `REVISED`, and changes the docstrings of `raise_record` and `record_status`. `design.md` changes *Decision records*' note bullet, and `tests/t-briefs.sh` its pin. README and the usage header change `crew record`'s lines.
