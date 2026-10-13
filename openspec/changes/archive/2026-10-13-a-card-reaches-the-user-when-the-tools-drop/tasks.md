# Tasks

## 1. The client and the decisions

- [x] 1.1 `plugin/lib/cards.py` holds the client for the fleet's `pendingyou mcp --app claude-code`. Per command it opens one session with `whoami` as its first call, waits at most 60 seconds for each reply, and refuses every failure as a `Refusal` in the bridge's or Pending You's words (design: *Decisions*; Task notes 1.1; `read.1`, `read.2`, `code.1`, `code.2`).
- [x] 1.2 The commands' decisions are functions of facts in `cards.py`: the post's arguments, a reply's object and refusal, the area, the area to make, the card a key names, and the answer's lines. Each has logic cases in `tests/py/test_card_commands.py`, and `tests/suite logic` ends with "0 failed" (Task notes 1.2; `code.7`, `tests.11`).

## 2. The commands

- [x] 2.1 `crew card post <key>` refuses what the hook refuses and a card giving crew's fields, fills the key, the session and the area, posts, prints the id and link, and records `card.post` from the reply (design: *Decisions*; Task notes 2.1–2.4; `briefs.11`, `briefs.13`, `briefs.16`, `roles.3`).
- [x] 2.2 `crew card change <key>` changes the agent's card at the version Pending You reports, refuses a change out of its row's form, and records `card.update`.
- [x] 2.3 `crew card close <key> --outcome|--reason` acks or withdraws, records `card.close` and ends the card's session as the hook does.
- [x] 2.4 `crew card read <key> [--json]` prints the card's status, turn, answer and words, and records nothing.

## 3. The stub and the end-to-end test

- [x] 3.1 `tests/stubs/pendingyou` answers `mcp --app claude-code` as Task notes 3.1 say, and `tests/run` refuses to start when it would not shadow `pendingyou` (`tests.4`).
- [x] 3.2 `tests/t-card-commands.sh` proves each command's wiring on the stub as Task notes 3.2 list, `tests/moon-tasks` is run and `tests/moon.yml` committed, and `tests/suite t-card-commands` ends with "0 failed" (`tests.10`, `tests.11`).

## 4. The command's documentation

- [x] 4.1 `plugin/bin/crew`'s usage, README and `plugin/skills/crew/SKILL.md` name the four commands together, and `tests/suite t-docs` ends with "0 failed" (`docs.2`).
- [x] 4.2 `tests/suite --affected` ends with "0 failed" (`tests.1`).
