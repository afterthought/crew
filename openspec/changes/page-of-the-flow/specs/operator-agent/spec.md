# Spec Delta

## ADDED Requirements

### Requirement: The operator agent opens the lineage page
On request, the operator agent SHALL make the partition's lineage page with `crew page <label>` and open it in terminal-browser beside its pane. It SHALL say when the page was made and name any host the page could not read.

#### Scenario: Show me the flow
- **WHEN** the user asks the operator agent on mac-studio to show how the week's findings flowed
- **THEN** it runs `crew page wldn`, opens the file beside its pane, and says as of when it is
