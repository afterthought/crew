# Design: a give to an idle team reaches its conductor

## Context

The proposal gives the box's case. This change touches the areas of `teams.md` (`plugin/lib/crew.py`, `plugin/bin/crew`), `plan.md` (`plugin/lib/plan.py`), `docs.md` (`README.md`) and `tests.md` (`tests/`). Rules it relies on:

- `teams.7`: every agent crew starts gets one first message; a plan write whose own command greets a team does not also notify its conductor. A give's command greets its team, so the give's notice is the give's to deliver.
- `teams.16`: a give beside a bolt that waits to land restarts neither role at once.
- `teams.19`, `teams.20`: a restart waits until herdr reads the agent idle, with no question open and no background work of its own but crew's waits; one whose team's bolt changed under it is restarted at its next stop, as one an update made due.
- `teams.11`, `teams.15`: a tell reaches its agent as a prompt or not at all, and a first message is taken or sent again.
- `code.7`: each decision is a function of facts, tested in the logic tier. `code.9`: a give answers once what it set in motion is handed to the host that runs it.
- `read.1`: where crew cannot read the conductor it says so and owes the notice all the same.
- `record.1`, `record.3`: one entry per act, done or refused; a refusal records crew's own words.
- `roles.5`: this is a fix to a mechanism crew already holds, the restart and greeting a give runs through `crew _renew`, and builds nothing Flume or Pending You is designed to hold. A crossed team's give starts no agent and is untouched.
- `tests.4`, `tests.8`, `tests.11`, `tests.12`.

It departs from no rule.

### Where the notice was lost

Read in `plugin/lib/plan.py`, `hold.py`, `crew.py` and `plugin/hooks/stop` at `eed4b1a6`, which the box's operator finds unchanged for a give's notice since v0.40.0:

1. `bolt_give` beside a waiting bolt runs `crew _tidy <team>` on the team's host (`team_handed`). `team_tidy` tells each standing pane its new branch and hands each role whose session carries another to `hold.hand`, a process of its own running `crew _renew`.
2. `renew` looks every five seconds for `SETTLE`, 120 seconds, for the agent idle with no question open and nothing of its own in the background (`renew_ready`). Then it restarts it, the conductor fresh, and greets it with both bolts (`greet_team`, `conductor_bolts`). That greeting is the only place the give is told. Otherwise it prints "the end of its next turn hands it back" and ends.
3. The Stop hook asks `crew.due_of(fleet, name)` with no `branch`, which reads only an update's restart (`update_due`). A restart for a branch (`branch_due`) needs the plan, which only `renew` reads (`branch_now`). So nothing hands such a restart back, and a conductor idle with background work of its own has no turn to end anyway.
4. A give to a team that held no bolt restarts both roles from the giver (`crew restart … --no-greet`), which leaves a working conductor running (`Agents.stop`), then greets the conductor from the giver with a ninety-second wait (`greet_agent`), said on the giver's standard error when it gives up.

swb-2-conductor's background task, a `crew tell` chain, read as running in its transcript (`transcript.pending`), held its restart at the drop at 20:01Z and at this give, and step 3 never brought it back.

## Decisions

### Decision 1: the give's notice is owed apart from the restart, on the team's host

A give on today's path runs `crew _notice <team> <bolt>` on the team's host before anything else starts (`give_notice`). There `given_noticed` reads the conductor through herdr. Not up: it says so and records a refused `bolt.notice`; the conductor's next start greets it. Otherwise it writes `<agent>.given` in `crew _renew`'s folder, holding the bolt, its partition and team, and the session the conductor runs, and hands the conductor to `crew _renew` (`hold.owe_given`, `hold.hand`). The giver prints what the host said; when the host did not answer or could not take it, the giver says so and records the refused `bolt.notice` itself (`noticed`, `notice_unhanded`).

The notice is owed first so that the restart the same give hands over finds it and its greeting names the bolt.

Considered and not taken:

