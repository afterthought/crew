# Proposal

## Why

The user wants a board they can open from the menu bar at any time: one that looks like their flywheel mockups, shows at a glance which bolt plans are waiting and which bolts are being built, one partition at a time with the others a click away, and narrowed to one team when they want (record 0010, "The page is the board the user looks at", 2026-10-09). `crew board` already reads all of that as four lanes, in the terminal and as JSON. `crew page`, which `page-of-the-flow` builds, already writes one self-contained HTML file per partition. This change puts the board on the page, drawn the way the mockup draws it, so the page becomes the board the user looks at. Serving the pages on the network every 30 seconds is swancloud's, not this change's.

## What Changes

- **The page opens on the board.** `crew page <label>` also makes the board's read for that partition and embeds it. The page opens on a board view: the four lanes of `crew board` (Inception, Bolt plan, Construction, Operation), drawn in the mockup's phases-view forms and glyphs. A signal is a quote with a left rule. A proposal is a sheet. A queued unit is a slip with its repository greyed before its name. A bolt is a flat ledger with its units as a chain, merged, building or queued. A landed bolt is a muted record with a stamp. Every rail row is a ✓ or ✎ marker on its object, and ! marks attention. The lineage view `page-of-the-flow` draws stays one switch away.
- **It fits the screen it is on.** The lanes sit side by side on a desktop, with Bolt plan as the narrow hatched gate, and stack one above the other under 760 px, as the phone does. The page follows the viewer's light or dark preference. It is still one file that needs no network: the mockup's styles are copied in, its web fonts are replaced by system fonts, and none of its sample data comes along.
- **One team at a time.** A control in the header narrows every lane to one of the partition's teams, or shows all of them. The choice is kept in the page's address and in the browser, so it survives a reload and the 30-second regeneration. What counts as a team's is decided once, in the board's read. A held bolt and a landing belong to the team that holds or held them. A signal belongs to the team whose agent captured it. A proposal belongs to the teams holding the bolts it touches and the teams that build its repositories. A planned bolt, a queued unit and an exploration belong to every team that builds their repository. The attention strip is never narrowed.
- **Every partition in the header.** The header names every partition in the teams file, the current one marked. Each of the others is a link to that partition's page beside this one (`../<label>/page.html`, crew's own layout under `~/.local/state/crew/`). So when the pages are served side by side, each is one click from the others.
- **`crew board --json` says which teams each object belongs to**, and lists the partition's teams, so the page narrows by reading those fields. The text board does not change.

## Capabilities

### New Capabilities

- `board-page`: the board view of crew's page. Its lanes, forms and markers; its layout on a desktop and a phone; light and dark; narrowing to one team, kept across reloads; and the header's links to the other partitions' pages.

### Modified Capabilities

- `crew-board`: its JSON also says which teams each object belongs to, and lists the partition's teams. (The capability is still being added by the unarchived `a-board-shows-the-flow-in-the-terminal`, so this delta only adds a requirement.)

## Impact

- `plugin/lib/page.py` and `plugin/lib/page.html`, which `page-of-the-flow` creates: the board read, the board view, the view switch, the team control and the partition links. This unit comes after `page-of-the-flow` and builds on its page.
- `plugin/lib/board.py`: the teams each object belongs to, and each partition's teams, in `board_data`.
- `tests/t-page.sh` and `tests/t-board.sh`, with `tests/moon.yml` regenerated if what they read changes.
- `README.md`, `plugin/skills/crew/SKILL.md` and the usage header in `plugin/bin/crew` say the page opens on the board (`docs.2`).
- `crew page` now reads the kits over ssh, as `crew board` does, which takes 2.4 to 4.7 s per partition from mac-studio. Nothing new is written anywhere but the page file. `crew board`'s text and `crew rail` do not change.
- Not here: serving the pages, regenerating them every 30 seconds and the SwiftBar link (swancloud record 0019), the deploys view (`the-page-shows-the-deploys`), and the page reloading itself.

## Touches

```
plugin/lib/page.py
plugin/lib/page.html
plugin/lib/board.py
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/t-page.sh
tests/t-board.sh
tests/moon.yml
```
