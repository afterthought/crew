# Tasks

## 1. A fix's place and branch name its bolt

- [x] 1.1 `crew fix <team> <name>` makes `fix/<bolt>/<name>` from the team's bolt at `places/fix-<bolt>--<name>`, and finds a fix it already holds by its new name or its old `fix/<name>`, using the branch and place its slot recorded (design.md, Task notes 1.1). Verify `tests/t-fix.sh`, rewritten for the new names, passes.
- [x] 1.2 A new fix whose branch or place already exists is refused before any slot is taken, and no fix agent starts in a place that is not on the fix's own branch tracking the team's bolt, each with a refused `fix.start` entry (design.md, Task notes 1.2). Verify with a test where swb-1 and swb-2 each start `bolt-takes-main` on their own bolts in one kit and get two places and two branches, plus a test for each refusal.
- [x] 1.3 Merging, freeing and removing a fix work from the place and branch its slot recorded, so an old `fix/<name>` fix merges and is removed, and the run record keeps `fix/<bolt>/<name>` objects and `fix(<name>)` reasons (design.md, Task notes 1.3). Verify with a test that merges a hand-made old-style fix, and with `tests/t-record-team.sh`, `tests/t-units-ws.sh`, `tests/t-bolts.sh` and `tests/t-sites.sh` updated for the new names.
- [ ] 1.4 The conductor's and coder's briefs, `README.md` and the usage header give a fix's new place and branch and say that a name already in use on the bolt is refused (design.md, Task notes 1.4). Verify `devenv shell -- tests/run` ends with "0 failed".
