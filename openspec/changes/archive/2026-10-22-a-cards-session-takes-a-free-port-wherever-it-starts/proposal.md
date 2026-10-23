# A card's reading session takes a free port wherever it starts

## Why

On 2026-10-22 the user ran `crew card session batch/13` on deneb from a shell outside any crew agent, and it failed: "Plannotator: port 19432 is already in use ... remote mode uses a fixed port". crew starts a card's reading session with `PLANNOTATOR_REMOTE=1` but leaves the port to whatever environment it runs in. Inside an agent that environment carries swancloud's range, `PLANNOTATOR_PORT=19432-19451`, from the agents' Claude settings (swancloud `lib/agent-config.nix`). A shell on a Mac does not, so plannotator falls back to its one fixed remote port, 19432, which crw-6's landing card's session had held for two days. Batches 13 to 15 stood without a reading session from 2026-10-20 because of it (signal 2026-10-22-chuck-mac-studio-fa252efd/01).

A reading card is meant to carry its session's link (`briefs.9`). Whether it does should not depend on which shell started it.

## What Changes

- Every reading session crew starts for a card (a batch's, a landing's, a long proposal's, and an old batch card's per unit) is given a port range, so plannotator takes the first free port in it. This is the same whether crew runs in an agent's pane, from a hand-typed command in a shell, or from a raise inside a merge.
- The range is the one the environment names when it names a range. Otherwise, when it names none, a single port, or something plannotator can't read, crew uses its own range, 19432–19451, which is swancloud's.
- When every port in the range is held, the session fails as it does today when plannotator ends before it is ready. Its card is raised without it, and the card, the command and the run record give plannotator's own words for why.
- The test stub for plannotator chooses a port the way plannotator 0.28.26 does. With no port named in remote mode it takes 19432 alone and refuses when that port is held, so the suite would have caught this.
- README's sentence on where a session's link comes from says crew gives the port range itself.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: a card's session takes a free port of plannotator's range wherever it is started.

## Impact

- `plugin/lib/plan.py`: a decision giving the environment plannotator starts in, used by `session_open`, which every card session goes through (`card_session`, `reading_open`, `land_session`).
- `tests/py/test_card_commands.py`: the decision's cases.
- `tests/stubs/plannotator`: chooses a port as plannotator 0.28.26 does (`tests.4`).
- `tests/t-cards.sh`: one case, a session started with no port named while another holds 19432.
- `README.md`: the sentence on the session's link.
- No change to swancloud. Nothing the board or the agents' bands draw changes (`code.8`).

## Touches

```
plugin/lib/plan.py
tests/py/test_card_commands.py
tests/stubs/plannotator
tests/t-cards.sh
tests/moon.yml
README.md
```
