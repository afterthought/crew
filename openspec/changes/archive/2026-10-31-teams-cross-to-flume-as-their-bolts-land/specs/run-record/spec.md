## ADDED Requirements

### Requirement: A team's crossing is an entry
When a crossed team's conductor and ops have both been ended for its crossing, crew SHALL record one `team.cross` entry on `team/<team>`, naming the stream its work now runs in, so `crew trace team/<team>` reads when it crossed.

#### Scenario: Traced
- **WHEN** crw-4's conductor and ops are ended at their stops after its last bolt of today's path lands
- **THEN** one `team.cross` entry on `team/crw-4` names stream `madswan`, and `crew trace team/crw-4` shows it after `x`'s landing
