# Design

## Context

See proposal.md for why. What stands today:

- **The card hook only records.** `plugin/hooks/cards` runs after Pending You's `post_request`, `update_request`, `cancel_request` and `ack_answer` (PostToolUse, `hooks.json`), and writes a `card.post`, `card.update` or `card.close` entry. A card whose key is one of the rail's four is on its row's object; any other key is on `agent/<name>`, recorded and let be. Nothing runs before a card is posted, and nothing at all runs for `create_area`.
- **Who owns a row is in the plan.** The planner owns `proposal/<n>` for each open proposal of its partition. A conductor owns the review, verify and land rows of the bolt its team holds: `plan.py` reads that with `holdings()`, and `role()` tells a crew agent's kind and team from its name alone. The four key shapes are `CARD_KEYS` in `plan.py` and `KEYS` in the hook.
- **The briefs.** `cards_how()` in `crew.py` is the card discipline the planner's and conductor's briefs share; it says only rows get cards and that the area is made with `create-area:<owner>/<kit>`. `needs_how()` is how a stage agent, and ops during a proof, stops short; it is the `{{NEEDS}}` of `construct.md`, `coder.md`, `verify.md` and `ops.md`. `ops.md` says nothing of cards. The conductor's brief posts the landing card "once ops's proof file reports it clean", and asks nothing on it but approval.
- **Pending You, as read on 2026-10-09** (its tool schemas in this session, and its skill at https://www.pendingyou.com/skill.md): `post_request` and `create_area` each require an `idempotencyKey` of 8 to 120 characters. A card's `kind` is how the user answers it; `approve` is yes or no on one action, and a high-stakes approval is held to send. A card also takes `action` (`where`, `steps` of `{text, command}`, `done`), the shape the skill gives for a step only the user can take, with each command copyable. `create_area` hands back an area already of that name in the group, but two creates under different keys at once are two calls, which is how brd-2 got two.
- **Claude Code's hooks**: a PreToolUse hook matches an MCP tool by name (`mcp__<server>__<tool>`) and refuses the call by printing `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<why>"}}` and exiting 0; the reason is shown to the agent, and the call never runs. A hook that times out does not refuse.

Rules this change rests on: `briefs.11` (the rule it builds), `roles.3` (a check, not firmer words), `read.1` (what can't be read refuses), `read.2` (the tool's input read by checked fields, an absent one never text), `code.1` (the standard library only), `code.2` (a refusal is a `Refusal`), `plan.12` (one fetch of the state branch per command), `briefs.1`, `briefs.3` and `briefs.6` (what ops and the conductor each do, proof the user takes, a wait the user is told of), `briefs.9` (what a card's words carry), `tests.6` (a brief's rule pinned in `t-briefs.sh`), `docs.5`. Pages whose area it touches: `briefs.md` (`plugin/roles/`), `plan.md` (`plugin/lib/plan.py`), `teams.md` (`plugin/lib/crew.py`), `tests.md` (`tests/`), `docs.md` (README, `docs/`). `plugin/hooks/` has no page; `core.md` binds it.

## Goals / Non-Goals

**Goals:**

- No crew agent can put a card before the user that is not a row of its own, or make an area under a key of its own.
- One card per step the user takes at a bolt's end, the landing card.

**Non-Goals:**

- Checking that a row is on the rail at this moment. A key a conductor owns but whose row has moved on (an old head, a stale stamp) is let through and shows on the rail as an open card with no row, as today.
- Checking `update_request`, `cancel_request` or `ack_answer`. Pending You lets only a card's poster change it, and crew records those as before.
- The deploy's after-steps of `plan.14` and their rows, which `a-deploy-is-approved-and-recorded-through-crew` builds. A step a proof leaves the user stays in the proof file until then.
- The Pending You reminder that tells every session "anything you need from your person also goes on a card". It is Pending You's; the refusal is what answers it for a crew agent.
- Removing the duplicate area brd-2 made. The user removes it in the app (ADR 0005).

## Decisions

### 1. The check runs before the call, in the card hook

The card hook gains a PreToolUse half, matched on Pending You's `post_request` and `create_area`, beside the PostToolUse half that records. It knows a crew session the same way (`CREW_AGENT` and `CREW_LABEL`, else the record session-start keeps), and finds Pending You's server under any name the same way (`is_pending_you`). Any other session, and any other server's tool, is let through untouched.

Alternatives: refusing after the post and withdrawing the card, which crew cannot do, since only the poster can withdraw a card (ADR 0005); a brief-only rule, which `roles.3` rules out; a separate hook file, which would split the card's key rules across two files when the four shapes already live in this one.

### 2. Ownership is read from the plan, by `plan.py`

A function in `plan.py` takes the fleet, the agent's name and its label, the tool and the key, and returns `None` to let the call through or the refusal's words. It reads the plan once (`plan.12`): for the planner, the open proposals of its partition (`open_proposals`); for a conductor, the bolt its team holds and that bolt's units (`holdings`). Everyone else, a team's ops and unit slots, the design agent, a dispatcher, main-level ops and an operator agent, owns no row and may post no card. The key's shape is checked against `CARD_KEYS` first, so a key that is no row's is refused without a fetch. The hook imports `plan` as it already does to end a card's session.

An area's key is checked against the teams file alone: `create-area:` and the `repo` of the agent's team's kit, or, for a main-level agent, of a kit any team of its partition builds. No plan read is needed.

Alternative: the whole rail, as `crew rail` computes it, which would also check that the row waits on the user now. It surveys every host of the partition over ssh, which a hook before every card can't afford, and the rail's list of cards with no row already shows the rare stale card.

### 3. The refusal names the key to use

The refusal is written for the agent that reads it, in one or two sentences:

- a conductor: the keys that are its own, `land/<bolt>/<head>` for its bolt by name, and `review/<unit>/<head>` or `verify/<unit>/<stamp>` for each unit of its bolt by name, with the head or stamp "from the `card:` line under its row in `crew rail --label <label>`"; or, when its team holds no bolt, that no row is its own;
- the planner: `proposal/<n>` for each proposal of its partition open now, or that none is open;
- a team's ops or a stage agent: a team's cards are its conductor's; ops writes what is left for the user in its proof file, and a stage says what it needs with `crew needs`;
- any other crew agent: only the planner and the conductors post cards, and it tells the partition's operator agents what it waits on, as its brief says (`briefs.6`);
- an area: the `create-area:<owner>/<kit>` key, or keys, the agent may use.

### 4. What can't be read refuses the card

When the check cannot read the teams file, the plan or the proposals, or fails on anything else, the call is refused and the refusal names what failed (`read.1`). The hook's PostToolUse half keeps its rule that it never fails a tool call, since what it does is bookkeeping after the fact; the PreToolUse half is a decision, and a card wrongly let through cannot be taken back by crew, while a card refused is posted again a moment later. The PreToolUse entry gets a 30-second timeout, room for one fetch of the state branch.

### 5. The user's steps go in the proof file, and on the landing card

ops writes, after the glyph list, a section *Left for the user* holding each step only the user can take or check, written as Pending You's skill writes a step: where, one action per step with its command or link, and what they will see when it worked. Each such item is ⏳ in the glyph list, waiting on the user. A proof with nothing failed and only such steps open is "clean but for the user's steps". ops posts no card and tells nobody else; crew already gives the conductor the proof file's path.

The conductor posts the landing card when the proof is clean or clean but for the user's steps. It stays the one `land/<bolt>/<head>` card, kind `approve`, high stakes. When there are steps, its title names the step and the landing ("Check the gateway on your Mac, then approve landing swb-gateway"), its summary says the steps first in plain words, and the steps are its `action`, so each command can be copied; the approval means the user took them and they worked. A note that a step failed is a defect: the conductor closes the card with that outcome, runs a fix on the bolt, has ops prove it again, and posts the landing card afresh.

Alternative: a grouped card (`questions`), which Pending You allows only for choice, multi, approve and text questions, none of which carries copyable steps; or a second card for the step, which is what this change ends.

### 6. One line in the shared stopping-short text

`needs_how()` gains one sentence, so every stage brief and ops's say it in the same words: post no Pending You card and make no area, since the team's cards are its conductor's. `cards_how()` gains one: crew refuses a card under any key but a row's of your own, and an area under any key but the kit's.

## Risks / Trade-offs

- [A hook that times out lets the card through] → one fetch, well inside 30 seconds; a card that slips through still shows on the rail as a card with no row, owned by whoever posted it.
- [GitHub unreachable means no card can be posted] → the refusal says so and the agent posts again later; the rail and the operator agents' tells still reach the user.
- [Pending You may not show an `action`'s steps on an `approve` card] → the summary carries the steps in plain words too, so nothing is lost but the copy button; *Proof in dev* checks it.
- [A conductor's own key with a stale head is let through] → as today, the rail lists it as a card with no row and asks its owner to close it.

## Proof in dev

Worked after the bolt lands and every host has pulled, on swancloud first:

1. In a team's ops pane on mac-studio, ask ops to post any Pending You card: it is refused before Pending You is called, the refusal says the team's cards are the conductor's, and `list_pending` holds no new card. The same for `create_area` under a key of ops's own.
2. The next bolt whose proof leaves the user a step: the user gets one card for it, the conductor's landing card, with the step in its first words and as copyable steps above the hold-to-approve button, on the phone and in Herdr's popup. This also settles whether Pending You shows an `action` on an `approve` card.
3. A conductor's ordinary review and landing cards and the planner's proposal cards still go through, each within a few seconds, on mac-studio and on the box.

## Task notes

### 1.1

In `plan.py`, beside `CARD_KEYS`: `card_refusal(fleet, agent, label, tool, key)` returning `None` or a string; raise nothing out of it but `Refusal` (`code.2`). `tool` is `post_request` or `create_area`. Read the key with `isinstance(key, str)` first (`read.2`); an absent or non-string key is refused as "no idempotencyKey". For `post_request`: `role(fleet, agent)`; `planner` → `open_proposals(fleet, [label])`, let through `proposal/<n>` when `n` is open; `conductor` → `plans(fleet, [label])` once, `holdings(plan)`, the bolt whose team is the conductor's, let through `land/<that bolt>/…`, `review/<u>/…` or `verify/<u>/…` matching `CARD_KEYS` for `u` in `plan.units_of(bolt)`; any other kind → refused with the words of decision 3. For `create_area`: let through exactly `create-area:<repo>` for the agent's kits (team kinds: `fleet["teams"][of]["kit"]["repo"]`; main-level kinds: every team of `label`). Words per decision 3; the planner's and conductor's name `crew rail --label <label>` as the full path the briefs use (`{HOME}/plugin/bin/crew`).

### 1.2

In `plugin/hooks/cards`: when `hook_event_name` is `PreToolUse`, and the tool is Pending You's `post_request` or `create_area`, and the session is crew's (`identity`), load the fleet as crew does and call `plan.card_refusal` with `tool_input["idempotencyKey"]`. On a string, print the deny object of Claude Code's PreToolUse output with it as `permissionDecisionReason`; on `None` print nothing. Any exception in this half denies with `crew could not check this card: <error>`. Leave the PostToolUse half as it is. In `hooks.json`, add a `PreToolUse` entry matched on `mcp__.*__(post_request|create_area)` running the same file with `timeout` 30, and say in the description that crew refuses a crew agent's card or area under another key. Update the module docstring to say both halves.

### 1.3

In `tests/t-cards.sh`, feed the hook PreToolUse input as Claude Code does (the existing `call` with `hook_event_name: "PreToolUse"` and no `tool_response`), with a world where a team holds a bolt with units and the partition has an open proposal. Cases, each asserting the deny object and a phrase of its reason, or no output: ops posting any key; a unit slot agent posting; a conductor's own `land/<bolt>/<head>` and `review/<u>/<head>` let through, and the bare `land/<bolt>` refused; a conductor's made-up key, and another team's unit's review key, refused naming `land/<bolt>/<head>`; the planner's open `proposal/<n>` let through and a closed one refused; the design agent refused; `create_area` under `area:<agent>` refused naming `create-area:<owner>/<kit>`, and under that key let through; an unreadable state branch refusing with its name; a session crew did not start, and another server's `post_request`, printing nothing. Update the opening comment. If the test now reads a file it did not, add it to `# Reads:`, run `tests/moon-tasks` and commit `tests/moon.yml`.

### 2.1

`needs_how()`: one sentence after the first, in these words or close: "Post no Pending You card and make no area: your team's cards are its conductor's, and crew refuses any other." Keep it one sentence so it reads the same in all four briefs.

### 2.2

`ops.md`, *Proving the bolt*: after the sentence that the results go to the proof file, say what goes under *Left for the user* (decision 5), that each such item is ⏳ waiting on the user, that a proof with nothing failed and only these left is clean but for the user's steps, and that the conductor asks them on the landing card, so ops posts no card for them.

### 2.3

`conductor.md`: in *Cards*, the landing card's line says it is posted once the proof is clean, or clean but for steps it leaves the user, and when it has steps carries them first, in its title, its first words and as the card's steps, so approving it means they were taken and worked; in the answers paragraph, a note on the landing card that a step failed is a fix on the bolt, then a new proof and a new landing card, never a landing. In step 5 of the bolt's course, "When the proof is clean" becomes clean or clean but for the user's steps. Say nowhere that ops posts a card.

### 2.4

`cards_how()`: after "every decision of yours the rail lists gets one card, and only those", add that crew refuses a card under any key but a rail row's of your own and an area under any key but `create-area:<owner>/<kit>`, and names the key to use. Leave the rest of the text alone: `a-card-reads-whole-at-a-glance` rewrites other sentences of it.

### 2.5

`tests/t-briefs.sh`: pin a phrase of each of 2.1 to 2.4 in the filled brief it lands in (ops and a stage brief for 2.1, ops for 2.2, the conductor for 2.3, the conductor and the planner for 2.4), as the file pins the others (`tests.6`).

### 3.1

`docs/architecture/briefs.md`: in `briefs.11`'s detail, drop the sentence that `ops.md` has no card rule and the hook refuses nothing until this unit lands, and name `plan.py` `card_refusal` and `tests/t-cards.sh` among its sources. `docs/architecture/_open.md`: remove the `briefs.11` item. `README.md`, the cards paragraph: one sentence that crew's hook refuses a card a crew agent posts under any key but a rail row's of its own, and an area under any key but the kit's `create-area:<owner>/<kit>`, naming the key to use, and that a team's ops and stage agents post no card. No command changes, so the usage and the skill stay as they are (`docs.2`).
