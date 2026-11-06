# A landing's close never waits on its own lock

## Why

On the Willdan box (wldn, crew main), crew deadlocked itself twice on 2026-11-06 while closing a landing, for landings #1394 and #1395. Each time a parent held `landings/<bolt>.lock` in team state while its own `crew _tidy` child blocked on that lock:

- wldn-ops's `crew bolt submit`, pid 4029933, for switchboard-kit's `production-takes-14-10`;
- crew's `_landing-read`, pid 2538257, for `everyone-on-the-host-reaches-its-units`.

wldn-ops freed both by SIGTERM'ing the `_tidy` children. The report came from wldn-planner through swancloud's operator. The user ruled that the box's crew faults are fixed on crew main: "Yes: fix them on crew main, for the box".

The lock is `landing_read`'s: one read of a bolt at a time on its team's host, so a landing's outcome is recorded once (bolt-teams "A landing is recorded by whatever reads the bolt after it"). Under it, a read that finds the bolt landed closes it with `crew bolt land`'s code (`landing_close`, `bolt_land`). That code runs the team's tidy on the team's host, `crew _tidy <team> --landed <bolt>` (`tidy_after`), and waits on it with no timeout. The tidy is the team's read (`team_tidy`, `reap`), and the team's read reads the landing of each bolt the team holds that may have an outcome or a close nothing recorded (`reap_landings`). That read is `landing_read`, which waits on the same lock.

The tidy finds the bolt still held when it reads the plan as it stood before the close. A decision reads the flywheel's branch below any commit whose run-record entry has not reached it (`read.5`, `decision_at`). The close's `bolt.land` entry reaches the branch as the commit after the close's plan write, and only once its push is taken. On a branch as busy as wldn's, that can be after the tidy has read the plan. The bolt then reads held, with every unit landed, so its landing read is due, and the tidy waits on its parent's lock for as long as the parent waits on it.

## What Changes

- **The tidy a landing's close runs reads no landing.** `reap`, run as `crew _tidy --landed <bolt>`, skips `reap_landings`. The landing it follows was read by the act that closed it, under its lock. The team's other bolts' landings are read by the team's next read. So no holder of a landing's lock ever waits on a command that takes one.
- **What the lock covers stays the same.** It still covers reading the outcome, recording it, the close and the close's tidy, so a second read waiting on it still finds all of that done and says what the first said.
- **The other locks have no such shape.** `waits/<slot>.lock`, `handed/.lock` and the cards' `land/.<kit>.lock` were read for it, and none changes (design, Decision 2).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a read never waits on itself. The tidy a read's close runs reads no landing, and the team's next read reads the rest.

## Impact

- `plugin/lib/plan.py`: `reap` skips `reap_landings` when it runs as a landing's tidy. The docstrings of `reap` and `team_tidy`, and the comment on `landing_read`'s lock, say why.
- Tests: `tests/py/test_landing.py` drives a landing whose close runs its tidy while the read holds the lock, and checks the read finishes within a bound.
- Nothing the board or the mod draws changes (`code.8` not reached), and nothing outside the standard library is imported (`code.1`). No command's behaviour a user sees changes, so README, the skill and the usage are unchanged (`docs.2`).

## Touches

```
plugin/lib/plan.py
tests/py/test_landing.py
```
