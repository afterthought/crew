# Design

Rules relied on: `briefs.10` (the door, `crew send`, the line in every brief), `briefs.1` (the operator writes nothing but the teams file, and carries), `roles.4` (every message is a tell, marked `[crew tell from <sender>]`), `teams.11` (a tell reaches its agent as a prompt or not at all), `read.1` (a name crew can't place is refused, never guessed), `code.2` (a refusal is a `Refusal`), `code.4` (names), `code.7` (the decision is a function of facts), `code.8` (the views), `docs.2` (README, the skill and the usage together), `docs.7` (`_open.md` is the design agent's). Pages whose areas this touches: `teams.md` (`plugin/bin/crew`, `plugin/lib/crew.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `record.md` (a comment in `plugin/lib/record.py`), `docs.md` (README), `tests.md`. Records: 0013 (the door), 0035 (the door is one main-level agent, `<label>-operator`).

## Context

`crew tell <agent> "<text>"` (`crew.py` `tell`, reached from `plugin/bin/crew`'s `tell)` case through `py tell`) prompts any agent crew started, wherever it runs, marked with `rec.who()`, refuses with nothing typed when the agent is not up or waits on a question, and records a `tell` entry in the recipient's partition with `Chars`. Every brief's roster comes from `team_tokens` or `main_tokens` in `crew.py`, which end with "… reached with `crew tell <agent>`" and `SENDERS`. Since record 0035 every partition has exactly one operator, `<label>-operator`, placed by `place_of_agent` through `role_session`. Nothing says how to reach another team or partition: the team roster says agents outside the team are reached with `crew tell`, which invites a tell to another team's conductor, and `operator.md`'s teams change from a box tells another partition's operator by name (`TEAMS_OPERATORS`).

## Goals / Non-Goals

**Goals:** one command any agent, or the user, runs without knowing hosts or operators; the operator knows who sent it and for whom; one record entry; one line in every brief.

**Non-Goals:** a reply path (the operator answers with `crew send` back, or the receiving agent does, through the same command); queuing a send while the operator is down; changing what `crew tell` does; the board's views, which draw no tell and so draw no send (`code.8` is not moved: nothing the views read changes).

## Decisions

### 1. The door is a decision of the teams file alone

`send_door(fleet, name, caller)` returns `(label, door, team)`: when `name` is a team in `fleet["teams"]`, its `label`, `<label>-operator` and the team; when it is a partition's label in `fleet["partitions"]`, the label, its operator and `None`; otherwise a `Refusal`: "crew send takes a team or a partition: teams <…>; partitions <…>", sorted. A partition is named by its label only, the name every roster and command uses (`crew main up <label>`); the `partition` field (personal, business) is not a key and may be shared, so it is not accepted (`read.1`). When `caller` is the door itself the decision refuses: "you are <label>'s door: carry it on with `crew tell <agent>`". It starts no process (`code.7`), so the logic tier holds its cases.

Alternatives: accept an agent's name and send to its partition's door, which would make `crew send swb-1-conductor` look like a tell that silently went elsewhere, so refused instead; fall back to the sender's own partition for an unknown name, ruled out by `read.1`.

### 2. The send is a tell to the door, with the addressee before the text

`send(fleet, name, text)` resolves the door, then calls `tell(fleet, door, f"(sent to {name}) {text}", record=False, sender=rec.who())`. The mark stays `roles.4`'s `[crew tell from <sender>]`, so `SENDERS`, `transcript.py`'s `TELL` and `asserter` read a send exactly as a tell (a signal the operator records from it is asserted `agent:<sender>`, or `user` for `<user>@<host>`), and nothing new is typed into any pane's grammar. `(sent to <name>)` is crew's own words after the mark, naming the team or partition as the sender named it, so the operator knows which conductor it is for. All of `tell`'s refusals apply unchanged (`teams.11`). It is not sent with `taken`: `crew tell` isn't either, and a send is a tell.

Like `crew tell`, `crew send` runs on the caller's host and reaches the operator's host through `on_machine` inside `tell`; it is not forwarded (`code.3` forwards commands about a team's or main level's state, which a send does not touch), so the entry is written where the sender ran, as a tell's is.

Alternative: a new mark, `[crew send from <sender> to <name>]`, which would depart from `roles.4`, needs `TELL` and `SENDERS` changed, and gives the operator nothing the prefix does not.

### 3. One `send` entry in the receiving partition's record

On a delivered send, `rec.emit(label, "send", on=[f"agent/{door}", f"team/{team}" if team else None], why=f"send {name}", Chars=len(text))` — the door's label, since a tell is recorded in its recipient's partition, and `record=False` on the tell so the send is one entry, not two. `emit` already drops empty `On` values and writes `By` and `Session`. The text is never written (run-record "An entry holds no text anyone typed"). `Chars` is already an allowed field; only the comment naming what carries it changes in `record.py`.

### 4. One line beside every roster

A `SENDS` line is built beside `SENDERS` and added to both rosters. In `team_tokens` the roster's last sentence becomes: the agents named here are reached with `crew tell <agent> "<text>"`; anything for another team, of this partition or another, or for another partition, is sent with `crew send <team or partition> "<text>"`, which reaches that partition's operator, and to nobody else. In `main_tokens`: the agents and teams named here are reached with `crew tell`; anything for another partition or one of its teams goes with `crew send`, and to nobody else. Every brief fills `{{ROSTER}}`, so every brief carries it, and no brief file needs its own line. The command is spelled with the brief's `TEAM_CMD` path, as `crew tell` is.

A team's agents count their own partition's other teams as another team, since `briefs.10` rules out sending a team's business to its conductors; the main level's own teams stay theirs to tell, as their briefs already have them answer conductors.

### 5. The operator's brief carries what is sent

`operator.md` *Carrying requests* gains one paragraph: a message marked `(sent to <team or partition>)` came by `crew send`; carry it as a request of the user's is carried, in the sender's words and naming the sender: a finding as a signal (`{{SIGNAL}}`, its excerpt the words as sent), a design question to `{{DESIGN_AGENT}}`, work to `{{PLANNER}}`, a message for a team to `<team>-conductor`. *Changing the teams*, on a box, sends the request with `{{TEAM_CMD}} send <label>` to one of `{{TEAMS_DOORS}}`, the labels of the partitions whose main level runs on a Mac keeping swancloud's checkout; `TEAMS_OPERATORS` becomes `TEAMS_DOORS`, built from the same `doors` list as labels.

### 6. Documents

`plugin/bin/crew`: a `send)` case beside `tell)`, `py send "${2:?usage…}" "${3:?usage…}"`, and the usage line `crew send <team or partition> "<text>"`. `crew.py` `main`: the `send` branch, exit 0 when delivered, 1 otherwise, a `Refusal` turned into its message (`code.2`). README: `crew send` in the main level's command block and one sentence beside its `crew tell` sentence. `plugin/skills/crew/SKILL.md`: a row, "send something to another team or partition", so a session that is no crew agent, the one in the signal, finds it too (`docs.2`). `_open.md` and `briefs.10`'s "Not built" are left to the design agent after the landing (`docs.7`).

## Risks / Trade-offs

- [The operator is down when a send arrives] → The send fails with tell's words and records nothing; the sender says so where it is, as with any tell. A queue would be a service crew does not run (`state.4`).
- [A team's agent now goes through the operator for a team of its own partition, one hop more] → Intended: `briefs.10` makes the operator the one door, and the operator hands it to the conductor in one tell.
- [`(sent to …)` is a convention the operator must read] → Its brief says what it means, and the mark itself is unchanged, so no reader of tells breaks.

## Task notes

**1.1** `send_door` in `crew.py`, beside `label_of_agent`. The refusal for an unknown name lists `sorted(fleet["teams"])` and `sorted(fleet["partitions"])`. The caller is `os.environ.get("CREW_AGENT")`, passed in by `send`, so the decision reads no environment. Cases in `tests/py/test_send.py`, on `facts.FLEET` (wldn, its teams swb-1 and swb-2) with a second partition added in the test: a team, a label, an agent's name, an unknown name, the door itself for its own team and its own label, and another partition's operator sending to wldn, which is allowed.

**1.2** `send` in `crew.py` and its `main` branch; the text is `f"(sent to {name}) {text}"`. Logic case: with `tell` and `rec.emit` replaced, a delivered send calls `tell` with `record=False` and the door, and emits one `send` entry with the `On`s, `Why` and `Chars` of decision 3; an undelivered one emits nothing.

**1.3** `plugin/bin/crew`: the case and the usage line after `crew tell`'s. The end-to-end step goes in `tests/t-journey-main.sh`, which brings wldn's main level up, `wldn-operator` among it, and already tells `wldn-planner` from the user's shell (`crew tell wldn-planner "Secret words ZQXR"`): add `CREW_AGENT=swb-1-conductor crew send swb-2 "…"` and one from the user's shell, `crew send wldn "…"`, and grep `$CREW_TEST_LOG` for `agent prompt wldn-operator '[crew tell from swb-1-conductor] (sent to swb-2) …'` on the main level's host and session, as `t-journey-review.sh` greps its tell; then the run record's `send` entry names `agent/wldn-operator` and `team/swb-2` with the length and not the words (that test already reads entries with its `field` helper); and `crew send nosuch "x"` fails naming the teams and partitions.

**2.1** The two roster sentences of decision 4. `tests/py/test_teams.py` pins `tok["ROSTER"]` only by `MAIN_SESSIONS` being in it, so no existing case changes; `tests/t-briefs.sh` gains: every team brief (`swb-1` × the five roles) and every main brief (`wldn` × the five standing roles) has the `crew send <team or partition>` line, and none says "Agents outside the team are reached with".

**2.2** `operator.md` and `TEAMS_DOORS`. `tests/t-briefs.sh`: `crewpy brief wldn operator` has "(sent to" and `send <label>` for the teams change from a box (`HOST=chuck-herdr-alpha`, as that test already prints the operator brief on a box), and lacks "TEAMS_OPERATORS".

**3.1** README, the skill row, the `record.py` comment ("a tell's or a send's Chars"). `tests/t-docs.sh` checks every README command is in the usage.

**3.2** Run `tests/moon-tasks` after adding `tests/py/test_send.py` only if it changes `tests/moon.yml`; commit it if so.
