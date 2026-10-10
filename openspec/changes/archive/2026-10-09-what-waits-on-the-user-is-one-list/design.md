# Design

## Context

See proposal.md for why. The decision is `docs/adr/0002-what-waits-on-the-user-is-shown-whole-and-read-from-state.md`, the "One list, read from state" part. Its "Shown whole" part, the `a-decision-is-shown-whole` unit, is already on this bolt: the briefs ask for answers in words, and an agent no longer recites the commands that answer a decision. Those commands belong on the rail.

What crew already reads, and where:

- **Open proposals.** `plan_proposed()` in `plugin/lib/plan.py` reads `proposals.rec` from each flywheel's branch and runs `describe()` on each open one. `describe()` gives `waiting`: the teams whose bolts the proposal touches and who have not agreed. A proposal's `Opened` is a date. Its `plan.propose` entry in the run record is written after the push, with the time in `At`. A later write carries it to the branch's `runs/`, and `record.gather()` reads the branch and then every host the partition runs on, one call per host.
- **A proposal's page.** A proposal is a record in `proposals.rec` on the flywheel's branch, never a file on any host. `page()` renders it as markdown, and `crew plan proposed <n>` prints that. The planner's brief has it write that page to a file and open it with `plannotator-tui herdr open <file>`; nothing in crew does so.
- **Stages.** `survey()` sends `plugin/lib/gather.py` to each host that holds active bolts, one call per host. `Stages` derives each unit's stage from the answer: `review`, `verify`, `merged`, `landed` and so on. `bolt_state()` gives `landed` or `active`. `bolts_view()` is how `crew bolts` puts these together, and how it names an unreachable host.
- **Head times.** `gather.py`'s `place()` reads each unit worktree's head sha, but not its time. It reads no bolt branch's time.
- **Verify reports.** The verify agent saves its report on the team's host as `~/.local/state/<team>-team/reports/verify-<unit>-<YYYYMMDD-HHMM>.md` (the `REPORTS` token in `plugin/lib/crew.py`, `plugin/roles/verify.md`). Nothing in crew reads that folder today.
- **The operator workspace.** `crew operator up` opens the `operator` workspace with the agent's tab, and `ensure_flow` adds a `flow` tab running `crew events --follow --label <label>`. It opens that tab only once, and remembers its pane in the panes file under the role `flow`.
- **plannotator-tui 0.9.4.** It opens a file or a folder in two ways. `plannotator-tui herdr open <file|folder>` opens a herdr pane beside the caller. `plannotator-tui <file|folder>` runs inline in the terminal it was started from.

## Goals / Non-Goals

**Goals:**
- One command, runnable from any host, that lists what waits on the user, read from state alone, with each row's time, age and pasteable answer.
- A tab that keeps the list current and gives the user a shell to answer it in.

**Non-Goals:**
- A question an agent stops on in its pane. No state records it, so the conductor's one-line tell to the operator agents stays as it is.
- The agenda's design-lane items and held units. They join the rail when `curation-and-agenda` and `blocking-findings` land.
- Item numbers of the rail's own, and a JSON output. A row is named by its id (proposal 3, unit x, bolt y).
- Making the kit read cheaper. That is the `a-command-reads-the-kits-once` unit's work (`openspec/explorations/command-cost/reading.md`).

## Decisions

### One read, composed in `plan.py`

`crew rail` is a new command in `plan.py`, beside `bolts_view`, because every read it needs is already there. For each label it reads the plan with `plans()` and the proposals as `plan_proposed()` does. It reads the kits with one `survey()` over the held bolts, then reads stages with `Stages`. Only when a proposal is open does it read the run record, with `record.gather()` from the oldest open proposal's `Opened` day. All of it is one Python run per refresh, with one call per team host for the kits and one per partition host for the record.

*Alternative:* print the rail by running `crew bolts --json` and `crew plan proposed` and joining their outputs. That is two more Python runs and a second fetch of the state branch for each refresh, and it would still need the new times from the hosts.

### The new reads ride in the existing kit call

`gather.py` gains three reads, all done with git and the file system. Like the rest of `gather.py`, they use nothing but python3's standard library.

- Each place's `head_at`: the committer time of `HEAD` (`git log -1 --format=%cI`).
- Each bolt's `head_at`: the committer time of `bolt/<bolt>`, when the branch exists.
- Each kit's `reports`: for each unit, its newest `verify-<unit>-<YYYYMMDD-HHMM>.md` across the reports folders named in the request, with the absolute path and the file's modification time. The request names the reports folders of the teams that build that kit on that host. `survey()` adds them from the teams file as `~/.local/state/<team>-team/reports`, and `gather.py` expands `~` on the host. A folder that isn't there is simply empty.

