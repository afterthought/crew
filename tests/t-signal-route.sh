# crew unit add --signal: the unit's source is the signal, and the signal's one move, route, goes in the same commit
# on the flywheel's branch: moves.rec beside plan.rec, checked on every replay. A signal is looked up on the
# flywheel's branch, where crew records them, then in the partition's first blueprints repo, where the daily pass
# writes a meeting's, which nothing here writes.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit)
crew state init wldn >/dev/null
sig=2026-09-08-switchboard-flywheel-repo-planning/02-scott-needs-a-repo-structure-guide
w=$T/bp; clone WilldanGroup/willdan-blueprints "$w"; mkdir -p "$w/signals/${sig%/*}"
printf -- '---\nsignal: %s\nkind: ask\n---\n\nScott needs a guide.\n' "$sig" > "$w/signals/$sig.md"
echo "# books" > "$w/books.md"; commit_all "$w" "signals: a capture"; git -C "$w" push -q origin main
before=$(git --git-dir "$ws" rev-parse wldn/main); main=$(git --git-dir "$wb" rev-parse main)
export CREW_LABEL=wldn

expect_ok crew unit add a-repo-onboards-from-a-written-guide "A written guide says how to lay out a repository." --repo switchboard-kit --signal "$sig"
has "$out" "plan(queue): add a-repo-onboards-from-a-written-guide ($me@mac-studio)"
has "$out" "signal $sig routed to unit/a-repo-onboards-from-a-written-guide, in the same commit"
eq "$(git --git-dir "$ws" rev-list --count "$before"..wldn/main)" "1"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main | grep -v '^runs/')" $'moves.rec\nplan.rec'
git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"
eq "$(recsel -t Unit -P Source "$T/plan.rec")" "signals/$sig"
eq "$(recsel -t Unit -P Bolt "$T/plan.rec")" ""
git --git-dir "$ws" show wldn/main:moves.rec > "$T/moves.rec"
recfix --check "$T/moves.rec" || fail "moves.rec fails recfix --check"
eq "$(recsel -t Move -e "Signal = '$sig'" -P Move,Target,By "$T/moves.rec")" "route"$'\n'"unit/a-repo-onboards-from-a-written-guide"$'\n'"$me@mac-studio"
eq "$(git --git-dir "$wb" rev-parse main)" "$main"
ok "the unit and its route move are one commit on the flywheel's branch, and the blueprints repo is untouched"

expect_fail "signal $sig already has its move: route" crew unit add twice "Twice." --repo switchboard-kit --signal "$sig"
expect_fail "no signal 2026-09-09-nothing/01-none on wldn/main of WilldanGroup/crew-state or on main of WilldanGroup/willdan-blueprints" crew unit add none "None." --repo switchboard-kit --signal 2026-09-09-nothing/01-none
git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; eq "$(recsel -t Unit -c "$T/plan.rec")" "1"
ok "a signal that is missing or already moved is refused, and the plan left as it was"

# A moves.rec whose Move enum has no route refuses the unit too: the commit holds both files or neither.
s=$T/state; git clone -q -b wldn/main "$ws" "$s"
rewrite "$s/moves.rec" 's/ drop route$/ drop/'; commit_all "$s" "moves: no route yet"; git -C "$s" push -q origin wldn/main
mkdir -p "$w/signals/2026-09-10-x"; printf -- '---\nsignal: 2026-09-10-x/01-y\n---\n' > "$w/signals/2026-09-10-x/01-y.md"
commit_all "$w" "signals: another"; git -C "$w" push -q origin main
expect_fail "moves.rec fails recfix --check" crew unit add unroutable "Unroutable." --repo switchboard-kit --signal 2026-09-10-x/01-y
git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; eq "$(recsel -t Unit -c "$T/plan.rec")" "1"
ok "without route in the Move enum, the unit is refused and the plan left as it was"

