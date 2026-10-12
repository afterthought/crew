# Design

Relies on `plan.16` (a landing is the user's word; amended here), `plan.14` (a landing records the commit main holds), `plan.8` (no landing on a main behind GitHub's), `roles.2`, `read.1` (a unit crew can't read is unknown, and refuses) and `code.7`. Touches `plan.md`'s area.

A held bolt's units are read on its team's host. A bolt no team holds has no host of its own, so crew reads its kit where a team of the partition builds it, the first by name (`builder`), with one survey of that team's kit: a unit whose change main holds, open or archived, and a chore whose trailer main's history holds, read landed, and any other its stage in the plan (`unheld_stages`). The rest is the landing as it stands: the batch guard, the read of main's commit and how far it is from GitHub's on that team's host, and one write removing the bolt and its units, its entry naming the kit and that commit. A held bolt's worktree is tidied after; an unheld one has none.
