# crew unit add --signal: the unit's source is the signal, and the signal's one move, route, is committed by path
# on the blueprints repo's main and pushed.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
k=$(kit chuck-herdr-alpha willdan switchboard-kit)
crew plan init WilldanGroup/willdan-blueprints wldn >/dev/null
sig=2026-09-08-switchboard-flywheel-repo-planning/02-scott-needs-a-repo-structure-guide
w=$T/bp; clone WilldanGroup/willdan-blueprints "$w"; mkdir -p "$w/signals/${sig%/*}"
printf -- '---\nsignal: %s\nkind: ask\n---\n\nScott needs a guide.\n' "$sig" > "$w/signals/$sig.md"
echo "# books" > "$w/books.md"; commit_all "$w" "signals: a capture"; git -C "$w" push -q origin main
before=$(git --git-dir "$wb" rev-parse main)
export CREW_AGENT=wldn-planner CREW_LABEL=wldn

expect_ok crew unit add a-repo-onboards-from-a-written-guide "A written guide says how to lay out a repository." --repo switchboard-kit --signal "$sig"
has "$out" "plan(queue): add a-repo-onboards-from-a-written-guide (wldn-planner)"
has "$out" "signal $sig routed to unit/a-repo-onboards-from-a-written-guide"
git --git-dir "$wb" show plan/wldn:plan.rec > "$T/plan.rec"
eq "$(recsel -t Unit -P Source "$T/plan.rec")" "signals/$sig"
eq "$(recsel -t Unit -P Bolt "$T/plan.rec")" ""
eq "$(git --git-dir "$wb" rev-list --count "$before"..main)" "1"
eq "$(git --git-dir "$wb" diff-tree --no-commit-id --name-only -r main)" "signals/moves.rec"
eq "$(git --git-dir "$wb" log -1 --format=%s main)" "signals($sig): route to unit/a-repo-onboards-from-a-written-guide (wldn-planner)"
git --git-dir "$wb" show main:signals/moves.rec > "$T/moves.rec"
recfix --check "$T/moves.rec" || fail "moves.rec fails recfix --check"
eq "$(recsel -t Move -e "Signal = '$sig'" -P Move,Target,By "$T/moves.rec")" $'route\nunit/a-repo-onboards-from-a-written-guide\nwldn-planner'
eq "$(git --git-dir "$wb" show main:books.md)" "# books"
ok "the unit is queued from the signal, and moves.rec gains its route move, passing recfix --check"

expect_fail "signal $sig already has its move: route" crew unit add twice "Twice." --repo switchboard-kit --signal "$sig"
expect_fail "no signal 2026-09-09-nothing/01-none in WilldanGroup/willdan-blueprints" crew unit add none "None." --repo switchboard-kit --signal 2026-09-09-nothing/01-none
ok "a signal that is missing or already moved is refused before anything is written"

# A blueprints repo whose Move enum has no route yet refuses before the plan is written.
git -C "$w" pull -q --no-rebase origin main
sed -i '' 's/ drop route$/ drop/' "$w/signals/moves.rec"
mkdir -p "$w/signals/2026-09-10-x"; printf -- '---\nsignal: 2026-09-10-x/01-y\n---\n' > "$w/signals/2026-09-10-x/01-y.md"
commit_all "$w" "signals: no route move yet"; git -C "$w" push -q origin main
expect_fail "signals/moves.rec fails recfix --check" crew unit add unroutable "Unroutable." --repo switchboard-kit --signal 2026-09-10-x/01-y
git --git-dir "$wb" show plan/wldn:plan.rec > "$T/plan.rec"; eq "$(recsel -t Unit -c "$T/plan.rec")" "1"
ok "without route in the Move enum, the unit is refused and the plan left as it was"
