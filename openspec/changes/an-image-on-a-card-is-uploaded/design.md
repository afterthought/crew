# Design

## Context

The card discipline is one text, `cards_how` in `plugin/lib/crew.py`, filled into the planner's brief and every conductor's brief as `{{CARDS}}`. It already says a card carries no path, no artifact of kind `path` or `file`, and that its plannotator link is no artifact: "leave the card's artifacts empty". `tests/t-briefs.sh` pins its phrases in `cards_say`, which runs for both briefs.

Record 0005, as amended 2026-10-10, settled two things the discipline does not yet say, from tests the operator agent ran with the user that day:

- An image a card needs is an artifact of kind `image` posted with `upload: true`, the file then put to the upload URL the post returns with its content type; the user sees the picture. An artifact of kind `path` to the same file shows only the path with a copy button, as madswan's spike found.
- Of four ways to show a document on a card, only inline Markdown rendered: an artifact of kind `code`, lang `markdown`, the text as its lines. An uploaded `.md` did not render, an uploaded `.html` was refused (HTTP 415), and inline HTML as kind `draft` did not render.

`briefs.9` already rules out the failing forms, a screenshot as a `path` and a document as an uploaded file or HTML. This change gives the briefs the working forms in the same words.

Rules relied on: `briefs.9` (what a card carries), `briefs.11` (who posts cards: the planner and the conductors, which are the briefs that carry the discipline), `tests.6` (every rule a brief carries is pinned by a phrase), `docs.4` (the spec changes through this change's delta), `docs.7` (the change edits no page under `docs/`; the design agent takes the item off `_open.md` after the landing). Pages whose areas the change touches: `briefs.md`, through the briefs crew fills; `tests.md`. `code.1` holds: the change is text in an existing function.

Pending You's schema, read 2026-10-11 from the session's `post_request` and `update_request` tools: an artifact is `{kind, title, ref}` with kind one of `image`, `diff`, `url`, `file`, `draft`, `code`, an optional `lang` among which `markdown`, `lines`, and `upload`, "image or file: true for an uploadUrl"; or a `path` artifact `{kind: "path", title, path}`. At most eight. `update_request` takes the same artifacts.

## Goals / Non-Goals

**Goals:**

- The discipline says how a picture reaches the user, how a document's substance is shown on a card, and that the whole document is reached through the link, in words a planner or conductor can act on without reading the record.
- "Leave the card's artifacts empty" no longer contradicts the image and the Markdown.

**Non-Goals:**

- A check in the card hook that refuses a `path`, `file` or `draft` artifact. `roles.3` asks for one when an agent breaks a rule its brief states; no brief stated this until now.
- Which cards carry a picture or Markdown. That is each card's own form, in the planner's and conductor's *Cards* and in the units queued for them (a proposal's card holding its picture and text is `a-proposals-card-shows-the-change-and-lets-new-units-be-left-out`).
- Any change to a card's words, link or key.

## Decisions

### One paragraph in the discipline, after the path paragraph

The new words sit after "No card carries a path…" and before the paragraph on the plannotator session, since they continue what a card may carry. The session paragraph's "The link is no artifact: leave the card's artifacts empty." becomes "The link is no artifact." so the two paragraphs do not disagree; "The link is no artifact" stays as `cards_say` pins it.

### The upload is spelled out

An agent cannot see the picture it posts, so the brief names the whole act: `upload: true` on the artifact, the URL the post's result gives for it, and the file put there with its content type. It gives the `curl` form so no agent invents one, and says the file's name is the artifact's `ref`, never its path, since no card carries a path.

### The words a reader needs, not the history

The discipline says what to do and the one reason a reader needs (a `path` shows only the path; a file or HTML shows nothing). The dates and the tests stay in record 0005 and `briefs.9`.

## Risks / Trade-offs

- [The result's field for the upload URL and the method it takes are known from the operator's test, not from Pending You's reference] → the brief says "the upload URL the post returns for it" without naming the field, and the *Proof in dev* list checks the method on a real card.
- [Briefs reach a running agent only at its next fresh start] → as every brief change; nothing to do.

## Proof in dev

Once the bolt has landed and every host has pulled, with the user watching the card in Pending You:

1. A conductor or the planner, started fresh, posts a test card under its own key with an uploaded `image` artifact as its brief now says. The user sees the picture on the card, not a path. If the post's result names the upload URL in a field the brief's words don't lead an agent to, or the upload takes a method other than PUT, the brief's words are a defect: a fix on the bolt.
2. The same card, or a second, carries a `code` artifact of lang `markdown`. The user sees it rendered.
3. The card is closed with its outcome.

## Task notes

### 1.1

In `cards_how` (`plugin/lib/crew.py`), after the paragraph that ends "the link is how the user reaches it.", add a paragraph to this effect, kept in the discipline's voice:

> A card carries an artifact only for a picture it needs or a document's substance it shows, so the user sees each as it is. An image, a screenshot or a page image, is an artifact of kind `image` with `upload: true`, the file's name as its ref; the post returns an upload URL for it, and you put the file there with its content type, `curl -fsS -X PUT -H "Content-Type: image/png" --data-binary @<file> "<url>"` for a PNG. Never attach an image as kind `path`: the user sees only the path. A document's substance beyond the card's words is inline Markdown, an artifact of kind `code` with lang `markdown` and the text as its lines, never an uploaded file and never HTML, which Pending You shows as nothing or refuses. The whole document is reached through the card's plannotator link, never attached.

In the session paragraph, "The link is no artifact: leave the card's artifacts empty." becomes "The link is no artifact."

### 1.2

In `cards_say` (`tests/t-briefs.sh`), add `has` phrases for "kind \`image\` with \`upload: true\`", "with its content type", "Never attach an image as kind \`path\`", "kind \`code\` with lang \`markdown\`", "never an uploaded file and never HTML" and "reached through the card's plannotator link", and `lacks "$out" "leave the card's artifacts empty"`. Mind the shell quoting of the backticks. `cards_say` runs for both the conductor's and the planner's brief. Run `tests/suite t-briefs`.
