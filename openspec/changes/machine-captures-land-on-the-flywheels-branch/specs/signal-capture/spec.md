## ADDED Requirements

### Requirement: A program's capture lands on the flywheel's branch
A capture a program records, a kit's release adapter's or its deployer's, SHALL land through `crew signal land <capture-dir> --label L`, run on the host that ran the program, on the flywheel's branch of that partition, in one commit, with a `capture` entry naming each signal. crew SHALL refuse, naming the file, a folder holding anything but `capture.md` and its signals; a capture that names no `source`, no `captured_by`, no `event_date` or no raw record on the landing host; a capture that is not read or does not count the signals it holds, at least one; and a signal that does not name itself, its kind and who asserted it, says nothing, quotes no excerpt, or is larger than 8 KiB. A file the branch holds the same SHALL be passed over, one it holds otherwise SHALL refuse the landing, and a capture landed already SHALL write nothing and exit 0.

#### Scenario: A deployer's failed deploy
- **WHEN** swancloud's deployer runs `crew signal land` on mac-studio for its capture of a failed deploy, whose log is banked there
- **THEN** the capture and its signal are one commit on swancloud/main, recorded as a `capture` by swancloud-deployer

#### Scenario: The same capture again
- **WHEN** the deployer offers the same capture again
- **THEN** nothing is written, crew says it is already landed, and the command exits 0

#### Scenario: Raw material in the folder
- **WHEN** the folder holds the step's log beside the capture
- **THEN** the landing is refused, naming the log, and nothing is written

#### Scenario: Landed from another host
- **WHEN** the capture's raw record is on mac-studio and `crew signal land` runs on the box
- **THEN** the landing is refused, saying the capture lands from the host that banked it
