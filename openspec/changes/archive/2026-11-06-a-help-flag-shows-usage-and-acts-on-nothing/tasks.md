# Tasks

## 1. A help flag shows a command's usage and acts on nothing

- [x] 1.1 Every Python entry point answers `-h` or `--help` among its arguments with the usage of the deepest command its words name, first, before it checks for recutils, reads the teams file or refuses a word ahead of the flag (design, Decisions 3 and 4; Task notes 1.1). Passes `tests/py/test_help.py` (`tests/suite logic`).
- [x] 1.2 `crew` answers the flag for every command whose arguments it reads with that command's own lines of its usage, hands it to the Python parser for the rest before anything is read or forwarded, and `crew-role` answers it with its header (design, Decisions 1, 2 and 5; Task notes 1.2). Verify `tests/suite t-help` ends with "0 failed".
- [x] 1.3 README, the crew skill and `crew`'s usage header say that a help flag prints a command's usage and does nothing else (`docs.2`; Task notes 1.3). Verify `tests/suite t-docs` ends with "0 failed".

## 2. The change's tests

- [x] 2.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
