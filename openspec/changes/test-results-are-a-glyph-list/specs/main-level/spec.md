## ADDED Requirements

### Requirement: Main-level ops reports results as one glyph per line
Whenever the main-level ops reports the results of a landing's checks, of main's deploy or of any test or proof it ran, it SHALL list them first, before any prose, one bullet per suite, check or proof: ✅ passed, with its counts where the tool gave them; ❌ failed, with how many failed and one line on why; ⏳ not yet run, or still running. It SHALL NOT state a result only in a sentence, nor fold several into one bullet.

#### Scenario: A landing whose gate is still running
- **WHEN** the main-level ops reports a landing while the merge's checks still run
- **THEN** its message opens with a ⏳ bullet for those checks, and says the bolt has not landed yet

#### Scenario: A landing that went through
- **WHEN** the merge's checks passed and main was deployed and found healthy
- **THEN** its message opens with a ✅ bullet for the checks, with their counts, and one for main's deploy, before it says the bolt is closed
