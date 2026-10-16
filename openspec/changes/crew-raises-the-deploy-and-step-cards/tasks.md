# Tasks

## 1. The deploy's and the step's cards

- [x] 1.1 `crew ops offer <env> --to <sha> --from <sha|none> [--notes <file>] [--steps <file>]` posts or changes the deploy's card with the kit's release notes and the range's steps on its face, following the landing card that put the head on main, and tells main-level ops the line that adopts it, `call get_request (requestId <id>, name <role>)`; `crew ops record --act end` closes it with the outcome; `crew ops step` posts a user's or a held step's card, one at a time, each following the one before, and closes it on done or declined. Logic: `tests/py/test_ops.py` `TestRows`, the held step's row and words, the notes handed and the offer with none, the one-at-a-time chain. Journey: `tests/t-journey-ops.sh` (`plan.14`).
- [x] 1.2 `crew ops offer`'s `--notes` and `--steps` are in `plugin/bin/crew`'s usage header, README and `plugin/skills/crew/SKILL.md`. Journey: `tests/t-docs.sh` (`docs.2`).
- [x] 1.3 `main-ops.md`'s *Deploying main* says crew raises the deploy's and the step's cards, ops adopting each by the line `crew tell` brings it and running `crew ops approve`, a step's state or a held step as the user answered; it no longer posts or closes them. Journey: `tests/t-briefs.sh` pins the words (`tests.6`, `plan.14`).

## 2. The suite

- [ ] 2.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
