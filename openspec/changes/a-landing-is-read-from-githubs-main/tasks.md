# Tasks

## 1. The landing is judged by main now

- [x] 1.1 `LANDING` reports main now after a fresh fetch, whether each main holds the submitted tip, sluice's exit and its last words, and no longer refuses a kit with no local `main` nor sets the mark itself (design.md, Decisions 1–2, Task notes 1.1); proven by 2.2.
- [x] 1.2 `bolt_submit` reads main now before submitting (refusing when it can't), decides through `landing_said` against it, marks the branch through a new `LANDED_MARK` script only once landed, and records the landing at main now's commit (design.md, Decisions 1, 3, 4, Task notes 1.2); proven by 2.1 and 2.2.
- [x] 1.3 `landing_said` calls a bolt landed when main now moved and holds its tip on any exit, naming a non-zero exit and sluice's words as after the push; says "main is where it was" only when main now did not move; and names a moved main without the bolt and a main it can't read (design.md, Decision 2); proven by 2.1.

## 2. Cases

- [x] 2.1 Logic cases in `tests/py/test_landing.py` cover every scenario of "A landing is read from GitHub's main", with the signal's case among them, and keep today's words for an exit of 0 (Task notes 2.1); `devenv shell -- moon run tests:logic` is green.
- [ ] 2.2 Contract cases in `tests/contract/test_git.py` land through a stand-in sluice that pushes to a bare origin and exits 3, and through one that pushes nothing and exits 2, alongside the existing cases with no origin (Task notes 2.2); `tests/suite contract` is green.
- [ ] 2.3 `tests/suite --affected` is green.
