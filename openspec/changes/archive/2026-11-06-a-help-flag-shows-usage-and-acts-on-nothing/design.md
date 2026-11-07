# Design: a help flag shows a command's usage and acts on nothing

## Context

The proposal gives the box's case. Rules this change relies on: `read.1`, which has crew refuse rather than guess, and a flag taken as words is a guess; `record.1`, under which a command that acts records its act, so a help request must stop before any act; `code.3`, which forwards a team's command to its host before it touches state, so the flag must be answered before the forward; `code.7`, which makes the decision of which usage is asked a function of the arguments alone; `docs.2`, which has README, the crew skill and `crew`'s usage header say the change together; `tests.4` and `tests.11`, which put the reproducing case in the lowest tier that holds it. The change adds `code.11` to `core.md`, the rule the brief asks for, binding all of crew. It touches the areas of `teams.md` (`plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/lib/crew.py`), `plan.md` (`plugin/lib/plan.py`), `record.md` (`plugin/lib/record.py`), `briefs.md` (`plugin/skills/`), `tests.md` (`tests/`) and `docs.md` (`README.md`, `openspec/`, `docs/`). It departs from no rule.

How crew reads a command's arguments today:

- **bash reads some.** `plugin/bin/crew` dispatches every command. It reads the arguments of the team commands, `needs`, `fix`, `tell`, `send`, `unit|chore free|wait|run`, `main up|down|status`, `review`, `console`, `revive`, `operator`, `_end-short`, `_tidy`, `_construct-again` and `_dispatch` itself, then runs one Python process with what it chose to pass (`one`), which may forward the command to the team's host. It puts free words after `--` (`needs`, `fix`, `unit run`), so no parser reads a flag there, and it drops what it does not read (`up <team> --help`, `main up <label> --help`, `_dispatch up <label> --help`, `revive --help`).
- **Python parsers read the rest.** bash hands the other commands whole to `plan.py`, `record.py`, `board.py`, `hold.py`, `ops.py`, `page.py` or `sites.py`. Each parses with argparse, whose subparsers answer `-h` and `--help`. But `plan.py` checks for recutils first, `board.py` and `hold.py` read the teams file first, and argparse refuses a word ahead of the flag that fails a type or a choice before it reaches the flag. `hold.py` reads `hold`, `go` and `update` by hand, and `crew hold <host> --help` holds the host with `--help` as its reason.

## Decisions

### Decision 1: the help flag is answered by whatever reads the command's arguments, at its entry

bash answers the flag for every command whose arguments it reads, right after it has split out `--force` and `--no-greet`, before it reads the Flume run's name, reads the teams file, runs Python or reaches another host. A command bash hands whole to a Python parser passes through to its arm, and that parser answers before anything else. `_end-short`, `_tidy`, `_construct-again` and `_dispatch`, which bash checks and passes to plan.py's entry of the same name, go to that entry at once, whose parser is their grammar. `hold`, `go` and `update`, which `hold.py` reads by hand, are answered by bash.

bash's list of the commands a Python parser answers is the arms that `exec` one. A command added to the dispatch and missing from the list is answered by bash, from its usage lines or the whole usage, and acts on nothing either way; `t-help` lists every arm and fails on one it does not run with the flag.

Considered: answering only in Python. bash drops, reorders or quotes the words before Python sees them, so the flag never reaches a parser for `needs`, `fix`, `unit run`, `up` or `revive`. Considered: one bash check for every command, printing the header's lines for each. It would replace argparse's usage for `crew bolt|unit|chore|plan|signal`, which the header's `--help says more` points to, and would print nothing for the internal commands the header does not list.

### Decision 2: one usage per command, the one its entry point already prints

