> A reading (2026-10-07): the exploration's report on a board over crew's state; its decisions are docs/adr/0010.

# Exploration: a board drawn from crew's existing state

Pane: exploration beside swancloud-design, session swancloud-1, mac-studio, 2026-10-07 evening.

## Explored

Whether flywheel-next's rail-and-board design (agentplot/blueprints `design/flywheel-next/`) can be approximated over crew's existing state, now that crew has a rail (`crew rail`, ADR 0002) and the rail is answered through Pending You cards (ADR 0005). Then: if drawn in the terminal, what it looks like and what renders it.

## Found

**The design's board rules.**
- The board is the status view drawn by phase; four lanes: Inception, Bolt plan (a narrow gate), Construction, Operation (read-only). `surfaces.md` S10, S12.
- Every decision is a marker on its object (✓ ? ✎ !); nothing is answered on the board. S17. The phases view never shows a decision as a card, nor the count. S18.
- The status view is a projection of the state the engine reads, never written by hand. `requirements.md` 141, 142. One form per object kind: ledger, sheet, slip, record, quote, row. 209.
- One board per flywheel; sinks are per member. 235, 236.

**crew's state, lane by lane (swancloud, read live at ~20:00).**
- Inception: 24 signal files on `refs/crew/swancloud/main` (`~/.cache/crew/git/afterthought/crew-state.git`), 14 moved (`moves.rec`: 11 route, 3 answered), so 10 unmoved: planner 6, crw-1-ops 2, swc-1-conductor 1, operator 1. `openspec list` on swancloud main shows elaboration in progress (dev-urls 24/45, roamgate-srv 27/28, herdr-partitions 12/15, workspace-boxes-as-clan-machines 27/28). Explorations are folders (`crew/main/openspec/explorations/`: command-cost, findings-to-design, testing-strategy; swancloud `openspec/explorations/rollout`). crew has no intent or elaboration object; agenda items arrive with `curation-and-agenda` (`crew/main/openspec/changes/curation-and-agenda/proposal.md`).
- Bolt plan: 4 open proposals (17, 35, 37, 42) from `crew rail`; `proposals.rec` holds 42, 39 closed. 5 planned bolts with no team and 7 queued units from `crew bolts`.
- Construction: 2 active bolts (`swancloud-is-tested-by-flake-check`, swc-1; `rail-answered-through-cards`, crw-1). Unit stages from the kits (`plan.py` class `Stages`: landed, merged, amended, verify, code, approved, review, construct, ready, waiting, queued, unknown). Fixes as `k["fixes"]` (the machinery row). Slot sessions from `crew status swc-1` (unit-1 working, code 4/8). Endpoints from `crew sites`.
- Operation: 7 `bolt.land` commits in the last two days on the state branch (`git log refs/crew/swancloud/main`, subjects "plan(<bolt>): land the bolt (swancloud-ops)"); no PR or checks exist, landing is `wt merge` (`plugin/roles/main-ops.md` step 3). Signals captured by ops agents are the "signals from operation".
- Markers: the four rail groups (`plan.py` `RAIL = ("proposals", "review", "verify", "land")`, `rail_rows`) each name an object: proposal → sheet, review/verify → unit in a ledger, land → ledger. Attention: a host that did not answer (`sv[h]["ok"]`); once the card unit lands, an open Pending You card with no row (ADR 0005, "the rail reconciles").
- Pending You is the answering surface and the rail the truth (ADR 0005 option 1); the board is read-only and changes nothing there. A marker can carry card state, the same column the rail gains.

**A gap the board shows and the rail misses.** Bolt `pending-you-on-every-crew-host` is `landed` in `crew bolts` (every unit on main) yet still in the plan, so `crew bolt land` has not run. `rail_rows`' land rule is `all in (merged, landed) and not all landed`, so an all-landed bolt appears nowhere. `plan.py:928` names this state ("landed but still in the plan: crew bolt land").

