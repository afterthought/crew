# Design

## Context

Today `crew console up <label>` (`plan.py` `console_cmd`) opens three tabs in the `console` workspace of the host's `<label>` session: `flow` (`crew events --follow --label <label>`), `rail` (the bash loop `crew _rail <label>` above, a shell with crew on its path below, `rail-shell`) and `board` (`crew _board <label>`, `board.py` `follow`). swancloud's timer runs it every five minutes, and `crew go` runs it for each partition with a session on the host (`hold.py` `go`). Each run keeps a tab already open and runs its command again where a restart left its pane a bare shell (`crew.tab_holds`, `read.4`).

The rail tab's loop is more than a view. Every 30 seconds, and on each run-record entry, it runs `crew _views <label>`, one read that prints the rail, ends the card sessions of closed cards and gone rows (card-sessions spec), writes the board's frame (`~/.cache/crew/board/<label>.json`) and every agent's view beside it (`<label>.agents.json`, which crew's mod draws in each band, `code.8`); and when crew's checkout or the teams file has moved, it runs `crew _update --label <label>`, which hands due agents their restarts (`teams.19`). With no rail tab, none of that happens.

The ruling this design rests on is `state.4`'s reading of 2026-10-28 (crew 42b5fc1d): one follower on a host serves every partition's tab there; crew requires no service for it (`roles.6`); where the host runs it as a job of its own, swancloud's, as it runs the board's word listener (record 0038 point 4), it runs with no tab and writes the rail's text as a frame as the board's is written, and the tabs draw the frames when the user opens them; where no job of the host's runs it, the rail tab's own loop is the follower, so a host never has two and never none (record 0047, move 6). The host's job is swancloud's unit a-host-runs-crews-follower-as-its-own-job, landing after this one.

## Goals / Non-Goals

**Goals:**
- The console opens a shell alone, and its three tabs on the user's word.
- One loop, `crew _follow`, that does the rail tab's whole refresh for every partition with an operator session on the host, with no tab; and a rail tab that draws its frame, or follows itself while no one else does.
- Exactly one follower per host at a time, read from a fact the OS keeps, never a guess (`read.1`).

