# A proposal's card shows the change and lets new units be left out

## Why

A proposal is where the user first meets a unit: the planner adds units inside its proposals, and a unit the design agent queued raises no card until a proposal moves it into a bolt. Today a proposal's card is one approval of the whole, its words the case and a line per change, so the user reads the change as prose and can take all of it or none. On 2026-10-10 the user asked that the card "make it easy to unselect one or more proposed units", with "feedback on removals or ammendments ... done through notes/chat", and that the change be seen at a glance on the phone, as a phone-sized PNG and as scannable text. The user approved the third sample card on the phone (signal 2026-10-11-chuck-mac-studio-7195e4e7/01), and record 0018 settles the card and what crew does with each answer; `plan.3`, `briefs.9` and `briefs.13` are already amended to it.

## What Changes

- **crew draws the card.** A new command, `crew plan card <n>`, reads only the plan and proposal `n` and prints every part of its card: a title with the counts (dropped, amended, new, moved), a three-line summary (what the proposal is, the unit count before and after, the bolt's goal), the case as bullets, the change as a monospace text block of at most forty characters a line, and the questions. It also writes the picture: a PNG 780 pixels wide, twice a phone's width, showing each bolt the proposal touches once approved, in order, each dropped unit struck where it stood with its reason, each amended unit's old intent struck above the new one, each new unit marked. crew draws the PNG itself, in Python's standard library with a bitmap font it carries: no browser, no renderer to install and no agent's hand.
- **The card asks what the user decides.** Its first question approves the proposal; its detail is the case as bullets and its rationale says how to object: to keep a dropped unit or change an amendment, the user does not approve and says why in the card's note, and the planner writes the proposal again; a note beside an approval changes nothing of what is applied. Then one question per five units new to a bolt (added, or moved in from the queue or another bolt), every unit ticked, each cleared to leave it out. A proposal with no new unit is a plain approval card. No question asks for words, since Pending You makes every question required. The card links no plannotator session: the picture, the text and the case are the proposal whole. Only a proposal of more than fifteen new units, which the card can't hold, carries no unit question and links its session instead.
- **An approval can leave units out.** `crew plan approve <n> --clear <unit>...` applies the proposal without each cleared unit's commands (its `unit add` or `unit move`, and any command that names only cleared units) in one commit, and records the cleared units on the proposal. A command that stays and names a cleared unit (an order against it, an `After` on it) refuses the whole approval, with nothing changed, so the planner writes the proposal again without the unit. A cleared unit from the queue stays in the queue; a cleared new unit is never made.
- **crew gathers a card's answers, split or not.** `crew plan answer <n> <question> <answer>` records one question's answer as the planner reads it, from the card or from a card the user split off it, and applies the approval only once it holds the approve question's answer and every unit question's. A note given beside an approval does not hold the approval: crew applies it, then prints the note to the planner as the user's word, to propose whatever it asks as a new proposal.
- **crew checks the card's form.** crew's card hook takes a proposal's card as an approval, or as a grouped card whose first question approves and whose other questions are the proposal's new units, each exactly once, and refuses any other form, a words question among them.
- **The briefs say so.** The planner's brief and the card discipline have the planner post what `crew plan card` prints, upload the picture, and answer through `crew plan answer`. The card discipline's rule that a card carries an artifact only for a picture or a document's Markdown names the proposal's picture and its text, which stays plain monospace text so it reads on the phone without wrapping.
- README, the crew skill and `crew`'s usage header say all of it (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plan-proposals`: approval with cleared units; new requirements for the card drawn from the plan and the proposal, for the answers gathered from a card and its splits, and for a note beside an approval.
- `rail-cards`: a proposal's card becomes the drawn approval with a choice per new unit, links no session unless it holds more than fifteen new units, and crew refuses a proposal's card in any other form; the requirements on a card's link, its words, its artifacts and the kinds no row's card takes say the proposal's exception.

## Impact

- The planner's brief and the card discipline every owner carries, at each agent's next fresh start. Open proposal cards posted before this lands stay as they are; a new card is posted only for a proposal opened after.
- `crew plan approve <n>` with no `--clear` behaves as today.
- The `rail-cards` delta modifies the requirement on a card's artifacts that `an-image-on-a-card-is-uploaded` adds, so that change is archived before this one.
- `crew plan answer` keeps a proposal's gathered answers on the planner's host under `~/.local/state/crew/cards/<label>/proposal/<n>/`, beside the card's session files, until the approval or the decline; nothing of it reaches the flywheel's branch but the approval itself (`state.2`, `state.4`).
- The proposal record gains a `Cleared` field, one per cleared unit, written only by an approval.
- Nothing is added to devenv and nothing outside the standard library is imported (`code.1`).
- After it lands, the design agent clears the `plan.3` and `briefs.13` lines from `_open.md` and names what builds them in those rules' details (`docs.7`); this change edits nothing under `docs/`.

## Touches

```
plugin/lib/plan.py
plugin/lib/picture.py
plugin/lib/font.py
plugin/hooks/cards
plugin/lib/crew.py
plugin/roles/planner.md
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/t-proposal-card.sh
tests/t-proposals.sh
tests/t-cards.sh
tests/t-briefs.sh
tests/moon.yml
```
