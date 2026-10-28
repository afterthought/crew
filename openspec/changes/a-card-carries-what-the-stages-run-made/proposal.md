# Proposal

## Why

The user wants a card that asks about work to carry a link to what the work made: a spike a stage built, a page it published, a running copy to try before a landing. Today a landing row holds a preview server up from the moment the row is posted until the bolt lands, which can be days, and no other card carries anything a stage made. Record 0043, accepted on 2026-10-28, settles the shape with Flume's record 0007: the stage's run writes what it made, crew carries it as written, and a thing that must run is brought up only when the user asks and released when they are done.

## What Changes

- A batch's card carries, under each unit, what that unit's stages recorded as made, each line as the run wrote it: its name, what it is and its address. crew makes, checks and rewrites none of it.
- Until crew runs stages through Flume, crew reads those lines from `made.jsonl` in the stage's place. The conductor's wait keeps a copy, as written, on the team's host, so the lines outlive the place's tidy. When a line is added while the batch's card waits on the user, the card changes in place.
- A line for a thing that must run names the branch and revision that bring it up, never a server's address. The card says how to bring it up: the user writes on the card naming it. The card's owner then runs one crew command, which brings it up through `sluice preview` on the team's host and lists the addresses sluice gives back on the card while it is up. It is released when the user writes that they are done, or when the card closes.
- **BREAKING** A kit's landings card no longer asks sluice for a preview when a row is posted. Where the kit's policy at the bolt's head names a preview, the row carries what brings it up, the bolt branch and its head, and says the preview comes up only when the user asks and goes when they are done. Where the policy names none, the row says "no preview". The preview comes up on the user's ask and is released on their done, at the landing, or when the bolt is held or dropped. It is never held while the card sits.
- When a bolt's head moves, its row says so and names the new head. A preview up at the old head is released and nothing is asked at the new one until the user asks again.
- A card about a landed revision, a deploy's card and a landing's close, carries the commit it landed as and no preview.
- The owners' briefs (main-level ops for a landings card, the planner for a batch's card) say how to act when the user writes on the card asking for a preview or saying they are done. The conductor's brief says the landing row's preview comes up only on the user's ask.
- Tests in the logic tier prove each card's facts, and the end-to-end landing journey proves a preview brought up on the user's ask and released at the landing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a landing row carries the bolt branch and head, or "no preview", in place of a preview held from the row's post; a preview comes up on the user's ask and is released on their done, at the landing, a hold or a drop, or when the head moves; a batch's card carries each unit's made lines as written and changes in place as lines are added; a thing that must run on any card is brought up and released the same way; a card about a landed revision carries its commit and no preview.
- `bolt-teams`: the conductor's wait reads `made.jsonl` in the stage's place at each look and keeps a copy, as written, on the team's host.

## Impact

- `plugin/lib/cards.py`: the landing and landings builders' preview words, the batch builder's made lines, and the words that say how to ask.
- `plugin/lib/plan.py`: the landing row's raise stops asking sluice; a `crew card preview` command that brings a thing up or releases it on the owner's run; the preview record keyed by card and thing; releases at head move, landing, hold, drop and card close; the conductor's wait reading and copying `made.jsonl`; the batch's raise reading the copies on each unit's team host.
- `plugin/bin/crew`, `README.md`, `plugin/skills/crew/SKILL.md`: the new command's usage, together (`docs.2`).
- `plugin/roles/main-ops.md`, `plugin/roles/planner.md`, `plugin/roles/conductor.md`: what the owner does when the user writes on a card for a preview.
- Tests: `tests/py/test_cards.py`, `test_landing.py`, `test_landings.py`, `test_card_commands.py`, `test_rail.py`, a new `tests/py/test_made.py`, `tests/t-journey-land.sh`, `tests/t-briefs.sh`, `tests/moon.yml`.
- Depends on sluice's `preview`, `previews` and `release` as sluice 0.51.3 gives them. sluice previews only a revision a branch it manages has landed, so a made line naming any other branch is refused by sluice, and the card says so in sluice's words.

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
plugin/roles/main-ops.md
plugin/roles/planner.md
plugin/roles/conductor.md
tests/py/test_cards.py
tests/py/test_landing.py
tests/py/test_landings.py
tests/py/test_card_commands.py
tests/py/test_rail.py
tests/py/test_made.py
tests/py/test_batch_answer.py
tests/py/test_batches.py
tests/t-journey-land.sh
tests/t-briefs.sh
tests/t-docs.sh
tests/moon.yml
```