**Non-Goals:**
- Making a refresh cheaper. A round still runs `crew _views` once per partition, as today; reading once for every partition and reading nothing when nothing moved is a-rail-refresh-after-no-change-reads-nothing (bolt crew-costs-an-idle-host-nothing, `plan.12`'s reading), which builds on this loop.
- The host's job itself: swancloud's.
- The flow tab's follow: it stays `crew events --follow`, as today. It is a view of the run record, not of the follower's read, so it draws no frame.
- Closing tabs a console already has open: the user's.

## Decisions

### 1. The console's tabs are a decision on what is asked, what is open and who follows

`crew console up <label> [flow] [rail] [board]` parses the tabs named after the label, any order, each at most once; another word is refused naming the three. A new decision `console_tabs(asked, open_tabs, follower)` in `plan.py` (`code.7`) returns which tabs to open and which to keep:

- `shell` always: a tab of its own, a shell with crew on its path (`export PATH=<crew>/plugin/bin:$PATH`, the words the rail's lower pane gets today), opened once.
- each tab named;
- `rail` when the follower is not the host's job (Decision 3), since the rail tab is then the follower;
- every tab the console's panes file records whose pane is live: kept, and run again where it holds its shell alone, as `keep` does now.

A tab the panes file records whose pane herdr no longer has was closed by the user: its line is dropped and it is not opened unless named, or unless it is the rail and no job follows. A tab opens in the order flow, rail (with its `rail-shell` split, as today), board, after `shell`. `crew console down` is unchanged: it closes every tab the panes file records, `shell` among them. `hold.py` `go` passes no tabs.

Considered: a `--tabs` flag, rejected as longer to type for the same thing; keeping a closed tab's record to reopen it, rejected since the user closing it is the user's word that it is not wanted.

### 2. The follower is one Python loop in `board.py`, the rail tab's and the job's

`crew _rail` moves from `plugin/bin/crew`'s bash to `board.py`, beside `_board`, and `crew _follow` is added there; the bash dispatch line for `board | _views | _board` takes both. One loop serves both:

- **Its partitions**: each label with a session of that name, in its partition, on this host in `herdr-hosts.json`, the test `crew.operator_session` makes, read again each round so a teams or hosts change reaches it.
- **Its wake**: a `crew events --follow --label <label>` child per partition, read with `select` with a 30-second timeout; a wake drains what arrives within 2 seconds, so a burst is one round, as the bash loop's `read -t 2` does; a follow that ends leaves that partition on the clock alone.
- **Its round**, per partition, as the bash loop does now: when crew's checkout's `HEAD` or the teams file's checksum has moved since the last round, `crew _update --label <label>`; then `crew _views <label>`, each a child process so every round reads afresh (a long-lived process keeping `plan`'s in-memory reading would serve stale reads, which the cost unit replaces with a keyed cache). The child's standard output and error together are the rail's text, as the tab shows them today.
- **The rail frame**: `<FRAMES>/<label>.rail.json`, `{"read_at", "from", "text", "updated"}`, `updated` being `_update`'s words when it ran, written whole by `write_frame`. `_views` itself is unchanged: it still prints the rail, and writes the board's frame and the agents' views.

`crew _follow` runs this loop for every partition, headless. `crew _follow --once` takes the lock, makes one round of every partition with no wait, and exits, for the tiers.

The rail tab, `crew _rail <label> [--once]`, draws `<label>.rail.json` at each change of its time, as `board.py` `follow` draws the board's frame, once a second; when the frame is older than `STALE` it is headed with its age; when there is none, it says there is no rail for the partition yet and that the host's follower writes it. Each second it tries the follower lock without waiting; while it holds it, it is the follower and runs the round itself when due, then draws. So a tab drawing the job's frames follows itself within a second of the job ending.

Considered: keeping the bash loop and taking the lock from it. macOS has no `flock(1)`, and a lock taken by a child on an inherited descriptor is subtle to keep; the wake over several partitions also wants `select`. Running the round in-process, rejected above.

### 3. One follower per host: an OS lock that says who holds it

The follower lock is `<FRAMES>/follower.lock`, taken with `fcntl.flock(LOCK_EX)` (standard library, `code.1`) on a file held open for the follower's life, so the OS lifts it when the follower ends, however it ends: nothing is left to go stale, and it is no state (`state.4`). Once taken, the holder truncates the file and writes one line, `job <pid> <time>` or `tab <label> <pid> <time>`.

- `crew _follow` waits for the lock, blocking and reading nothing, then follows.
- A rail tab tries it each second without waiting (Decision 2).
- The console's read, `follower_here()`, tries it without waiting: taken means no one follows (and it is released at once); refused means someone does, and the file's line says whether it is the job. A decision `follower_of(line, free)` turns that into `none`, `job` or `tab`, and an unreadable line into `unknown` (`read.1`), which `console_tabs` treats as not the job, so the rail tab is opened and at worst draws frames: a host is never left with none.

Considered: a pid file, rejected as stale after a crash, a guess at whether its pid is still the follower; asking herdr for a rail pane, rejected because the job has no pane; asking swancloud whether its job is loaded, rejected as a fact of another tool's that crew would read only to guess what this lock reads directly.

### 4. What crew says names the host's follower

The words that name the rail tab as the writer change with the writer, and nothing of the views file's shape changes (`code.8` holds with the words alone):

- `board.py` `no_frame`: no board for `<label>` yet; the host's follower writes it, swancloud's job or the console's rail tab, which `crew console up <label>` opens while no job runs.
- `agent_views`' `stale` line: the board was last read at `<time>`, too long ago to show; crew's follower on `<from>` has not refreshed it since.
- `plugin/hooks/status.js`: its comments, and its no-views line, which names the host's follower and `crew console up <label>`.
- `plugin/bin/crew`'s usage for `crew console` and `crew update`, `plugin/skills/crew/SKILL.md`'s console row, README's console and band paragraphs (`docs.2`), and `plugin/roles/operator.md`'s rail line, which says `crew console up {{LABEL}} rail` opens the console's `rail` tab with a shell below.

## Risks / Trade-offs

- [A rail tab can take the lock before the host's job starts, after a reboot, and keep it while it stays open; the job then waits.] → One follower still runs; the job takes over within a second of the user closing the tab. The console's next run sees `tab` and opens nothing new for it.
- [Each console already open keeps its flow, rail and board tabs, by the rule that an open tab is kept.] → Its rail tab becomes a drawer of the job's frames once the job runs; the user closes the tabs they do not want, or runs `crew console down <label>` and `crew console up <label>`.
- [A round per partition is as costly as today's rail refresh, and now runs on a host whether or not any tab is open.] → It is the same work the rail tab already did on every host with a console; the cost unit makes an idle round read nothing.
- [The flock is advisory and per open file: a process that opens the lock file and writes it without locking could mislead the console.] → Only crew opens it, and only through the one helper that locks before it writes.

## After deploy

None: every behaviour here is proven in crew's tiers. A host keeps following through its rail tab, as the console opens it while no job runs, until swancloud's a-host-runs-crews-follower-as-its-own-job runs `crew _follow` there.

## Task notes

**1.1** `board.py`: `lock_follower(kind, label=None, wait=True)` opens `FRAMES/follower.lock` (`FRAMES.mkdir` first) with mode `a+`, `fcntl.flock` with `LOCK_EX` (with `LOCK_NB` when not waiting, `BlockingIOError` meaning held), truncates and writes the holder's line, and returns the open file, kept by the caller for its life; `follower_here()` returns `follower_of(line, free)`. Logic cases in `tests/py/test_board.py` with `FRAMES` pointed at `tmp_path`: a held lock refuses a second try in the same process and reads `tab wldn`; a released one is free; a line that is neither reads `unknown`. (Two `open()`s are two open file descriptions, so `flock` conflicts between them in one process on macOS and Linux.)

**1.2** `board.py`: `labels_here(fleet)`, each label whose session of that name on `crew.this_host()` is in its partition; the round (`_update` when `HEAD`/`cksum` moved, then `_views`, as children of `plugin/bin/crew`, output captured); `write_frame(label, {...}, rail_path(label))`; the loop with one `events --follow` child per label and `select`. `crew _follow [--once]` and `crew _rail <label> [--once]` added to `main`'s subcommands and the module's usage docstring; `plugin/bin/crew`'s dispatch line gains `_rail | _follow`, and its bash `_rail)` case goes. Logic cases for `labels_here` and for the rail frame's text: fresh, stale headed with its age, none (`tests/py/test_board.py`).

**1.3** `board.py` `rail_follow(label, once)`: draws the rail frame as `follow` draws the board's, and tries `lock_follower("tab", label, wait=False)` each second, running the round while it holds it. Case for one draw with `--once` in **4.2**.

**2.1** `plan.py`: `console_tabs(asked, open_tabs, follower)` returns `(open, keep, forget)`: `open` the tabs to open in the order shell, flow, rail, board; `keep` the recorded live tabs; `forget` the recorded dead ones not reopened. `follower` is `none`, `job`, `tab` or `unknown`, from `board.py` `follower_here()` (**1.1**). Cases in a new `tests/py/test_console.py`: a first up with the job following opens `shell` alone; with none following, `shell` and `rail`; `rail` named while the job follows; a second up keeps all and opens nothing; a closed `board` forgotten; a closed `rail` reopened while no job follows; `unknown` opens the rail.

**2.2** `plan.py` `console_cmd`: the parser's `_console` takes `tabs` (`nargs="*"`, choices flow, rail, board, refused otherwise with the three named); open each tab `console_tabs` returns with `c.opened("console", tab, c.cwd, tab)`, the `shell` and `rail-shell` panes given the PATH line, every kept tab through today's `keep`, and `c.drop("panes", tab)` for each forgotten one (with `rail-shell` beside `rail`). `plugin/bin/crew`'s `console)` passes the words after the label; `operator up` passes none. `hold.py` `go`: `argparse.Namespace(act="up", label=label, tabs=[])`. Cases in `tests/py/test_hold.py` if it builds that namespace; end to end in **4.1**.

**3.1** The words of Decision 4 in `board.py` (`no_frame`, `agent_views`' `stale`), `plugin/hooks/status.js` and its cases in `plugin/tests/status.test.ts` where they pin the words; `tests/py/test_board.py`'s cases for the stale line and the no-board words.

**3.2** README, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage, `plugin/roles/operator.md` (Decision 4). `tests/t-briefs.sh` checks the operator brief for "the console's \`rail\` tab" and "console up wldn": keep both in the new line, and add "console up wldn rail".

**4.1** `tests/t-journey-main.sh`: before the console's first up, hold mac-studio's follower lock as the job with a background `python3` that takes `fcntl.flock` on `$(home_of mac-studio)/.cache/crew/board/follower.lock`, writes `job`, and sleeps until the test kills it; `crew console up wldn` leaves the workspace `console` with tab `shell` alone and runs no `_rail`; `crew console up wldn rail` adds `rail`; a second `crew console up wldn` makes, runs and greets nothing. Kill the holder, then a console of another label, or wldn's after `crew console down wldn`, opens `shell` and `rail`. The restart section opens `flow rail board` by name first, then proves as now that each tab's command runs again in its bare shell, `crew _rail wldn` among them. Its `ok` lines say what they prove.

**4.2** `tests/t-journey-board.sh`: `crew _follow --once` with no tab open writes wldn's board frame, rail frame and agents' views, and ends the dead card session the test already sets up; `crew _rail wldn --once` then draws the rail `crew rail --label wldn` prints, and `crew _board wldn --once` the board, as the existing checks read them; `crew _rail wldn --once` before any frame says the host's follower writes it. Add `plugin/lib/board.py`'s new reads to the tests' `# Reads:` lines where they change, run `tests/moon-tasks`, and commit `tests/moon.yml`.
