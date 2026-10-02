# The write path: each write fetches plan/<label>, applies itself to the tip, checks, commits through a
# temporary index and pushes without force. A push refused because another host wrote first is applied again
# on the new tip, and a write whose subject the other one removed is refused, naming that commit.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew plan init WilldanGroup/willdan-blueprints wldn >/dev/null
export CREW_AGENT=wldn-planner
crew bolt new tenant-environments "A tenant holds environments of its own." --repo switchboard-kit >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew unit add the-deploy-names-its-host-tenant "The deploy writes the host tenant." --bolt tenant-environments >/dev/null
crew unit add a-tenant-creates-its-environments "A tenant creates environments by name." --bolt tenant-environments >/dev/null
before=$(git --git-dir "$wb" rev-parse plan/wldn)

# The planner on mac-studio moves a unit while swb-1's conductor on the box narrows the same unit's intent.
race WilldanGroup/willdan-blueprints chuck-herdr-alpha swb-1-conductor \
  unit split the-deploy-names-its-host-tenant "The deploy writes the host tenant's connection." --into the-deploy-writes-its-environment "The deploy writes its one environment."
expect_ok crew unit move the-deploy-names-its-host-tenant console-pages
[[ ! -f $T/race ]] || fail "the competing write never ran"
has "$(cat "$T/race.log")" "split the-deploy-names-its-host-tenant"
log=$(git --git-dir "$wb" log --format='%s' "$before"..plan/wldn)
eq "$log" $'plan(console-pages): move the-deploy-names-its-host-tenant from tenant-environments (wldn-planner)\nplan(tenant-environments): split the-deploy-names-its-host-tenant into the-deploy-writes-its-environment (swb-1-conductor)'
eq "$(git --git-dir "$wb" rev-list --merges plan/wldn | wc -l | tr -d ' ')" "0"
git --git-dir "$wb" show plan/wldn:plan.rec > "$T/plan.rec"; recfix --check "$T/plan.rec" || fail "the result fails recfix"
eq "$(recsel -t Unit -e "Unit = 'the-deploy-names-its-host-tenant'" -P Bolt "$T/plan.rec")" "console-pages"
eq "$(recsel -t Unit -e "Unit = 'the-deploy-names-its-host-tenant'" -P Intent "$T/plan.rec")" "The deploy writes the host tenant's connection."
eq "$(recsel -t Unit -e "Unit = 'the-deploy-writes-its-environment'" -P Bolt "$T/plan.rec")" "tenant-environments"
ok "two racing writes both land, one after the other, and neither is merged"

# The planner moves a unit the conductor has just dropped.
race WilldanGroup/willdan-blueprints chuck-herdr-alpha swb-1-conductor unit drop a-tenant-creates-its-environments "the portal does it"
expect_fail "no unit a-tenant-creates-its-environments in plan/wldn of WilldanGroup/willdan-blueprints" crew unit move a-tenant-creates-its-environments console-pages
dropped=$(git --git-dir "$wb" log -1 --format='%h %s' plan/wldn)
has "$dropped" "drop a-tenant-creates-its-environments (swb-1-conductor)"
has "$out" "$dropped removed it"
eq "$(git --git-dir "$wb" log -1 --format=%b plan/wldn)" "the portal does it"
ok "a write whose unit was dropped is refused, naming the commit that dropped it"

# Nothing was written through a working tree: crew's cache of the repo is bare.
eq "$(git -C "$(home_of mac-studio)/.cache/crew/git/WilldanGroup/willdan-blueprints.git" rev-parse --is-bare-repository)" "true"
