# Tasks

## 1. A help flag shows a command's usage and acts on nothing

- [x] 1.1 Every Python entry point answers `-h` or `--help` among its arguments with the usage of the deepest command its words name and exits 0, before it checks for recutils, reads the teams file or refuses a word ahead of the flag (design, Decisions 2 to 4; Task notes 1.1). Passes `tests/py/test_help.py` (`tests/suite logic`).
- [x] 1.2 Every command `crew` dispatches, and `crew-role`, answers the flag with its usage and exits 0, calling no tool, starting no agent, writing no entry and moving no branch, and a word that is not the flag is a word (design, Decisions 1, 4 and 5; Task notes 1.2). Verify `tests/suite t-help` ends with "0 failed".

## 2. The docs and the change's tests

- [x] 2.1 README, the crew skill, `crew`'s usage header and `code.11` say every command answers a help flag and acts on nothing (`docs.2`; Task notes 1.3). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 2.2 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
