# Proposal

## Why

`plan.14`'s first clause: a landing records the sha main holds afterwards. `crew bolt land` recorded none, so nothing could tell which landings a deploy carried.

## What Changes

- `crew bolt land` reads the commit the kit's main holds on the team's host, with the check of how far it is from GitHub's that it already ran, and its `bolt.land` entry names the kit (`Repo`) and that commit (`Head`). `crew events` and `crew trace` show it on the landing's line.

## Capabilities

### Modified Capabilities

- `bolt-teams`: a landing records the commit main holds afterwards.

## Impact

`plugin/lib/plan.py` (`MAIN`, `main_held`, `bolt_land`, `write`), `plugin/lib/record.py` (`Repo`), README, the usage; `tests/py/test_bolt_commands.py`, `tests/py/test_record.py`, `tests/contract/test_git.py`, `tests/t-journey-land.sh`.

## Touches

```
plugin/lib/plan.py
plugin/lib/record.py
README.md
tests/**
```
