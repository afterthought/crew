# Design: a landing's reading opens past Plannotator's limit

## Context

The proposal gives the box's case. This change touches the areas of `plan.md` (`plugin/lib/plan.py`) and `tests.md` (`tests/`). Rules it relies on:

- `read.1`: nothing is dropped silently. What crew leaves out of a reading, it names.
- `code.7`: how the diff is split is a decision, a function of the diff's text that starts no process.
- `tests.4`: the fix's case goes in the logic tier, and crew's stub of Plannotator behaves as Plannotator does.
- `code.1`: nothing outside the standard library.

It departs from no rule.

### Where Plannotator refuses, and what it counts

Read in Plannotator 0.28.48, the version on deneb, from the source its binary carries. It was then checked against the binary itself on deneb on 2026-11-05.

- **The limit.** `MAX_ANNOTATABLE_FILE_BYTES = 2 * 1024 * 1024`, 2,097,152 bytes. It counts one file's size on disk (`stat.size`) and refuses a file that is larger (`size > MAX`). A file of exactly 2,097,152 bytes opened, and one of 2,097,153 bytes was refused.
- **The refusal.** `annotate` with several paths opens them as one review (`annotate-bundle`). Before any server starts, `resolveAnnotateBundleFiles` checks each path in turn, and one file over the limit refuses the whole review: "File too large to annotate (max 2MB): <path>". A single path is refused the same way. With `--result-file`, as crew runs it, the exit is 2.
- **No cap on a review's files together.** Nothing in the bundle's check adds the sizes up. The page loads each document on its own (`/api/doc`) when the reader opens it. Five files of 7.8 MB in all opened as one review, and each was served whole.
- **A folder** (`annotate <folder>/`) starts, but each document in it goes through the same 2 MB check when served (`DOC_TOO_LARGE`, 413), so a file over the limit opens nowhere.
- **`plannotator review --patch-file`** shows a unified diff in Plannotator's code-review view. But it is a session of its own with a decision of its own. A landing's reading is one review with one decision (card-sessions "One session per card key").

So Plannotator's way past the limit is several files, each within it, in one review.

## Decisions

### Decision 1: the diff in as many files as the limit asks, each of whole files' changes

`diff_parts(diff, most)` splits git's diff at its `diff --git` headers into sections, one for each file changed. It packs them in git's order into parts, starting a new part where the next section would take the part past `most` bytes as UTF-8. `most` is `PLANNOTATOR_MOST`, 2 MiB. A file's change is never split across two parts.

`landing_reading` names a diff that fits in one part `<nn>-<bolt>-diff.txt`, as before, so every reading that opened before reads the same. It names several parts `<nn>-<bolt>-diff-<k>-of-<m>.txt` and says on the page: "That diff comes in <m> files, each holding whole files' changes in git's order, since plannotator opens no file over 2 MB."

`landing_write` writes every file as UTF-8, the encoding the parts were measured in, so a file's size on disk is the size crew counted.

Considered: sluice core.43's shape alone. That would carry one diff file whole as far as the limit holds and name the rest by their paths, their count and the compare view. Rejected, because Plannotator opens several files with no cap on them together. Splitting the diff keeps every file's change that can open whole in the reading, where core.43's shape alone would leave out every file past the first 2 MB. The brief asked for core.43's shape unless Plannotator gives a better way, and this is that better way for the files that fit.

### Decision 2: a file whose own change passes the limit is named, never cut

No part can hold such a file's change whole. Here the reading takes core.43's shape, which rules out cutting an item within itself to fit a limit and naming nothing past it:

- In the file's place in the diff, a line names it: "<path>: its change, <size>, passes the 2 MB plannotator opens in one file, so it is not in this reading; its first page says where to read it whole."
- The page lists every such file with its size, says how many there are, and says where to read them whole: GitHub's compare view, `https://github.com/<repo>/compare/<base>...<head>`, and `git -C <main> diff <base> <head> -- <path>` on the team's host. `<repo>` is the kit's `repo` from the teams file. `<base>` is where the bolt last met main and `<head>` is the bolt's head, both full commits, the same range the reading's diff is read from. Both commits are on GitHub: base on main, and head on the bolt's branch (`plan.19`). The git command reads the same range on the host when GitHub's view does not render a large diff.

`diff_path` names the file from its header, `diff --git a/<path> b/<path>`. When the two sides differ, as for a rename or a path git quotes, it gives both as git wrote them.

A size is said in Plannotator's own MB, 2^20 bytes, rounded up to a tenth (`megabytes`), so a file just past the limit never reads as "2.0 MB".

Considered: cutting such a file's change at its hunks, or at line ends, into parts of its own. Rejected for three reasons. core.43 rules out cutting an item within itself. A single file's change of 2 MB is generated or vendored text, which a reader is not helped by reading in pieces. And one line over 2 MB, as in a minified file, can't be cut at a line end at all.

### Decision 3: crew's stub of Plannotator refuses as Plannotator does

`tests/stubs/plannotator` refuses a file over 2 MiB before it registers anything, with Plannotator's words and its exit, 2 with a result file and 1 without (`tests.4`). An end-to-end reading that wrote one file too large now fails in the suite as it failed on the box.

### Not changed

- A unit's change Markdown is written whole as before. No change's Markdown near 2 MB has been seen.
- A batch's reading holds no diff.
- The conductor's brief, `plugin/skills/crew/SKILL.md` and `crew`'s usage header describe the reading as a page, the changes and the diff, which still holds. README's account of the files is the one that says more, and it changes (`docs.2`).

## Risks

- A bolt of very many large files makes a reading of many parts. Plannotator loads each part only when the reader opens it, so the session starts as before.
- GitHub's compare view does not render a file's diff past its own limits. The git command on the team's host reads it whole.

## After deploy

None. Every behaviour here is code proven in crew's tiers. wldn's box gets it when swancloud moves its crew pin, which is swancloud's deploy and no step of this change. After that, the rail's next try of the landings card opens the bolt's reading by itself.

## Task notes

**1.1** `plan.PLANNOTATOR_MOST`, `plan.diff_parts(diff, most)`, `plan.diff_path(section)`, `plan.megabytes(n)`. Cases in `tests/py/test_landing.py`: five 0.9 MB files' changes in three parts, two, two and one, none over the limit, together the diff; a diff of exactly the limit in one part, and one byte more in two; a file named by its path, a rename and a quoted path by both sides; sizes said rounded up.

**1.2** `plan.landing_reading(..., diff, whole)`, where `whole` is `dict(repo, base, main, host)`: the parts' names, the page's count of parts, the page's list of files left out with the compare view and the git command, and the line in each one's place. The existing cases pass `WHOLE`. Case: `README.md`, `vendor/bundle.js` at 2.5 MB, then `README.md` again.

**1.3** `plan.landing_write` builds `whole` from the team's kit (`repo`, `main`, `machine`) and the facts' `base`, and writes each file as UTF-8. Case: a diff of 1.5, 1.5 and 3 MB files written as two parts, every file within the limit on disk, the 3 MB file named on the page and in its place.

**1.4** `tests/stubs/plannotator`: the refusal and the docstring's sentence on it. `tests/t-journey-land.sh` runs the landing's reading on the stub.

**2.1** README's paragraph on a card's reading, under *Operations*, where it lists the files of a landing's reading.
