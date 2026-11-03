# Tasks

Each check is a moon task of the `tests` project run through `tests/suite`. `logic` is `tests:logic`, `contract` is `tests:contract`, and an end-to-end test `t-<name>` is `tests:t-<name>`. Build the groups in order. Submit nothing, and never run `wt submit --help`.

## 1. The teamless crew on today's main

- [x] 1.1 The branch holds one commit applying ccb5f9a9's tree three-way against 09b2cf4d onto f3c5abd4, with every one of the 21 conflicts resolved as Decision 2's table says and no conflict marker or unmerged path left (design Decisions 1 and 2; Task notes 1.1). Verify `tests/suite logic contract` ends with "0 failed".
- [x] 1.2 Nothing of #430's stuck report is left: no `stuck_report`, `stuck_said`, `report_time`, `gather.since` or `transcript.last_words`, and none of their cases, unless something the teamless crew reaches calls it (design Decision 3; Task notes 1.2). Verify `tests/suite logic contract` ends with "0 failed".
- [x] 1.3 A partition's batch is reckoned as the teamless crew reckons it, on its main level's host over every started bolt, with nothing of #435's wait or team reckoning left, and the rail's branch-alone cases keep their fixed clock (design Decision 4; Task notes 1.3). Verify `tests/suite logic` ends with "0 failed".
- [x] 1.4 The design agent's brief carries the teamless words, the Opus model and #425's and #426's words on records. `t-briefs` pins those words and none of the conductor's stuck report or the stage briefs' browser words (design Decisions 2 and 4; Task notes 1.4). Verify `tests/suite t-briefs` ends with "0 failed".
- [x] 1.5 README, the crew skill and `crew`'s usage header say the teamless crew together, with nothing of #430's (design Decision 3; `docs.2`; Task notes 1.5). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 1.6 `tests/moon.yml` is in step with the tests: no task for a deleted test, no `# Reads:` path that is gone (`tests.10`; Task notes 1.6). Verify `tests/suite logic` ends with "0 failed", since it refuses to run while the tasks are out of step.

## 2. The specs and the pages

- [x] 2.1 `openspec/specs/` holds `the-team-machinery-leaves`'s synced specs, with main's Opus models and #430's requirement kept for this change's delta to remove, and the restored archives are present (design Decision 2; Task notes 2.1). Verify `openspec validate crew-runs-without-teams-on-deneb` and `openspec validate --specs` both pass.
- [x] 2.2 crew refuses the box's version-2 teams file and a version-5 file holding `teams`, each naming swancloud's `lib/crew-teams.nix` and doing nothing (main-level delta; Task notes 2.2). Passes `tests/py/test_teams.py` (`tests/suite logic`).
- [x] 2.3 The rule pages carry #418's amendments around main's later records, cite this change on `teamless/deneb` where they cited the reverted landing, and `_open.md` names deneb's crew from the branch and the stage briefs' browser words left behind (design Decision 6; Task notes 2.3). Verify `git grep -n 9d590e9f -- docs/architecture` prints nothing.

## 3. The gate and the branch

- [x] 3.1 Every check crew's gate requires of main that the head affects passes on the branch (design Decision 7; Task notes 3.1). Verify `sluice exec main` passes every check it runs.
- [x] 3.2 The branch is on GitHub as `teamless/deneb`, pushed without force, and main is untouched (design Decision 7; Task notes 3.2). Verify `git ls-remote origin refs/heads/teamless/deneb` names `git rev-parse HEAD`.
