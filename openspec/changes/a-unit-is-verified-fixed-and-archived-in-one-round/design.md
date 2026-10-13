# Design

## Context

Record 0027, accepted on 2026-10-13 on the user's words in the recovery session, makes a unit's verify one round with no card, grounded in the unit's change as written, and builds record 0006's archive at the merge. Today `conductor.md` step 3 has the conductor read the report, tell the user what it would do about each finding and post a verify card (`verify/<unit>/<stamp>`, a `choice` or `multi`); the rail lists the report as a row until a commit or the merge ends it (`rail_rows`); starting construct, code or merge on a unit in verify names that row's card for the conductor to close (`ends_row`, `stage_ended_row`); a write that takes a unit out of a team's bolt names its verify row (`lost_rows`); the board marks the unit ✎; and crew refuses a chore's merge until verify has run since its last code (`chore_refusal`, `verified`). Nothing archives a change.

The rules this rests on: `state.2`, `read.1`, `code.6`, `code.7`, `code.8`; `briefs.2`, `briefs.11`, `briefs.13`, `briefs.15`; `teams.2`, `teams.4`, `teams.5`, `teams.14`, `teams.17`; `plan.11`; `tests.4`, `tests.6`, `tests.10`, `tests.11`; `docs.2`, `docs.4`, `docs.5`, `docs.6`. Pages whose area this touches: `plan.md`, `teams.md`, `briefs.md`, `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- A unit goes from every task ticked to merged with no wait on the user: verify once, fix once when the report says so, archive, merge.
- Verify answers to the unit's change as written: nothing it finds changes what the change says.
- A change reaches its bolt, and so main, archived.

**Non-Goals:**
- A loop of verify and fix until the report is clean: the user's "later".
- The merge stage's command and gate, which `units-merge-and-bolts-land-only-through-sluice` rewrites; this adds the archive before whatever the merge runs.
- Archiving the changes already open on main: chores, as `chores-beside-units-and-fixes` names them.

## Decisions

### The report marks each finding, and the marks are taken as they stand

Verify checks the code against the unit's change as it is written, its proposal, specs, design and tasks: a finding is where the code falls short of the change or goes beyond it, and the change is never what verify would change (the user, accepting record 0027: "the whole point of verify is that it should be grounded in the original proposal"). Its brief has it end the report OpenSpec's verify produced, left whole, with a section of its own, `## What to do`: a line per finding, in the report's order, starting **fix** or **leave**, with why. Fix is where the code does not do what the change says, or does more, and can be put right in code, tests, a task's own work or the Touches block; leave is what is not worth a round or not the unit's. A CRITICAL finding is never left. A chore's report is marked the same way, against its words.

The report's author decides, not the conductor: the verify agent has read the change against its code, and the conductor writes no design (`briefs.1`). The conductor chooses no findings, posts no card, asks the user nothing and takes nothing of it to the planner. crew does not parse the section: the conductor reads it and the coder reads it, and a check on its shape would refuse a stage's deliverable over prose.

