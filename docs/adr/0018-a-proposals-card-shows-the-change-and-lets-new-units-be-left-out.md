---
number: 18
title: A proposal's card shows the change drawn and in text, and lets the user leave a new unit out
status: accepted
date: 2026-10-11
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A proposal's card shows the change drawn and in text, and lets the user leave a new unit out

Deciders: the user, from the Flywheel site spike on 2026-10-10 and 11 ("i think if possible, the pendingyou card should make it easy to unselect one or more proposed units. feedback on removals or ammendments would need to be done through notes/chat"; "we know now that the best upload for pending you is a PNG, and probably we would want that to be phone-sized"; "You want it to be scannable and legible, maybe as an ASCII-type thing"; "The only problem with it is that I am forced to answer this third question"), who approved the third sample card on his phone (req_ec261ceb0dee437990a6) and sent it to crew (signal 2026-10-11-chuck-mac-studio-7195e4e7/01); swancloud-design.
Sources: `agentplot/flywheel-next:openspec/explorations/bolt-plan-change-diagram/proposal-card.md` at 3bf57919, read whole, with its `examples/` (the card as sent, the picture, the text) and `gen.ts`; `plugin/roles/planner.md` *Cards*; `docs/architecture/plan.md` plan.3 and plan.4; record 0005 as amended 2026-10-10 (an image is uploaded; a document's substance is inline Markdown; no file); Pending You's guide 2.52 as that page read it: a PNG uploads and an SVG does not, every question is required, a question lists two to five options, a card takes two to four questions, a card with questions names what it is about, the user may split a card and the answers come back on the splits.

## Context and problem statement

A proposal is where the user first meets a unit: the planner adds units inside proposals, and the design agent's queued units raise no card until a proposal moves them into a bolt. Today a proposal's card is one approval of the whole, with the case and a line per change; the user can take all of it or none, and reads the change as prose. The user wants the change seen at a glance on the phone, drawn and as scannable text, and a way to leave one or more new units out while approving the rest, with words only where words are needed.

## Decision outcome

A proposal's card, posted by the planner under its row's key as today, is:

1. A title with the counts: dropped, amended, new.
2. A summary of three short lines: what the proposal is, the unit count before and after, the bolt's goal.
3. The picture: a PNG twice a phone's width, uploaded as record 0005 has it, showing the bolt once approved in order, each dropped unit struck where it stood with its reason, each amended unit's old intent struck above the new, each new unit marked. The picture is drawn from the proposal's data by crew, with no browser and no agent's hand: by a renderer the kit puts on the host's path, named when absent, or by crew itself; a card with no picture still carries everything else.
4. The change as text: a monospace block at most about forty characters a line, one line per change with its kind, and the bolt's order once approved with each unit marked, drawn from the same data.
5. No plannotator link: the picture, the text and the case are the proposal whole, read on the card, and there is no session to open or to end (the user, 2026-10-11, approving proposal 102 with the note "I approve this although I don't think we really need a planotator for this one if we have the content right in the card and the picture", signal 2026-10-11-swancloud-planner-99c33984/01). Only a proposal the card cannot hold whole, one of more than fifteen new units, links the whole as `briefs.9` has it.
6. The approve question, whose detail is the case as bullets and whose rationale says how to object: to keep a dropped unit or change an amendment, the user does not approve and says why in the card's note, which the planner reads and answers with the proposal written again; a note beside an approval changes nothing of what is applied (batch 5's reviewer, 2026-10-11: a note never holds an approval, so a hint that says "object by a note" misleads).
7. One multiple-choice question per five units new to the bolt, added or moved in, every option ticked, each option the unit's name with its intent as detail and "cleared: not added; the rest still applies" as consequence; none when the proposal adds no unit. There is no text question, since Pending You makes every question required; the note is the place for words. A proposal with more than fifteen new units carries no unit question and links the whole.

What crew does with the answer:

- **Approved with every unit ticked**: the approval applies every command, as today.
- **Approved with units cleared**: the approval applies the proposal without the cleared units' commands, their `unit add` or `unit move` and any command that only concerns them, in one commit, and records which were cleared and by whom; a command that stays and names a cleared unit (an order against it, an `After` on it) refuses the whole, and the planner writes the proposal again without the unit, with a new card. A cleared unit from the queue stays in the queue; a cleared new unit is never made. This amends `plan.3`: an approval applies the commands the user read and kept, in one commit or none.
- **Not approved**: as today, with the note's words to the planner.
- **A note beside an approval**: the approval is applied, and the note goes to the planner as the user's word, which proposes whatever the note asks as a new proposal; an approval never waits on a note's reading, since the user chose to approve.
- **A split card**: crew gathers a proposal's answers from the card and its splits before acting, and acts once it has the approve question's answer and every unit question's.

The picture's animated form, the change a step at a time, belongs to crew's page as a proposal's view once `the-board-is-a-page` exists; this record does not plan it.

### Consequences

- One unit in crew, `a-proposals-card-shows-the-change-and-lets-new-units-be-left-out`: the card's parts drawn from the plan's records and the proposal's `Case` and `Do` lines, the renderer read, the approval with cleared units, the splits gathered, the planner's brief and the card discipline, and the `rail-cards` and `plan-proposals` deltas.
- `plan.3` and `briefs.13` amended; record 0005's proposal card bullet points here.
- `briefs.9` narrowed on 2026-10-11 to a document the card cannot hold whole; the unit's intent, which named the link first, is amended by the planner's proposal.
- The exploration's `gen.ts` is the construct's reading of what the picture, the text and the card's words are, not code crew ships: crew is Python with the standard library (`code.1`).

## Considered options

1. The card above, crew applying the approved subset: the user read and chose each command, so the approval is still of what was read.
2. Every cleared unit sends the proposal back to the planner for a new proposal and card: a round trip for a choice the user already made.
3. A text question for feedback: refused by the user, since Pending You makes it required.
