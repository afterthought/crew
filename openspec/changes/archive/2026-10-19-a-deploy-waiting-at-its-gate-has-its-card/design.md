# Design

## Context

When a hosted deployer holds a deploy at a gate whose one reviewer is the user, the user has to click at the gate, and nothing tells them to. `plan.14` already says what that wait is: a step that is the user's, `op/<env>/<n>`, recorded by whoever dispatched the deploy with `crew ops step … --doer user --state waiting`, the gate's link as its text; its card is main-level ops's, with the gate's link as its one step; the click at the gate is the deploy's word, so no offer is posted; and the step is marked done when the deployer shows the gate passed, or by the user.

Most of that runs on main today. `crew ops step` records a user's step, crew raises its card in main-level ops's name under `op/<env>/<n>` (`ops.raise_step`, `cards.step_card`), one at a time on an environment, and closes it when the step is recorded done or declined (`crew-raises-the-deploy-and-step-cards`, record 0031). What is wrong is how crew reads a gate's step: as one that comes *after* a deploy. Its card is titled "After dev's deploy: https://…" with the link as its summary; its rail row says "an operation after the deploy of dev to 4f2a9c1"; main-level ops's view says "after 4f2a9c1". And no brief says to record the gate at all.

The other half of the intent, the card hook taking the operations' keys, is already built differently from how the intent puts it. Record 0031 made the deploy's and the step's cards crew's own: crew raises them under the rows' keys, `deploy/<env>` and `op/<env>/<n>` (`plan.CARD_KEYS`, `ops.rows`), records each act under that key (`plan.row_card_change`), and the hook refuses an agent's own post under them (`plan.card_refusal`, `CREWS`). The hook has no `KEYS` or `FORMS` any more (e112a98e). Nothing in this change touches it.

