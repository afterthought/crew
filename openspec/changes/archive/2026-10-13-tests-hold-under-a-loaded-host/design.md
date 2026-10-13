Recorded on 2026-10-13, after the build, from the commits that built it.

# Design

Relies on `tests.8` (a test waits on a condition, never on the clock, with limits that hold under load), `tests.5` and `tests.9` (the suite runs side by side, a host's slots bounding it). Touches `tests.md`'s area.

A limit is there to end a test that would otherwise hang, not to judge its speed, so it is set far past what a loaded host takes: ten minutes for a wait on a condition, thirty for a background wait, and a wait ends the moment its condition holds, so a green run costs nothing more. Where a test needed time to pass, a commit in a later second, it moves the time instead (`GIT_COMMITTER_DATE`), which load cannot stretch.

What `tests.8` names as left, crew's own fifteen-second read-back of a prompt it sent (`taken_within`), is a clock in crew, not in a test, and is not built here: `_open.md`.

## After deploy

None: crew is pulled, not deployed.
