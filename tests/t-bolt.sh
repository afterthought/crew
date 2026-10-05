# crew bolt new|give|order|drop|land: give makes bolt/<bolt> from main and <kit>/bolts/<bolt> on the team's
# host, and every refusal the bolt-plan spec names.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
kit chuck-herdr-alpha willdan breadboard-kit >/dev/null
mkdir -p "$k/.devenv/profile/bin"
printf '#!/usr/bin/env bash\necho "$KIT" > .prepared\n' > "$k/.devenv/profile/bin/crew-prepare"; chmod +x "$k/.devenv/profile/bin/crew-prepare"
printf '.devenv/\n.prepared\n' > "$k/.gitignore"; commit_all "$k" "chore: ignore what preparing a worktree makes"
crew plan init WilldanGroup/willdan-blueprints wldn >/dev/null
export CREW_AGENT=wldn-planner
plan() { git --git-dir "$wb" show plan/wldn:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }

expect_ok crew bolt new tenant-environments "A tenant holds environments of its own." --repo switchboard-kit --source books/switchboard-kit/src/account-onboarding.md
has "$out" "plan(tenant-environments): add the bolt (wldn-planner)"
crew bolt new console-pages "The console lists a tenant's environments." --repo switchboard-kit >/dev/null
crew bolt new apex-zones "Each install's apex is its own zone." --repo switchboard-kit --before console-pages >/dev/null
crew bolt new board-builds "A board builds." --repo breadboard-kit >/dev/null
eq "$(plan -t Bolt -P Bolt)" $'tenant-environments\napex-zones\nconsole-pages\nboard-builds'
eq "$(plan -t Bolt -e "Bolt = 'tenant-environments'" -P Source)" "books/switchboard-kit/src/account-onboarding.md"
expect_fail "plan/wldn already has bolt console-pages" crew bolt new console-pages "again" --repo switchboard-kit
expect_fail "no team builds rocs-kit" crew bolt new rocs "x" --repo rocs-kit
ok "bolt new adds bolts in order"

expect_ok crew bolt order console-pages --first
expect_ok crew bolt order tenant-environments --before apex-zones
eq "$(plan -t Bolt -P Bolt)" $'console-pages\ntenant-environments\napex-zones\nboard-builds'
crew bolt order console-pages --last >/dev/null
eq "$(plan -t Bolt -P Bolt)" $'tenant-environments\napex-zones\nboard-builds\nconsole-pages'
ok "bolt order moves a bolt"

expect_fail "bolt board-builds is in breadboard-kit, and swb-1 builds switchboard-kit" crew bolt give swb-1 board-builds
expect_ok crew bolt give swb-1
has "$out" "plan(tenant-environments): give to swb-1"
has "$out" "swb-1 holds tenant-environments: bolt/tenant-environments at $kd/bolts/tenant-environments on chuck-herdr-alpha"
eq "$(plan -t Bolt -e "Bolt = 'tenant-environments'" -P Team)" "swb-1"
eq "$(git -C "$kd/bolts/tenant-environments" branch --show-current)" "bolt/tenant-environments"
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$(git -C "$k" rev-parse main)"
eq "$(cat "$kd/bolts/tenant-environments/.prepared")" "$k"
ok "give takes the team's first planned bolt, and makes its branch and worktree on the team's host"

expect_fail "bolt tenant-environments is held by swb-1" crew bolt give swb-2 tenant-environments
crew unit add the-deploy-names-its-host-tenant "The deploy writes the host tenant." --bolt tenant-environments >/dev/null
expect_fail "swb-1 holds bolt tenant-environments, whose unit the-deploy-names-its-host-tenant has not landed (ready)" crew bolt give swb-1
ok "give is refused while the team holds a bolt with a unit that has not landed"

expect_fail "unit the-deploy-names-its-host-tenant has not landed on main: it is ready" crew bolt land tenant-environments
change "$k" the-deploy-names-its-host-tenant 3 3; commit_all "$k" "feat: the deploy names its host tenant"
git -C "$kd/bolts/tenant-environments" merge -q --ff-only main
expect_ok crew bolt land tenant-environments
has "$out" "plan(tenant-environments): land the bolt"
[[ ! -d $kd/bolts/tenant-environments ]] || fail "the bolt's worktree is still there"
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still there"
eq "$(plan -t Unit -c)" "0"; eq "$(plan -t Bolt -P Bolt)" $'apex-zones\nboard-builds\nconsole-pages'
ok "land is refused until every unit has landed, then removes the bolt, its units and its worktree"

expect_ok crew bolt give swb-1
has "$out" "swb-1 holds apex-zones"
[[ -d $kd/bolts/apex-zones ]] || fail "the next bolt's worktree is missing"
ok "after landing, the team is given its next planned bolt with no edit and no deploy"

crew bolt give brd-1 >/dev/null
expect_ok crew bolt drop board-builds "the board ships as is"
eq "$(git --git-dir "$wb" log -1 --format=%b plan/wldn)" "the board ships as is"
crew unit add a-console-page "A page lists them." --bolt console-pages >/dev/null
crew unit add a-console-filter "It filters them." --bolt console-pages --after a-console-page >/dev/null
expect_ok crew bolt drop console-pages "folded into the portal" --requeue
eq "$(plan -t Unit -P Unit)" $'a-console-page\na-console-filter'
eq "$(plan -t Unit -e "Bolt != ''" -c)" "0"; eq "$(plan -t Unit -e "After != ''" -c)" "0"
eq "$(plan -t Bolt -P Bolt)" "apex-zones"
ok "drop removes a bolt and its units, or with --requeue queues them"
