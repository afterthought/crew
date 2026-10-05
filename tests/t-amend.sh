# A unit in flight goes back through construct and review: the plan's Amended mark, the stage it gives a unit
# whatever its tasks say, construct run again at any stage before merge, code, verify and merge refused while the
# mark stands, and crew unit approve clearing it. Each scenario of unit-amendments' bolt-plan and bolt-teams specs.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
tip() { git --git-dir "$ws" rev-parse wldn/main; }
# by_hand <python>: plan.rec edited on the branch by hand, the python statement changing `p`, a plan.Plan
by_hand() {
  local w=$T/hand; rm -rf "$w"; git clone -q -b wldn/main "$ws" "$w"
  python3 - "$CREW/plugin/lib" "$w/plan.rec" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
exec(sys.argv[3])
open(f, "w").write(p.text())
PY
  commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
}
mark() { by_hand "p.unit('$1').set('Amended', '$2')"; }
old_schema='old = {plan.declares(q): q for q in plan.Plan(plan.HEADER.replace(" Amended", "")).paras if plan.declares(q)}; p.paras = [old.get(plan.declares(x), x) for x in p.paras]'

# A branch started before the mark was allowed: it reads, and state init or any write brings its descriptors in step.
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
by_hand "$old_schema"
lacks "$(plan -t Unit -c; cat "$T/plan.rec")" "Amended"
expect_ok crew bolts; has "$out" "tenant-environments"
expect_ok crew state init wldn
has "$out" "brought the plan's record descriptors in step with crew's"
plan -t Unit -c >/dev/null; has "$(grep '^%allowed: Unit' "$T/plan.rec")" "Amended"
expect_ok crew state init wldn; has "$out" "nothing to do"
by_hand "$old_schema"
crew unit add coding "Unit coding." --bolt tenant-environments >/dev/null 2>&1
plan -t Unit -c >/dev/null; has "$(grep '^%allowed: Unit' "$T/plan.rec")" "Amended"
mark coding proposal/4
plan -t Unit -c >/dev/null; recfix --check "$T/plan.rec" || fail "a plan holding Amended: proposal/4 fails recfix --check"
eq "$(plan -t Unit -e "Unit = 'coding'" -P Amended)" "proposal/4"
by_hand "p.unit('coding').drop('Amended')"
ok "a plan from before the mark still reads, and state init or the next write brings its descriptors in step"

# Units with ticked tasks, approved once, in each state of the mark, beside one never amended.
for u in m-proposal m-intent m-started m-committed; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null 2>&1; done
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
for u in coding m-proposal m-intent m-started m-committed; do
  p=$(place "$k" tenant-environments $u); change "$p" $u 2 3; commit_all "$p" "docs($u): the change"
  git -C "$p" commit -q --allow-empty -m "review($u): approved" --trailer "Reviewed-by: Test User"
done
started=$(git -C "$k" rev-parse unit/m-started); committed=$(git -C "$k" rev-parse unit/m-committed)
git -C "$kd/places/m-committed" commit -q --allow-empty -m "docs(m-committed): the change again"
mark m-proposal proposal/4; mark m-intent intent; mark m-started "$started"; mark m-committed "$committed"
expect_ok crew bolts --json; j=$out
st() { jq -r --arg u "$1" '[.partitions[].plans[].bolts[].units[] | select(.unit == $u) | .stage] | first' <<<"$j"; }
for pair in coding:code m-proposal:amended m-intent:amended m-started:construct m-committed:review; do eq "$(st "${pair%%:*}")" "${pair#*:}"; done
expect_ok crew bolts
has "$out" "  m-proposal                               amended      places/m-proposal"
has "$out" "  m-started                                construct    places/m-started"
has "$out" "  m-committed                              review       places/m-committed"
has "$out" "  coding                                   code 2/3     places/coding"
ok "a marked unit reads amended, construct while its head is where construct started, and review once it has moved, whatever its tasks"
