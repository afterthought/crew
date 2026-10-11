---
number: 19
title: An elaboration works one question in one workspace and ends on one card
status: proposed
date: 2026-10-11
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# An elaboration works one question in one workspace and ends on one card

Status: proposed to the user on 2026-10-11, as `briefs.15` has it; accepted only on their yes. Record 0016, the spike, waits on this one.

Deciders: the user, who asked for it (2026-10-11: "I think the real concept is intent elaboration and if we could have some simple version of intent elaboration, that's what I really want. It doesn't have to be that a spike runs beside the design agent. Again it's about the elaboration and I would probably want one workspace per elaboration." "I don't want to have some hard-coded thing just for spikes." "What's the simple mental model for an elaboration in Crew that gets us 80% of the benefit of the design from Flywheel Next without fully implementing it?"), with a side session's starting point, not a ruling: one elaboration is one question, one session and one workspace with its own worktree; its notes and any prototype stay in its folder; what it concludes comes to the user as one document to approve; prototype code reaches main only through a unit.

Sources, read whole on 2026-10-11: `agentplot/flywheel-next` main at 3bf57919, `definitions/intent.yaml` (version 6), `definitions/elaboration.yaml` (version 2), `definitions/elaboration-types/` (`self-closing@3`, `standing@3`, `with-operator@4`, `fundamentals@2`); crew's `openspec/explorations/` (`findings-to-design`, `command-cost`, `board-from-crew-state`, `testing-strategy`) and `docs.1`; the signal moves (`design.md`); record 0016; the spike `swancloud-spike-clan-core` run today in a pane with no crew support, which ended with its findings as six signals and a tell.

## Context and problem statement

Flywheel Next's model, as read: an **intent** is one long-lived thread of design work about one subject, proposed by curation or opened by the operator, with many elaborations over its life, its own line off the blueprints' shared line, and a change directory that holds its elaborations' records while the book holds what they conclude; it closes only by the operator. An **elaboration** is one unit of design work on an intent: one session, one conversation, one place; its **type** decides how it ends: self-closing (research, ends itself when its document is written; idle two hours is a stall), standing (a prototype or page, kept running until the operator finishes it; idle is offered as finish or keep), with-operator (a conversation the operator is in, ended only by their word), fundamentals (writes the book's invariants). It goes proposed, approved, placing (its own place off the intent's line), working, writing-back (records fanned out to each covered intent), finishing (a self-closing place merges into the intent's line; a standing one is kept until finished), done. Deliverables are the book's chapters, claims, maps, diagrams, a surface specification.

crew has the parts around it and not the middle: signals and their moves (`attach` to an open intent, `new-territory` for a cluster no claim covers), the design agent's records (rules, decision records, specs), `openspec/explorations/<name>/` for readings and explorations (`docs.1`), units as OpenSpec changes, herdr workspaces, Pending You cards, plannotator sessions on a document. Record 0016 added a spike: a standing elaboration by another name, hard-coded to prototypes, and committed as accepted without the user.

The question is the simple model that gives most of Flywheel's benefit: a question worked somewhere of its own, with its notes kept, concluded in one document the user approves, and nothing reaching main but through a unit.

## Decision outcome

1. **An intent is a question the design holds open**, in one sentence, named like a unit. crew records it on the flywheel's branch (`intents.rec`: the name, the question, who opened it and when, closed when) when the user opens one in their own words or the design agent proposes one from clustered signals, the `new-territory` move's target, and the user says yes. Signals `attach` to it as today. It closes only on the user's word, given on a conclusion card.

2. **An elaboration is one run at that question**: one session, in one herdr workspace named for it, in one worktree of the kit the question is about, `<kit>/elaborations/<name>` on `elaboration/<name>` cut from main through the kit's worktree tool, so the kit's hooks run. Its prompt is the question, the intent's signals and the records that bear on it, and the design agent's name. Everything it makes stays in `openspec/explorations/<name>/` of that worktree: readings, notes, mockups, pages, prototype code. There is no type. A prototype that must keep running is kept running by its session, and the session stays until the user has answered.

3. **It ends on one document**, `openspec/explorations/<name>/conclusion.md`: the question; what was read, with where; what it proposes, as records to write or amend, units to queue, a prototype to keep or drop, each in one line the user decides from. The session tells the design agent once, and the design agent puts the conclusion to the user on one card: its words inline, a plannotator session on the folder, and the answers *accept*, *accept and close the question*, *go on*, with a note, and *drop*. Accept: the design agent writes the records as proposed and accepted on that same yes, since the card carried their words (`briefs.15`), queues the units with the conclusion as their source, and commits the folder's documents, never its code, onto main under `openspec/explorations/<name>/` as its record. Go on: the note is the session's next prompt, in the same workspace. Drop: nothing lands, and the branch is kept as `plan.10` keeps unmerged work.

4. **Prototype code reaches main only through a unit**, whose source names the conclusion and whose construct reads the branch. crew never merges or lands an elaboration branch; its worktree is kept while a unit that reads it is unmerged and tidied as `plan.9` tidies once the user says so.

5. **crew's part is small**: `crew intent open <name> "<question>"` and `crew intent close`; `crew elaborate <intent> --repo <kit>`, which makes the worktree and the workspace and starts the session; the session's `crew elaborate <name> --conclude`, which ends its run and tells the design agent; the rail row `elaboration/<name>` from the conclusion's existence, whose card is the design agent's; the tidy. Nothing else is hard-coded: a spike is an elaboration whose conclusion keeps a prototype; research is one whose conclusion is its readings.

What is left out of Flywheel's model, and why: elaboration types, since one ending serves every kind and the user's answer is the only finish; an elaboration covering several intents, since one question is one intent; the intent's own line and its archive, since main holds the conclusion as a record and the branch is kept; the book and claims, since crew's records are its rules, decision records and specs; the close offered by the machinery, since the user closes a question on a conclusion card.

### Consequences

- Record 0016 is superseded by this one when accepted; `a-spike-runs-beside-the-design-agent` is dropped or amended to the elaboration's unit, the planner's proposal.
- Units, queued only once this record is accepted (`briefs.15`): `an-intent-is-a-question-crew-holds-open` (`intents.rec`, `crew intent`, the `new-territory` move's target), `an-elaboration-works-one-question-in-one-workspace` (`crew elaborate`, the worktree, the workspace, the session's brief, the conclusion, the rail row and its card, the tidy).
- `plan.9`'s layout gains `<kit>/elaborations/`; `design.md` gains the elaboration as the way a question is worked; `docs.1`'s exploration is the elaboration's folder.

## Considered options

1. Flywheel Next's model whole: intents with lines and archives, typed elaborations, a book and claims. More than crew needs and a second engine beside crew's files.
2. Record 0016's spike alone: a prototype-only kind, hard-coded, with research and conversation left out.
3. This record: one question, one workspace, one document, one card; what it keeps of Flywheel is the shape, what it drops is the machinery.
