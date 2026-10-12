---
number: 21
title: A test takes what it runs as its inputs, and a host bounds the tests it runs at once
status: accepted
date: 2026-10-11
decision-makers:
- Chuck Swanberg
---

# A test takes what it runs as its inputs, and a host bounds the tests it runs at once

Deciders: the user, who stopped every team on 2026-10-11 with mac-studio at a load of 135 to 386 and asked for crew's developer loop to be fixed first, sized for three or more crew teams at once; the recovery session, which measured what follows.
Amends: record 0008, its option "tasks narrower than `plugin/**`", which it rejected.
Sources: the measurements below, taken on mac-studio (10 cores) with every team down; `tests/moon-tasks`; `tests/slot`; `tests/t-slot.sh`; `tests/t-suite.sh`.

## Context and problem statement

Every task's inputs held all of `plugin/**`, so an edit to a role's brief, a skill or a hook, a third of crew's recent plugin edits, reran all 59 tests, and so did every `--affected` run of a coder touching one. Nothing bounded the tests a host ran at once: each suite runs ten wide, and three crew teams' coders, gates and verifications each ran theirs. One full suite, uncached, on an idle mac-studio took 401 s of wall time and 1,922 s of CPU and reached a load of 146 by itself; two side by side took 601 s each; with three teams the host went past 380 and tests that wait on the clock failed.

What a test's outcome depends on was read rather than assumed. Each test ran with Python's audit hook logging every file under `plugin/` it opened or ran, `__pycache__` mapped to its source: 26 tests touch only the command core (`plugin/bin/` and the modules `plan.py` and `crew.py` import), 29 run `plugin/hooks/` (the stub claude runs the session-start hook for every agent it starts, and three tests run the card and question hooks), 27 read `plugin/roles/`, and `board.py`, `page.py`, `page.html` and `sites.py` are each read by the one or two tests of their own. The roles were then read with their prose replaced word for word, frontmatter and tokens kept: of the 27, only `t-briefs` and `t-record-team` failed, and `t-roles` builds every role, so a broken role is caught by a test that names the roles.

## Decision outcome

1. **A task's inputs are the command core and what its test names.** `tests/moon-tasks` gives every task the core (`plugin/bin/**`, `crew.py`, `plan.py`, `record.py`, `gather.py`, `transcript.py`, `questions.py`), `tests/run`, `tests/slot`, `tests/lib.sh`, `tests/stubs/**` and the devenv files; anything else of `plugin/` is the input of a test that names it on its `# Reads:` line: `plugin/hooks/` when it starts an agent, `plugin/roles/` when its outcome rests on a brief's words, and the board, page and sites modules when it runs them. A test that refers to a path through `$CREW` or `$TESTS` its inputs leave out still refuses the suite (`tests/moon-tasks --check`); the folder `plugin/lib` itself, put on Python's path to import the core, counts as the core.
2. **A landing runs every test afresh.** The merge gate passes its target (`tests/suite --gate {{ target }}`); a merge onto main runs with nothing replayed, so a test whose inputs missed something can replay a stale pass into a bolt but never onto main.
3. **A host bounds the tests it runs at once (`tests.9`).** `tests/run` runs each test in one of the host's slots (`tests/slot`): lock files under `~/.cache/crew/test-slots`, half the host's cores unless `CREW_TEST_SLOTS` says otherwise, shared by every worktree, team and suite on the host, let go by the system when the test ends, killed or not. A test started inside another's slot runs in it.

### Consequences

- Amended the same day: with two fewer slots than cores, eight tests at once still left mac-studio no idle CPU, since each test keeps about a core busy starting processes; a host's slots are half its cores, so the agents and the user keep the rest.

- An edit to a role's prose reruns 3 tests, not 59; to a hook, 29; to the board, page or sites module, its own one or two. An edit to the core still reruns everything: that is the work every command does.
- Three teams' suites at once queue on the host's slots rather than thrash it; a suite alone is still ten tasks wide, and moon's scheduling is unchanged.
- The gate's command changed, so each host's first merge after this lands waits for the user's `wt config approvals add` in crew's main checkout.
- A test that comes to read a new plugin file through Python names it, or its stale pass is caught at the landing.

## Considered options

- Keep `plugin/**` for every task, as record 0008 chose: correct by construction, and it is what kept every role edit at the cost of the whole suite.
- Inputs read from a trace on every run: exact, but a traced run costs more than it saves, and moon reads inputs before it runs a task.
- A cap through `MOON_CONCURRENCY` alone: bounds one suite, not three teams' suites side by side.
