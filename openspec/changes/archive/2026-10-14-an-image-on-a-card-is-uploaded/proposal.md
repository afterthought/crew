# An image on a card is uploaded

## Why

The card discipline the planner's and the conductor's briefs carry says what a card's words hold and that a card attaches nothing, but it says nothing of a picture or of a document shown on the card. The user and the operator agent tested both on 2026-10-10 (record 0005 as amended that day): a screenshot attached by its path shows only the path with a copy button, while the same image uploaded shows as the picture; and of four ways to show a document, only inline Markdown rendered, while an uploaded `.md` file did not render, an uploaded `.html` was refused, and inline HTML did not render. `briefs.9` already rules out the forms that fail, but an agent following its brief has no word on the form that works, and madswan's spike put its screenshot on a card as a path.

## What Changes

- The card discipline says an image a card needs reaches the user as the picture: an artifact of kind `image`, posted with `upload: true`, and the file then put to the upload URL the post returns, with the file's content type. Never a `path` artifact for it.
- It says a document's substance shown on a card, beyond its words, is inline Markdown: an artifact of kind `code` with lang `markdown`, the text as its lines. Never an uploaded file and never HTML.
- It says the whole document is reached only through the card's plannotator link, as it already does for a card that asks the user to read something.
- "Leave the card's artifacts empty" becomes: the link is no artifact, and the only artifacts a card carries are such an image or such Markdown.
- `tests/t-briefs.sh` pins the new words in both briefs (`tests.6`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: two new requirements, "A card's picture is uploaded" and "A card's document is inline Markdown".

## Impact

- The planner's and every conductor's brief, at each agent's next fresh start; no command changes, so README, the crew skill and `crew`'s usage stay as they are (`docs.2` is not touched).
- Cards already posted are unchanged.
- No check in crew's card hook reads a card's artifacts yet; this change adds none.

## Touches

```
plugin/lib/crew.py
tests/t-briefs.sh
```
