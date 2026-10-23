# Design

## Context

`page.nav(labels, label)` (`plugin/lib/page.py`) draws the header's partitions, each other one a link `../<label>/page.html`, crew's own layout: the default output is `record.ROOT / <label> / "page.html"`, `~/.local/state/crew/<label>/page.html`. `render(d)` puts that into the template's `<!--{{PARTITIONS}}-->` placeholder; `page()` works out the output path after the data is read and calls `write(out, render(d))`. `--json` prints the data and writes nothing, so it draws no header.

swancloud's maker runs `crew page <label> --out "$WORK/<label>.html"`, nothing else, copies the file to swancloud-srv as `<dir>/<label>.html`, and Caddy serves the pages side by side at `https://board.swancloud.net/<label>.html` (swancloud `packages/swancloud-board/swancloud-board.sh`, `lib/board.nix`, `modules/board-server.nix`). swancloud's own `board-page` spec already expects it: "a link in one page to `<other label>.html` opens the other". So the file name the maker asks for is the name the page is served under, and the page's links resolve only once they follow it. Record 0010's page bullet, read 2026-10-12, rules: "The served layout is the kit's; the page's partition links open the pages where the kit serves them."

Area pages touched: `docs.md` (README, the skill's line and the spec delta). Rules this design rests on: `code.7`, `read.1`, `state.4`, `code.8`, `docs.2`, `docs.4`.

## Goals / Non-Goals

**Goals:**
- On the served board, each other partition's link opens that partition's page, with no change to swancloud.
- crew's own layout keeps linking as it does today.
- No page links to a page crew cannot place.

**Non-Goals:**
- Writing every partition's page from one `crew page` run; serving stays the kit's (record 0010).
- Any change to the page's data, its views, the board's read or the agents' bands.

## Decisions

### The links follow the layout of the page's own file

The page links each other partition where the same layout puts it, read from the path the page is written to. Two parts of that path can name the partition: the file's stem (`swancloud.html`) and its folder's name (`swancloud/page.html`). Each part that equals the page's label exactly is swapped for the other partition's label, and the link is the result relative to this page's folder:

| This page's file | madswan's link |
|---|---|
| `…/swancloud/page.html` (crew's default) | `../madswan/page.html` |
| `…/swancloud.html` (swancloud's maker) | `madswan.html` |
| `…/swancloud/swancloud.html` | `../madswan/madswan.html` |
| `…/board.html`, `…/x/page.html` | none |

The file's suffix is kept as written. A stem or folder that only contains the label (`swancloud-board.html`) does not name it.

The kit says its layout by the file it asks for, which it already does: swancloud writes each page under the name it serves it by. That makes the intent true with this change alone, and a kit that serves its pages another way side by side gets links that follow by naming its files the same way.

Alternatives considered:
- *An option naming the link pattern* (`crew page <label> --links '{label}.html'`): explicit, but nothing reaches the served board until swancloud's maker passes it, a change in another kit, and swancloud's maker runs `crew page` with `--out` and nothing else by its own spec's wording ("Each page is crew's whole page").
- *A field in the teams file naming where each partition's page is served*: crew reads the teams file and never writes it, and no field has a default (`code.5`), so every host would refuse a teams file without it until swancloud's deploy; and the link is a fact about files laid out side by side, not about the fleet.
- *Links always `<label>.html`*: breaks crew's own layout, which the operator agent opens from disk.

### A page whose layout names no partition links none and says so

When neither the file's stem nor its folder is the page's label, crew cannot tell where the other partitions' pages are, so the header names each other partition as text, the way the current one is drawn but without its mark, and `crew page` prints a line after the header line: `the other partitions are not linked: <path> is neither named <label>.html nor in a folder <label>`. It does not guess a link (`read.1`), and a link that opens nothing is the bug this change fixes. A teams file with one partition prints no such line, since there is nothing to link.

### The decision is a function of plain facts

The link is worked out from the labels, the page's label and its output path as a `pathlib.PurePath`, touching no file (`code.7`): `page.beside(path, label, other)` returns the relative link or `None`, `page.nav(labels, label, path)` draws the header from it, and `render(d, path)` takes the path the page will be written to. `page()` already knows the path before it writes; it passes it to `render` and prints the line. Nothing is read or written that was not before (`state.4`), and the data block is unchanged, so `board.agent_views` and `plugin/hooks/status.js` are untouched (`code.8`).

## Risks / Trade-offs

- [A kit names its files for the partition but serves them under other names] → its links break as they do today; the rule is stated in README and the usage, so a kit can lay its files out to match, and swancloud's already does.
- [The label equals a common file stem, such as a partition named `page`] → `page/page.html` reads as both, which links `../<other>/<other>.html`; labels today are madswan, swancloud and wldn, and a kit hitting it can write the page under another name.
- [The usage's `crew page` lines change] → swancloud's maker finds the command by a line beginning `crew page` in crew's usage; the task keeps that line's first words as they are.

## Migration Plan

None: the next page swancloud's maker makes after the landing reaches a host carries the links, and crew's own layout links as before.

## After deploy

None: every scenario is proved by crew's logic and end-to-end tiers; whether the served board's links open the other pages is swancloud's `board-page` spec's to prove, and it needs nothing from swancloud.

## Task notes

**1.1** In `plugin/lib/page.py`, add `beside(path, label, other)`: `path` a `pathlib.PurePath`; `folder = path.parent.name == label`, `named = path.stem == label`; neither → `None`; else the link is `(f"../{other}/" if folder else "") + (f"{other}{path.suffix}" if named else path.name)`. Change `nav(labels, label, path)` so each other label is `<a class="part" href="{escaped link}">` when `beside` gives a link and `<span class="part">{label}</span>` when it gives none; the current one stays `<span class="part" aria-current="page">`. Rewrite both docstrings to say the links follow the layout of the page's file. Cases in `tests/py/test_page.py`, replacing `test_the_header_names_every_partition_its_own_current_and_each_other_linked`: crew's layout (`/s/wldn/page.html` → `../madswan/page.html`), the served layout (`/w/wldn.html` → `madswan.html`), both (`/s/wldn/wldn.html` → `../madswan/madswan.html`), neither (`/s/board.html` and `/s/x/page.html` → spans, no `<a`), and a stem that only contains the label (`/s/wldn-board.html` → no link).

**1.2** `render(d, path)` passes the path to `nav`; update the two existing `page.render(...)` callers in `tests/py/test_page.py` (`TestFile`, the board-view test) to pass a path in crew's layout. In `page()`, compute `out` before rendering (it already is), call `write(out, render(d, out))`, and after the header line print `the other partitions are not linked: {out} is neither named {label}.html nor in a folder {label}` when the teams file has more than one partition and `beside(out, label, other)` is `None`. Keep `--json` as it is. In `tests/t-journey-board.sh`, after the existing `crew page wldn` case: `crew page wldn --out "$T/served/wldn.html"` writes a page whose header holds `href="madswan.html"` and `href="swancloud.html"` and prints no not-linked line; `crew page wldn --out "$T/served/board.html"` writes a page whose `<nav class="parts"` holds no `<a ` and prints the not-linked line. Its `# Reads:` line already names `page.py` and `page.html`, so `tests/moon.yml` is unchanged.

**1.3** README's `crew page` paragraph: replace "each other one is a link to its page beside this one, `../<label>/page.html`: that holds while the pages keep crew's layout, `~/.local/state/crew/<label>/page.html` or the same under another folder, and not for a page written with `--out` anywhere else" with the rule: each other partition links to its page in the layout of this page's file, `../<label>/page.html` in crew's own, `<label>.html` beside a page written as `<label>.html` as swancloud's board serves them, and none, said by the command, for a file whose name and folder are not the partition's. `plugin/bin/crew`'s usage for `crew page`: replace "(../<label>/page.html)" with the same in a few words, keeping the line `crew page     <label> [--out <file>] [--since <time>]` exactly. `plugin/skills/crew/SKILL.md`'s row: "linking each other partition's page beside it, in the layout of its own file". `tests/t-docs.sh` checks the usage against README.
