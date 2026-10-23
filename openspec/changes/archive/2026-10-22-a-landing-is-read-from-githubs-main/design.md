# Design

## Context

What went wrong is in proposal.md. Here is how the landing reads today, on main (`plugin/lib/plan.py`):

- `LANDING`, the script `bolt_submit` runs on the team's host, reads `refs/heads/main` before and after `wt submit main --no-remove`. It refuses when the kit has no local branch `main`. It marks `branch.bolt/<bolt>.crew` landed only when `rc = 0` and the local main moved, and it prints one line of assignments: `RC OLD NEW KEPT WHY LEVEL MARKED`.
- `landing_said` calls a bolt landed only when `RC=0` and `NEW != OLD`. On every other exit it says "did not land: …, and main is where it was", without reading whether main moved.
- `crew bolt land` already reads main now through `MAIN` and `kit.main_now`: `origin/main` after a fetch for a kit with an origin, its own `main` otherwise (`plan.18`).

sluice, as read: sluice 0.36.4's `sluice submit --help` gives exit 0 landed, 1 failed (blamed), 2 conflict or refusal, 3 "sluice itself failed; the cause is on stderr", 4 withdrawn, 64 bad command line, 130 stopped. `wt-submit` exits with sluice's exit (sluice main 3d354b9, `crates/sluice/src/profiles/worktrunk/wt_submit.rs`). sluice lands by a leased push to GitHub and then moves the host's branch (sluice ADR 0017, record 0032 §1). An error after the push, such as a place's release failing (`crates/sluice/src/runs.rs`: "a release that fails is an error"), therefore exits 3 with GitHub's main already moved and the host's `main` possibly not.

