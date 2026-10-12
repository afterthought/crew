# Design

Relies on `plan.14`, `plan.8` (a landing is refused while main is behind GitHub's), `read.2` (what the host said is read as a commit or refused) and `code.7` (`plan.main_held` is a function of what the host said). Touches `plan.md`'s and `record.md`'s areas.

`crew bolt land` runs after main-level ops has merged the bolt and pushed main, so the commit the kit's main holds when it runs is the landing's. The script that already fetched GitHub's main on the team's host now prints main's commit first, then how far it is from GitHub's when it has one; `main_held` reads both. The entry's `Head` is the field a stage end and a deploy already use for a commit; `Repo` is new to the run record's descriptor, which a carry writes afresh on the branch.