These ride in the call `survey()` already makes, so the rail adds no host call. `crew bolts` and `crew sites` ignore the new fields.

*Alternative:* a separate ssh per team for the reports folder. That is a second call per host, every 30 seconds, for what one `os.listdir` in the existing call reads.

### When each row began to wait

These follow the ADR's table:

- **Proposal.** The `At` of the run-record entry whose `Act` is `plan.propose` and whose `On` includes `proposal/<n>`, in the proposal's partition. When there is no such entry (the host that wrote it doesn't answer, or the entry is older than the files read), the row uses the `Opened` date at 00:00 UTC and shows the date alone.
- **Review.** The unit place's `head_at`.
- **Verify.** The report's modification time. The row appears only when that time is later than the place's `head_at`.
- **Land.** The bolt's `head_at`.

Times are printed in the local time of the host running the rail, as `YYYY-MM-DD HH:MM`, or `YYYY-MM-DD` for a proposal dated only by `Opened`. The age is the largest two units: `45s` becomes `<1m`, then `14m`, `3h 05m`, `2d 04h`. Rows within a group are sorted by that time, oldest first. Rows of several partitions share a group.

### What each row says, and the commands it carries

The list is plain text, made to be read in a narrow pane. A header line comes first: `What waits on you (<labels>), as of HH:MM:SS`. Then come the four groups in order (`proposals`, `review`, `verify`, `land`), each heading on its own line, followed by its rows or `  none`. A row is one line: the time, the age, and what it is. Below that come its commands, each on its own line, indented and labelled (`read:`, `open:`, `answer:`). The labels are aligned, so a command can be selected by itself and pasted.

| group | the row's line | its commands |
|---|---|---|
| proposals | `proposal <n> (<label>), by <by>: <first line of the case, cut at 70>`, then a line `still needs the agreement of <t>-conductor, …` while any is missing | `read: crew plan proposed <n> --label <label>`, `open: crew plan proposed <n> --label <label> --open`, `answer: crew plan approve <n> --label <label>` |
| review | `unit <unit> (<label>), <team> on <host>` | `open:` the plannotator command for `<worktree>/openspec/changes/<unit>/`, `answer: crew unit approve <unit> --label <label>` |
| verify | `unit <unit> (<label>), <team> on <host>: report <path>` | `open:` the plannotator command for the report, `answer: crew tell <team>-conductor "On <unit>'s verify report: "` |
| land | `bolt <bolt> (<label>), <team> on <host>: every unit merged; <label>-ops lands it` | `answer: crew tell <label>-ops "Land bolt <bolt>."` |

Every path and every argument with a space is quoted with `shlex.quote`, so a command pastes as it reads.

A proposal still waiting on a conductor carries `crew plan approve` anyway. The command is refused until the conductor agrees and says so, and the row has already said whose agreement is missing. That keeps one rule for every proposal row. It also leaves the user's agreeing for a team (`crew plan agree`) as a choice the user makes deliberately, not one a pasted command makes for them.

The verify row's answer is a `crew tell` to the conductor with an open quote. The user finishes it in their own words, since what to fix is decided with the conductor (`plugin/roles/conductor.md`, step 3). The land row's answer asks the main-level ops, who lands on the user's word (`plugin/roles/main-ops.md`).

### Opening a proposal

A proposal's row opens it as a review row opens a change: in plannotator, for the user to read and annotate. Since a proposal is no file, `crew plan proposed <n>` gains `--open`. It renders the page as `crew plan proposed <n>` prints it, writes it to `~/.local/state/crew/proposals/<label>-<n>.md` on the host it runs on, replacing any earlier copy, and opens that file: with `plannotator-tui herdr open <file>` when `HERDR_ENV` is `1`, else with `plannotator-tui <file>` inline in the terminal. Like the rest of `crew plan proposed`, it reads only the flywheel's branch, so the same command opens the proposal from any host, and no row needs an ssh form. The file is a copy for reading, not state: nothing reads it back, and the next `--open` of that proposal replaces it with the page as it then stands.

`--open` needs a proposal's number, and is refused with `--json`.

*Alternative:* a shell line on the row that writes the page to a file and runs plannotator on it, `crew plan proposed <n> --label <label> > <file> && plannotator-tui herdr open <file>`. It needs no change to `crew plan proposed`, but it is twice as long in a narrow pane, it names a file path the user has no reason to see, and only the rail would have it.