Rules this rests on: `plan.18` (every read of main is `origin/main` after a fetch, and its details for 2026-10-22 state this reading), `plan.16` (the landing procedure: submit, then `crew bolt land`), `plan.19` (sluice pushes; crew pushes nothing, `state.5`), `code.7` (a decision is a function of facts), `read.1` (what crew can't read lands nothing and refuses), `read.2` (output checked before use), and `tests.4` / `tests.11` (each case in the lowest tier that holds it). Pages whose areas this touches: `plan.md` (`plugin/lib/plan.py`) and `tests.md` (`tests/`). It departs from no rule.

## Goals / Non-Goals

**Goals:**
- A landing is judged by main now: moved, and holding the bolt's submitted tip. sluice's exit only shapes the words.
- One decision, in Python. The script reports facts and does not decide.

**Non-Goals:**
- What sluice should exit when something fails after its push, and the try place it left on deneb. Both are sluice's (the signal names them for sluice).
- The bolt branch's place on GitHub (`plan.19`) and the landing worktree's cut. `LANDING` still makes its worktree from the local `bolt/<bolt>`, as `no-worktree-holds-main-or-a-bolt-branch` and `bolts-on-github` leave it.
- The levelling of a main checkout on branch `main`. It stays as it is, judged by the host's own `main`, which is what that checkout is on.
- The "A bolt lands on main on the user's word" requirement, which the open change `no-worktree-holds-main-or-a-bolt-branch` rewrites. This change adds a requirement beside it, so the two deltas never touch the same text.

## Decisions

### 1. Main now is read twice: before by `MAIN`, after by `LANDING`

`bolt_submit` first runs the existing `MAIN` script on the team's host (`host_run`) and decides with `kit.main_now`. A refusal there (the fetch failed, GitHub has no main, the kit has neither main) refuses the landing before any worktree is made (`read.1`), and the commit it read is *before*. `LANDING` drops its own read of `refs/heads/main` as the measure. After sluice's outcome it runs `MAINS` (embedded, as `POLICY` and `MAIN` embed it), and for each main that exists it reports whether that main holds the submitted tip: `HELD_GITHUB` and `HELD_OWN` are yes or no, from `git merge-base --is-ancestor`, with the tip being the landing worktree's `HEAD` read just before `wt submit`.

Why: `MAIN` and `kit.main_now` already decide "main now" for `crew bolt land`. Reusing them keeps one reading of main in crew. The alternative, deciding inside the script (refusing when `git fetch` fails), would copy `main_now`'s rules into bash.

Why also "holds the tip", and not only "moved": the signal's own words are "a landing is on main once GitHub's main holds the bolt's merge". Main can move under a failed submission by another landing, and the tip check keeps that from reading as this bolt's. The tip is a parent of sluice's landing merge, so ancestry is exact.

### 2. `LANDING` reports facts; `landing_said` decides

`LANDING` keeps the host's own `main` before and after only for levelling, so a missing local `main` no longer refuses: it simply has nothing to level. Its output becomes the `MAINS` lines (`ORIGIN`, `FETCHED`, `GITHUB`, `OWN`), `HELD_GITHUB`, `HELD_OWN`, and a last line of assignments `RC TIP KEPT WHY LEVEL SAID`. `SAID` is the last non-empty line sluice printed, captured by sending `wt submit`'s output to a temporary file that is then passed on to standard error whole, as today. `bolt_submit` collects standard error only after the command ends, so nothing is lost by not streaming it.

`landing_said(bolt, kit, said, before, marked="")` then:

1. Words it can't read, as today: "crew can't read what the submission of bolt/<b> to <kit>'s main came to: …", not landed.
2. `kit.main_now(said)` refused: not landed, "crew can't tell whether bolt/<b> landed on <kit>'s main: <why>; the submission exited <rc>." This is followed by the kept worktree, if any. Nothing about main's position, nothing about a mark.
3. Main now ≠ *before* and the matching `HELD_*` is yes: landed. `rc = 0` gives today's words: "bolt/<b> landed on <kit>'s main at <sha7>: now crew bolt land <b>." Any other exit inserts, before the level, mark and kept notes: " sluice exited <rc> after its push: <SAID>. That is sluice's to report, apart from the landing." (When `SAID` is empty: "sluice said nothing".)
4. Main now = *before*: not landed, today's words "bolt/<b> did not land: <why>, and main is where it was. …", with the same `why` per exit (1, 2, 130, else "the submission exited <rc>"). Add 3: "sluice itself failed", 4: "it was withdrawn while it waited", 64: "sluice could not read its command line".
5. Main now ≠ *before* but not held: not landed, "bolt/<b> did not land: <why>; <kit>'s main moved to <sha7> without it." followed by the same tell-the-conductor sentence as 4.

### 3. The mark is set after the decision, by its own script

The mark is no longer set inside `LANDING`. A short `LANDED_MARK` script (`main=$1 bolt=$2`) sets `branch.bolt/<b>.crew` to `landed` when the branch carries crew's mark, and prints `MARKED=yes|no|<why>` exactly as `LANDING` does today. `bolt_submit` runs it with `crew.on_machine` only when `landing_said` says landed, then builds the words with the mark note. The mark sentence and its order stay as today's tests pin them: landed words, then level, then mark, then kept.

Why: `code.7`. Today the bash and the Python each decide "landed", and the signal is exactly where they diverged. Running the mark as a second call costs one ssh round trip, and only on a landing. A failure to reach the host for it is named as the mark not set ("crew could not mark bolt/<b> landed: <host's words>"), and the landing stands.

### 4. `bolt_submit` records and prints on any landed exit

`bolt_submit` records `bolt.submit` with main now's sha (not `NEW=` sliced from the output) and prints the words. It exits non-zero through `fail` on any not-landed outcome, so ops's background wait reads success exactly when the bolt landed.

## Risks / Trade-offs

- [A fetch before every landing adds seconds] → The landing already takes minutes in sluice's queue. The fetch is the one `plan.18` requires of a decision of the moment.
- [`HELD_*` is false when sluice squashes or rebases] → sluice lands as a merge commit with the submitted head as its second parent (`tests/stubs/wt-submit`, sluice's landings). A change in sluice's landing shape would show as "main moved without it", never as a false landing.
- [Main moves by another landing *and* this one in the same window] → Held is true and moved is true, so it reads as landed, which is right: main holds it.

## After deploy

Nothing. Every scenario is proven by the logic and contract cases this change adds. The contract case drives real git with a stand-in sluice that pushes to a bare origin and exits 3, which is the signal's shape.

## Task notes

**1.1** `LANDING`: drop `old=… refs/heads/main || exit 2` as a refusal. Read `own_old` with `|| own_old=`. Record `tip=$(git -C "$path" rev-parse HEAD)` once the worktree exists. Run `wt submit main --no-remove` with stdout and stderr to `$(mktemp)`, cat it to stderr, and take `said` from its last non-empty line. After the worktree removal, read `own_new` and level as today when `own_old` and `own_new` are both set and differ. Then append `MAINS`, the two `HELD_*` lines (`-` when that main is absent), and `printf 'RC=%s TIP=%s KEPT=%q WHY=%q LEVEL=%q SAID=%q\n'`. Keep the `crew-landing` pid mark and its emptying exactly as they are: `landing_now` reads them. The mark block moves to `LANDED_MARK` (task 1.2).

**1.2** `bolt_submit`: `before` comes from `kit.main_now(host_run(fleet, machine, MAIN, main), kit, machine)` and is refused with its why. Then `LANDING`, then `landing_said(bolt, kit, out, before[1])`. When landed: `LANDED_MARK` through `crew.on_machine`, then `landing_said(…, marked=<its output>)` for the final words, or a small `marked_words` helper if cleaner. Record and print. `landing_said` stays pure (`code.7`).

**2.1** Logic cases in `tests/py/test_landing.py`. Rewrite `said()` to emit the `MAINS` lines, `HELD_*` and the last line. Keep every existing case's assertion text, since the words for exit 0 are unchanged. Add the signal's case (rc 3, GitHub moved and holds the tip, own main unmoved: landed, its words naming exit 3 and `SAID`), main unmoved on rc 0 and on rc 3, moved-but-not-held, fetch failed after, and a kit with `ORIGIN=no` judged by `OWN`. Name the signal in the signal case's docstring.

**2.2** Contract cases in `tests/contract/test_git.py`. Update `landing()` to run `MAIN` before, as `bolt_submit` does, and to pass `before`. Add an origin case: give `repo` a bare origin with `main` pushed, and a stand-in `wt-submit` that forms the merge, pushes it to `origin main`, leaves `refs/heads/main` alone, prints "sluice: releasing …: its command failed" to stderr and exits 3. Assert that `landing_said` says landed at origin's new commit naming exit 3 and that line, and that `LANDED_MARK` then marks the branch. Add a second stand-in that exits 2 having pushed nothing: assert not landed and "main is where it was". The existing cases keep a kit with no origin.
