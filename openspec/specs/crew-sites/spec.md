# crew-sites Specification

## Purpose
Lists every host's bolts, units and running dev servers in one place, with the URL to open each from where you are, so the user and the operator agent never hunt for a port or a worktree.

## Requirements

### Requirement: The URL is the one to open from where crew runs
On the host that runs the server, the URL SHALL be its local name: `.local` on a publishing host, `.localhost` otherwise. On another host, it SHALL be the server's `dev.swancloud.net` name when its host publishes. A box SHALL NOT be given a `dev.swancloud.net` URL to open, since a box cannot resolve those names. It SHALL be shown that name marked to open from a Mac.

#### Scenario: From mac-studio
- **WHEN** `crew sites wldn` runs on mac-studio and the server runs on the box
- **THEN** its URL is `https://<branch>--<project>--chuck-herdr-alpha.dev.swancloud.net`

#### Scenario: From the box
- **WHEN** the same command runs on the box
- **THEN** the server is shown with that name, marked to open from a Mac

### Requirement: A host that does not answer is named
When a host cannot be reached, `crew sites` SHALL list its bolts from the plan with no worktrees or URLs, and name the host as unreachable.

#### Scenario: The box is stopped
- **WHEN** the box is down
- **THEN** its bolts are listed from the plan, marked unreachable, and every other host's sites are listed as usual

### Requirement: Sites are listed by bolt, with no server for a started bolt's work
`crew sites [<label>] [--json]` SHALL list, for each of the partition's hosts, its main level's and each its runners answer on, each bolt in flight there, as the runner that took its work reported. A started bolt SHALL be listed with no place and no dev server, saying its work runs in Flume's places, whose servers crew does not show yet, until the runner reports a place's addresses. A host that does not answer SHALL be named, with its bolts from the plan.

#### Scenario: A started bolt's work shows no server
- **WHEN** `an-installs-apex-is-its-own-zone` is a unit of started bolt `apex-zones`, and `devurl-serve` runs in a worktree of its kit on the box
- **THEN** `crew sites wldn` lists `apex-zones` under the box saying its work runs in Flume's places, whose servers crew does not show yet, with no URL

#### Scenario: A host that does not answer
- **WHEN** the box does not answer
- **THEN** `crew sites wldn` names the box as not answering, with `apex-zones` from the plan, and lists every other host's bolts
