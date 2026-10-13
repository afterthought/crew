Recorded on 2026-10-13, after the build, from the commits that built it: 34588ca and 0908779.

# Proposal

## Why

On 2026-10-10 `t-stage-ends` and `t-amend` failed under a load average of 247 on mac-studio and passed alone (signal 2026-10-10-crw-1-conductor-e7003d11/01): `t-stage-ends` slept 1.1 s so a commit landed in a later second, and its waits had limits of sixty seconds. A test that decides its outcome by the clock reddens a bolt's verification for the host's load rather than the bolt's fault (`tests.8`).

## What Changes

- A test waits on the condition it proves: `until_ok` in `tests/lib.sh` runs a check every tenth of a second until it holds, for up to ten minutes, and ends as soon as it holds, so a green run waits no longer than it must and a loaded host does not redden it.
- Every polling loop a test makes has a ten-minute limit, and a background wait's timeout is thirty minutes.
- `crew events --follow`'s test waits for its follower's tails to start and to go, rather than sleeping two seconds and one.
- A test that needs a commit in an earlier second backdates it rather than sleeping into the next one.
- The prompts journey's stop-short is said once the stage's wait has made its first look, a condition, rather than within crew needs' minute.
- A sleep that only orders two writes, which load can only lengthen, stays.

## Capabilities

### Modified Capabilities

- `test-suite`: a test waits on a condition, never on the clock.

## Impact

`tests/lib.sh` and the end-to-end tests' waits; `docs/architecture/tests.md` (`tests.8`).

## Touches

```
tests/**
```
