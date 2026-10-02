# A write to an active bolt by anyone other than its conductor sends that conductor the commit's subject.
. "$TESTS/lib.sh"
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew plan init WilldanGroup/willdan-blueprints wldn >/dev/null
export CREW_LABEL=wldn
CREW_AGENT=wldn-planner crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
CREW_AGENT=wldn-planner crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
CREW_AGENT=wldn-planner crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit >/dev/null
CREW_AGENT=wldn-dispatch-chuck-herdr-alpha crew bolt give swb-1 tenant-environments >/dev/null 2>&1
CREW_AGENT=wldn-dispatch-chuck-herdr-alpha crew bolt give swb-2 console-pages >/dev/null 2>&1
for team in swb-1 swb-2; do  # the conductors, up in the stub herdr on the box
  p=$(as chuck-herdr-alpha herdr --session wldn-1 workspace create --cwd / --label $team | jq -r .result.root_pane.pane_id)
  as chuck-herdr-alpha herdr --session wldn-1 stub agent "$p" $team-conductor
done
prompts() { grep "^chuck-herdr-alpha wldn-1 agent prompt $1-conductor " "$CREW_TEST_LOG" || true; }  # what the stub herdr received

: > "$CREW_TEST_LOG"
CREW_AGENT=wldn-planner crew unit add the-deploy-names-its-host-tenant "The deploy writes the host tenant." --bolt tenant-environments >/dev/null
eq "$(prompts swb-1)" "chuck-herdr-alpha wldn-1 agent prompt swb-1-conductor 'plan(tenant-environments): add the-deploy-names-its-host-tenant (wldn-planner)'"
eq "$(prompts swb-2)" ""
ok "the planner adds a unit to swb-1's bolt, and swb-1's conductor receives the commit's subject"

: > "$CREW_TEST_LOG"
CREW_AGENT=swb-1-conductor crew unit add a-tenant-creates-its-environments "A tenant creates them." --bolt tenant-environments >/dev/null
eq "$(prompts swb-1)" ""
ok "the conductor's own write sends it nothing"

: > "$CREW_TEST_LOG"
CREW_AGENT=wldn-planner crew unit add zone-one "Zone one." --bolt apex-zones >/dev/null
eq "$(grep -c ' wldn-1 agent prompt ' "$CREW_TEST_LOG" || true)" "0"
ok "a write to a bolt no team holds tells no one"

: > "$CREW_TEST_LOG"
CREW_AGENT=wldn-planner crew unit move a-tenant-creates-its-environments console-pages >/dev/null
has "$(prompts swb-1)" "plan(console-pages): move a-tenant-creates-its-environments from tenant-environments (wldn-planner)"
has "$(prompts swb-2)" "plan(console-pages): move a-tenant-creates-its-environments from tenant-environments (wldn-planner)"
ok "a move between two teams' bolts tells both conductors"
