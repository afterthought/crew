# crew page: a flywheel's lineage page, drawn from its run record alone. Its objects are the signals, agenda items,
# proposals, units and bolts the entries name, each linked to what the same entry names in the next column, an entry
# on a proposal linking only the proposal to what it names; each object's history is what crew trace prints for it.
# Labels and present status come from the flywheel's state at the commit the entries were read at; one the state no
# longer holds is labelled from its entries, and a unit whose host does not answer has no stage. The page also holds the partition's board, as crew board reads it at the same commit,
# with a host that does not answer in its attention, and opens on it: four lanes in the flywheel mockup's forms, for a
# desktop and a phone, light and dark, with nothing loaded from outside the file; a header naming every partition, the
# others linked to their pages beside it; and the partition's teams to narrow it to.
# Reads: plugin/lib/board.py plugin/lib/page.py plugin/lib/page.html plugin/lib/sites.py
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
k=$(kit chuck-herdr-alpha willdan switchboard-kit)
crew state init wldn >/dev/null
box=chuck-herdr-alpha
ws=$(remote WilldanGroup/crew-state)
export CREW_LABEL=wldn
emit() { as mac-studio python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@" >/dev/null; }
# the page's data, as crew page draws it, printed rather than written
pagedata() { as "$HOST" python3 "$CREW/plugin/lib/page.py" page wldn --json "$@"; }
j() { jq -r "$@" <<<"$json"; }
node() { j --arg n "$1" ".nodes[] | select(.id == \$n) | $2"; }
json=$(pagedata) || fail "crew page --json: $json"
before=$(j '.entries | length')  # crew state init's own
start=$(date -u +%Y-%m-%dT%H:%M:%SZ)

emit --act capture --on signals/a --why "signals(a): capture a"
emit --act signal.move --on signals/a --on agenda/8 --why "signals(a): route to agenda/8"
emit --act plan.propose --on proposal/3 --on unit/u --on bolt/b --why "plan(proposal 3): propose"
emit --act unit.add --on unit/u --on bolt/b --from agenda/8 --from proposal/3 --why "plan(b): add u"
emit --act bolt.land --on bolt/b --on unit/u --why "plan(b): land the bolt"
emit --act capture --on signals/z --why "signals(z): capture z"
emit --act tell --on agent/wldn-planner --field Chars=5 --why "tell wldn-planner"

json=$(pagedata) || fail "crew page --json: $json"
eq "$(j '[.nodes[].id] | join(" ")')" "signals/a signals/z agenda/8 proposal/3 unit/u bolt/b"
eq "$(j '[.edges[] | "\(.from)>\(.to)"] | sort | join(" ")')" "agenda/8>proposal/3 proposal/3>unit/u signals/a>agenda/8 unit/u>bolt/b"
eq "$(j '[.edges[] | select(.from == "signals/z" or .to == "signals/z")] | length')" "0"
eq "$(j '.entries | length')" "$((before + 7))"
eq "$(j '[.entries[] | select(.Act == "tell")] | length')" "1"
eq "$(j '[.edges[] | select(.from == "proposal/3") | .entries | length] | first')" "2"
eq "$(j '[.histories | keys[]] | sort | join(" ")')" "agenda/8 bolt/b proposal/3 signals/a signals/z unit/u"
ok "five linked nodes in the flow's order, four edges each kept once with the entries that made it, and an unmoved signal with none"

emit --act unit.move --on unit/v --on bolt/c --from bolt/b --why "plan(c): move v from b"
json=$(pagedata) || fail "crew page --json: $json"
eq "$(j '[.edges[] | select(.from == "unit/v" or .to == "unit/v") | "\(.from)>\(.to)"] | join(" ")')" "unit/v>bolt/c"
ok "a unit's move draws a line to the bolt it moved to, none from the bolt it left"

for act in plan.propose plan.approve; do
  emit --act "$act" --on proposal/4 --on unit/x --on bolt/e --on unit/y --on bolt/f --why "plan(proposal 4): ${act#plan.}"
done
emit --act unit.add --on unit/x --on bolt/e --from proposal/4 --why "plan(e): add x"
emit --act unit.add --on unit/y --on bolt/f --from proposal/4 --why "plan(f): add y"
json=$(pagedata) || fail "crew page --json: $json"
eq "$(j '[.edges[] | select(.to | startswith("bolt/")) | select(.from == "unit/x" or .from == "unit/y") | "\(.from)>\(.to)"] | sort | join(" ")')" "unit/x>bolt/e unit/y>bolt/f"
eq "$(j '[.edges[] | select(.from == "proposal/4") | "\(.to):\(.entries | length)"] | sort | join(" ")')" "unit/x:3 unit/y:3"
ok "a proposal's entries join the proposal to each unit it names, and each unit only to the bolt its own entry puts it in"

for n in $(j '.nodes[].id'); do
  expect_ok crew trace "$n"
  eq "$(j --arg n "$n" '.histories[$n][] as $i | .entries[$i] | "\(.At[5:10]) \(.At[11:19]) \(.Act)"')" "$(awk '{print $1, $2, $3}' <<<"$out")"
done
eq "$(j '[.histories["unit/u"][] as $i | .entries[$i].Act] | sort | join(" ")')" "bolt.land plan.propose signal.move unit.add unit.move"
ok "for every node, the page's history is the entries crew trace prints for it, in the same order"

json=$(pagedata --since "$(date -u -v+1d +%F 2>/dev/null || date -u -d tomorrow +%F)") || fail "crew page --json --since: $json"
eq "$(j '.nodes | length') $(j '.entries | length') $(j '.edges | length')" "0 0 0"
json=$(pagedata --since "$start") || fail "crew page --json --since $start: $json"
eq "$(j '.nodes | length') $(j '.edges | length') $(j '[.entries[] | select(.Act != "state.init")] | length')" "13 9 12"
ok "--since keeps the entries from then on, and the nodes, lines and histories they make"

# The state: a bolt swb-1 holds with unit a in code, unit c from a routed signal, and unit d dropped; a proposal; and
# agenda item 8, which the fixture's signal.move names.
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew unit add a "Unit a." --bolt tenant-environments >/dev/null
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
pa=$(place "$k" tenant-environments a); change "$pa" a 1 2; commit_all "$pa" "feat(a): task 1"
sig=$(crew signal plans-are-checked "Plans should be
checked before they run." | sed -n 's/^signal \([^: ]*\)[: ].*/\1/p')
crew unit add c "Unit c." --bolt tenant-environments --signal "$sig" >/dev/null
crew unit add d "Unit d." --bolt tenant-environments >/dev/null
crew unit drop d "Not needed." >/dev/null
printf '%s\n' 'Case: The console gets a bolt of its own.' 'Do: bolt new console-two "The console, again." --repo switchboard-kit' > "$T/proposal.rec"
crew plan propose "$T/proposal.rec" >/dev/null
st=$T/state; git clone -q -b wldn/main "$ws" "$st"
printf '%%rec: Item\n%%key: Item\n\nItem: 8\nLane: plan\nSubject: Plans are checked.\nState: open\nOpened: 2026-10-06\nBy: wldn-curator\n' > "$st/agenda.rec"
commit_all "$st" "agenda: item 8"; git -C "$st" push -q origin wldn/main

json=$(pagedata) || fail "crew page --json: $json"
eq "$(j .made.commit)" "$(git --git-dir "$ws" rev-parse wldn/main)"
eq "$(j '.made.unreachable | length')" "0"
eq "$(node unit/a '[.label, .stage, .status] | join("|")')" "Unit a.|code|flight"
eq "$(node unit/c '[.label, .stage, .status] | join("|")')" "Unit c.|ready|open"
eq "$(node bolt/tenant-environments '[.label, .team, .status] | join("|")')" "Tenants hold environments.|swb-1|flight"
eq "$(node "signals/$sig" '[.label, .status, (.facts | join(" "))] | join("|")')" "Plans should be checked before they run.|done|route"
eq "$(node proposal/1 '[.label, .status] | join("|")')" "The console gets a bolt of its own.|open"
eq "$(node agenda/8 '[.label, .status, (.facts | join(" "))] | join("|")')" "Plans are checked.|open|plan open"
ok "each node carries its label and present status from the state: a unit's intent and stage, a bolt's goal and team, a signal's assertion and move, a proposal's case, an item's subject"

eq "$(node unit/u '[.label, .status, .gone] | join("|")')" "plan(b): land the bolt|done|true"
eq "$(node bolt/b '[.label, .status, .gone] | join("|")')" "plan(b): land the bolt|done|true"
eq "$(node unit/d '[.label, .status] | join("|")')" "plan(tenant-environments): drop d|dropped"
eq "$(node proposal/3 '.status')" "null"
ok "a landed bolt and its units, gone from the plan, and a dropped unit are labelled from their newest entry, and a proposal the state never held has no status"

echo "$box" > "$T/down"
json=$(pagedata) || fail "crew page --json with $box down: $json"
rm "$T/down"
eq "$(node unit/a '[.label, .stage, .status] | map(. // "-") | join("|")')" "Unit a.|-|-"
eq "$(node bolt/tenant-environments '.status')" "null"
has "$(j '.made.unreachable | keys | join(" ")')" "$box"
ok "a unit whose host does not answer has no stage, and the host is named"

# The file: the data in its one block, as JSON, and nothing loaded from outside it; typed text stays in the data.
crew signal ends-the-block "Ends </script><b>here</b> & more." >/dev/null
expect_ok crew page wldn --out "$T/page.html"
block() { python3 -c 'import re, sys; t = open(sys.argv[1]).read(); m = re.findall(r"<script type=\"application/json\" id=\"data\">(.*?)</script>", t, re.S); print(m[0] if len(m) == 1 else "")' "$1"; }
outside() { python3 -c 'import re, sys; print(re.sub(r"(<script type=\"application/json\" id=\"data\">).*?(</script>)", r"\1\2", open(sys.argv[1]).read(), flags=re.S))' "$1"; }
json=$(block "$T/page.html"); [[ -n $json ]] || fail "no data block in the page"
eq "$(j '[.nodes[].id] | join(" ")')" "$(pagedata | jq -r '[.nodes[].id] | join(" ")')"
has "$(j '[.nodes[].label] | join("|")')" "Ends </script><b>here</b> & more."
lacks "$(cat "$T/page.html")" "</script><b>"
rest=$(outside "$T/page.html")
for no in "<script src" "<link" "@import" "http://" "https://" "src=" "url("; do lacks "$rest" "$no"; done
lacks "$(cat "$T/page.html")" "{{DATA}}"
has "$rest" 'id="hide"'; has "$rest" 'id="find"'; has "$rest" 'id="bars"'; has "$rest" "prefers-color-scheme: dark"
has "$rest" "Nothing has been recorded"
ok "the page holds its data in one block, escaped so typed text cannot end it, and loads nothing from outside the file"

has "$rest" '<body data-view="board">'
has "$rest" "@media (max-width:759px)"; has "$rest" "prefers-color-scheme:dark"; has "$rest" ':root[data-theme="dark"]'
for lane in Inception "Bolt plan" Construction Operation; do has "$rest" "aria-label=\"$lane\""; done
has "$rest" "repeating-linear-gradient"; has "$rest" "design/flywheel-next/mockups/rail-and-board.html"
for form in .quote .sheet .slip .ledger .record .mark.attention .lg-unit.building; do has "$rest" "$form"; done
for sample in atlas plan-decisions books Manrope "JetBrains Mono"; do lacks "$rest" "$sample"; done
lacks "$rest" "innerHTML"
ok "the page opens on the board view: the four lanes in the mockup's forms, a phone layout under 760 px and its dark colours, with none of its sample data or fonts, and no state set as markup"

teams=$(home_of mac-studio)/.config/crew/teams.json
eq "$(grep -o 'href="[^"]*"' <<<"$rest" | sort | tr '\n' ' ')" "$(jq -r '.partitions[].label | select(. != "wldn") | "href=\"../\(.)/page.html\""' "$teams" | sort | tr '\n' ' ')"
lacks "$rest" 'href="../wldn/page.html"'
has "$rest" '<span class="part" aria-current="page">wldn</span>'
eq "$(grep -o 'class="part"[^>]*>[a-z0-9-]*<' <<<"$rest" | sed 's/.*>\(.*\)</\1/' | tr '\n' ' ')" "$(jq -r '.partitions[].label' "$teams" | tr '\n' ' ')"
eq "$(j '[.board.teams[].team] | join(" ")')" "swb-1 swb-2 brd-1 atl-1"
eq "$(j '.board.teams[0] | "\(.team) \(.kit) \(.host)"')" "swb-1 switchboard-kit chuck-herdr-alpha"
has "$rest" 'id="team"'; has "$rest" "history.replaceState"; has "$rest" '"crew-page:" + D.label'
ok "the header names every partition in the teams file's order, its own marked current and each other linked to its page beside this one, and offers the partition's teams to narrow the board to"

# The command: the page written whole where it says, its path and what it was made from printed, nothing appended.
mine=$(home_of mac-studio)/.local/state/crew/wldn
record() { cat "$mine"/runs/*/*.rec; }
before=$(record)
expect_ok crew page wldn
eq "$(sed -n 1p <<<"$out")" "$mine/page.html"
made="^as of [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}Z · wldn/main $(git --git-dir "$ws" rev-parse --short=7 wldn/main)\$"
[[ $(sed -n 2p <<<"$out") =~ $made ]] || fail "expected the header line, got: $(sed -n 2p <<<"$out")"
eq "$(wc -l <<<"$out" | tr -d ' ')" "2"
[[ -f $mine/page.html ]] || fail "no page at $mine/page.html"
eq "$(block "$mine/page.html" | jq -r .made.commit)" "$(git --git-dir "$ws" rev-parse wldn/main)"
eq "$(ls -A "$mine" | grep -c '^\.page')" "0"
eq "$(record)" "$before"
ok "crew page writes the page whole under the partition's state folder, prints its path and as of when and which commit, and appends no entry"

json=$(block "$mine/page.html")
eq "$(j .board.label) $(j .label)" "wldn wldn"
eq "$(j '.board | [has("inception", "bolt_plan", "construction", "operation")] | all')" "true"
eq "$(j '[.board.construction[].bolt] | join(" ")') $(j '[.board.construction[].team] | join(" ")')" "tenant-environments swb-1"
eq "$(j '.partitions | join(" ")')" "$(jq -r '[.partitions[].label] | join(" ")' "$(home_of mac-studio)/.config/crew/teams.json")"
eq "$(j .made.plan)" "$(j .made.commit)"
eq "$(j '.board.attention | length')" "0"
ok "the page holds the partition's board as crew board reads it, the teams file's partitions in order and its own label, its labels read at the commit the board read"

echo "$box" > "$T/down"
expect_ok crew page wldn
rm "$T/down"
has "$(sed -n 3p <<<"$out")" "$box did not answer"
has "$(block "$mine/page.html" | jq -r '.made.unreachable | keys | join(" ")')" "$box"
has "$(block "$mine/page.html" | jq -r '[.board.attention[] | select(.what == "host") | .name] | join(" ")')" "$box"
ok "a host that does not answer is named, in the board's attention too, and the page is still written"

cp "$mine/page.html" "$T/earlier.html"
mv "$ws" "$ws.away"
expect_fail "no page is written: wldn/main of WilldanGroup/crew-state could not be read" crew page wldn
mv "$ws.away" "$ws"
cmp -s "$mine/page.html" "$T/earlier.html" || fail "the earlier page was changed"
expect_fail "no partition 'nope'" crew page nope
expect_fail "--since takes a date" crew page wldn --since yesterday-ish
ok "when the branch cannot be read nothing is written and the branch is named; an unknown partition or time is refused"

blueprints afterthought/blueprints >/dev/null
crew state init swancloud >/dev/null
rm -rf "$(home_of mac-studio)/.local/state/crew/swancloud/runs"
expect_ok crew page swancloud
has "$out" "nothing has been recorded"
json=$(block "$(home_of mac-studio)/.local/state/crew/swancloud/page.html")
eq "$(j '.entries | length') $(j '.nodes | length')" "0 0"
ok "an empty record writes a page saying nothing has been recorded"
