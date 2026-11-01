## ADDED Requirements

### Requirement: An ask and a turn are entries
Each ask crew writes SHALL be one `ask` entry in the asked partition's record, naming the role's run and the record the ask names, with the length of its words and never their text. A run's start SHALL be one `turn.begin` entry naming the run and how many it took, and its end one `turn.end` entry. `crew trace agent/<label>-<role>` SHALL list them with the rest of the role's entries.

#### Scenario: A tell that is an ask
- **WHEN** `crew tell madswan-planner "<forty characters>"` is written as an ask
- **THEN** madswan's record holds an `ask` entry on `agent/madswan-planner` with `Chars: 40` and not the text

#### Scenario: A turn traced
- **WHEN** the planner's run took two asks and ended
- **THEN** `crew trace agent/madswan-planner` lists the two asks, the `turn.begin` taking two and the `turn.end`
