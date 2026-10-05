# The write path: each write fetches the flywheel's branch <label>/main, applies itself to the tip, checks, commits through a
# temporary index and pushes without force. A push refused because another host wrote first is applied again
# on the new tip, and a write whose subject the other one removed is refused, naming that commit.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
export CREW_AGENT=wldn-planner
crew bolt new tenant-environments "A tenant holds environments of its own." --repo switchboard-kit >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew unit add the-deploy-names-its-host-tenant "The deploy writes the host tenant." --bolt tenant-environments >/dev/null
crew unit add a-tenant-creates-its-environments "A tenant creates environments by name." --bolt tenant-environments >/dev/null
before=$(git --git-dir "$ws" rev-parse wldn/main)

# The planner on mac-studio moves a unit while swb-1's conductor on the box narrows the same unit's intent.
race WilldanGroup/crew-state chuck-herdr-alpha swb-1-conductor \
  unit split the-deploy-names-its-host-tenant "The deploy writes the host tenant's connection." --into the-deploy-writes-its-environment "The deploy writes its one environment."
expect_ok crew unit move the-deploy-names-its-host-tenant console-pages
[[ ! -f $T/race ]] || fail "the competing write never ran"
has "$(cat "$T/race.log")" "split the-deploy-names-its-host-tenant"
log=$(git --git-dir "$ws" log --format='%s' "$before"..wldn/main)
eq "$log" $'plan(console-pages): move the-deploy-names-its-host-tenant from tenant-environments (wldn-planner)\nplan(tenant-environments): split the-deploy-names-its-host-tenant into the-deploy-writes-its-environment (swb-1-conductor)'
eq "$(git --git-dir "$ws" rev-list --merges wldn/main | wc -l | tr -d ' ')" "0"
git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recfix --check "$T/plan.rec" || fail "the result fails recfix"
eq "$(recsel -t Unit -e "Unit = 'the-deploy-names-its-host-tenant'" -P Bolt "$T/plan.rec")" "console-pages"
eq "$(recsel -t Unit -e "Unit = 'the-deploy-names-its-host-tenant'" -P Intent "$T/plan.rec")" "The deploy writes the host tenant's connection."
eq "$(recsel -t Unit -e "Unit = 'the-deploy-writes-its-environment'" -P Bolt "$T/plan.rec")" "tenant-environments"
ok "two racing writes both land, one after the other, and neither is merged"

# The planner moves a unit the conductor has just dropped.
race WilldanGroup/crew-state chuck-herdr-alpha swb-1-conductor unit drop a-tenant-creates-its-environments "the portal does it"
expect_fail "no unit a-tenant-creates-its-environments in wldn/main of WilldanGroup/crew-state" crew unit move a-tenant-creates-its-environments console-pages
dropped=$(git --git-dir "$ws" log -1 --format='%h %s' wldn/main)
has "$dropped" "drop a-tenant-creates-its-environments (swb-1-conductor)"
has "$out" "$dropped removed it"
eq "$(git --git-dir "$ws" log -1 --format=%b wldn/main | head -1)" "the portal does it"
ok "a write whose unit was dropped is refused, naming the commit that dropped it"

# Nothing was written through a working tree: crew's cache of the repo is bare.
eq "$(git -C "$(home_of mac-studio)/.cache/crew/git/WilldanGroup/crew-state.git" rev-parse --is-bare-repository)" "true"

# madswan and swancloud share afterthought/crew-state, each on its own branch: a write to one is never replayed
# because the other wrote, and neither fetches the other's branch.
ab=$(blueprints afterthought/blueprints); blueprints agentplot/blueprints >/dev/null; as=$(remote afterthought/crew-state)
crew state init madswan >/dev/null; HOST=chuck-herdr-alpha crew state init swancloud >/dev/null
sig=2026-10-06-standup/01-a-greeting
w=$T/abs; clone afterthought/blueprints "$w"; mkdir -p "$w/signals/${sig%/*}"; printf -- '---\nsignal: %s\n---\n' "$sig" > "$w/signals/$sig.md"
commit_all "$w" "signals: a capture"; git -C "$w" push -q origin main
printf '#!/usr/bin/env bash\nwhile read -r old new ref; do echo "$ref" >> "$CREW_TEST_ROOT/pushes"; done\n' > "$as/hooks/post-receive"
chmod +x "$as/hooks/post-receive"; : > "$T/pushes"
race afterthought/crew-state chuck-herdr-alpha swancloud-design signal move "$sig" drop --reason "a greeting" --label swancloud
export CREW_AGENT=madswan-planner
expect_ok crew bolt new flywheel-loop "The loop runs." --repo flywheel-next --label madswan
[[ ! -f $T/race ]] || fail "swancloud's write never ran"
has "$(cat "$T/race.log")" "drop"
eq "$(sort "$T/pushes" | uniq -c | awk '{print $1, $2}')" $'1 refs/heads/madswan/main\n1 refs/heads/swancloud/main'
eq "$(git --git-dir "$as" log -1 --format=%s madswan/main)" "plan(flywheel-loop): add the bolt (madswan-planner)"
eq "$(git --git-dir "$as" log -1 --format=%s swancloud/main)" "signals($sig): drop (swancloud-design)"
eq "$(git -C "$(home_of mac-studio)/.cache/crew/git/afterthought/crew-state.git" for-each-ref --format='%(refname)' refs/crew/)" "refs/crew/madswan/main"
ok "two flywheels in one repository write at the same moment, each pushing once, neither fetching the other's branch"
