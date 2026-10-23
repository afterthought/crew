## Why

When several bolts are proven at once, the user gets one landing card per bolt, approves each on its own, and main-level ops lands them one at a time; the order lives only in ops's replies, and two waiting bolts that touch the same files are found only when sluice refuses the second. In wldn on 2026-10-23, with ten landing cards open, the user asked for "only one landing card at a time that shows the order in which they should be submitted to the queue", and ruled that ops submits every approved bolt into sluice's queue together: "This is standard behavior" (wldn signals 2026-10-23-wldn-ops-658ea7d1/01 and 6bdfe94a/01). Record 0031, as amended and accepted on 2026-10-23, answers with one landings card per kit's main, and `briefs.11`, `briefs.13` and `plan.16` already say so; crew still builds the card per bolt and ops's brief still says "Land one bolt at a time".

## What Changes

- **One card per kit's main.** crew raises one landings card for each kit with a proven bolt waiting, keyed `land/<kit>`, in main-level ops's name, on the partition's main host. It lists every proven bolt of the kit as a row, in the order crew proposes: the plan's order. It is changed in place as a bolt is proven, moves its head, is held for a fix or lands, and closed when nothing waits to land on that kit's main; the next proven bolt raises it again.
- **Each row carries what the bolt's own card carried**: the bolt and its conductor, its units and chores, the batches its units were read in, sluice's verdict at its head and when, how far main has moved since the bolt was cut, sluice's pull request, its reading session's link and its preview's addresses.
- **Each row carries the conflicts crew forecasts** between the bolt and main, and between the bolt and each bolt above it on the card, so a bolt that must take another's merge first is seen before the send, not at a refusal.
- **The user's ticks and one send are the word.** Every row that can land is a box, ticked as crew proposes; the user clears what should wait and sends once. A lone bolt keeps today's hold-to-approve of high risk. A note on the card can move a bolt in the order or name a defect, which ops passes to that bolt's conductor.
- **Ops submits them in order, each closed as it lands.** `crew bolt submit` takes several bolts. It queues each in sluice behind the one before, so sluice tests them as one chain. It closes each with `crew bolt land` as it lands, and holds a refused one on its row for its team's fix while the rest go on.
- **A refused or held bolt stays on its row**, saying why, with no box, until its fix merges and it reads proven again.
- **Each row's reading and preview stay with the bolt**, on its team's host, under `land/<bolt>`: started when the bolt reads proven, as today, and ended when its row leaves the card. The conductor waits on the reading's notes as today and holds no landing card. It tells main-level ops that its bolt is proven.
- **The rail shows one landing row per kit**, holding each bolt that waits on it. The agents' views and the board mark each bolt from that row.
- **The briefs follow.** Main-level ops's brief takes the landings card and its send as the word, and no longer says to land one bolt at a time. The conductor's brief loses its landing card and keeps its reading and its fixes. The planner's brief and crew's skill name the kit's card. **BREAKING** for open per-bolt landing cards: the rail's sweep withdraws each, saying its bolt is now a row of its kit's landings card, and that card is raised in its place.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the landing card becomes one landings card per kit's main, in main-level ops's name, with a row per proven bolt in order, its forecasts, ticks and one send; who acts on its answer; its rows' previews.
- `main-level`: main-level ops lands the ticked bolts in the card's order, submitting each into sluice's queue behind the one before and closing each as it lands.
- `bolt-teams`: `crew bolt submit` takes several bolts in order, and a refused one is held on its row while the rest go on.
- `crew-rail`: one landing row per kit, holding each bolt that waits to land on its main.
- `card-sessions`: a landing's reading is its row's, keyed by the bolt on its team's host, its link carried on the kit's card, waited on by its conductor without a card of its own.

## Impact

- `plugin/lib/plan.py`: the landing's raise, its facts and forecasts, the rail's landing rows, row owners and sweep, `crew bolt submit` over several bolts, the card and session commands for `land/`, the merge's end, a fix's start and a landing's close.
- `plugin/lib/cards.py`: the landings card's builder, what it follows, its key's object.
- `plugin/lib/board.py` and `plugin/hooks/status.js`: each bolt marked from its kit's landing row (`code.8`).
- `plugin/roles/main-ops.md`, `conductor.md`, `planner.md`, `plugin/lib/crew.py`'s card words, and, for `crew bolt submit`'s several bolts, `README.md`, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew` (`docs.2`).
- Tests in the logic tier and the end-to-end landing and card journeys, with the stubs they run on.
- No rule changes: `briefs.11`, `briefs.13` and `plan.16` already say this, amended with record 0031 on 2026-10-23.

## Touches

```
README.md
plugin/bin/crew
plugin/lib/plan.py
plugin/lib/cards.py
plugin/lib/board.py
plugin/lib/crew.py
plugin/hooks/status.js
plugin/tests/**
plugin/roles/main-ops.md
plugin/roles/conductor.md
plugin/roles/planner.md
plugin/skills/crew/SKILL.md
tests/py/**
tests/contract/test_git.py
tests/t-journey-land.sh
tests/t-cards.sh
tests/t-briefs.sh
tests/stubs/**
tests/moon.yml
```
