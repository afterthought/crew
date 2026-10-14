## ADDED Requirements

### Requirement: crew raises a batch's one card
When `crew review` finds a batch due, it SHALL cut the batch, start its one reading session and raise its one card in the planner's name, keyed `batch/<n>`, as `rail-cards` says a batch's card is; the planner SHALL write nothing of it and post nothing. `crew card wait batch/<n>` SHALL give the planner the notes and close the card.

#### Scenario: A batch due
- **WHEN** the partition's eighth change since batch 6 is constructed and `crew review` runs
- **THEN** batch 7 is cut, its session started, and one card keyed `batch/7` is open in the planner's name

## REMOVED Requirements

### Requirement: The planner posts a batch as one card
**Reason**: crew raises it when the batch is due; the planner reads the notes (record 0031).
