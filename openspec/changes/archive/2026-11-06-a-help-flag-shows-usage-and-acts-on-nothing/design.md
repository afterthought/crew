# Design: a help flag shows a command's usage and acts on nothing

## Context

The proposal gives the box's case and what this line takes of crew main's fix (57c6381a). Rules this change relies on: `read.1`, which has crew refuse rather than guess, and a flag taken as words is a guess; `record.1`, under which a command that acts records its act, so a help request must stop before any act; `code.3`, which forwards a main level's command to its host before it touches state, so the flag must be answered before the forward; `code.7`, which makes the decision of which usage is asked a function of the arguments alone; `docs.2`, which has README, the crew skill and `crew`'s usage header say the change together; `tests.4` and `tests.11`, which put the reproducing case in the lowest tier that holds it. The change adds `code.11` to `core.md`, as main's fix did, binding all of crew. It touches the areas of `teams.md` (`plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/lib/crew.py`), `plan.md` (`plugin/lib/plan.py`), `record.md` (`plugin/lib/record.py`), `briefs.md` (`plugin/skills/`), `tests.md` (`tests/`) and `docs.md` (`README.md`, `openspec/`, `docs/`). It departs from no rule.

How this line reads a command's arguments:

- **bash reads some.** `plugin/bin/crew` reads the arguments of `tell`, `send`, `main up|down|status`, `review`, `console`, `revive`, `operator` and `_sweep` itself, then runs one Python process with what it chose to pass (`one`, or `py`), which may forward the command to the main level's host. It drops what it does not read (`main up <label> --help`, `revive --help`).
- **Python parsers read the rest.** bash hands the other commands whole to `plan.py`, `record.py`, `board.py`, `hold.py`, `ops.py`, `page.py` or `sites.py`. Each parses with argparse, whose subparsers answer `-h` and `--help`, but `plan.py` checks for recutils first, `board.py` and `hold.py` read the teams file first, and argparse refuses a word ahead of the flag that fails a type or a choice. `hold.py` reads `hold`, `go` and `update` by hand.

## Decisions

### Decision 1: the help flag is answered by whatever reads the command's arguments, at its entry

bash answers the flag for every command whose arguments it reads, right after it has split out `--force`, before it reads the Flume run's name, reads the teams file, runs Python or reaches another host. A command bash hands whole to a Python parser passes through to its arm, and that parser answers before anything else. `_sweep`, which bash checks for a label before it hands it to `plan.py`'s entry of the same name, goes to that entry at once, whose parser is its grammar. `hold`, `go` and `update`, which `hold.py` reads by hand, are answered by bash.

bash's list of the commands a Python parser answers is the arms that `exec` one. A command added to the dispatch and missing from the list is answered by bash, from its usage lines or the whole usage, and acts on nothing either way; `t-help` lists every arm and fails on one it does not run with the flag.

Considered, as main did: answering only in Python, where bash drops the flag before Python sees it for `main up` and `revive`; and one bash check printing the header's lines for every command, which would replace argparse's usage and print nothing for the internal commands the header does not list.

### Decision 2: one usage per command, the one its entry point already prints

`crew` prints its header as its usage. `usage <command> [<word>]` prints only the command's lines there: each line `crew <command> ...` with the lines indented under it, those whose next word names `<word>` when any does (`crew main up`, `crew hold status`), else every line of the command (`crew tell`). `operator`, the console's old name, prints `crew console`'s lines. A command the header names nowhere prints the whole usage. A command a Python parser answers prints argparse's usage of the deepest command its words name. There is no second text to keep in step.

`plan.py`'s `review-delivered` parser takes `prog="crew review delivered"`, as `signal-move` does, so its usage names the command as typed.

### Decision 3: a Python entry point answers before it reads anything, and past a word it would refuse

`crew.usage_asked(ap, argv)` decides: with no argument exactly `-h` or `--help` it is `None`; otherwise it walks the leading words down the parser's subcommands and gives the deepest parser they name. `crew.answer_usage(ap, argv)` prints that parser's help and exits 0. Each Python entry point calls it first: `plan.py` before `need_recutils`, `board.py` with its parser built before the teams file is read, `hold.py` for its `_` commands before it reads the teams file, `record.py`, `ops.py`, `page.py` and `sites.py` before they parse.

### Decision 4: only an argument exactly `-h` or `--help` asks, wherever it stands

The flag is read among all of a command's arguments, free words included. Any other word is a word: `--helpful`, `-hx`, `help` and `--help with the tenant table` are passed on as before.

### Decision 5: crew-role too

`crew-role` is crew's other command. Its header is its usage; with the flag among its arguments it prints the header and starts no Claude.

## After deploy

None. Every case is held by the logic tier and by `t-help` on the stubs; what deneb runs is swancloud's pin of `teamless/deneb`, not a step of this change.

## Task notes

**1.1** `plugin/lib/crew.py`: `HELP`, `usage_asked`, `answer_usage`. Called first in `plan.py` `main`, `record.py` `main`, `board.py` `main`, `hold.py` `main`, `ops.py` `main`, `page.py` `main`, `sites.py` `main`; `plan.py` `parser`'s `review-delivered` prog. Logic: `tests/py/test_help.py`, `TestAsked` (the deepest command; a refused word before the flag; a word that is not the flag; record's, hold's and ops's parsers) and `TestAnswered` (each entry point prints its usage and exits 0 with no recutils on PATH and a teams file that fails to be read).

**1.2** `plugin/bin/crew`: `usage` with a command and a word; the help check after `cmd`, setting `asked`, which the Flume run's name read skips. `plugin/bin/crew-role`: its check before `scope`. End to end: `tests/t-help.sh`: `crew tell wldn-planner --help` and `-h`, the planner running as its kind, nothing asked; `crew fix tenant-environments tidy --help`, nothing launched; every dispatched command with `--help` and `-h`, its usage printed, with no call in the stubs' log, no launch, no entry on either host and the state branch unmoved; `crew --help`, `crew -h`, `crew-role wldn planner --help`; and `crew tell wldn-planner "--help with ..."` asked of the planner.

**1.3** README's paragraph after the bolt commands, the crew skill's line under the command's path, `crew`'s usage header's closing paragraph, and `code.11` in `core.md`.