**Rendering in the terminal.**
- The rail tab's loop (`plugin/bin/crew` `_rail`, lines 633 to 645): clear the pane, print `crew rail`, again on a run-record entry (`crew events --follow`) or after 30 s.
- crew's devenv shell has Python 3.14.7 standard library only: `curses` present; rich, textual, blessed, urwid missing (checked with `devenv shell -- python3 -c 'import …'`). devenv.nix packages: jq, python3, recutils.
- On this host: plannotator-tui 0.9.4 (Markdown for annotation; `herdr open`), terminal-browser 0.13.1 (zenbu-labs, a real browser in a Herdr pane; swancloud `flake.nix:49`; what `lineage-page/design.md:71` opens pages in), glow and bat (not in crew's devenv). Herdr 0.9.3 has no page viewer of its own (`herdr pane` subcommands only).
- The mock drawn for the user: header line (label, as-of, hosts answered, rail count); lanes stacked (S236's phone layout as the terminal layout); one object per line truncated to width; ✓/? at the left of a line for a rail row on that object; Attention at the foot; commands stay on the rail and its shell.

## Recommended (mine, not yet ruled on)

- `crew board [--label L] [--json]` beside `crew rail`, composing `rail_rows` and the `bolts_view` reads plus proposals, moves, run record, in the one kit read `a-command-reads-the-kits-once` is about.
- Text first: Python stdlib, ANSI bold/dim off under NO_COLOR, width from `shutil.get_terminal_size()`; a `board` tab beside `flow` and `rail`, or one tab with board above rail. One read, two renderings: the loop should read the kits once and print both.
- Not now: rich/textual (not in devenv; answering is paste-into-shell), plannotator (annotation), glow (dependency for little).
- Later: the `page-of-the-flow` unit (ready, bolt `lineage-and-daily-pass`) draws the lanes as a second view in its HTML, fed by `crew board --json`, opened in terminal-browser. Borrow the mockup's forms, not its file (`mockups/rail-and-board.html` is 445 KB of seeded sample detail).
- Fix beside it: the rail's land group should also list an all-landed bolt still in the plan.

## Decided

The user settled nothing beyond sending this on. Their words: "new idea. look at my flywheel-next project under agentplot. it has a rail and board design. we have added a psuedo-rail concept to crew and just now also connected it to a new pendingyou system which sends the operator pending cards for human in the loop. i'm wondering if we could approximate a board design against our existing state." Then: "If we did it in the terminal, what would it look like and what technology would we use to render it?" Then: "send this to crew".

## Open

1. Terminal tab first, or straight to the page? (My recommendation: text first, `--json` for the page.)
2. Planned bolts with no team: in Bolt plan (the transition) or in Construction?
3. Operation window: how many days a landed bolt stays on the board (flywheel 186 bounds it).
4. One tab (board above rail, one read) or a third tab beside `rail`?
5. Ordering against `a-command-reads-the-kits-once` and `page-of-the-flow`.
6. Whether the all-landed-bolt gap is a fix on the rail unit or part of the board unit.

## Pointers

- Design: `/Users/chuck/Code/github_agentplot/blueprints/main/design/flywheel-next/surfaces.md` (S1–S19 page, rail, board; S27–S28 dock), `requirements.md` (141–146, 209, 235–236), `mockups/rail-and-board.html` (`ledgerHtml`, `recordHtml`, `sheetHtml`, `slipHtml`, `renderInception`…), `mockups/README.md`.
- crew: `plugin/lib/plan.py` (`rail_rows` 2760, `rail_view` 2810, `bolts_view` 2648, `class Stages`), `plugin/bin/crew` (`ensure_rail` 262, `_rail` 633), `docs/adr/0002`, `docs/adr/0005`, `openspec/changes/lineage-page/`, `openspec/changes/curation-and-agenda/`.
- Live reads used: `crew bolts --label swancloud`, `crew rail --label swancloud`, `crew status swc-1`, `crew plan proposed --label swancloud`, `crew events --label swancloud`, `git -C ~/.cache/crew/git/afterthought/crew-state.git log refs/crew/swancloud/main`.
- Tools: `terminal-browser --help`, `plannotator-tui` usage, `herdr pane --help`.
