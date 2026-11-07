## MODIFIED Requirements

### Requirement: A give to a team holding a waiting bolt restarts its roles at their next stop
A give to a team that holds a proven bolt SHALL restart neither its conductor nor its ops at once: each SHALL be restarted at its next stop, once idle, as an agent whose team's bolt changed under it is, the conductor fresh and ops with its conversation. The conductor's greeting at that restart SHALL name the bolt it now builds, the bolt that waits to land as a row of its kit's landings card, main-level ops's, that crew tells it when the user sends that bolt's reading and `crew card read land/<bolt>` then gives the notes, and each fix in flight on it. It SHALL name no wait to start. A give to a team that holds no bolt SHALL restart its ops at once, greeted with the bolt, and its conductor fresh on the team's host, at once when herdr reads it idle with no question open and nothing of its own running in the background, else at its next stop, its greeting naming the bolt.

#### Scenario: A give while the conductor waits on its landing card
- **WHEN** `crew bolt give swc-1` gives `ssh-fix` while swc-1 holds `doctor-rows`, a row of its kit's landings card, and swc-1-conductor is idle
- **THEN** the conductor is restarted fresh once idle, and its first message says it builds `ssh-fix`, that `doctor-rows` waits to land as a row of the kit's landings card, that crew tells it when the user sends `land/doctor-rows`'s reading and `crew card read land/doctor-rows` gives the notes, and names no `crew card wait`

#### Scenario: A give to a team that holds no bolt
- **WHEN** `crew bolt give swb-1 smoke` gives swb-1 its only bolt while its conductor and ops are idle with nothing of their own running
- **THEN** the give restarts ops and greets it with `smoke`, and the conductor is restarted fresh on its host at once, its greeting saying its team now holds `smoke`

## ADDED Requirements

### Requirement: A give's notice reaches its conductor whatever it is doing
Every give to a team on today's path SHALL reach the team's conductor with the bolt it was given, handed to the team's host before the give starts any agent. The host SHALL tell an idle conductor with no question open at once: by its restart's greeting when it is due a restart that may run now, else by crew's notice naming the bolt, or both bolts beside one that waits to land. A working conductor SHALL be told at the end of its turn. A start of the conductor after the give SHALL be its notice.

#### Scenario: An idle conductor whose restart waits on its own background work
- **WHEN** `crew bolt give swb-2` gives `the-hand-run-takes-a-release-whole-again` while swb-2 holds `the-full-stand-passes-the-runner-test-on-githubs-runner`, which waits to land, and swb-2-conductor is idle with a `crew tell` of its own running in the background
- **THEN** crew tells swb-2-conductor at once that its team builds `the-hand-run-takes-a-release-whole-again` and that `the-full-stand-passes-the-runner-test-on-githubs-runner` waits to land, and that crew starts it again at a later stop, the run record holds a `bolt.notice` for it, and it is restarted only once that work is over

#### Scenario: A working conductor
- **WHEN** the give finds swb-2-conductor working
- **THEN** nothing is typed to it, and at the end of its turn it is told, by its restart's greeting or by crew's notice

#### Scenario: Started since the give
- **WHEN** swb-2-conductor is started again by `crew rebuild swb-2` before its notice is given
- **THEN** crew tells it nothing more of the give, its greeting having told it

### Requirement: A give's notice is recorded, and one not given is said
crew SHALL record a `bolt.notice` on the bolt, its team and the conductor when crew's notice tells the conductor. When the conductor is not up, its team's host could not take the notice, or it did not take it, crew SHALL say so and record a refused `bolt.notice` in crew's words, which say how the conductor is told, each reason once. A notice not taken SHALL be tried again at the end of the conductor's next turn.

#### Scenario: A conductor not up
- **WHEN** the give finds swb-2-conductor not up
- **THEN** the give says it was not told and that `crew up swb-2` starts and greets it, and the run record holds a refused `bolt.notice` in those words

#### Scenario: The team's host does not answer
- **WHEN** chuck-herdr-alpha does not answer the give's hand-off of the notice
- **THEN** the give says swb-2-conductor was not told, since its host did not answer, with the `crew tell` that tells it, and records it refused

#### Scenario: A notice not taken
- **WHEN** swb-2-conductor does not take crew's notice, sent twice
- **THEN** the run record holds one refused `bolt.notice` saying so, and the notice is tried again at the end of its next turn