- **Tell the conductor from the giver.** `crew tell` waits on an idle agent for a short while and fails on a working one (`teams.11`, `send_taken`). The give would have to wait, or lose the notice exactly as the greeting did (`code.9`).
- **Fix only the Stop hook.** Handing a branch restart back at the next stop (Decision 3) does not reach swb-2's case: idle with its own background work, it had no next turn, and its restart would wait on that work however often it was handed.
- **Pass the notice on `crew _tidy`.** `team_tidy` runs `reap` first, which can refuse; the giver could not tell whether the notice was owed before it refused. A command of its own answers for the notice alone.

### Decision 2: `crew _renew` gives the notice at once when idle, else at the end of the turn

`renew` reads the mark at every look, so a give that owes a notice while another `crew _renew` of the conductor runs is picked up by that one. At each look (`notice_now`):

- **Due a restart that may run now:** the restart. Its greeting names the bolt, or both bolts beside one waiting to land (`greet_team`'s `bolt`, `conductor_bolts`), and reports whether it was taken (`outcome`); taken, the mark goes; not taken, it is recorded refused.
- **Idle, no question open, and its restart not due or waiting on background work of its own:** crew's notice, once per handing (`notice_tell`): the bolt or both bolts, crew's greeting to read where it stands and carry on, and, when a restart is still owed, that crew starts it again at a later stop so sluice's board names its branch (`give_notice_said`). It is sent as `[crew]`, taken or sent again (`teams.15`), recorded as a `bolt.notice` with its length (`record.3`), and the mark goes. Not taken, it is said and recorded refused once per distinct reason, and the mark stays for the next stop (`notice_refused`).
- **Working, or a question open:** nothing now. When the looks run out, the mark stays and the Stop hook hands it back at the end of the turn.
- **Not up:** said and recorded refused, the mark dropped; its next start greets it.
- **Started since the give:** the mark is spent and dropped, since every start of a conductor is greeted and told to read where its bolt stands (`notice_spent`).

A second `crew _renew` handed while one runs and a notice is owed waits for the first to end, looking once a second within its looks, so a notice owed as the first ends is not left with no one to give it to an idle conductor.

Considered and not taken:

- **Restart the conductor anyway, cutting its own background work.** `teams.19` rules that out, and the box's case shows why: the work was a tell to ops.
- **A notice by tell beside every restart.** A conductor restarted fresh has no conversation; its greeting is its first message (`teams.7`), and a second message about the same give would be a second greeting.

### Decision 3: the Stop hook hands back what `crew _renew` owes

`renew` keeps `<agent>.owed` when its looks run out on a due agent, or its stop gave up, and lifts it once the agent is restarted or no longer due (`owe_restart`). The Stop hook hands the agent to `crew _renew` when it is due for an update, as before, or when either mark stands (`crew.renew_owed`, `crew.stop_hands`), for the session its last start recorded. Reading two files costs the hook nothing it did not already spend; reading the plan at every turn's end would.

### Decision 4: a give to a team that held no bolt restarts its conductor on its host

The giver restarts ops at once, greeted with the bolt, as before. The conductor is handed by Decision 1: idle with nothing of its own running, `crew _renew` restarts it fresh at once, its greeting naming the bolt; working, at the end of its turn; idle with its own background work, it is told now and restarted later. A conductor started with no bolt carries the branch `""`, so the new bolt makes it due (`branch_due`). The give answers once the host has the hand-off, rather than after a restart and a greeting (`code.9`).

### Decision 5: a conductor not told is said where the bolt is read

`notice_unsent` reads the partition's run record: the newest refused `bolt.notice` of a bolt since its newest give to its team, until a `bolt.notice` that told it or a `greet` of the conductor. The board's head line says the bolt's state and that its conductor was not told of its give, with those words, carries the attention gutter, and the attention line names it (`head_said`, `needs_eye`). Every band that draws the head line says it too; the views keep their shape (`code.8`). `crew rail` lists each such bolt after its groups, with when, the team and the words, which say how the conductor is told (`untold_gives`). The rail's groups are what waits on the user's answer; this is a fact about a give, so it is a section like the questions and the decision records, not a fifth group.

## Is the fix needed on `teamless/deneb`

No. On deneb's crew without teams no team stands, so no give restarts or notifies a conductor, and every bolt goes through Flume, whose give starts no agent (`bolt_give`'s crossed path, untouched here). The Stop hook's hand-back of a restart `crew _renew` gave up on reaches deneb's main-level agents only if that branch keeps today's `_renew`; a merge of main carries it there unchanged.