Alternatives considered: crew reading the marks and starting the fix round itself (a parser of an agent's prose deciding a stage); the conductor's options without a card (the conductor deciding design).

### One fix round is a code stage told the report's path

`crew unit run <unit> code "Fix every finding the verify report at <path> marks fix."`, a fresh coder in the unit's slot (`teams.2`), with `/opsx:apply` as every code stage has, so the kit's apply guidance holds. The coder fixes every finding marked fix and only those, commits each, and runs the tests of what it changed; a finding marked fix that would need a task reworded or a spec changed is no fix, and it stops to say so (`briefs.2`). Its deliverable is code's: a commit since it began with every task ticked (`teams.4`). No stage is new: the plan's step 2 is the code stage run once more.

A fix round that stops short or fails is a stuck stage: the conductor tells the user as it tells one today, and runs it again, or merges without it, only on the user's word.

### A verify stands through its fix round

`verified` reads a delivered verify end later than every construct start of the unit; a code start after it no longer undoes it. So a unit fixed once still waits to merge, a forecast reaches it as a settle (`reach_way`, `teams.14`), and a chore's merge needs its verify once (`chore_refusal`, `teams.5`). Construct run again undoes it, since the change is new and its round starts over.

### A unit's merge archives its change first, and delivers only so

The coder's brief has a unit's merge run `openspec archive <unit> --yes` in its place and commit it as `docs(openspec): archive <unit>` before the merge command the prompt names (record 0006: "the archive is the last commit before the head is submitted"). An archive openspec refuses, a delta naming a requirement the specs do not hold yet, stops the stage with openspec's words, and nothing merges (record 0006: such a unit merges after the sibling that adds it). The merge's prompt is unchanged, so the merge stage `units-merge-and-bolts-land-only-through-sluice` rewrites keeps its words.

`delivered` reads a unit's merge as delivered only once its bolt holds the change archived (`gather.archived`); a bolt holding it open is not the deliverable, and the wait names it. The unit still reads `merged`, since a bolt holding its change either way merged it (record 0006).

`gather.place` reads a place whose change its merge archived, `openspec/changes/archive/YYYY-MM-DD-<unit>` with no open `openspec/changes/<unit>`, from the archive: its tasks, its Touches, its planning complete, and `archived` true. Without it, a unit between its archive and the bolt holding it would read `construct` (`read.1`).

Alternatives considered: crew archiving at the merge's start (crew committing in a unit's place, with openspec's refusals for crew to word); an archive stage of its own between verify and merge (a stage with nothing to do but the archive when nothing is to fix).

### The verify row, its key and its card go

`RAIL` loses `verify`; `rail_rows` makes no row of a report, and gather no longer reads the reports folders for the rail. `card_refusal` no longer gives a conductor `verify/<unit>/<stamp>`; the card hook drops the verify form but keeps the key among those it records, and `CARD_KEYS` keeps it, so a card posted before this lands is a card whose row is gone: the rail lists it with the tell to close it, `crew card close` and `crew card end` take it, and the sweep ends its session. `stray_cards` and the sweep judge no verify key blind, since no row can hold one. `ends_row` and `stage_ended_row` go, since no stage ends a row; `lost_rows` names only a landing row. The board's units carry no markers, and ✎ goes from the board, the views and the page (`code.8`); `status.js` reads no marker and does not change.

### Specs that other open changes touch

`Each rail row has a card key`, `The owner of a row posts its card`, `A card carries what the user would read and the row's answers` and `A card's words are the document's own` in `rail-cards`, and `A session is started for a card's row by its key` in `card-sessions`, are also modified by changes open on main with every task ticked (`units-build-at-once-and-are-reviewed-in-batches`, `a-batch-cards-notes-are-its-note-and-its-sessions`, `a-card-lost-to-its-owner-is-posted-again`, `a-proposals-card-shows-the-change-and-lets-new-units-be-left-out`). This change's deltas are written on the text those changes leave, less what it drops, so they hold once those are archived first. The `crew card` requirements `a-card-reaches-the-user-when-the-tools-drop` added, archived on main, show a landing card where they showed a verify card. `every-crew-card-goes-through-crew` and `units-merge-and-bolts-land-only-through-sluice`, not built, are not read here; whichever archives later carries the other's words.

## Risks / Trade-offs

- [A finding marked leave that the user would have fixed] → The report keeps it, and the user can read every report; one round is the user's choice, a loop later work.
- [A merge agent merges without archiving] → The merge never delivers and the wait says why; the change is then archived by a chore, as the fourteen open on main are.
- [A merge stage in flight when this lands, started under the old brief] → Its deliverable is read the new way: told stuck, the conductor archives it by a chore.

## Migration Plan

A verify card open when this lands is listed by the rail as a card whose row is gone, for its owner to close; nothing else carries over.
