## ADDED Requirements

### Requirement: A card's picture is uploaded
A card a crew agent posts SHALL carry an image it needs, a screenshot or a page image, as an artifact of kind `image` posted with `upload: true`, its file then put to the upload URL Pending You returns for that artifact with the file's content type, so the user sees the picture. It SHALL NOT carry the image as an artifact of kind `path`.

#### Scenario: A screenshot on a card
- **WHEN** an agent posts a card that needs a screenshot of a page
- **THEN** the card holds one artifact of kind `image` posted with `upload: true`, the agent puts the image to the upload URL the post returned with its content type, `image/png` for a PNG, and the user sees the picture on the card, with no path of the image anywhere on it

### Requirement: A card's document is inline Markdown
A document's substance shown on a card beyond its words SHALL be inline Markdown, an artifact of kind `code` with lang `markdown` and the text as its lines, never an uploaded file or HTML. The whole document SHALL be reached only through the card's plannotator link, but for a proposal's card, which holds its proposal whole. A card SHALL carry no artifact but such a picture or such Markdown, and a proposal's card its change as text.

#### Scenario: A document's substance on a card
- **WHEN** an agent shows part of a document on a card beside its words
- **THEN** that part is an artifact of kind `code` with lang `markdown`, its lines the document's Markdown, and the whole document is reached through the card's plannotator link, never attached as a file

#### Scenario: A card with nothing to show
- **WHEN** a card needs no picture and shows no part of a document beyond its words
- **THEN** its artifacts are empty, and its plannotator link is in its words and its links, never an artifact

### Requirement: A proposal's card carries its change as text
A proposal's card SHALL carry its change as an artifact of kind `code` with lang `text`, its lines those `crew plan card <n>` prints, each at most forty characters, so it reads in monospace on a phone without wrapping.

#### Scenario: A proposal's change as text
- **WHEN** the planner posts the card for proposal 4, which drops a unit and adds two
- **THEN** the card carries two artifacts, the uploaded picture and a `code` artifact of lang `text` holding the change as `crew plan card 4` prints it, and no Markdown artifact and no link