# A flywheel-next unit for madswan, designed in agentplot/blueprints, is queued from a signal in
# afterthought/blueprints: its source names the signal, and the move is on madswan/main.
ab=$(blueprints afterthought/blueprints); blueprints agentplot/blueprints >/dev/null; as=$(remote afterthought/crew-state)
crew state init madswan >/dev/null
msig=2026-10-02-standup/01-the-loop-should-turn-daily
m=$T/ab; clone afterthought/blueprints "$m"; mkdir -p "$m/signals/${msig%/*}"; printf -- '---\nsignal: %s\n---\n' "$msig" > "$m/signals/$msig.md"
commit_all "$m" "signals: a capture"; git -C "$m" push -q origin main
mkdir -p "$(space mac-studio agentplot)/flywheel-next/main"; kit mac-studio agentplot flywheel-next >/dev/null 2>&1 || true
CREW_LABEL=madswan expect_ok crew unit add the-loop-turns-daily "The loop turns once a day." --repo flywheel-next --signal "$msig"
git --git-dir "$as" show madswan/main:plan.rec > "$T/mplan.rec"
eq "$(recsel -t Unit -P Source "$T/mplan.rec")" "signals/$msig"
eq "$(git --git-dir "$as" show madswan/main:moves.rec | recsel -t Move -P Signal,Move)" "$msig"$'\n'"route"
ok "a signal of the partition's first blueprints repo routes a unit designed in its second, on the flywheel's branch"

# A signal recorded through crew is on the flywheel's branch: it is moved and routed there just the same, directly
# and inside a proposal, and a meeting's signal in the blueprints is moved as before.
id_of() { sed -n 's/^signal \([^: ]*\)[: ].*/\1/p' <<<"$1"; }
git -C "$s" pull -q origin wldn/main; rewrite "$s/moves.rec" 's/ answered drop$/ answered drop route/'
commit_all "$s" "moves: route again"; git -C "$s" push -q origin wldn/main
main=$(git --git-dir "$wb" rev-parse main)
mine=$(id_of "$(crew signal plans-are-checked "Plans should be checked before they run." --label wldn)")
git --git-dir "$ws" cat-file -e "wldn/main:signals/$mine.md" || fail "the user's note is not on wldn/main"
expect_ok crew unit add plans-are-checked "A plan is checked before it runs." --repo switchboard-kit --signal "$mine"
has "$out" "signal $mine routed to unit/plans-are-checked, in the same commit"
eq "$(git --git-dir "$ws" show wldn/main:moves.rec | recsel -t Move -e "Signal = '$mine'" -P Move,Target)" "route"$'\n'"unit/plans-are-checked"
noted=$(id_of "$(crew signal noted-twice "The same thing was noted twice." --label wldn)")
CREW_AGENT=wldn-design expect_ok crew signal move "$noted" drop --reason "a duplicate"
eq "$(git --git-dir "$ws" show wldn/main:moves.rec | recsel -t Move -e "Signal = '$noted'" -P Move)" "drop"
msig=2026-09-11-standup/01-a-meeting-said-so
mkdir -p "$w/signals/${msig%/*}"; printf -- '---\nsignal: %s\n---\n\nA meeting said so.\n' "$msig" > "$w/signals/$msig.md"
commit_all "$w" "signals: a meeting"; git -C "$w" push -q origin main; main=$(git --git-dir "$wb" rev-parse main)
CREW_AGENT=wldn-design expect_ok crew signal move "$msig" new-territory
eq "$(git --git-dir "$ws" show wldn/main:moves.rec | recsel -t Move -e "Signal = '$msig'" -P Move)" "new-territory"
ok "a signal on the flywheel's branch is routed and moved there, and one in the blueprints is moved as before"

asked=$(id_of "$(crew signal deploys-are-dry-run "Deploys should be dry-run first." --label wldn)")
printf 'Case: The user asked for it.\nDo: unit add deploys-dry-run-first "A deploy is dry-run before it runs." --repo switchboard-kit --signal %s\n' "$asked" > "$T/p.rec"
expect_ok crew plan propose "$T/p.rec"
n=$(sed -n 's/^proposal \([0-9]*\) is open.*/\1/p' <<<"$out")
expect_ok crew plan proposed "$n"
has "$out" "From: signals/$asked: \"Deploys should be dry-run first.\""
has "$out" "Excerpt (own): > \"Deploys should be dry-run first.\" — "
expect_ok crew plan approve "$n"
eq "$(git --git-dir "$ws" show wldn/main:moves.rec | recsel -t Move -e "Signal = '$asked'" -P Move,Target)" "route"$'\n'"unit/deploys-dry-run-first"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main | grep -v '^runs/')" $'moves.rec\nplan.rec\nproposals.rec'
eq "$(git --git-dir "$wb" rev-parse main)" "$main"
ok "inside a proposal, a signal on the flywheel's branch is shown with its excerpt and grade, and routed on approval"
