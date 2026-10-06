# "<team> units": made with the first unit or fix in flight, one tiled pane per slot, closed when the last one
# frees. crew status lists the standing roles and each slot's unit and stage. Two teams share a session.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
for u in a b c; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew unit add p "Unit p." --bolt console-pages >/dev/null
crew bolt give swb-1 tenant-environments >/dev/null 2>&1; crew bolt give swb-2 console-pages >/dev/null 2>&1
crew up swb-1 >/dev/null; crew up swb-2 >/dev/null
export CREW_AGENT=swb-1-conductor
labels() { herdr_state $box wldn-1 '[.workspaces[].label] | join(",")'; }
eq "$(labels)" "swb-1,swb-2"

crew unit run a construct >/dev/null
eq "$(labels)" "swb-1,swb-2,swb-1 units"
ws=$(herdr_state $box wldn-1 '.workspaces | to_entries[] | select(.value.label == "swb-1 units") | .key')
in_ws() { herdr_state $box wldn-1 "[.panes | to_entries[] | select(.value.workspace == \"$ws\") | .key] | join(\" \")"; }
p1=$(in_ws)
crew fix swb-1 edge-sign-in "It answers an object." >/dev/null
crew unit run b construct >/dev/null
crew unit run c construct >/dev/null
splits=$(grep "^$box wldn-1 pane split $ws:" "$CREW_TEST_LOG" | awk '{print $5, $7}')
set -- $(in_ws)
eq "$#" "4"
eq "$splits" "$p1 right"$'\n'"$2 down"$'\n'"$3 right"
ok "the first unit in flight makes the units workspace; each next slot halves the newest pane, right then down"

expect_ok crew status swb-1
for want in "swb-1-conductor" "swb-1-ops" "a  construct" "fix/tenant-environments/edge-sign-in  fix" "b  construct" "c  construct"; do has "$out" "$want"; done
change "$kd/places/b" b 1 4; commit_all "$kd/places/b" "feat(b): one task"
expect_ok crew status swb-1; has "$out" "b  code 1/4"
ok "status lists the standing roles and each slot's unit and stage"

CREW_AGENT=swb-2-conductor crew unit run p construct >/dev/null
eq "$(labels)" "swb-1,swb-2,swb-1 units,swb-2 units"
ok "two teams in one session each have their workspace and units workspace"

for u in a b c; do CREW_AGENT= crew unit drop $u "not wanted" >/dev/null; done
eq "$(labels)" "swb-1,swb-2,swb-1 units,swb-2 units"
eq "$(in_ws | wc -w | tr -d ' ')" "1"
echo fixed > "$kd/places/fix-tenant-environments--edge-sign-in/x"; commit_all "$kd/places/fix-tenant-environments--edge-sign-in" "fix: it answers a string"
git -C "$kd/bolts/tenant-environments" merge -q --ff-only fix/tenant-environments/edge-sign-in
expect_ok crew status swb-1; has "$out" "fix/tenant-environments/edge-sign-in has merged into its bolt"
eq "$(labels)" "swb-1,swb-2,swb-2 units"
grep -q "^$box wldn-1 workspace close $ws" "$CREW_TEST_LOG" || fail "the units workspace was not closed"
ok "the units workspace closes when its last slot frees"
