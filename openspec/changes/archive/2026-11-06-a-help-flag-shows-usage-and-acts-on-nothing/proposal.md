# A help flag shows a command's usage and acts on nothing

## Why

On the Willdan box (wldn, chuck-herdr-alpha), a code agent on atlas-kit's gateway unit ran `crew needs --help` to read the command's usage. crew took `--help` as what the agent needed and ended its stage, at 25 of 27 tasks: "It needs: --help" (01:09:16Z on 2026-11-07; signal `WilldanGroup/crew-state:wldn/main signals/2026-11-07-atl-1-conductor-f0eb3ad4/01-crew-needs-help-ends-a-stage`). The user ruled that the box's crew faults are fixed on crew main ("Yes: fix them on crew main, for the box").

The cause is in `plugin/bin/crew`: `needs)` takes `$2` as the words, whatever they are, and hands them to plan.py after `--`, where no parser reads a flag. Other commands act on a help flag the same way. `crew fix <team> <name> --help` starts a fix whose words are `--help`; `crew unit run <unit> code --help` sends the words to the stage; `crew tell <agent> --help` and `crew send <partition> --help` send them; `crew hold <host> --help` holds the host with `--help` as its reason; `crew up <team> --help`, `crew main up <label> --help` and `crew _dispatch up <label> --help` drop the flag and run; `crew revive --help` revives. Others print a usage only when an argument is missing, and exit non-zero.

The family answers a help flag one way. Flume and sluice read `-h` and `--help` among any command's arguments as a request for its usage: they print it, exit 0 and act on nothing. crew's Python commands already do this through argparse, and the line `(crew bolt|unit|chore|plan|signal --help says more)` in `crew`'s usage relies on it. This makes it one rule for all of crew.

## What Changes

- **Every command answers a help flag.** `-h` or `--help` among a command's own arguments prints its usage and exits 0, before anything is read, recorded, started, told or sent to another host. That holds for every command `crew` dispatches, the internal `_` commands, the commands whose words or names are free, and those crew runs on another host, and for `crew-role`.
- **One usage per command.** A command `crew` reads itself prints its own lines of `crew`'s usage header, the lines `crew` already prints whole as its usage: `crew needs --help` prints `crew needs`'s lines, `crew fix ... --help` the four lines of `crew fix`, `crew unit run ... --help` the line of `crew unit run`. A command `crew` hands whole to a Python parser prints that parser's usage, as `crew bolt give --help` always did. `crew --help` and `crew -h` print the whole usage and exit 0.
- **The Python entry points answer first.** `plan.py`, `record.py`, `board.py`, `hold.py`, `ops.py`, `page.py` and `sites.py` answer the flag before they check for recutils or read the teams file, and before a word ahead of the flag that their parser would refuse, so `crew plan approve three --help` prints `crew plan approve`'s usage.
- **A word is a word.** Only an argument that is exactly `-h` or `--help` asks for the usage: `crew needs "--help with the tenant table"` ends its stage as any needs does.
- README, the crew skill and `crew`'s usage header say this (`docs.2`), and `code.11` states the rule.

## Capabilities

### New Capabilities

- `crew-command`: what the `crew` command does with what it is given, whatever the command; its first requirement, "A help flag shows a command's usage and acts on nothing".

### Modified Capabilities

- `bolt-teams`: "A stage's agent says what it needs through crew" says that `crew needs --help` asks for the usage and ends no stage.

## Impact

- `plugin/bin/crew`: `usage` prints a command's own lines; the help check after the arguments are read, before the Flume run's name is read and before the dispatch; the usage header's paragraph on the flag.
- `plugin/bin/crew-role`: the same check, printing its own header.
- `plugin/lib/crew.py`: `HELP`, the decision `usage_asked` and the act `answer_usage`, which every Python entry point calls first: `plan.py` `main`, `record.py` `main`, `board.py` `main` (its parser built before the teams file is read), `hold.py` `main`, `ops.py` `main`, `page.py` `main`, `sites.py` `main`. `plan.py`'s `review-delivered` parser is named `crew review delivered`, as `crew signal move`'s is.
- `README.md`, `plugin/skills/crew/SKILL.md`, `docs/architecture/core.md` (`code.11`).
- Tests: `tests/py/test_help.py`, `tests/t-help.sh`, `tests/moon.yml`.
- Nothing crew models changes, so neither `board.agent_views` nor the mod does (`code.8` not reached). Nothing outside the standard library is imported (`code.1`).

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
README.md
plugin/skills/crew/SKILL.md
docs/architecture/core.md
tests/py/test_help.py
tests/t-help.sh
tests/moon.yml
```