`crew` prints its header as its usage. `usage <command> [<word>]` prints only the command's lines there: each line `crew <command> ...` with the lines indented under it, those whose next word names `<word>` when any does (`crew unit run`, `crew main up`, `crew hold status`), else every line of the command (`crew fix`, `crew tell`). `operator`, the console's old name, prints `crew console`'s lines. A command the header names nowhere prints the whole usage. A command a Python parser answers prints argparse's usage of the deepest command its words name, as `crew bolt give --help` always did. There is no second text to keep in step.

`plan.py`'s `review-delivered` parser takes `prog="crew review delivered"`, as `signal-move` does, so its usage names the command as typed.

### Decision 3: a Python entry point answers before it reads anything, and past a word it would refuse

`crew.usage_asked(ap, argv)` decides: with no argument exactly `-h` or `--help` it is `None`; otherwise it walks the leading words down the parser's subcommands and gives the deepest parser they name. `crew.answer_usage(ap, argv)` prints that parser's help and exits 0. Each Python entry point calls it first: `plan.py` before `need_recutils`, `board.py` with its parser built before the teams file is read, `hold.py` for its `_` commands before it reads the teams file, `record.py`, `ops.py`, `page.py` and `sites.py` before they parse. Since the decision reads only the words, `crew plan approve three --help` gives `crew plan approve`'s usage where argparse alone would refuse `three` first.

### Decision 4: only an argument exactly `-h` or `--help` asks, wherever it stands

The flag is read among all of a command's arguments, free words included, since a free word that is exactly `--help` is a request for the usage, as the signal's agent meant it. Any other word is a word: `--helpful`, `-hx`, `help` and `--help with the tenant table` are passed on as before.

Considered: reading `--` as the end of flags. bash takes no `--` from the user, and its own `--` before free words is what let `--help` through to `_needs`.

### Decision 5: crew-role too

`crew-role` is crew's other command. Its header is its usage; with the flag among its arguments it prints the header and starts no Claude.

### What deneb's teamless crew gets

`teamless/deneb` dispatches the same bash `tell`, `send`, `main up|down|status`, `review`, `console`, `revive` and `operator`, and `hold.py`'s `hold`, `go` and `update`; `crew tell <agent> --help`, `crew send <partition> --help`, `crew hold <host> --help`, `crew main up <label> --help` and `crew revive --help` act there as they did here. It needs the same check on its own dispatch. That line is not main, so this change does not reach it.

## After deploy

None. Every case is held by the logic tier and by `t-help` on the stubs; what a host runs is its pin of crew's release, not a step of this change.

## Task notes

**1.1** `plugin/lib/crew.py`: `HELP`, `usage_asked`, `answer_usage`. Called first in `plan.py` `main`, `record.py` `main`, `board.py` `main`, `hold.py` `main`, `ops.py` `main`, `page.py` `main`, `sites.py` `main`; `plan.py` `parser`'s `review-delivered` prog. Logic: `tests/py/test_help.py`, `TestAsked` (the deepest command; a refused word before the flag; a word that is not the flag; record's, hold's and ops's parsers) and `TestAnswered` (each entry point prints its usage and exits 0 with no recutils on PATH and a teams file that fails to be read).

**1.2** `plugin/bin/crew`: `usage` with a command and a word; the help check after `cmd`, setting `asked`, which the Flume run's name read skips. `plugin/bin/crew-role`: its check before `scope`. End to end: `tests/t-help.sh`: `crew needs --help` and `-h` as `swb-1-unit-1` in construct, its stage still begun, no `stage.end`, nobody told, its agent's pane kept; `crew fix swb-1 tidy --help`, no place and no branch; `crew unit run b code --help`, no place; every dispatched command with `--help` and `-h`, its usage printed, with no call in the stubs' log, no launch, no entry on either host, the state branch unmoved and the stages file unchanged; `crew --help`, `crew -h`, `crew-role swb-1 conductor --help`; and `crew needs "--help with ..."` ending its stage.

**1.3** README's paragraph after the team commands, the crew skill's line under the command's path, and `crew`'s usage header's closing paragraph.
