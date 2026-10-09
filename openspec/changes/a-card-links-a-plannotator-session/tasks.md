# Tasks

## 1. crew starts, waits on and ends a card's session

- [x] 1.1 `crew card session <key>` starts one plannotator session, with no browser and an Approve button, on the document of the rail row with that key, prints its link, gives back the running session's link when run again, and refuses a land key, a key with no row, a document on another host and a link only the host can open (design.md, Task notes 1.1).
- [x] 1.2 `crew card wait <key>` returns the session's decision, approved, annotated or closed, with the user's words verbatim, or that it ended with none, including a decision made before the wait began (design.md, Task notes 1.2).
- [x] 1.3 `crew card end <key>` ends only a plannotator process crew started for that key and still serving its document, and forgets the key either way (design.md, Task notes 1.3).
- [x] 1.4 A stub `plannotator` behaves as the readings say: the three decision shapes, no result when killed, a session list by pid, and whether a browser was skipped (design.md, Task notes 1.4).
- [x] 1.5 `tests/t-card-session.sh` holds every case in the `card-sessions` spec, and `tests/moon.yml` has its task (design.md, Task notes 1.5). Verify `tests/suite t-card-session` ends with "0 failed".
- [ ] 1.6 The usage of `plugin/bin/crew`, README and the crew skill name `crew card session|wait|end` (design.md, Task notes 1.6). Verify `tests/suite t-docs` ends with "0 failed".

## 2. A card's close ends its session

- [ ] 2.1 The card hook ends the session for a keyed card's key when a crew agent closes or withdraws that card, and never fails the tool call (design.md, Task notes 2.1). Verify `tests/suite t-cards t-card-session` ends with "0 failed".

## 3. The briefs and the rules

- [ ] 3.1 The card discipline the planner and the conductor share has them start a card's session, carry its link, wait on its decision in the background, act on it as the card's answer and withdraw the card, and start them again after a restart (design.md, Task notes 3.1).
- [ ] 3.2 The planner's and the conductor's *Cards* say each reading card carries its session's link in place of a file or path, and `tests/t-briefs.sh` pins the new phrases (design.md, Task notes 3.2). Verify `tests/suite t-briefs t-roles` ends with "0 failed".
- [ ] 3.3 `briefs.9` reads as built and `briefs.4`'s detail says a card's session opens nothing (design.md, Task notes 3.3). Verify `tests/suite --affected` ends with "0 failed".
