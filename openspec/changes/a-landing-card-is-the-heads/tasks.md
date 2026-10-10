# Tasks

## 1. The landing key carries the bolt's head

- [x] 1.1 crew's read of a host's kits gives each bolt's head commit beside its time (design.md, Task notes 1.1).
- [x] 1.2 The rail keys a bolt ready to land `land/<bolt>/<head>`, offers no land row when the head can't be read, and lists a landing card under an older head as a card whose row is gone (design.md, Task notes 1.2). Verify `tests/suite t-rail t-bolt` ends with "0 failed".
- [x] 1.3 crew's card hook and `crew card` read a landing key as `land/<bolt>/<head>`, a bare `land/<bolt>` is no row's key, and `crew card session` still refuses every landing key (design.md, Task notes 1.3). Verify `tests/suite t-cards t-card-session` ends with "0 failed".

## 2. The briefs and the docs

- [x] 2.1 The card discipline says a row whose key changes gets its old card closed with what changed and a new card under the new key, and the conductor's brief keys its landing card `land/<bolt>/<head>` and closes an open one when a fix moves the bolt (design.md, Task notes 2.1). Verify `tests/suite t-briefs t-roles` ends with "0 failed".
- [ ] 2.2 README names the landing key with the bolt's head and says a bolt proven again on a new head gets a new card (design.md, Task notes 2.2). Verify `tests/suite t-docs` ends with "0 failed", then `tests/suite --affected` ends with "0 failed".

## Workflow follow-up

- Archive after `the-rail-is-answered-through-cards` and `a-card-links-a-plannotator-session`, whose specs this change's deltas modify.