## Found, not fixed here

swb-2-conductor's background task, a `crew tell` chain, read as still running long after a tell ends in seconds. `transcript.pending` takes a task as running until a `<task-notification>` naming its id appears in the transcript. If Claude Code on the box does not write that notification for a task the agent never read back, every restart of that agent waits forever. This fix does not depend on it, since the notice no longer waits on the restart, but the restart still does; the box's transcript is the reading that would settle it.

## After deploy

None. The logic tier proves each decision, and the land, teams and hold journeys the wiring. The box runs it once its crew moves to a release that holds it, through swancloud's pin, and nothing there can be checked by hand.

## Task notes

**1.1** `plugin/lib/plan.py`: `give_notice`, `noticed`, `notice_unhanded`, `notice_on`, `notice_handed_said`, `given_noticed` (`crew _notice`, registered in `parser`, `COMMANDS` and `TEAM_COMMANDS`); `bolt_give` runs it first on both paths. `plugin/lib/hold.py`: `owe_given`, `keep_given`, `given_of`, `drop_given`. `plugin/bin/crew`: `_notice` forwarded with `one`. Cases in `tests/py/test_teams.py` (`TestTeamGreetings`): the host's words for an idle, a working and a not-up conductor, and one crew can't read; the giver's for a host that did not answer or could not take it.

**1.2** `plugin/lib/hold.py`: `notice_spent`, `notice_now`, `give_notice_said`, `notice_tell`, `notice_refused`; `renew` reads the mark at every look and, on the lock held while a notice is owed, waits. `plugin/lib/plan.py`: `greet_team`'s `bolt` names both bolts when the team holds two, and `outcome`. Cases in `tests/py/test_hold.py` (`TestGiveNotice`), driving `renew` with the box's facts: idle with background work of its own and due, told and its restart kept owed; idle and not due, told; working, kept; not up, refused; started since, spent; not taken, kept and recorded once; a second `renew` waiting on the first.

**1.3** `plugin/lib/crew.py`: `RENEW`, `renew_owed`, `stop_hands`; `hold.RENEW` is it. `plugin/hooks/stop` hands when `stop_hands`. `hold.owe_restart` where `renew` gives up and where it restarts. Cases in `tests/py/test_hold.py`; `tests/t-hold.sh` runs the hook for a conductor whose start carries a branch its team no longer holds, with `<agent>.owed` standing, and waits for its restart.

**1.4** `bolt_give`'s no-bolt path restarts ops alone from the giver. `tests/t-journey-teams.sh` waits for the conductor's restart on its host and checks its greeting names the bolt.

**1.5** `plugin/lib/plan.py`: `notice_unsent`, `untold_gives`, `rail_text`'s section. `plugin/lib/board.py`: the ledger's `record` carries `untold`; `head_said`, `needs_eye`, the attention item `untold` and `attention_text`. Cases in `tests/py/test_teams.py`. `tests/t-journey-land.sh`: the beside give with the conductor running background work of its own (told, recorded, not restarted until the work ends, then restarted as before); the give of `kept-work` to swb-2, whose conductor is not up, said and on `crew rail` until the bolt is dropped.

**1.6** README, `plugin/skills/crew/SKILL.md` and the usage of `bolt give` and `rail` in `plugin/bin/crew` say what a give tells its conductor and what the rail lists (`docs.2`).

**2.1** `tests/suite --affected`, against the merge-base with main.
