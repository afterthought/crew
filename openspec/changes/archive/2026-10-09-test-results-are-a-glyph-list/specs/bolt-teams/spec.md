## ADDED Requirements

### Requirement: A team reports results as one glyph per line
Whenever the conductor, ops, construct, coder or verify reports the results of tests, checks or proofs, it SHALL list them first, before any prose, one bullet per suite, check or proof: ✅ passed, with its counts where the tool gave them; ❌ failed, with how many failed and one line on why; ⏳ not yet run, or still running. It SHALL NOT state a result only in a sentence, nor fold several into one bullet. It SHALL use the same list in a file or a message that carries results.

#### Scenario: A bolt's verification after a merge
- **WHEN** ops reports the bolt's verification and two of its tests failed
- **THEN** its message opens with one ❌ bullet naming the suite, the two failures and one line on why, and only then says what it would do

#### Scenario: Proof in dev
- **WHEN** ops has worked three items of a unit's *Proof in dev* list and the fourth waits on the user
- **THEN** its report opens with one bullet per item, three with ✅ or ❌ and the fourth with ⏳ and what it waits on

#### Scenario: The conductor passes results on
- **WHEN** the conductor tells the user what ops or a verify reported
- **THEN** it shows that agent's list as it is, first, and then says in plain English what it would do about each ❌

#### Scenario: A construct's validation
- **WHEN** a construct agent ends after `openspec validate <unit>` passed
- **THEN** its final message opens with a ✅ bullet for that validation

#### Scenario: Nothing passed in a sentence
- **WHEN** every suite a coder ran passed
- **THEN** its summary still lists each suite with ✅ and its counts, and never says only "the tests all pass"
