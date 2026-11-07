## MODIFIED Requirements

### Requirement: The follower follows each kit's queue through sluice's overview
The host's follower SHALL learn that a kit's merge queue moved from sluice's overview alone. It SHALL keep one `sluice overview --json --watch` running in each kit whose queue its read shows, on the kit's host, take a line whose document differs from the last (its time aside) as the queue's move, and read the queue from that line. Where no watch can run, because the host's sluice has no watch or the kit's watch ended or could not start, it SHALL ask `sluice overview --json` once on its clock instead, and open an ended watch again at the next tick. A gather of a kit SHALL start no sluice process for its queue while a watch's line gives the queue, and at most one `sluice overview --json` where none does; it SHALL run no `sluice status` for a held bolt's branch or for the kit's main, and SHALL run one `sluice status <n> --json` for each bolt whose head sluice landed beside its queue, the record of that landing's submission, which names the verdict that covers it (merge-gate "A landing beside reads as the verdict that covers it"), and none for any other head. The follower SHALL keep, for each kit, every submission of a held bolt it has seen stand, with when it was submitted and, once a candidate tested it, when its checks began, and SHALL keep it across later lines and gathers while the bolt is held. When a line no longer holds a kept submission, the follower SHALL take it as decided at the time that line's recent events give for it, or at that line's own time when they name it in no event, reading nothing else. crew SHALL read and name no folder of sluice's.

#### Scenario: A merge moves in sluice's queue
- **WHEN** a unit's merge into a bolt of switchboard-kit on the box is queued in sluice, and the kit's overview watch prints a new line
- **THEN** the follower's next refresh, within a few seconds, shows the submission's number on the unit's row, gathers no kit and starts no sluice

#### Scenario: One watch for each kit
- **WHEN** the follower on mac-studio reads two partitions whose bolts are both in switchboard-kit on the box
- **THEN** it keeps one overview watch for switchboard-kit, over one ssh to the box, and a refresh that gathers the kit takes its queue from the watch's line and starts no sluice process

#### Scenario: A host whose sluice has no watch
- **WHEN** the box's sluice refuses `--watch`
- **THEN** the follower asks the box's kits' overviews once at each tick of its clock, in that tick's one ssh to the box, and not between ticks

#### Scenario: A watch ends
- **WHEN** the ssh holding switchboard-kit's watch drops
- **THEN** the kit's row says its queue can't be read and why until the next tick, which opens the watch again and asks the overview once

#### Scenario: A held bolt's decided merges
- **WHEN** the follower gathers switchboard-kit while bolts `b` and `c` are held there, with merges of both decided and one of `b`'s standing
- **THEN** the gather runs no `sluice status`, for `bolt/b`, `bolt/c` or main, and the rows of `b` and `c` are drawn from the overview the watch last printed and what the follower kept of each submission

#### Scenario: A held bolt whose head landed beside the queue
- **WHEN** the follower gathers switchboard-kit while bolt `b`'s head is a take-main fix sluice landed beside its queue as `#1319`, and bolt `c`'s head a merge landed through the queue
- **THEN** the gather runs one `sluice status 1319 --json` in the kit's main checkout and no other `sluice status`

#### Scenario: A merge decided between gathers
- **WHEN** `b`'s merge `#41`, kept since it was submitted at 14:00 and tested from 14:05, leaves the queue on a line whose recent events say it landed at 14:17
- **THEN** the follower keeps `#41` decided at 14:17, starts no process to learn it, and still holds it after the next gather of the kit

#### Scenario: A withdrawn merge
- **WHEN** a kept merge of `b` leaves the queue on a line printed at 14:20 whose recent events do not name it
- **THEN** the follower keeps it decided at 14:20
