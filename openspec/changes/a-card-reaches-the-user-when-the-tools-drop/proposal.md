# A card reaches the user when the tools drop

## Why

A crew agent posts its cards with Pending You's MCP tools in its own Claude Code session. Every way that has failed so far is that session's:
- **Lost tools.** On 2026-10-09 the service timed out for half an hour, and Claude Code, once a reconnection's `tools/list` failed, never fetched the tools again. crw-2 and crw-3 lost theirs, and crw-3's review reached the user with no card (signals 2026-10-09-swancloud-operator-mac-studio-fa4348e4/01 and 2026-10-09-swancloud-design-6d65f646/01, /02).
- **Results that don't parse.** crew's record of a card is written by a hook that parses Claude Code's rendering of the tool's result, and one post was recorded with no card id (signal 2026-10-08-swancloud-planner-02c7ce29/01).
- **Sessions with no sign-in.** Read on 2026-10-12: mac-studio has had no host sign-in since 2026-10-10, so sessions of an account never signed in to Pending You through Claude Code have no tools at all.

The user ruled on 2026-10-12, on the reading `openspec/explorations/pending-you-api/reading.md`, that crew's own commands become the one way crew's agents handle cards. They act as the asking assistant through Pending You's MCP endpoint under the host's sign-in. ADR 0005 is amended that day and `briefs.16` added. This change builds the commands. `every-crew-card-goes-through-crew` then moves the briefs to them and refuses an agent's own calls.

## What Changes

- `crew card post <key>` posts a card. The agent gives the card's own fields as one JSON object on standard input.
  - **Checks.** Before anything reaches Pending You, crew refuses a key that is not the agent's own, and a row's card in another form than its row's, in the words the card hook uses today.
  - **What crew fills.** The idempotency key is the card key. The session is the agent's crew name, this host and the folder it runs in. The area is the one Pending You matches to the folder's git remote, or the kit's area made under `create-area:<owner>/<kit>` when none matches.
  - **The post.** It goes through the fleet's `pendingyou mcp --app claude-code`, under the host's sign-in. crew prints the card's id and its link, and records a `card.post` entry with the id from Pending You's own reply.
- `crew card change <key>` changes the card the agent holds under the key, with the fields to change on standard input. crew reads the card's id from the run record and its version from Pending You, refuses a change that takes a row's card out of its form, and records `card.update`.
- `crew card close <key> --outcome "<line>"` closes the agent's card once it has acted on the answer. `--reason "<line>"` withdraws it. Either records `card.close` and ends the card's plannotator session, as the hook does when an agent closes a card through Pending You's tools.
- `crew card read <key>` prints where the agent's card stands: its status, whose turn it is, the user's answer and their words, and any messages. It records nothing.
- **Refusals.** What Pending You refuses is refused in its own words and recorded as the act refused. When the sign-in or the service cannot be reached, the command refuses saying so and to try again later. Nothing is posted twice: a retry under the same key gives Pending You's card back.
- **Tests.** The tests run on a stub `pendingyou` that answers as the fleet's `pendingyou mcp` does. `tests/run` refuses to start when the stub would not shadow the real one.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a crew agent's card can be posted, changed, closed and read through `crew card`, acting as the asking assistant under the host's sign-in. Its acts are recorded from Pending You's reply.

## Impact

- `plugin/lib/cards.py` (new):
  - the client for `pendingyou mcp`;
  - the commands' decisions as functions of facts: the call's arguments, the reply's object and refusal, the area, and which card a key names in the run record.
- `plugin/lib/plan.py`: the `card post|change|close|read` parsers and commands, and `card.post`, `card.update` and `card.close` among the acts a refusal records.
- `plugin/hooks/cards`: unchanged. `crew card post` and `change` load its key and form checks, so the two paths refuse alike until `every-crew-card-goes-through-crew` replaces the checks.
- `plugin/bin/crew` usage, README and `plugin/skills/crew/SKILL.md`: the four commands (`docs.2`).
- Tests:
  - `tests/stubs/pendingyou` (new);
  - `tests/run`, which also checks the new stub shadows `pendingyou`;
  - `tests/py/test_card_commands.py` (new);
  - `tests/t-card-commands.sh` (new);
  - `tests/moon.yml`.
- No brief changes here. Agents keep posting through Pending You's tools until `every-crew-card-goes-through-crew` lands.

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/stubs/pendingyou
tests/run
tests/py/test_card_commands.py
tests/t-card-commands.sh
tests/moon.yml
```
