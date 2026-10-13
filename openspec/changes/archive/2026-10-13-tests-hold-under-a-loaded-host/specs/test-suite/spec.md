## ADDED Requirements

### Requirement: A test waits on a condition, never on the clock
No fixed sleep SHALL decide a test's outcome: a test SHALL wait on the condition it proves, ending as soon as it holds, with a limit that holds on a host loaded far past its cores, ten minutes for a wait on a condition and thirty for a background wait; a test that needs time to have passed SHALL move the time rather than wait for it.

#### Scenario: A follower's tails on a loaded host
- **WHEN** the test of `crew events --follow` runs on a host loaded past its cores and the follower's tails take longer than usual to start
- **THEN** the test waits until they start, up to ten minutes, and passes

#### Scenario: A commit in an earlier second
- **WHEN** a test needs a commit made before a stage began
- **THEN** it backdates the commit rather than sleeping into the next second
