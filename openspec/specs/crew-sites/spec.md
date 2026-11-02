# crew-sites Specification

## Purpose
Lists every host's bolts, units and running dev servers in one place, with the URL to open each from where you are, so the user and the operator agent never hunt for a port or a worktree.

## Requirements

### Requirement: Sites are listed as bolt, unit and URL
`crew sites [<label>] [--json]` SHALL list, for each host where the partition's teams run, each bolt and its worktrees: the bolt's own, each unit's and each fix's. Each has the URL of the dev server running in it, if any. A server SHALL be found from the host's portless routes, and matched to its worktree by `devurl`'s naming.

#### Scenario: A unit's server is running
- **WHEN** `devurl-serve` runs in `places/an-installs-apex-is-its-own-zone` on the box
- **THEN** `crew sites wldn` lists that unit under its bolt with the server's URL

#### Scenario: A worktree with no server
- **WHEN** a unit's worktree has no dev server running
- **THEN** the unit is listed with its worktree and no URL

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
