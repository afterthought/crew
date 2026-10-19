# Proposal

This is the lineage page the user approved on 2026-10-03 (`openspec/changes/lineage-page`), carried into this unit as written, in the form a unit's change takes now.

## Why

`crew trace` answers "what happened to this one thing" as lines of text, and `crew events --follow` shows acts as they happen. Neither shows the shape of the whole: which signals led to which agenda items, which items to which units, which units sit in which bolts, and where each stands. That shape is what the findings-to-design work set out to make visible (`openspec/explorations/findings-to-design/proposal.md`, invariants 18 and 19 and the comparison of views in section 4; `roadmap.md`, change 8), and the user chose a lineage page as the second view after the text one, ahead of a zoetrope provider, because zoetrope draws agents and this is about work.

The view must stay replaceable: it reads the run record and adds nothing to it.

## What Changes

- **`crew page <label>`** writes one self-contained HTML file from the flywheel's run record: signals, agenda items, proposals, units and bolts as columns, with the links between them, a timeline of the entries beneath, and each object opening to its own history: who did what, when, on which host, with which commit, and the session to open for the detail.
- The page's objects and links come from the run record alone, by the same walk `crew trace` uses, so the page and the trace cannot disagree. Its labels (a signal's assertion, an item's subject, a unit's intent, a bolt's goal) are read from the flywheel's state.
- The file needs no network and no server: its data, style and script are inside it. It says the time and the state commit it was made from, and names any host whose newest entries it could not read.
- It is written under `~/.local/state/crew/<label>/` on the host where the command runs, or where `--out` says. It is never committed.
- The operator agent makes and opens it on request, in terminal-browser beside its pane.

## Capabilities

### New Capabilities

- `lineage-page`: the page that draws a flywheel's objects and the links between them from the run record, and what it must and must not depend on.

### Modified Capabilities

- `operator-agent`: the operator agent makes and opens the lineage page on request.

## Impact

- A new `plugin/lib/page.py` and its template, `plugin/lib/page.html`; `plugin/lib/record.py` exposes the lineage walk `crew trace` uses as one function both call.
- `plugin/bin/crew`: `page`, and its usage header. `plugin/roles/operator.md`: one paragraph.
- `README.md`, `plugin/skills/crew/SKILL.md`, a new `tests/t-page.sh`, the brief's phrase in `tests/t-briefs.sh`, and `tests/moon.yml` regenerated for the new test.
- Nothing is written to any repository, and no existing command changes: `crew events` and `crew trace` print what they print today.
- Depends on `run-record` and `state-repository`, both built. Proposals show now that `plan-proposals` is built; the agenda column stays empty until `curation-and-agenda` adds agenda items, and the page shows bolts, units and signals without it.
- Later units add views to this page: the board drawn from `crew board --json` (`the-page-shows-the-board`) and the deploys (`the-page-shows-the-deploys`), as record 0010 says. This change builds neither.

## Touches

```
plugin/lib/page.py
plugin/lib/page.html
plugin/lib/record.py
plugin/bin/crew
plugin/roles/operator.md
plugin/skills/crew/SKILL.md
README.md
tests/t-page.sh
tests/t-events.sh
tests/t-briefs.sh
tests/moon.yml
```
