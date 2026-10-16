# Tasks

## 1. `crew record`

- [ ] 1.1 `crew record <kit> <n> --proposed|--accepted|--rejected [--settled-in-pane] [--alternatives <file>]` records the status, raises the card unless settled in the pane, as a choice when a rule decided, closes it on accepted or rejected, and refuses a status the file does not hold or an alternatives file it cannot read. Logic: `tests/py/test_cards.py`, the record builder's two forms and the refusals. Journey: `tests/t-cards.sh` (`briefs.15`).
- [ ] 1.2 `crew record` is in `plugin/bin/crew`'s usage header, README and `plugin/skills/crew/SKILL.md`. Journey: `tests/t-docs.sh` (`docs.2`).

## 2. The suite

- [ ] 2.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