*Alternative:* the rail writes every open proposal's page on each refresh, and the row opens that file. That makes the rail write on every refresh, which it otherwise never does, and leaves files behind for proposals long closed.

### Opening a change that lives on another host

A unit's change and its verify report are files on the team's host. The rail runs on any host, and its shell is on the operator's host. When the team's host is the one running the rail, the open command is `plannotator-tui herdr open <path>`, as the ADR has it. When it is another host, the command is `ssh -t <ssh name> plannotator-tui <path>`, which runs plannotator inline in the rail's shell over ssh. That is the one form that reaches a file on another host from that shell. The ssh name comes from the hosts file (`fleet["hosts"][host]["ssh"]`), as `there()` in `plugin/bin/crew` uses it.

*Alternative:* print only the path for a remote change. The user then has to know the host and type the command, which is what the rail is meant to spare them.

### An unreachable host, an unread plan

As in `bolts_view`: a host whose survey failed is named after the groups, as `<host> did not answer (<why>): its units and bolts may also wait on you`. Its units are `unknown` and make no row. A host that didn't answer the run-record read only changes how a proposal's time is found, so it is not named twice. A plan that can't be read is named on standard error, the rest is printed, and the exit is non-zero.

### The rail tab

`ensure_rail` in `plugin/bin/crew` sits beside `ensure_flow`, and `crew operator up` calls it right after `ensure_flow`. It opens a `rail` tab in the `operator` workspace and remembers its pane as the role `rail`. It splits that pane `down` for a shell, remembered as `rail-shell`. In the shell it runs `export PATH=<crew's plugin/bin>:$PATH`, so `crew` there is this host's crew. In the upper pane it runs `bash <crew> _rail <label>`. When the `rail` pane is live it does nothing. When the tab is there but the shell has gone, it splits again for the shell.

`crew _rail <label>`, an internal command like `_revive`, is the loop. It starts `crew events --follow --label <label>` on a file descriptor. Then it repeats three steps: compute `crew rail --label <label>`; clear the pane and print the result, so the list never flickers empty; wait on that descriptor up to 30 seconds. When an entry arrives, it reads any more that come within 2 seconds, so a burst of entries refreshes once. When the follow has ended (`read` fails rather than times out), it sleeps 30 seconds instead, so the list still refreshes on the clock.

`teardown` and `revive` need nothing new. `stop` on a pane with no agent returns at once, and `revive` touches only the standing roles.

### The operator's brief

"Where things stand" lists `crew rail --label <label>` among the reads. Its "anything waiting on the user" sentence says to answer it from `crew rail`, oldest first in each group, and to point the user to the `rail` tab, whose shell takes each row's command. The rule from `a-decision-is-shown-whole` stays: each open proposal is shown whole, never by number alone; answers are asked for in words, and no command is recited; an approval is run only on the user's word. An agent blocked on a question stays in the list, from the tells.

## Risks / Trade-offs

