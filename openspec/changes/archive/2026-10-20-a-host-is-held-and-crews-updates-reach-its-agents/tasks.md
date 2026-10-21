# Tasks

## 1. A host's hold

- [x] 1.1 `crew hold <host>|--all "<why>" [--now]` writes the hold on each host named, records it without its words, tells every standing agent up there, and with `--now` ends every crew agent there. Verify `tests/suite t-hold` ends with "0 failed".
- [x] 1.2 While a host is held every command that would start an agent there refuses with the hold's words. Verify `tests/suite t-hold` ends with "0 failed".
- [x] 1.3 `crew hold status` says what still works; `crew hold wait` ends every crew agent once the host is quiet, its panes kept. Verify `tests/suite logic t-hold` ends with "0 failed".
- [x] 1.4 `crew go` lifts the hold, revives and greets, tells the agents still up, and runs the update sweep. Verify `tests/suite t-hold` ends with "0 failed".

## 2. Updates reach every agent

- [x] 2.1 The SessionStart hook records the crew a start loaded and crew-role's launch digest. Verify `tests/suite t-session-hook` ends with "0 failed".
- [x] 2.2 `crew.update_due` and `crew.due_of` say whether a standing agent is due, and why. Verify `tests/suite logic` ends with "0 failed".
- [x] 2.3 crew's Stop hook hands a due agent to `crew _renew`, which restarts it once idle, a conductor fresh and every other role resumed and told; `crew update` and the rail tab's sweep do the same for agents sitting idle. Verify `tests/suite t-hold` ends with "0 failed".

## 3. The bands

- [x] 3.1 Each standing agent's band shows the crew it started on and, once due, the one it takes at its next stop; every band on a held host opens with the hold. Verify `tests/suite logic mod` ends with "0 failed".
