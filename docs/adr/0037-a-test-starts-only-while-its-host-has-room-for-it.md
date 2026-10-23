---
number: 37
title: A test starts only while its host has room for it
status: rejected
date: 2026-10-23
decision-makers:
- Chuck Swanberg
---

# A test starts only while its host has room for it

Status: rejected by the user on 2026-10-23, on their card (req_5b3c18a5cdc547959225): "This is terrible. I don't like the decision". `tests.9` stands as record 0021 left it; no unit is queued from this record.

Deciders: the user, who on 2026-10-23 asked the design agent to look at crew's test load again, through the operator: "Also I don't know. I know we did a lot of work to improve the performance of crews running their end-to-end tests but they are just spiking the CPU on this machine. I feel like the designer should look at that again" (signal 2026-10-23-swancloud-design-70084228/01); their words reopen what they held on 2026-10-11 (no new proposals for crew's test load) and settle nothing else here. The decision below is the design agent's, on the user's card.
Amends: record 0021 §3 and its consequences; `tests.9`.
Sources: the reading of deneb below; `tests/slot`; `tests/run`; crew's `.config/sluice.toml` (`[branches."bolt/*"]`, `timeout = "20m"`); swancloud's `.config/sluice.toml` (`parallel = 4`, `batch = true`, 38 `flake-check` tasks); the records of sluice's rounds on deneb at 13:29Z.

## Context and problem statement

Record 0021 bounded the tests a host runs at once by a count of crew's own tests: slots in `~/.cache/crew/test-slots`, the host's cores less two, shared by every crew suite on the host. That bound takes the host as crew's own. Read on deneb (18 cores, 128 GiB) on 2026-10-23 at 13:30Z, the load was 95 (63 at 09:27Z, when the user looked), no CPU idle and half of it the kernel's, with 2,016 processes and 10,918 threads:

- three kits' sluice rounds at once: crew's suite, holding 8 of its 16 slots with six end-to-end tests under way; swancloud's 38 flake checks as moon tasks side by side, `parallel = 4` on each branch; flywheel-next's moon at a concurrency of 4;
- 44 Claude sessions, about two and a third cores and 21 GiB between them;
- the user's own applications: Finder alone at nine tenths of a core for seven days, WindowServer, Wispr Flow;
- memory full (126 of 128 GiB used, 12 GiB in the compressor), not swapping.

crew's round itself held about a core and a half across 79 processes. Its cost is the processes it starts: every crew command is a Python start of a 12,900-line module, 0.15 s of CPU and, on this host that morning, 1 to 4 s of wall time; an end-to-end test runs hundreds. Sixteen such tests at once on a host already carrying two other kits' rounds and forty sessions is the overload record 0021 named for two suites sized as if alone, now across kits and sessions, and the slot count cannot see any of it.

## Decision outcome

A crew test starts only while its host has room for it. The bound on the tests running at once on a host is read from the host's load at each test's start, counting everything running there, crew's other suites, other kits' checks, the agents and the user, not from a count of crew's own tests; a test that would push the host past its cores waits its turn, as `tests.8` has every wait hold under load. The slots stay the lock a test holds for its life; how many may be held at a moment is the room the host has then, never more than its cores less two. The reserve for the host's agents and user is what they are using, not two cores.

How the room is read is the coder's: a load average with the slots already held against the cores, or an idle-core read; the test proves that a loaded host admits fewer tests and an idle one as many as before.

### Consequences

- A suite on a loaded host takes longer and never spikes it; on an idle host it runs as wide as today.
- A run on a saturated host may reach sluice's twenty-minute timeout for crew's checks, whose premise, two minutes alone and seven loaded, is read again when the unit lands.
- swancloud's rounds, 38 checks wide under `parallel = 4`, and sluice's per-branch parallelism size themselves as if alone in the same way; neither is crew's. A finding went to madswan's partition on 2026-10-23 for sluice's design (a bound across the rounds one host runs), and swancloud's policy is read on its own page.
- Finder's seven days at nine tenths of a core on deneb is the user's machine, said to them.
- No unit: the record was rejected.

## Considered options

- **A smaller fixed count**, half the cores as the amendment of 2026-10-11 tried, then cores less two: right on an idle host, blind to the other kits and the sessions, so wrong on deneb and on any Mac a fleet shares.
- **A host-wide bound in sluice** across the rounds of every kit on a host: sluice's to decide, and crew's suite would still size itself as if alone inside its round; sent to madswan as a finding.
- **Fewer teams on a host**: the user's capacity choice, not a test rule; the sessions were a quarter of deneb's CPU that morning. Named for the user, decided here by nobody.
- **Heavy tests through sluice's test-only run on another host**: the user's own sluice work, held (`a-unit-stages-proof-is-a-submission-to-sluice`).
- **Read the host's load at each test's start** (chosen): the one reader at the moment a test would add to the load, counting what is actually there.
