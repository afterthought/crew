# crew plan init makes plan/<label> an orphan branch holding only plan.rec, with the schema and no records,
# reached over https (rewritten here to the bare test remotes).
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints); ab=$(blueprints afterthought/blueprints)

expect_ok crew plan init WilldanGroup/willdan-blueprints wldn; has "$out" "plan/wldn"
eq "$(git --git-dir "$wb" ls-tree --name-only plan/wldn)" "plan.rec"
eq "$(git --git-dir "$wb" rev-list --count plan/wldn)" "1"
git --git-dir "$wb" show plan/wldn:plan.rec > "$T/plan.rec"
recfix --check "$T/plan.rec" || fail "recfix --check fails on the new plan"
has "$(cat "$T/plan.rec")" "%rec: Bolt"; has "$(cat "$T/plan.rec")" "%type: Bolt rec Bolt"
eq "$(recsel -t Unit -c "$T/plan.rec")" "0"
ok "an initialized plan passes recfix --check"

expect_fail "already has plan/wldn" crew plan init willdan-blueprints wldn
expect_fail "is not one of wldn's blueprints repos" crew plan init afterthought/blueprints wldn
expect_fail "no partition 'nope'" crew plan init afterthought/blueprints nope
ok "init refuses an existing plan, another partition's repo, and an unknown label"

# One repo, two partitions' plans.
expect_ok crew plan init afterthought/blueprints madswan
expect_ok crew plan init blueprints swancloud
eq "$(git --git-dir "$ab" for-each-ref --format='%(refname:short)' refs/heads/plan/)" $'plan/madswan\nplan/swancloud'
ok "afterthought/blueprints holds madswan's plan and swancloud's"
