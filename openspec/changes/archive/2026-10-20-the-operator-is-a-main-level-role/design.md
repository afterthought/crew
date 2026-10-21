# Design

Rules relied on: `teams.2` (whatever opens a role's pane), `teams.7` (every agent crew starts is greeted once), `briefs.6` and `briefs.10` (the partition's operator, the main level's, as amended by record 0035), `briefs.11` (the operator asks nothing on a card), `code.8` (the board's views follow what crew models). Pages touched: `teams.md`, `briefs.md`.

1. The main level's standing roles are `MAIN_STANDING`, design, planner, ops and operator, in that order; `crew main up` opens a tab for each that is not up, as it opened three, so a main level brought up again gains the operator's tab beside the others.
2. The operator runs where the main level runs, in the main level's checkout, as its other roles do; its brief keeps what it does for the user and says it is the partition's door, the console's tabs being the user's to read.
3. An agent named `<label>-operator-<host>` is no longer one crew starts; plan's `role` still reads one as the operator, so a card or a plan write from one still running before the console retires it is refused in the operator's words.
4. Changing the teams is done from swancloud's checkout on a Mac: an operator whose main level runs on a box carries the request to an operator whose main level runs on a Mac keeping that checkout, read from the hosts file (`TEAMS_OPERATORS`).
