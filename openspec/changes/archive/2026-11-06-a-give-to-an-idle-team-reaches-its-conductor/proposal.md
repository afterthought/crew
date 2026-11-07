# A give to an idle team reaches its conductor

## Why

On the Willdan box (wldn, crew release 0.40.0), wldn-dispatch gave bolt `the-hand-run-takes-a-release-whole-again` to team swb-2 at 21:02:24Z on 2026-11-06, recorded as `bolt.give` at 3d1f1c5 on `wldn/main`. swb-2 was idle after its previous bolt. swb-2-conductor says no notice of the give reached its pane. It sat idle for an hour, holding the fix a production deploy waits on, until wldn-operator told it at 22:03:03Z. The report came from wldn-operator through swancloud-operator, relayed by swancloud-planner. The user ruled that the box's crew faults are fixed on crew main: "Yes: fix them on crew main, for the box".

What the box's records show, read with `crew trace` and `crew events --about` and the box's renew log, read-only:

- swb-2's previous bolt, `the-full-stand-passes-the-runner-test-on-githubs-runner`, had its last chore merged at 21:01:21Z and waited to land; its landing was submitted at 21:30:54Z. So the give at 21:02:24Z was a give beside a bolt that waits to land (`teams.16`).
- That give restarts neither role at once. Its team's host (`crew _tidy`) hands each role whose session carries an old branch to `crew _renew`, which restarts it once it is idle with nothing of its own running in the background, and the conductor's greeting at that restart was the give's only notice (`teams.20`, `teams.7`).
- swb-2-ops was renewed at 21:06:30Z and told at 21:07:34Z. swb-2-conductor has no `agent.renew` and no `greet` between 19:32 and 22:03. Its renew log ends twice with `swb-2-conductor is not restarted: it runs background work of its own: … $C tell swb-2-ops …; the end of its next turn hands it back`: once for the drop of `a-self-deploys-history-tells-its-whole-path` at 20:01:16Z, once for this give.
- The end of its next turn hands nothing back. crew's Stop hook asks `crew.due_of` with no branch, so it sees only an update's restart, never one for a bolt that changed under the agent; that one only `crew _renew` reads, since it reads the plan. A conductor idle with background work of its own also has no next turn to end.
- A give to a team that held no bolt has the same hole: it restarts the conductor at once from the giver, which a working conductor refuses, and greets it with a ninety-second wait, said on the giver's standard error when it gives up. At 20:01:20Z swb-2's give of the bolt before restarted and greeted ops alone; the conductor learned of it from the planner.

So the give's notice rode on a restart that waits for things a notice does not need, and nothing carried it to a later stop.

## What Changes

- **A give hands its conductor's notice to the team's host, whatever the conductor is doing.** A new hidden command, `crew _notice <team> <bolt>`, run by every give on today's path before anything else starts, keeps the notice owed there and hands the conductor to `crew _renew`. A conductor herdr reads not up is said, and recorded as a refused `bolt.notice`.
- **`crew _renew` gives the notice.** At once when the conductor is idle: by its restart's greeting, which names the bolt, when it is due a restart that may run now; else by crew's notice, which names the bolt (both bolts beside one waiting to land) and says a restart still owed comes at a later stop. A working conductor is told at the end of its turn. A notice not taken is kept for the next stop and recorded refused once per reason; a start of the conductor since the give spends it, its start's greeting having told it.
- **The Stop hook hands back what `crew _renew` owes.** A restart `crew _renew` gave up on, and a notice not yet given, are kept as marks on the host, and the Stop hook hands the agent back at the end of its turn while either stands.
- **A give to a team that held no bolt restarts its ops at once and its conductor on its host,** at once when it is idle with nothing of its own running, else at its next stop, its greeting the give's notice.
- **A conductor not told is said where it is read.** The give says so. The bolt's head line on the board, and the agents' bands that draw it, say its conductor was not told of its give, with crew's words, and the attention line names it. `crew rail` lists each such bolt after its groups. Each says so until a `bolt.notice` that told it or a greeting of the conductor.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a give's notice reaches its conductor whatever it is doing; a give to a team that held no bolt restarts its conductor on its host.
- `host-holds-and-updates`: a restart that gives up is handed back at the end of the agent's next turn, whatever made it due.
- `crew-rail`: a bolt whose conductor was not told of its give is said after the groups.
- `crew-board`: the head line and the attention line say a bolt's conductor was not told of its give.

## Impact

- `plugin/lib/plan.py`: `bolt_give` hands the notice first (`give_notice`, `noticed`, `notice_unhanded`) and restarts only ops from the giver when the team held no bolt; `crew _notice` (`given_noticed`, `notice_handed_said`); `greet_team` names both bolts for a give beside a waiting one and reports each role's outcome; `notice_on`, `notice_unsent` and `untold_gives`, read by the board and the rail; `rail_text` prints the new section.
- `plugin/lib/hold.py`: `crew _renew` reads the notice at every look and gives it (`notice_now`, `notice_tell`, `notice_refused`, `notice_spent`, `give_notice_said`); the marks (`owe_given`, `given_of`, `drop_given`, `owe_restart`); a `crew _renew` that finds another running while a notice is owed waits for it.
- `plugin/lib/crew.py`: `RENEW`, `renew_owed` and `stop_hands`. `plugin/hooks/stop` hands back what is owed.
- `plugin/lib/board.py`: the head line, its attention gutter and the attention line. The views keep their shape, so `plugin/hooks/status.js` draws them unchanged (`code.8`).
- `plugin/bin/crew`: `_notice`'s routing to the team's host, and the usage of `bolt give` and `rail`. README and the skill say the same (`docs.2`).
- Tests: `tests/py/test_hold.py`, `tests/py/test_teams.py`; `tests/t-journey-land.sh`, `tests/t-journey-teams.sh`, `tests/t-hold.sh`.
- The run record gains the act `bolt.notice` on the bolt, its team and the conductor, with `Refused` when it was not given. Nothing outside the standard library is imported (`code.1`).

## Touches

```
README.md
plugin/bin/crew
plugin/hooks/stop
plugin/lib/board.py
plugin/lib/crew.py
plugin/lib/hold.py
plugin/lib/plan.py
plugin/skills/crew/SKILL.md
tests/py/test_hold.py
tests/py/test_teams.py
tests/t-hold.sh
tests/t-journey-land.sh
tests/t-journey-teams.sh
```
