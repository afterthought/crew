# Tasks

## 1. The card discipline says how a picture and a document reach the user

- [x] 1.1 The card discipline in `cards_how` says an image a card needs is an `image` artifact posted with `upload: true` and the file put to the returned upload URL with its content type, never a `path`; that a document's substance on a card is inline Markdown, a `code` artifact of lang `markdown`, never an uploaded file or HTML; that the whole document is reached through the plannotator link; and it no longer says to leave the artifacts empty (design: *One paragraph in the discipline*, *The upload is spelled out*; Task notes 1.1; `briefs.9`).
- [ ] 1.2 `tests/t-briefs.sh` pins those words in the planner's and the conductor's briefs and checks the old "leave the card's artifacts empty" is gone, and `tests/suite t-briefs` ends with "0 failed" (Task notes 1.2; `tests.6`).