- [Each refresh reads every team host's kits, about 2 s with three units in flight, every 30 seconds and on every entry] → The bursts are folded into one refresh, and the read is the one `crew bolts` makes. `a-command-reads-the-kits-once` lowers it for both.
- [A proposal's entry is on its host until a later write carries it] → `record.gather()` reads the hosts as well as the branch. When neither has it, the `Opened` date stands.
- [Where plannotator sends the user's annotations when it is opened from a plain shell, with no agent in the pane, isn't checked] → It is worked under *Proof on real work*, for a proposal and for a change. The rail's answer is the `answer:` command, not the annotations.
- [`plannotator-tui` may not be installed on the box] → Also under *Proof on real work*. A row whose open command fails still carries its answer and the path.
- [A report's file time can be touched by hand] → Accepted. The report's time is the only record of when verify ran, as the ADR has it.

## Migration Plan

Land, then pull on every host. `crew rail` works at once. The `rail` tab opens at each host's next `crew operator up <label>`, run by hand or by the operator session's supervisor. The operator agents take the brief at their next fresh start, or when told what changed. Rollback: revert, and close the `rail` tab.

## Proof on real work

Once the bolt has landed and every host has pulled:

1. On mac-studio, `crew operator up <label>` opens a `rail` tab with the list above and a shell below, and `crew list` run in the shell prints the teams.
2. With a unit of a team on mac-studio in review, its row's `open:` command, pasted into the rail's shell, opens the whole change in plannotator. Note where annotations made there go: into the shell, to the clipboard, or nowhere.
3. With a unit in review on the box, its row's `ssh -t … plannotator-tui …` command, pasted into the rail's shell on mac-studio, shows the change inline. If `plannotator-tui` is not on the box's path, say so.
4. With a proposal open, its row's `open:` command, pasted into the rail's shell on mac-studio, opens the proposal beside the shell in plannotator, reading as `crew plan proposed <n>` prints it. Note where annotations made there go, as in step 2.
5. Approving that unit with its row's `answer:` command makes the row leave the list within a few seconds, without waiting for the 30 seconds.
6. The next proposal the planner opens shows under proposals with the time of its `plan.propose` entry, not midnight.

## Task notes

**1.1** `plugin/lib/gather.py`. In `place()`, add `"head_at"`: `git log -1 --format=%cI HEAD` in the place, stripped, or `None`. In `kit()`, add `"head_at"` to each `out["bolts"][b]`: `git log -1 --format=%cI bolt/<b>` when it exists, else `None`. Add `"reports"` to the kit's answer: for each folder in `req.get("reports", [])`, after `os.path.expanduser`, each file matching `^verify-(.+)-(\d{8}-\d{4})\.md$`, keeping per unit the file with the greatest `os.path.getmtime`, as `{unit: {"path": <absolute>, "at": <UTC ISO time of the mtime>}}`. A folder that doesn't exist gives nothing. Update the module docstring's account of the answer. In `plan.py`'s `survey()`, give each kit's request `"reports"`: the `~/.local/state/<team>-team/reports` of every team in `fleet["teams"]` on that host with that kit main, sorted and without duplicates. `tests/t-bolts.sh` and `tests/t-sites.sh` must pass unchanged; the new fields are checked through `tests/t-rail.sh` (2.5).

**2.1** `plugin/lib/plan.py`. Add `rail_view(fleet, a)` after `bolts_view`, with a parser entry `rail` taking `--label`, and `("rail", None): rail_view` in `COMMANDS`. Leave it out of `ACTS`: it is a read. Take the labels as `bolts_view` does (`default_label`, else every partition). Read plans with `plans(fleet, labels, errors)`, and survey every held bolt of those plans once. Build the rows as *What each row says* has them:
- Proposals: factor the loop in `plan_proposed()` that lists open proposals into `open_proposals(fleet, labels)`, returning each `describe()` with its label. Use it in both places. `plan_proposed()`'s own output must not change: `tests/t-proposals.sh` holds it.
- Review and verify: per unit of a held bolt, from `Stages.of()` and the place in the survey's kit (worktree, `head_at`) and the kit's `reports`.
- Land: per bolt with a team, whose units are all `merged` or `landed` and not all `landed`, timed by the kit's `bolts[b]["head_at"]`. A bolt whose stages are unknown, or whose branch has no time, gives no row.

Parse every ISO time to an aware UTC datetime for sorting. Print in local time (`astimezone()`).

**2.2** The proposals' times. When any proposal is open in a label, call `record.gather(fleet, [label], <oldest Opened>)`. Find, per proposal, the earliest entry with `Act == "plan.propose"` and `proposal/<n>` in `On`. Fall back to `Opened` at 00:00 UTC, shown as the date alone. Don't name the record's unreachable hosts in the rail.

**2.3** `crew plan proposed <n> --open`, as *Opening a proposal* has it. In `plan.py`'s parser, give `proposed` an `--open` flag. In `plan_proposed()`, refuse `--open` without `n` ("`--open` needs a proposal's number") and with `--json`. With it, write `page(d, label)` to `pathlib.Path.home() / ".local/state/crew/proposals" / f"{label}-{n}.md"`, making the folder as needed, then run `plannotator-tui herdr open <file>` when `os.environ.get("HERDR_ENV") == "1"`, else `plannotator-tui <file>`, with `subprocess.run`, and exit with its status. When `plannotator-tui` isn't on the path, fail naming it and the file written, so the user can still read it. Without `--open`, `plan_proposed()`'s output must not change. Add `--open` to the module docstring's usage line for `crew plan proposed`. Add `tests/stubs/plannotator-tui`, a bash stub that appends `<CREW_TEST_HOST> plannotator-tui <args>` to `$CREW_TEST_LOG`, as the ssh stub does, and exits 0. The rail's proposal row carries `open: crew plan proposed <n> --label <label> --open`.

**2.4** The open commands of review and verify rows. Given the host of the file and `crew.this_host()`: `plannotator-tui herdr open <quoted path>` when they are the same; otherwise `ssh -t <fleet["hosts"][host]["ssh"]> plannotator-tui <quoted path>`. The change folder is `<place path>/openspec/changes/<unit>/`, with its trailing slash.

**2.5** `tests/t-rail.sh` (new, starting with the `TESTS` line every test has). Build a world as `tests/t-bolts.sh` does, with `wldn`, team `swb-1` on chuck-herdr-alpha and its kit. Commit with `GIT_COMMITTER_DATE` set, so times are known, and set report times with `touch -t`, which both BSD and GNU `touch` take. Then check:
- with nothing waiting, the four headings in order, each with `none`;
- two units in review, committed at different times, listed oldest first, each with an age, and `crew unit approve <unit> --label wldn`;
- run as `HOST=chuck-herdr-alpha`, the review row's `plannotator-tui herdr open <path>/openspec/changes/<unit>/`; run as `HOST=mac-studio`, `ssh -t <the box's ssh name> plannotator-tui`;
- a unit in verify with a report in `$(home_of chuck-herdr-alpha)/.local/state/swb-1-team/reports/` newer than its head is listed with the path; one whose report is older than its head is not;
- an open proposal (written with `crew plan propose <file>` as the user, so no conductor needs to agree), with `crew plan proposed <n> --label wldn`, `crew plan proposed <n> --label wldn --open` and `crew plan approve <n> --label wldn`, timed today. With today's run-record file on the writing host removed before the next write, it is timed by its `Opened` date;
- a proposal touching swb-1's bolt says it still needs `swb-1-conductor`'s agreement;
- `crew plan proposed <n> --label wldn --open` with `HERDR_ENV=1` writes `$HOME/.local/state/crew/proposals/wldn-<n>.md` with exactly what `crew plan proposed <n> --label wldn` prints, and the log has `plannotator-tui herdr open` with that path; with `HERDR_ENV` unset, `plannotator-tui` with the path and no `herdr open`; `crew plan proposed --open` and `crew plan proposed <n> --open --json` fail; and the branch's tip is unchanged;
- a bolt whose only unit has merged under land, with `crew tell wldn-ops "Land bolt <bolt>."`;
- after `crew unit approve` of a review row's unit, that row is gone;
- `crew rail` leaves the state repository's tip unchanged and writes no run-record entry;
- with `echo chuck-herdr-alpha > "$T/down"`, the proposal rows still print, the box is named as not answering, and the exit is zero.

**3.1** `plugin/bin/crew`. Add `rail` to the case that hands off to `plan.py` (`bolts | bolt | signal | state | plan | rail`). In the usage header, under the plan's section, add `crew rail [--label L]` with "what waits on the user: proposals, reviews, verify reports and bolts to land, each with when it began to wait and the command that answers it". Add `ensure_rail`, and the `_rail` case running the loop, as *The rail tab* has them, and call `ensure_rail` after `ensure_flow` in `operator)`. Tests: in `tests/t-record-team.sh`, beside the `flow` checks: one `rail` tab after `crew operator up wldn`; a `pane run` of `_rail wldn` and one of `export PATH=` for crew's `plugin/bin`; and a second `operator up` opening no second tab. `tests/t-operator.sh`'s "run twice" check must still pass: on a second run, `ensure_rail` makes and runs nothing.

**3.2** `plugin/roles/operator.md`, *Where things stand*. Add a bullet: "`{{TEAM_CMD}} rail --label {{LABEL}}`: everything that waits on the user, oldest first in each group, each with when it began to wait and the command that answers it; the `rail` tab of your workspace keeps it on screen, with a shell below to paste those commands in." In the answer paragraph, make "anything waiting on the user" read from the rail: "…and anything waiting on the user, as `{{TEAM_CMD}} rail` lists it: units in review, each with the folder its change is in; …" Then keep the rest of that paragraph as it is: proposals shown whole, answers in words, no recited command, approvals only on the user's word. End it with "The commands are on the rail; send the user to its tab rather than reciting them." `tests/t-briefs.sh`: in the `wldn operator` checks, `has` "rail --label wldn" and "the `rail` tab". The existing checks must still pass.

**3.3** `README.md`, *The main level and the operator agent*. Add `crew rail [--label L]` to the block of commands. Add a paragraph saying what it lists, in the four groups and in order, with each row's time, age and command, all read from state with nothing kept by hand. In the plan's command block, make the line `crew plan proposed [<n>] [--label L] [--json] [--open]`, and in the paragraph on `crew plan proposed`, add that `--open` writes the page to a file on the host and opens it in plannotator, beside the caller in herdr. Add that `crew operator up` also opens the `rail` tab: the list above, printed again every 30 seconds and on each run-record entry, and a shell below with crew on its path. In `plugin/skills/crew/SKILL.md`'s table, add a row: "see everything that waits on the user, and the command that answers each" | `crew rail [--label <label>]`. `tests/t-docs.sh` checks the README against crew's usage. Run it.
