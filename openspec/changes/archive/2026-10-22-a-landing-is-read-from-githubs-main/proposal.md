## Why

On 2026-10-22 swancloud's bolt `a-landed-places-preview-is-released` landed on GitHub's main at bf8ae5d, yet `crew bolt submit` told main-level ops "did not land: the submission exited 3, and main is where it was". sluice had pushed the landing and only then failed, releasing a try place whose release command the landing itself had changed; it exited 3 ("sluice itself failed"). crew's landing reads the host's own `main` before and after the submission and trusts only an exit of 0, so it called a landed bolt unlanded, left its branch unmarked and sent ops away from `crew bolt land` (signal 2026-10-22-swancloud-ops-b237b51b/01).

A landing is on main once GitHub's main holds the bolt's merge, whatever sluice exited after its push. `plan.18` already has every read of main in crew be `origin/main` after a fetch; the landing is the read that still isn't.

## What Changes

- `crew bolt submit` reads main now (GitHub's `origin/main` after a fetch, or the kit's own main when it has no origin) before it submits, and refuses, submitting nothing, when it can't.
- After sluice's outcome it reads main now again, after a fresh fetch, and whether that holds the commit it submitted.
- The bolt has landed when main moved and holds the bolt's tip, whatever sluice exited. When sluice's exit is not 0, crew says the bolt landed and names sluice's exit and last words as what came after the push, sluice's to report apart.
- A landed bolt's branch is marked landed and ops is told `crew bolt land <bolt>`, on any exit.
- crew says "main is where it was" only when main now did not move. When main moved without the bolt (another landing), crew says the bolt did not land and names where main is. When GitHub can't be read after the submission, crew says it can't tell whether the bolt landed, naming why and sluice's exit, and marks nothing.
- The decision moves wholly into Python. The landing script only reports what it read, and the mark is set by a short script crew runs once it has decided the bolt landed (`code.7`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: adds the requirement "A landing is read from GitHub's main". It stands beside "A bolt lands on main on the user's word", which the open change `no-worktree-holds-main-or-a-bolt-branch` rewrites and this change leaves alone.

## Impact

- `plugin/lib/plan.py`: `LANDING`, `landing_said`, `bolt_submit`, and a new mark script beside `LANDING`. It reuses `MAIN`, `host_run` and `kit.main_now` as `crew bolt land` already does.
- `tests/py/test_landing.py`: the logic cases of `landing_said`, rewritten to the new facts, plus the signal's case.
- `tests/contract/test_git.py`: the landing's contract cases. These are joined by a kit with an origin, where a stand-in sluice pushes the landing and exits 3 without moving the host's main.
- No brief, rule or other spec changes. `main-ops.md` already sends ops to `crew bolt land` on crew's word, and `plan.18`'s details already state this reading.

## Touches

```
plugin/lib/plan.py
tests/py/test_landing.py
tests/contract/test_git.py
```
