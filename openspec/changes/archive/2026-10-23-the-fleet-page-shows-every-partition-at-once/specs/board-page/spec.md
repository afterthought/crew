## MODIFIED Requirements

### Requirement: The header names every partition and links to its page
The page's header SHALL name every partition in the teams file, in its order, with the page's own partition marked as current. Each other partition SHALL be a link to that partition's page in the layout of this page's own file: `<label>.html` beside it when this page's file is named for its partition, `../<label>/` with the same file name when this page's folder is named for its partition, both when both are. When neither names its partition, the other partitions SHALL be named and not linked, and `crew page` SHALL say so. Before the partitions the header SHALL link to the fleet page in the same layout: `index.html` beside a page whose file alone is named for its partition, as the board is served, and `../page.html` from a page written as `page.html` in a folder named for its partition, as crew writes them; a page in any other layout SHALL have no link to the fleet page, since crew cannot tell where the fleet page is.

#### Scenario: Three partitions
- **WHEN** the teams file holds madswan, swancloud and wldn and `crew page swancloud` writes `~/.local/state/crew/swancloud/page.html`
- **THEN** the header links to the fleet page at `../page.html`, then shows madswan, swancloud marked as current, and wldn, and madswan links to `../madswan/page.html` and wldn to `../wldn/page.html`

#### Scenario: Pages written side by side as they are served
- **WHEN** `crew page swancloud --out <folder>/swancloud.html` writes the page, as swancloud's board asks for it
- **THEN** the header links to the fleet page at `index.html`, madswan links to `madswan.html` and wldn to `wldn.html`, so on the board served as `<label>.html` side by side each link opens that partition's page

#### Scenario: A folder and a file both named for the partition
- **WHEN** the page is written to `<folder>/wldn/wldn.html`
- **THEN** madswan links to `../madswan/madswan.html`, and the header has no link to the fleet page

#### Scenario: A page written where its layout names no partition
- **WHEN** `crew page wldn --out <folder>/board.html` writes the page
- **THEN** the header has no link to the fleet page and names madswan and swancloud without linking them, and `crew page` prints a line saying the other partitions are not linked because the page's file and folder are not named for wldn
