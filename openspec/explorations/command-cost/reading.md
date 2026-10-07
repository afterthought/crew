# Why crew's test suite takes ~20 minutes

Measured by crw-1-ops on 2026-10-07 at bolt/decisions-shown-whole (a0a35a3), on mac-studio, with `devenv shell -- tests/run <name>`. All tests passed.

## Times, one test at a time

| Test | Time | Share of a 20 min run |
|---|---|---|
| t-units-ws | 70.9 s | 5.9% |
| t-merge | 70.2 s | 5.9% |
| t-fix | 46.3 s | 3.9% |
| t-bolt | 41.2 s | 3.4% |
| t-tidy | 12.5 s | 1.0% |
| t-greet | 11.9 s | 1.0% |
| t-docs | 2.3 s | 0.2% |
| t-recutils | 1.7 s | 0.1% |

Starting `devenv shell` takes 19.6 s cold and about 0.4 s warm, and a full run starts it once. The other 33 tests take about 15¾ min together, roughly 28 s each on average; they were not profiled.

## How it was measured

- Each test line was traced with timestamps (bash xtrace with `$EPOCHREALTIME`, enabled through `BASH_ENV` for `tests/t-*.sh` only).
- Timing shims on PATH wrapped `git`, `python3`, `jq` and `wt`, logging each process's start, end and parent. From those, each command's own time was computed, excluding the processes it started.
- Tests ran through `tests/run` as usual, so the stubs stayed in place.

Test-side work (the tests' own git, jq and python) is under 1 s per test. The rest is `crew` itself.

## Three costs

**1. The kit read starts `openspec` twice per unit worktree, and runs several times per command.**
`plugin/lib/gather.py` `place()` runs `openspec list --json` and `openspec status --change <unit> --json` for every unit worktree under places/. `openspec` is a Node CLI and takes about 0.3–0.5 s just to start (`openspec --version` takes 0.26 s; `openspec list` takes 0.5–0.9 s). So one read of the kits costs about 0.65 s per unit in flight: 0.6 s with one unit, 1.3 s with two, 1.9–2.0 s with three.

`crew` (bash) calls `plan.py` as separate processes per step, and several steps each do their own full read (`plan.py:654`):
- `crew unit run` reads in `_slots`, `_ends` and `_run`.
- `crew status` reads in `_slots` (often twice) and `_ends`.

Nothing is shared between those reads. In t-merge, 23 reads took about 33 of 69 s; in t-units-ws, 29 reads took about 30 of 70 s.

**2. Each command is several Python runs, each with a fixed cost of about 0.25 s.**
That cost covers Python start, `import plan` (~65 ms), a `git fetch` of the state repository (~55 ms) and reading the plan. One `crew unit run` makes 5–6 `plan.py` runs: `_team-of` twice with identical arguments, then `_slots`, `_tidy`, `_ends` and `_run`. t-merge made 56 such runs, about 14 s of fixed cost.

**3. The stub `herdr` is Python, at about 40 ms per call.** Slow tests make 100–165 calls, costing 4–7 s.

## Why t-fix and t-bolt are slow

A fix's worktree is read with git only, so these two barely pay cost 1. They are slow because they run many commands: t-fix runs about 20 `crew` commands and t-bolt about 38, at 1–2 s each. That is cost 2 plus a commit and push to the state repository on every plan write.

## The production cost is the same

A real `crew status` on a team with three units in flight pays about 2 s per kit read, and reads two or three times.

## Levers that look obvious (not designed, not tried)

- Read the kits once per `crew` command and pass the result to the later steps, rather than once per `plan.py` step.
- Get a place's task counts and planning status without `openspec`: parse `tasks.md` and check which artifacts exist. Alternatively, call `openspec` once per kit rather than twice per place.
- Fold the per-step `plan.py` calls (`_team-of` ×2, `_slots`, `_tidy`, `_ends`, `_run`) into one Python run per command.
- Fetch the state repository once per command, not once per step.

## What is decided from this reading (swancloud-design, 2026-10-07)

The three costs are one shape: a `crew` command is several `plan.py` runs, each of which reads the kits and fetches the state branch again. What must be true is that a command reads each kit once and fetches the state branch once, however many steps it has, and that `crew status` on a team with three units in flight answers in about the time of one kit read. How the facts a stage rests on are read, through the `openspec` command line or from the change's files directly, is the construct's choice, under one constraint: on the same worktree the two readings agree, and a test holds them to it, so the stage rules keep openspec's meaning. The stub `herdr`'s cost is the test harness's and goes with the same work. Unit: `a-command-reads-the-kits-once`.
