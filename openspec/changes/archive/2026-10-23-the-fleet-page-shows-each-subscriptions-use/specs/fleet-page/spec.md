## ADDED Requirements

### Requirement: The fleet page shows every Claude subscription
The fleet page SHALL hold a section of Claude subscriptions, one for each account the hosts file gives a session and each account a host published a reading for, by name, apart from the partitions' blocks.

#### Scenario: Accounts from sessions and from readings
- **WHEN** the hosts file gives sessions the accounts madswan, madswan-2 and ia, and deneb has published a reading for madswan and for fable-test, which no session names
- **THEN** the subscriptions section holds fable-test, ia, madswan and madswan-2, in that order

### Requirement: A subscription shows its use as it was published
A subscription SHALL show the five-hour and seven-day use of its newest reading a host made, each as the percentage used and when it resets, and each weekly use by model the reading gives, Opus, Sonnet and each model the server names, as published. A window the reading leaves out or gives no figure for SHALL be said not given. Nothing SHALL be graded, summed or derived from the figures.

#### Scenario: Use with a model the server names
- **WHEN** deneb read madswan at 11:58Z with five-hour 34% resetting at 14:00Z, seven-day 61% resetting on 2026-10-27 at 09:00Z, Sonnet's week 20% and Fable's week 40% with their resets, and no Opus window
- **THEN** madswan shows five-hour 34% resetting 14:00Z, seven-day 61% resetting 2026-10-27 09:00Z, Sonnet 20% and Fable 40% with their resets, and no Opus line

#### Scenario: A window with no figure
- **WHEN** a reading gives the five-hour window with no utilization
- **THEN** the subscription says the five-hour use is not given, never a blank or 0%

### Requirement: A subscription says which host read it and how old the reading is
A subscription SHALL name the host whose reading it shows and how long before the page was made that reading was made, and SHALL list each other host that published for it with its reading's age, or with that host's own words for why it could not read.

#### Scenario: Read on two hosts
- **WHEN** deneb read madswan 2 minutes before the page was made and mac-studio read it 9 minutes before
- **THEN** madswan's figures are deneb's, said read by deneb 2 min ago, and mac-studio is listed as read 9 min ago

### Requirement: A reading a host could not make is marked
A reading a host published as not made SHALL be marked so on its subscription with the host's words for why and when it tried. A subscription with no reading made SHALL say its use could not be read; one no host published for SHALL say no host has published its use.

#### Scenario: Only a failed reading
- **WHEN** deneb published for credits that it could not read its use, "the usage endpoint answered 401", and no other host published for credits
- **THEN** credits shows no figures, says its use could not be read, and names deneb with "the usage endpoint answered 401" and when it tried

#### Scenario: Nothing published
- **WHEN** ia is given to a session in the hosts file and no host published a reading for it
- **THEN** ia says no host has published its use

### Requirement: What crew cannot read of the published use is named
A published file the fleet page cannot read, or a reading in it that is not of the published shape, SHALL be named on the page and in what `crew page --fleet` prints, with what was wrong, and every other reading SHALL still be shown. When no host has published anything, the command SHALL say so. The page SHALL still be written.

#### Scenario: A file that is not of the shape
- **WHEN** the published use holds deneb's readings and a file for mac-studio that is not JSON
- **THEN** the page shows deneb's readings, names mac-studio's file as unreadable, and the command prints a line saying so

#### Scenario: No use published
- **WHEN** no host has published any use
- **THEN** the page is written, each subscription says no host has published its use, and the command prints that no use is published

### Requirement: A subscription shows the sessions and partitions on it beside its use
A subscription SHALL list each session the hosts file gives its account, by host, with crew's agents in it and, for each team among them, how many of its slots are at work and what its conductor waits on, and SHALL name the partitions whose agents run in those sessions. A session no crew agent runs in SHALL be listed as running none. Nothing SHALL be computed from the use and the work together.

#### Scenario: Two partitions on one subscription
- **WHEN** swancloud's main level runs in deneb's session swancloud and madswan's team mad-1 in deneb's session madswan, both on account madswan, and mad-1 has 1 of 4 slots at work
- **THEN** madswan lists deneb's sessions madswan, with mad-1, 1 of 4 slots at work and what its conductor waits on, and swancloud, with swancloud's design agent, planner, ops and operator, and names the partitions madswan and swancloud

#### Scenario: A session crew runs nothing in
- **WHEN** deneb's session agentplot-2 is on account madswan and no agent of any partition runs there
- **THEN** madswan lists deneb's agentplot-2 as running no crew agent
