# Tasks

## 1. crew refuses a row's card in another form

- [x] 1.1 The card hook knows each row's form, the review card's an approval with a note, and says what is wrong with a card that departs from it (design.md, decision 1; Task notes 1.1).
- [x] 1.2 Before Pending You's `post_request` or `update_request` runs in a crew session, the hook refuses a row's card in another form with the form to use, refuses what it cannot check, its own input unreadable among it, and lets every other card, session and server through (design.md, decision 2; Task notes 1.2).
- [x] 1.3 `tests/t-cards.sh` covers each row's form refused and let through, the review card as an approval, an update that takes a landing card out of high stakes, input the check cannot read, and the cards and sessions the check leaves alone (design.md, Task notes 1.3). Verify `tests/suite t-cards` ends with "0 failed".

## 2. The briefs

- [ ] 2.1 The conductor's and planner's *Cards* name each row's card in Pending You's kinds, the review card an approval whose decline carries a note for changes, the landing card a high-stakes approval whose yes tells main-level ops to land and never a step to land it (design.md, decision 3; Task notes 2.1).
- [x] 2.2 The card discipline says a row's card takes its row's form and crew refuses another (design.md, decision 3; Task notes 2.2).
- [x] 2.3 The operator agent's brief posts no card, sends nothing for a wait whose card is open on the rail, and shows a wait with none as a notification (design.md, decision 4; Task notes 2.3).
- [ ] 2.4 `tests/t-briefs.sh` pins 2.1 to 2.3 in the filled briefs (design.md, Task notes 2.4). Verify `tests/suite t-briefs t-roles` ends with "0 failed".

## 3. The docs

- [ ] 3.1 `briefs.13` reads as built, `_open.md` no longer lists it, and README says a row's card has its row's form, a review's an approval with a note, and crew refuses another (design.md, Task notes 3.1). Verify `tests/suite t-docs` ends with "0 failed", then `tests/suite --affected` ends with "0 failed".

## Workflow follow-up

- Archive after `the-rail-is-answered-through-cards` (archived), `a-card-links-a-plannotator-session`, `a-landing-card-is-the-heads` and `a-card-reads-whole-at-a-glance`, whose deltas to `rail-cards` come first.
- Whichever of this bolt and `a-teams-cards-are-its-conductors` lands second joins the two PreToolUse halves of `plugin/hooks/cards` into one (design.md, decision 2).
