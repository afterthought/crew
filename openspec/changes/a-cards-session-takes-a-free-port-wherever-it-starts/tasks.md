# Tasks

## 1. A card's session takes a free port of the range

- [ ] 1.1 crew starts every card's reading session with a port range, the environment's own when it names one and else 19432–19451, proved by cases in `tests/py/test_card_commands.py` and a green `devenv shell -- moon run tests:logic` (design, Task notes 1.1).
- [ ] 1.2 The stub plannotator chooses its port as plannotator 0.28.26 does, and a card's session started with no port named, while another holds 19432, prints a link on another port, proved by `tests/suite cards` passing and failing without 1.1 (design, Task notes 1.2).

## 2. The documents say it

- [ ] 2.1 README says a card's session takes the first free port of the environment's range or crew's own, proved by `tests/suite docs` passing (design, Task notes 2.1).
- [ ] 2.2 `tests/suite --affected` passes once the change is done.
