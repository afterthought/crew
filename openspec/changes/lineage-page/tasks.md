# Tasks

## 1. The data

- [ ] 1.1 `record.py` exports the lineage walk `crew trace` uses as one function, and `crew trace` calls it. Verify the existing trace tests pass unchanged.
- [ ] 1.2 `plugin/lib/page.py` builds nodes, edges and per-node histories from the gathered entries as design.md describes, for the kinds `signals`, `agenda`, `proposal`, `unit` and `bolt`, with `--since`. Verify with a fixture run record of a signal routed to an item, proposed, approved into a bolt and landed: five nodes, four edges, and an unmoved signal as a node with no edge.
- [ ] 1.3 For every node of the fixture, the page's history equals `crew trace <object>`'s entries in order. Verify with a test that compares them for every node.
- [ ] 1.4 Labels and present status from the flywheel's state (assertion, subject and lane, case and state, intent and stage, goal and team), a node the state no longer holds labelled from its entries, and unit stages left blank when a host does not answer. Verify against the state test remote, with a landed bolt whose records are gone from the plan.

## 2. The page

- [ ] 2.1 The template: one HTML file with a JSON data block, inline CSS and inline JavaScript; five columns with their counts; lines between linked nodes; selection that marks ancestors and descendants and lists the history with time, act, who, host, commit, refusal and `zoe <session>`; the timeline; the hide-closed filter and the name box; light and dark. Verify by opening a page made from the fixture with the network off: it renders, a selection marks the whole chain, and the browser's console shows no request and no error.
- [ ] 2.2 `crew page <label> [--out <file>] [--since <time>]` writes the file under `~/.local/state/crew/<label>/` by default and prints its path and the header line: the time made, the branch's commit, hosts that did not answer. An empty run record still writes a page saying so. Verify with the stubs, including a simulated host made unreachable.
- [ ] 2.3 Document `crew page` in `README.md` (in "Seeing what happened"), `plugin/skills/crew/SKILL.md` and the usage header. Verify every command in the README appears in `crew`'s usage.

## 3. The operator agent

- [ ] 3.1 `plugin/roles/operator.md`: on request, make the page with `crew page <label>` and open it in terminal-browser beside the pane, saying as of when it is and any host it could not read. Verify the brief prints for the `wldn` fixture with no unfilled token.

## 4. Proof on real work

- [ ] 4.1 After the flow has run on wldn (`curation-and-agenda`'s proof), ask the operator agent on mac-studio to show the flow. Verify the page opens beside its pane; the proof's two signals each show a line through an item to a unit; selecting each unit lists the same entries `crew trace unit/<unit>` prints; and the header names the time and the commit.
- [ ] 4.2 Make the page with the box unreachable from the Mac. Verify it is written, complete as far as the box had carried, and names the box.