Rules relied on: `plan.14` (the gate is the user's step with ops's card and the gate's link), `briefs.11` (crew raises every row's card in the name of the row's role; no agent posts one), `briefs.16` (crew posts its own cards under the row's key), `code.7` (reading a gate is a decision on the step's facts), `code.8` (the views and mod follow what crew models), `read.1` and `read.2` (crew reads the gate's link as text handed to it and checks nothing at GitHub), `state.4` (every view is computed from the run record), `docs.6` (no proof list but *After deploy*), `docs.7` (proposed: the rule pages are the design agent's). Pages whose areas the change touches: `briefs.md` (`plugin/roles/main-ops.md`), `tests.md` (`tests/`). `plugin/lib/ops.py`, `cards.py` and `board.py` load no area page.

## Goals / Non-Goals

**Goals:**
- A gate's step reads as a deploy waiting at its gate, on its card, its rail row and the views.
- Main-level ops's brief says how a gate is recorded and ended.

**Non-Goals:**
- crew reading GitHub, or any hosted deployer, to see whether a gate is waiting or passed. The agent that dispatched the run reads it; crew records what it is told.
- A new flag, key or command. `plan.14` names the command as it is.
- A check refusing a deploy offer beside a gate's step: `plan.14` rules out the second ask, and the brief says it; `roles.3` adds a check once an agent breaks it.
- Telling team ops or the dispatcher to record a gate: no brief but main-ops's names a hosted deployer's run, and which roles dispatch one is not settled (named for the design agent).
- The rule pages' notes: `plan.14`'s *Not built* clause for the gate's card, `briefs.11`'s note that the hook lacks the operations' keys, and `_open.md`'s item are left for the design agent after the landing (`docs.7`).

## Decisions

**A gate is a user's step whose words are one link alone.** `plan.14` says the gate's link is the step's text, so crew reads the gate from that: a step whose doer is the user and whose words, all its text says before its first field (`ops.step_words`), are a single `http://` or `https://` link with nothing else. Fields after it, such as `- why:`, stay as on any step. An agent's step is never a gate, since a gate's reviewer is the user. Considered: a `--gate <url>` flag on `crew ops step`, which names the gate outright but adds an interface `plan.14` does not, and a step with a link and nothing to say is no after-deploy step anyone writes; a key prefix such as `gate-`, which makes crew read meaning into keys the dispatcher picks freely; crew asking GitHub for the run's pending deployments, which is a vendor call inside a decision (`code.7`) and ties crew to one deployer.

**The gate's card is the user's `do`, its one step and its where the link.** Pending You's `action` takes `steps` (each `text`, and `command` only for "one whole command that runs on its own") and `where` ("\"Terminal on your Mac\", or a link"), read from `post_request`'s schema on 2026-10-19. So the one step's text is the gate's link, as `plan.14` says, `where` is the link, which is what Pending You makes the place to go, and the details' links hold it too. The title names the act and the thing: "Approve the deploy of <sha7> to <env> at its gate", or "Approve the deploy to <env> at its gate" when the step names no commit. The summary says the deploy waits at its gate for the user's approval there, that the approval at the gate is the word to deploy and nothing else asks for it, then the step's why when it gives one. Its *done* says the run goes on past its gate. Kind, intent, key, urgency and *follows* are a step card's as they are now. Considered: an `approve` card, which would make the card itself look like the word to deploy, the thing `plan.14` rules out ("a second ask for a deploy whose gate is the user's own click").

**The row and the views say "waits at its gate".** The rail row reads "the deploy of dev to 4f2a9c1 waits at its gate (wldn), yours to approve there: <link>" (or "a deploy of dev waits at its gate" with no commit), its done and decline commands as every step's. `ops.environments` gives each waiting step a `gate` (its link, or none), which the board's Operation lane reads as "waits at its gate for the user" and main-level ops's view as "gate of 4f2a9c1" in place of "after 4f2a9c1" (`code.8`). The mod draws the views' lines and reads no step's fields, so it does not change; `tests/py/test_board.py`'s case pinning the keys the mod reads still passes.

**One card at a time stays.** A gate's card is raised by the same rule as every step's on its environment: the first waiting step with no card, while no step card of that environment is open. A gate is recorded when its run is dispatched, before any step of its own deploy, so it is normally first. Considered: a gate jumping ahead of an open after-deploy step's card, which `plan.14` does not say and would break the cards' *follows* chain.

**Ending the step.** Whoever dispatched the run watches it and records the step done once the run shows the gate passed, or declined once the gate was rejected; main-level ops runs the row's done or decline command on the user's Done or Skip, as for every step that is theirs. Either closes the card (`ops.step`, unchanged).

## Risks / Trade-offs

- [A user's after-deploy step written as a bare link is read as a gate] → No step the deployers hand today is a bare link (swancloud's after-deploy steps are sentences with fields); a gate's card still asks the user to open that link, which is what such a step would ask.
- [Nobody records the gate, and it waits with no card as before] → main-ops's brief says who records it and how; which other roles dispatch a hosted deployer's run, and their briefs, go to the design agent.
- [An open step card of an earlier deploy holds the gate's card back] → The rail shows the gate's row at once whatever its card does, and the earlier card's close raises it.

## After deploy

None. Every behaviour here is a decision the logic tier proves, the brief's words are proved by `tests/t-briefs.sh`, and the card's way to Pending You is the one every step's card already takes. The first hosted deploy held at the user's gate after the landing shows the card as it is.

## Task notes

**1.1** In `plugin/lib/ops.py`, beside `step_words`, a decision `gate_of(e)`: the link when the entry's `Doer` is `user` and its words (`step_words(e.get("Text"))[0]`) match `^https?://\S+$`, else None. `step_facts` adds `gate` (that link or None) and `to` (`e.get("Head")` or None) to the facts it gives `cards.step_card`. Cases in `tests/py/test_ops.py`: a user's bare link is a gate; a link with a `- why:` field after it is a gate with its why; words around a link are not; an agent's held step with a bare link is not.

**1.2** In `ops.rows`, a step with a gate reads "the deploy of {env} to {to[:7]} waits at its gate ({label}), yours to approve there: {link}", or "a deploy of {env} waits at its gate ({label}), yours to approve there: {link}" with no `to`; its key and commands as now. Case beside `test_a_step_the_user_is_to_take_that_waits_is_a_row_until_marked_counted_among_its_environments_steps`.

**1.3** In `ops.environments`, each `waiting` entry gains `gate`: `gate_of` of its latest entry. Case beside `test_the_operations_waiting_are_those_waiting_handed_or_failed_the_users_with_its_row`.

**2.1** In `plugin/lib/cards.py`, `step_card` takes `f["gate"]` and `f.get("to")`; with a gate it builds the `do` as the decisions say: title "Approve the deploy of {to[:7]} to {env} at its gate" or "Approve the deploy to {env} at its gate"; summary "The deploy{ of to7} to {env} waits at its gate for your approval there. Approving it at the gate is the word to deploy; nothing else asks for it." then the why; `action` `{"steps": [{"text": link}], "where": link, "done": "The run goes on past its gate."}`; links `[("The gate", link)]`. Without a gate, `step_card` is unchanged. Update the docstring's `f:` list. Cases in `tests/py/test_cards.py` beside `test_the_users_step_is_a_do_with_its_commands_whole_where_and_done_when`: the swb-4 card with and without a commit and with a why; a user's step with no gate keeps its title "After {env}'s deploy: …".

**3.1** In `plugin/lib/board.py`, `waiting_fields` says "waits at its gate for the user" for a waiting entry with a `gate`, and `ops_view` gives "gate of {to[:7]}" (or "gate") in place of "after {to[:7]}" for one. Cases in `tests/py/test_board.py` beside the `ops_view` lines at 356–363, with a gate's step added to a copy of `OPS`, not to `OPS` itself, so the other cases' counts stay.

**4.1** In `plugin/roles/main-ops.md` *Deploying main*, a bullet after the step's: **A deploy waiting at its gate.** When a kit's hosted deployer holds a deploy at a gate whose reviewer is the user, whoever dispatched the run records it as the user's step: `{{TEAM_CMD}} ops step <env> --to <sha> --key <key> --doer user --state waiting --text <file>`, the file holding the gate's link alone, and you do so for a run you dispatch. crew raises its card in your name with the gate's link, as for any step of the user's. Post no offer for that deploy: the user's approval at the gate is its word. Record it done once the run shows the gate passed, or declined once it was rejected, and on the user's Done or Skip run the row's command. In `tests/t-briefs.sh`, add the bullet's key phrases to the `for want in …` list for `wldn main-ops` (the gate's command line, "Post no offer for that deploy", "the user's approval at the gate is its word").

**5.1** Run `tests/suite logic`, `tests/suite t-briefs`, then `tests/suite --affected` once; each prints "0 failed".
