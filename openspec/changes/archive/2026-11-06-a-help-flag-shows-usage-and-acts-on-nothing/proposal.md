# A help flag shows a command's usage and acts on nothing

## Why

On the Willdan box a code agent ran `crew needs --help` to read the command's usage, and crew took `--help` as what the agent needed and ended its stage at 25 of 27 tasks: "It needs: --help" (2026-11-07; signal `WilldanGroup/crew-state:wldn/main signals/2026-11-07-atl-1-conductor-f0eb3ad4/01-crew-needs-help-ends-a-stage`). crew main fixed it on 2026-11-07, 57c6381a, released in v0.41.9, and its commit named this line: "teamless/deneb needs the same check: its bash tell, send, main up, revive and hold.py's hold act on a help flag as main's did." agentplot-design ruled that `teamless/deneb` takes the fix: "it guards every command."

On this line `crew tell <agent> --help` tells the agent, or asks a role that runs as its kind, the words `--help`; `crew send <partition> --help` sends them to the partition's operator; `crew hold <host> --help` holds the host with `--help` as its reason; `crew main up <label> --help` and `crew revive --help` drop the flag and act. The Python commands answer through argparse, but `plan.py`, `board.py`, `hold.py`, `page.py` and `sites.py` check for recutils or read the teams file first, and argparse refuses a word ahead of the flag that fails a type or a choice before it reaches the flag.

## What Changes

- **Every command answers a help flag.** `-h` or `--help` among a command's own arguments prints its usage and exits 0, before anything is read, recorded, asked, launched, started, told or sent to another host. That holds for every command `crew` dispatches, the internal `_` commands, the commands whose words or names are free, and for `crew-role`.
- **One usage per command.** A command `crew` reads itself prints its own lines of `crew`'s usage header: `crew tell ... --help` the lines of `crew tell`, `crew main up ... --help` the line of `crew main up|down|status`. A command `crew` hands whole to a Python parser prints that parser's usage, as `crew bolt start --help` always did. `crew --help` and `crew -h` print the whole usage and exit 0.
- **The Python entry points answer first.** `plan.py`, `record.py`, `board.py`, `hold.py`, `ops.py`, `page.py` and `sites.py` answer the flag before they check for recutils or read the teams file, and before a word ahead of the flag that their parser would refuse, so `crew plan approve three --help` prints `crew plan approve`'s usage.
- **A word is a word.** Only an argument that is exactly `-h` or `--help` asks for the usage: `crew tell <agent> "--help with the tenant table"` is a tell.
- README, the crew skill and `crew`'s usage header say this (`docs.2`), and `code.11` states the rule.

main's fix also guards `crew needs`, `crew fix <team> ...`, `crew unit run`, `crew up <team>`, `crew _end-short`, `crew _tidy`, `crew _construct-again` and `crew _dispatch`, and amends bolt-teams' requirement "A stage's agent says what it needs through crew". This line has none of those commands, nor that requirement, so neither is carried; `crew fix <bolt> <name>`, which this line hands to `plan.py`'s parser, is guarded with every Python command.

## Capabilities

### New Capabilities

- `crew-command`: what the `crew` command does with what it is given, whatever the command; its first requirement, "A help flag shows a command's usage and acts on nothing".

### Modified Capabilities

None.

## Impact

- `plugin/bin/crew`: `usage` with a command and a word; the help check after the arguments are split, before the Flume run's name is read or anything runs. `plugin/bin/crew-role`: its check before anything.
- `plugin/lib/crew.py`: `HELP`, `usage_asked`, `answer_usage`. Called first by `plan.py`, `record.py`, `board.py`, `hold.py`, `ops.py`, `page.py`, `sites.py`; `plan.py`'s `review-delivered` parser names its prog.
- `docs/architecture/core.md`: `code.11`. README, `plugin/skills/crew/SKILL.md`, `crew`'s usage header.
- Tests: `tests/py/test_help.py`; `tests/t-help.sh`, with its task in `tests/moon.yml`.
- Nothing crew models changes, so the board, the views and the mod are untouched (`code.8` not reached). Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/bin/crew
plugin/bin/crew-role
plugin/lib/crew.py
plugin/lib/plan.py
plugin/lib/record.py
plugin/lib/board.py
plugin/lib/hold.py
plugin/lib/ops.py
plugin/lib/page.py
plugin/lib/sites.py
docs/architecture/core.md
README.md
plugin/skills/crew/SKILL.md
tests/py/test_help.py
tests/t-help.sh
tests/moon.yml
```
