# Spec Delta

## ADDED Requirements

### Requirement: A capture written outside crew is landed through crew
`crew signal land <capture-dir>` SHALL write a capture directory, its `capture.md` and its signal files, to `signals/<capture>/` on main of the partition's first blueprints repo, by crew's path: fetched over https, applied to the tip, committed by its own paths alone, pushed without force, and applied again to the new tip when the push is refused. Landing a directory whose files are all on main already SHALL write nothing.

#### Scenario: The morning's meeting
- **WHEN** the daily pass has written a capture and its seventeen signals in a scratch directory and runs `crew signal land` on it
- **THEN** one commit on the blueprints repo's main adds those eighteen files, and no checkout pushed anything

#### Scenario: Landed twice
- **WHEN** the same directory is landed again
- **THEN** nothing is written, and the command says so

#### Scenario: Main moved meanwhile
- **WHEN** someone pushes to the blueprints repo's main while a capture is being landed
- **THEN** the landing is applied again to the new tip and lands, with nothing merged

### Requirement: What is landed is checked
Before anything is written, `crew signal land` SHALL check that the capture names itself as its directory, its source and its event date; that each signal's id is its path, its kind is one of the five, and it has an asserter, an assertion and, in a capture marked read, a quoted excerpt; and that the directory holds no other file. A directory that fails SHALL be refused, naming the file and the fault, with nothing written.

#### Scenario: A signal with no excerpt
- **WHEN** a signal file of a read capture has an assertion and no quotation
- **THEN** the landing is refused, naming that file

#### Scenario: A transcript among the files
- **WHEN** the directory holds a file that is neither `capture.md` nor a numbered signal file
- **THEN** the landing is refused, naming it, since raw material never enters git

#### Scenario: A capture with no signals yet
- **WHEN** the directory holds only a `capture.md` marked unread
- **THEN** it is landed as it is, to be read later

### Requirement: A landed signal is never changed
A signal file that is on main SHALL NOT be replaced: a landing whose signal file differs from the one on main SHALL be refused, naming it. A capture's `capture.md` on main MAY be replaced only to mark it read and set its count of signals.

#### Scenario: An edited signal
- **WHEN** a directory is landed again after one of its signal files was edited
- **THEN** it is refused, naming the file; a correction is a new signal

#### Scenario: An unread capture is read
- **WHEN** a capture landed unread is landed again with its signals and `status: read`
- **THEN** the signals are added and `capture.md` is replaced

### Requirement: A landing is in the run record
Landing SHALL leave a `capture` entry for the capture when it is first landed and one for each signal added, naming the signal and the commit, with whoever ran the landing as the one who asked.

#### Scenario: Tracing a meeting signal
- **WHEN** `crew trace signals/<id>` runs for a signal the daily pass landed and curation later moved
- **THEN** its first line is the capture, with the daily pass's name and host, and the move follows
