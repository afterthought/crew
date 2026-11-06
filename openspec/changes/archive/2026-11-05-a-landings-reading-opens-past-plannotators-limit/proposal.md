# A landing's reading opens past Plannotator's limit

## Why

On 2026-11-06 at 03:12Z on chuck-herdr-alpha, switchboard-kit's bolt `a-deploy-row-follows-its-stack-to-the-end` was proven and stood on wldn's landings card with no reading. Its reading would not open, and `crew card session` refused it again with the same words from Plannotator: "File too large to annotate (max 2MB): /home/chuck/.local/state/crew/cards/wldn/land/a-deploy-row-follows-its-stack-to-the-end/df72a7f/11-a-deploy-row-follows-its-stack-to-the-end-diff.txt" (signals wldn 2026-11-06-swb-4-conductor-8fde2fb6/01, relayed as swancloud 2026-11-06-swancloud-operator-e8f1eb96/01). The bolt can land without it, but the user reads a landing's reading before they tick it.

crew writes a bolt's whole diff against main into one text file. Plannotator 0.28.48 refuses any file of more than 2 MiB, and with it the whole review that names it. So any bolt whose diff passes 2 MiB has no reading.

The user ruled that the box's crew faults are fixed on crew main, for the box: "Yes: fix them on crew main, for the box". So this is a fix on crew's main.

## What Changes

- **The diff comes in several files when it must.** A landing's reading holds the bolt's diff in as many files as keep each within the 2 MB Plannotator opens in one file. Each file holds whole files' changes, in git's order. A diff that fits in one file is written as before, `<nn>-<bolt>-diff.txt`. Several are `<nn>-<bolt>-diff-<k>-of-<m>.txt`, and the reading's first page says how many there are. Plannotator puts no cap on a review of several files together, so every part opens.
- **A file whose own change passes the limit is named, never cut.** No part can hold such a file's change whole. In its place in the diff, a line names the file and its size. The first page names each such file with its size and how many there are, and says where to read them whole: GitHub's compare view of the bolt against main, from where it last met main to its head, and the `git diff` that reads them on the team's host. This is the shape of sluice's rule core.43 for a pull request's commits past the forge's limit.
- crew's stub of Plannotator refuses a file over 2 MiB as Plannotator does (`tests.4`).
- README says how the reading holds a large diff (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: a landing's session holds the bolt's diff in as many files as Plannotator opens. A file whose own change passes the limit is named, with where to read it whole.

## Impact

- `plugin/lib/plan.py`: `landing_reading` takes where the diff is read whole, and `landing_write` gives it that and writes UTF-8. New: the decision `diff_parts`, with `diff_path`, `megabytes` and the constant `PLANNOTATOR_MOST`.
- `tests/stubs/plannotator`, `README.md`.
- Tests: `tests/py/test_landing.py`.
- Nothing the board or the mod draws changes (`code.8` not reached). The run record's fields don't change. Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
tests/stubs/plannotator
tests/py/test_landing.py
README.md
```
