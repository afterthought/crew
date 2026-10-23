## ADDED Requirements

### Requirement: A landing's pull request is a draft whenever the user's word does not stand
In a kit whose sluice policy at main takes pull requests into main, crew SHALL leave the pull request a bolt's landing opened from `bolt/<bolt>` into main a draft, which sluice never takes into main's queue, whenever the user's word to land does not stand for the bolt's head, so that no merge into the bolt lands it by itself. crew SHALL mark it a draft when `crew bolt submit` ends with the bolt not on main, before it answers, naming its link and saying the next `crew bolt submit` on the user's word makes it live again; when a fix starts on the bolt, as the landing card is held for the fix; and before any unit's, chore's or fix's merge into the bolt starts, which SHALL NOT start when crew cannot read or mark it.

#### Scenario: A refused landing leaves its pull request a draft
- **WHEN** `crew bolt submit` runs on a bolt whose kit takes pull requests into main and sluice refuses it as conflicting with main
- **THEN** nothing lands, the bolt's pull request into main is a draft, and the command's words name its link, say it is a draft, and say the next `crew bolt submit` on the user's word makes it live again

#### Scenario: A failed landing leaves its pull request a draft
- **WHEN** `crew bolt submit` runs and main's checks fail on the bolt
- **THEN** nothing lands and the bolt's pull request into main is a draft

#### Scenario: A landing that lands marks nothing
- **WHEN** `crew bolt submit` runs and the bolt lands on main
- **THEN** no pull request is marked a draft, and the command's words are those of a landing

#### Scenario: A fix's start holds the pull request with the card
- **WHEN** a fix starts on a bolt whose landing was refused and whose pull request into main is ready for review
- **THEN** the pull request is a draft and the bolt's landing card is withdrawn as held for the fix

#### Scenario: A merge into the bolt does not land it
- **WHEN** a unit's, chore's or fix's merge into a bolt starts while the bolt's pull request into main is ready for review
- **THEN** the pull request is a draft before the merge starts, so the merge's move of `bolt/<bolt>` submits nothing to main

#### Scenario: A merge that can't hold the pull request does not start
- **WHEN** a merge into a bolt starts in a kit that takes pull requests and `gh` cannot list the kit's pull requests or cannot mark the bolt's one a draft
- **THEN** the merge does not start, and crew names the pull request, or the repository it could not list, with `gh`'s words

### Requirement: The next landing on the user's word readies the pull request
`crew bolt submit` SHALL mark the bolt's draft pull request into main ready for review before it submits, so sluice takes it at the head the bolt then has, and SHALL refuse, submitting nothing, when it cannot.

#### Scenario: The next landing readies the pull request
- **WHEN** the user's word to land a bolt whose pull request into main is a draft reaches main-level ops and it runs `crew bolt submit`
- **THEN** the pull request is marked ready for review before the submission, and the landing goes on as any landing does

#### Scenario: A pull request crew can't ready submits nothing
- **WHEN** `crew bolt submit` runs and `gh` cannot mark the bolt's draft pull request ready for review
- **THEN** nothing is submitted, and crew names the pull request with `gh`'s words

### Requirement: A kit that takes no pull requests is asked nothing of GitHub
crew SHALL read or mark no pull request on GitHub for a kit whose sluice policy at main has no pull requests table for main.

#### Scenario: A kit that takes no pull requests is asked nothing
- **WHEN** a landing, a fix's start or a merge runs in a kit whose sluice policy at main has no pull requests table for main
- **THEN** crew runs no `gh` command, and the landing, fix or merge goes on as before
