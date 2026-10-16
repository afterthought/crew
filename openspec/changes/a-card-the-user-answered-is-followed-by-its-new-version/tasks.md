# Tasks

## 1. The act

- [x] 1.1 `row_card_change` changes a waiting card in place. It acks a card the user answered with the change note and posts the new version following it, and posts a card that is not found again. Every post under a row's key after a closed card takes the key's revision. Logic: `tests/py/test_card_commands.py`, `cards.revision`, `cards.post_key` and the act on its stand-in. Journey: `tests/t-cards.sh` on the stub, which refuses changing an answered card (`briefs.16`).

## 2. The suite

- [ ] 2.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
