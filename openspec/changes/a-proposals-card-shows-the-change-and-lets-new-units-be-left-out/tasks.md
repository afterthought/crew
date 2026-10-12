# Tasks

## 1. crew draws the card and applies what the user kept

- [x] 1.1 crew draws a PNG of rectangles, lines and monospace text in the standard library alone, with the public-domain misc-fixed 6×13 font it carries (design: *crew draws the PNG itself*; Task notes 1.1; `code.1`).
- [x] 1.2 `crew plan card <n>` prints a proposal's card as Pending You takes it, its title, summary, background, questions (the approval's rationale saying to object by not approving and saying why in the note) and text, and writes its 780-pixel picture, from the plan and the proposal alone (design: *The card is drawn from the proposal applied to a copy of the plan*, *The change as text*, *The card's fields*; Task notes 1.2; `plan.12`, `briefs.9`, `briefs.13`, `code.2`).
- [x] 1.3 `crew plan approve <n> --clear <unit>...` applies the proposal without the cleared new units' commands in one commit, refuses with nothing changed when a kept command names a cleared unit or a cleared unit is not new, and records `Cleared` on the proposal (design: *An approval leaves out what only the cleared units concern*; Task notes 1.3; `plan.3`, `plan.1`, `state.1`).
- [x] 1.4 `crew plan answer <n> <question> <answer>...` gathers a card's answers, split or not, applies the approval once it holds every one, and prints a note beside it to the planner afterwards (design: *crew gathers a card's answers on the planner's host*, *A note beside an approval follows it*; Task notes 1.4; `roles.2`, `state.2`).

## 2. crew refuses a proposal's card in another form

- [x] 2.1 crew's card hook lets through a proposal's card only in the form `crew plan card` prints, its unit questions holding the proposal's new units each once and no words question, and refuses any other naming what is wrong (design: *The hook checks a proposal's card against the proposal*; Task notes 2.1; `briefs.13`, `roles.3`, `read.1`).

## 3. The briefs say so

- [x] 3.1 The planner's brief and the card discipline have the planner post what `crew plan card` prints, upload its picture, carry no artifact but its picture and its text, link no session but for more than fifteen new units, and answer through `crew plan answer` or `crew plan approve --clear` (design: *The briefs*; Task notes 3.1; `briefs.9`, `tests.6`).

## 4. Tests

- [x] 4.1 `tests/t-proposal-card.sh` proves the card's fields, text and questions for none, one, two, seven and sixteen new units, the approval's rationale for a proposal that drops and one that drops and amends nothing, and a valid 780-pixel PNG drawn with nothing installed (Task notes 4.1; `tests.2`).
- [x] 4.2 `tests/t-proposals.sh` proves approval with cleared units, its refusals, and `crew plan answer`'s waiting, applying, declining and note (Task notes 4.2).
- [x] 4.3 `tests/t-cards.sh` proves the hook passes a proposal's card in its form and refuses the others, `tests/moon.yml` is in step, and `tests/suite --affected` ends with "0 failed" (Task notes 4.3; `tests.4`).

## 5. Docs

- [x] 5.1 README, the crew skill and `crew`'s usage header name `crew plan card`, `crew plan answer` and `--clear`, and say a proposal's card is drawn by crew and links no session, and `tests/suite t-docs` ends with "0 failed" (design: *Docs*; Task notes 5.1; `docs.2`).
