# Design

## Context

A restart for an update is `crew _renew <agent>` (`hold.renew`), a process of its own on the agent's host, handed by crew's Stop hook at the end of a due agent's turn or by `crew update` (`teams.19`). Once herdr reads the agent ready (`renew_ready`) it calls `Agents.stop(role, waits=True)`, which types `/exit`, looks for the agent's exit once a second for 30 seconds (answering Claude Code's exit question when it shows), types Ctrl+C twice, looks once more two seconds later, and then returns "<agent> did not exit (busy or waiting on the user); it was left running". `renew` prints that and returns, starting nothing.

That give-up is true when it is said (`teams.2`: `stop` fails rather than lies), but the keys it typed are still working. On deneb on 2026-10-23 swancloud-operator and fwn-1-conductor each exited within a minute of their restart giving up, and their panes stood as shells for nine hours until `crew revive` (signal 2026-10-23-chuck-mac-studio-8d53f475/01). Why their exits took longer than 32 seconds was not read; this design does not depend on it.

A restarted agent is otherwise started as now: `Agents.start(role, "resume")`, a conductor fresh, then told the restart's notice or greeted (`teams.7`), and recorded `agent.renew`.

Rules relied on: `teams.19` (when and how a due agent is restarted, never on a held host), `teams.2` (never start over a running agent; `stop` never lies), `teams.7` (one first message per start), `read.1` and `read.2` (a pane read as empty only from herdr's listing; what crew can't read starts nothing), `read.4` (never take over a pane an agent holds), `code.7` (the decision is a function of facts), `code.9` (the watch runs in `_renew`'s own background process, never in a command an agent waits on). Pages whose areas the change touches: `teams.md` (`plugin/lib/crew.py`) and `tests.md` (`tests/`). No rule is departed from.

## Goals / Non-Goals

**Goals:**
- A restart for an update ends with its agent running: on crew as it now is, or as it was.
- An exit the restart's own keys caused, early or late, is followed by the agent's start.

**Non-Goals:**
- Any other caller of `Agents.stop` (`crew down`, `restart`, a stage's start, `hold wait`, retiring an old operator): their stops behave exactly as now.
- Finding why an agent takes longer than 32 seconds to exit.
- Bringing back an agent that exited for any other reason; that stays `crew revive`'s.

## Decisions

### 1. The restart watches for the exit after its stop gives up

When `Agents.stop` returns its give-up words inside `renew`, `renew` does not return. It keeps looking at the agent, every five seconds for up to ten minutes (`hold.EXITING`, counted in looks so the tests' stubbed sleep ends the loop), through a new `Agents.exited(role, looks)` that reads herdr's status afresh each look as the stop itself does and adds the role to `ended` once herdr reads no agent. The moment it reads none, `renew` goes on to the start, the notice and the record exactly as after a stop that succeeded.

The watch is in `renew`, not in `Agents.stop`, so every other caller keeps the stop it has. Ten minutes is far past the minute deneb's agents took, and costs only a sleeping process.

Considered: a longer wait inside `Agents.stop` for every caller, which would hold `crew down` and a stage's start for minutes on an agent that will never exit; and a SessionEnd hook that hands the restart back when the session ends, which rests on Claude Code running a hook's detached child past its own exit, unread.

### 2. A restart that could not end its agent says so and leaves a mark

When the watch ends with the agent still up, `renew` prints the stop's words followed by "; it runs on as it was, still due: the end of its next turn hands it back", records nothing, and returns. Nothing is typed into the pane after that, so the agent runs on as it was (`teams.2`, `read.4`).

Before the watch begins, `renew` writes `RENEW/<agent>.exiting` holding the session the restart typed its exit into (the session of the start it read, `started["session"]`). It is removed once `renew` starts the agent. A mark whose session is not the agent's last recorded start is stale: another start has happened since, and `renew` removes it when it reads it.

### 3. A later restart starts an agent its earlier restart's keys ended

An agent can exit past the watch: an `/exit` herdr delivered while the agent had gone back to work waits behind that turn, and Claude Code runs it once the turn ends, after the Stop hook has handed a new restart. That restart's loop now reads, when herdr reports the agent not up, the pane as `read_pane_agent` reads it and the mark, and asks a new decision, `hold.renew_exited(holds, unread, marked, session, down)`:

- start, with no stop, when herdr lists the pane with no agent in it (`holds` False, nothing unread), the mark names the agent's last recorded session, and the agent's team, main level or dispatcher was not taken down (`Agents.down()`);
- otherwise not, with why: "it is not up" when no mark names its session, "it was taken down" when it was, and "crew can't tell whether its pane holds it: <why>" when the pane could not be read (`read.1`).

When the decision is to start, the loop leaves at once and `renew` skips the stop and goes to the start as in Decision 1. When it is not, the loop goes on waiting as it does today, and gives up at its deadline saying why. The host's hold is read first, as now, so nothing starts on a held host.

The mark is what keeps this to exits the restart caused: an agent the user ended by hand, or one a crash took, has no mark naming its session and stays `crew revive`'s.

Considered: starting any due agent read not up. That would let `crew update` bring back every standing agent whose pane is a shell, taking `revive`'s place without its checks, and racing a `revive` already running.

## Risks / Trade-offs

- [An agent exits more than ten minutes after its restart gave up, with no turn ending after] → it stays down until its next restart is handed, by `crew update` or the timer moving crew, or `crew revive`. The keys a restart types act within seconds or behind one turn; an exit later than both is not one this change can tell from any other.
- [`revive` and a restart both find the same empty pane] → `revive` starts a new session, which makes the mark stale; `Agents.start` refuses over an agent already up (`teams.2`), so at worst one of them says it did not start.
- [A herdr hiccup reads the agent gone during the watch] → `Agents.start` reads the pane again before typing and starts nothing over a running agent, as every start does.

## Migration Plan

None: the mark is new, and a restart running when this lands finishes on the code it started with.

## After deploy

None. Every scenario is proved by the logic and end-to-end tiers, and the change reaches each host as every landing does.

## Task notes

**1.1** `plugin/lib/hold.py`: `renew_exited(holds, unread, marked, session, down)`, a function of facts as `renew_ready` is, returning `(start, why not)`: `(True, None)` only for `holds is False`, `unread` None, `marked` and `session` equal and not empty, and `down` false; `(False, "it was taken down; it stays down")` when down; `(False, f"crew can't tell whether its pane holds it: {unread}")` when unread; `(False, "it is not up")` otherwise, a stale or missing mark among it. Cases in `tests/py/test_hold.py` beside `renew_ready`'s: each branch, and a mark of another session read as not up.

**1.2** `plugin/lib/crew.py` `Agents.exited(role, looks)`: for each of `looks`, `nap(5)` then `self.herdr.status(pane, fresh=True)`; once it is falsy, append the role to `self.ended` and return True; False after the last look. Its docstring says what it is for: the exit a stop's keys set going after the stop gave up (teams.19). Cases in `tests/py/test_hold.py` with a fake herdr like `Exiting`, one whose agent stays up a given number of fresh reads after `/exit` and Ctrl+C: `stop` gives up and `exited` then returns True with the role in `ended`; and one that never goes, where `exited` returns False and nothing else is typed into the pane (no `pane run`, no further keys after the stop's).

**1.3** `plugin/lib/hold.py` `renew`: `EXITING = 120` looks (ten minutes at five seconds); the mark `RENEW/<agent>.exiting`, its one line the session. After `agents.stop(role, waits=True)` returns words: write the mark with `started["session"]` when there is one, print "<agent> did not exit at once; crew watches for its exit" , then `agents.exited(role, EXITING)`; when False print the stop's words + "; it runs on as it was, still due: the end of its next turn hands it back" to standard error and return. In the readiness loop, when `status` is None and nothing is unread: read the mark, `crew.read_pane_agent(fleet, name)` and the holding Agents' `down()`, and call `renew_exited`; on start, leave the loop with the stop skipped. Remove the mark after a successful `agents.start`, and when it is read stale. Keep the order of checks: held first, then due, then readiness.

**1.4** `tests/stubs/herdr`: `herdr --session S stub linger <pane|name> <n>`: the agent's next `/exit` prompt and Ctrl+C leave it up and idle, and it is gone (as `/exit` removes it now) after the next n `agent get` of it; n 0 ends a lingering agent at the next `agent get`. Document it in the stub's opening with the other stub verbs. `tests/t-hold.sh`, after the update case and before the Stop hook's, three cases on swb-1-ops, each making its start stale as the update case does: lingering past the stop's looks (n about 40), `crew update` ends with its log saying "swb-1-ops is restarted on crew" and its launch `resumed`, told its restart; lingering past the watch (n past the stop's looks and `EXITING`), its log says "did not exit" and "runs on as it was", the agent is still up and nothing was launched; then that agent ended in the stub with its mark left, and its restart handed again (the Stop hook, as the conductor's case hands it), which starts it `resumed` with no `/exit` typed to it in `$CREW_TEST_LOG`. The reads line keeps `plugin/hooks/` and `plugin/lib/hold.py`; run `tests/moon-tasks` if its inputs change.

**2.1** `tests/suite --affected` from the worktree's root.
