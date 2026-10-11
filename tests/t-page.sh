# crew page: a flywheel's lineage page, drawn from its run record alone. Its objects are the signals, agenda items,
# proposals, units and bolts the entries name, each linked to what the same entry names in the next column; each
# object's history is what crew trace prints for it.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
crew state init wldn >/dev/null
export CREW_LABEL=wldn
emit() { as mac-studio python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@" >/dev/null; }
# the page's data, as crew page draws it, printed rather than written
pagedata() { as "$HOST" python3 "$CREW/plugin/lib/page.py" page wldn --json "$@"; }
j() { jq -r "$1" <<<"$json"; }
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

json=$(pagedata --since "$(date -u -v+1d +%F 2>/dev/null || date -u -d tomorrow +%F)") || fail "crew page --json --since: $json"
eq "$(j '.nodes | length') $(j '.entries | length') $(j '.edges | length')" "0 0 0"
json=$(pagedata --since "$start") || fail "crew page --json --since $start: $json"
eq "$(j '.nodes | length') $(j '.edges | length') $(j '[.entries[] | select(.Act != "state.init")] | length')" "8 5 8"
ok "--since keeps the entries from then on, and the nodes, lines and histories they make"
