# Design

Relies on `plan.14` (a deploy is recorded as it runs; a landing records the commit main holds), `state.4` (every view is computed from the files and the run record, nothing running and nothing written), `read.1` (what can't be read is said, never guessed), `code.7` (the view is a function of the entries), `code.8` (a change to what crew models updates the agents' views and the mod in the same change) and `briefs.11` (a deploy's and a user's step's card is main-level ops's). Touches `plan.md`'s area (`plugin/lib/plan.py`, `rail_record`).

## A deploy, folded from the entries

`ops.environments(entries, since)` walks the partition's entries oldest first, keeping, for each environment, the deploys still open by their commit. An offer opens a deploy waiting on the word, unless that commit's deploy is open already, and closes as *replaced* every open offer of another commit no one answered or started: `crew ops` lets a newer offer replace an unanswered one and wait beside an approved one, and the fold does the same. An approval not refused gives the open deploy its word. A start opens a deploy when none is open for its commit, *unasked*: an `auto` environment's, or one offered before the record's window. Each step adds its outcome, a step's rows are the suite's checks, and the end closes the deploy with its outcome. The same commit offered again after its deploy ended is a new deploy. A deploy is kept when it moved since `since` or is still open.

Every after-deploy step recorded against the deploy's commit is listed on it, with its doer and latest state. The operations waiting on an environment are the steps whose latest state is waiting, handed or failed. A deploy waiting on the word and a user's step waiting carry the key of the rail row `ops.rows` makes for them, so the board puts their marker on them, and the steps are numbered the way the rail numbers them (`ops.numbered`).

## What a deploy carried

A landing's entry names the kit and the commit its main holds afterwards. A deploy from F to T carried the landings on the kit of the landing that left main at T, after the one that left it at F, up to it; from nothing deployed, every one up to it. When no landing in the record left main at T or at F, as when a commit of the user's own sits on top of the last landing, the deploy says which commit the record can't place, and names no bolt (`read.1`). crew reads no kit's git for this: the view stays a function of the record.

The page's release notes for a carried bolt are the proposals the lineage joins to it, through its units or straight, read from the page's own edges, so they agree with `crew trace`.

## The board and the agents' views

`rail_record` already reads the main level's host's ops entries for the rail's rows; it hands them, with the landings, to the board's read. The Operation lane keeps the week's landings first, then each environment's deploys and waiting operations, one to a line, with their markers. The JSON's `environments` gives each environment the teams on its host, which is what the page narrows by. The operator's view names each environment with something on it under Operation and counts their cards with the rest. Main-level ops, which posts the operations' cards (`briefs.11`), gets a view of its own: the deploys waiting on the word, approved or running, and each operation step waiting, handed or failed with its doer, environment by environment. The views file's shape does not change, so the mod draws them as it is.

## The deploys view

A third view of the page, kept in its address like the flow view. Each environment is a column whose deploys run oldest at the top, as a timeline, so the sequence of what was approved, replaced or left waiting reads down the page. Each deploy shows the commit and the one it comes from, its stamp, the word (approved by whom and when, waiting, replaced, or no word asked), its steps, the checks, what it carried with each bolt's proposals, and its after-deploy steps; the operations waiting are at the column's foot. The team control is hidden there, as on the flow view.

## Not here

A declined deploy: nothing records a decline today, so a deploy the user would not hold stays waiting until a newer offer replaces it.

## Proof in dev

The logic cases and the board journey prove it; crew has nothing to deploy. Once landed and every host has pulled, `crew page swancloud` on mac-studio shows the deploys view with the deployer's recorded deploys.
