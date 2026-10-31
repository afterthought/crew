## MODIFIED Requirements

### Requirement: Sites are listed as bolt, unit and URL
`crew sites [<label>] [--json]` SHALL list, for each host that keeps one of the partition's kits, each bolt and its places: the bolt's own, each unit's and each fix's. Each has the URL of the dev server running in it, if any. A server SHALL be found from the host's portless routes, and matched to its worktree by `devurl`'s naming.

#### Scenario: A unit's server is running
- **WHEN** `devurl-serve` runs in `places/an-installs-apex-is-its-own-zone` on the box
- **THEN** `crew sites wldn` lists that unit under its bolt with the server's URL

#### Scenario: A worktree with no server
- **WHEN** a unit's worktree has no dev server running
- **THEN** the unit is listed with its worktree and no URL
