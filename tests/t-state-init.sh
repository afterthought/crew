# crew state init <label>: creates the flywheel's branch <label>/main in its state repository, adopting what the
# partition had: the first blueprints repo's plan/<label>, history and all; another blueprints repo's plan, joined in
# one commit naming where it came from; and the first blueprints repo's moves. Run again, it writes nothing; stopped
# partway, it is finished by running it again.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints); ab=$(blueprints afterthought/blueprints); gb=$(blueprints agentplot/blueprints)
ws=$(remote WilldanGroup/crew-state); as=$(remote afterthought/crew-state)
# planfile [<records>]: plan.rec as crew writes it, each record (recutils text, \n for a line break) in its own set
planfile() {
  python3 - "$CREW/plugin/lib" "${1:-}" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
p = plan.Plan(plan.HEADER)
for para in sys.argv[2].replace("\\n", "\n").split("\n\n"):
    fields = [tuple(l.split(": ", 1)) for l in para.splitlines() if l.strip()]
    if fields:
        p.insert(plan.Rec(fields[0][0], fields))
sys.stdout.write(p.text())
PY
}
# old_plan <owner/name> <label> <records>: plan/<label> as crew kept it in a blueprints repo, in two commits
old_plan() {
  local w=$T/old-${1//\//-}-$2; rm -rf "$w"; git init -q "$w"; git -C "$w" checkout -q --orphan "plan/$2"
  planfile > "$w/plan.rec"; commit_all "$w" "plan: start plan/$2 (chuck@mac-studio)"
  planfile "$3" > "$w/plan.rec"; commit_all "$w" "plan: records (chuck@mac-studio)"
  git -C "$w" push -q -f "$(remote "$1")" "plan/$2"
}
count() { git --git-dir "$1" rev-list --count "$2"; }

# A partition with no plan anywhere: an empty plan, then moves.rec, both passing recfix.
expect_ok crew state init wldn
has "$out" "wldn/main of WilldanGroup/crew-state"; has "$out" "started an empty plan"; has "$out" "added moves.rec with 0 moves"
eq "$(git --git-dir "$ws" ls-tree --name-only wldn/main)" $'moves.rec\nplan.rec'
git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recfix --check "$T/plan.rec" || fail "plan.rec fails recfix --check"
eq "$(recsel -t Unit -c "$T/plan.rec")" "0"; has "$(cat "$T/plan.rec")" "%type: Bolt rec Bolt"
git --git-dir "$ws" show wldn/main:moves.rec > "$T/moves.rec"; recfix --check "$T/moves.rec" || fail "moves.rec fails recfix --check"
has "$(cat "$T/moves.rec")" "%type: Move enum attach challenge new-territory answered drop route"
eq "$(count "$ws" wldn/main)" "2"
has "$(git --git-dir "$ws" log -1 --format=%B wldn/main)" "Crew-Entry: "
expect_ok crew state init wldn
has "$out" "wldn/main of WilldanGroup/crew-state exists, at"; has "$out" "nothing to do"
eq "$(count "$ws" wldn/main)" "2"
ok "a new flywheel gets an empty plan and moves file, and a second run writes nothing"

# madswan had a plan in each of its blueprints repos, and afterthought/blueprints a move.
old_plan afterthought/blueprints madswan 'Bolt: site-refresh\nRepo: swancloud\nGoal: The site reads well.\nSource: books/site.md\n\nUnit: the-home-page-loads-fast\nRepo: swancloud\nBolt: site-refresh\nIntent: The home page loads in a second.\nSource: books/site.md\n'
old_plan agentplot/blueprints madswan 'Bolt: flywheel-loop\nRepo: flywheel-next\nGoal: The loop runs.\n\nUnit: the-home-page-loads-fast\nRepo: flywheel-next\nIntent: Twice named.\n'
first=$(git --git-dir "$ab" rev-list --max-parents=0 plan/madswan)
w=$T/abm; clone afterthought/blueprints "$w"
printf '\nSignal: 2026-10-01-standup/01-noise\nMove: drop\nReason: a greeting\nDate: 2026-10-01\nBy: madswan-design\n' >> "$w/signals/moves.rec"
commit_all "$w" "signals: a move"; git -C "$w" push -q origin main
moved=$(git --git-dir "$ab" rev-parse --short main)

expect_fail "plan/madswan of afterthought/blueprints and plan/madswan of agentplot/blueprints both hold unit the-home-page-loads-fast" crew state init madswan
has "$out" "nothing was written"
eq "$(git --git-dir "$as" for-each-ref refs/heads)" ""
ok "two plans that share a name refuse the init before anything is pushed"

old_plan agentplot/blueprints madswan 'Bolt: flywheel-loop\nRepo: flywheel-next\nGoal: The loop runs.\nSource: design/loop.md\n\nUnit: the-loop-turns\nRepo: flywheel-next\nIntent: The loop turns once a day.\nSource: design/loop.md\n'
joined=$(git --git-dir "$gb" rev-parse --short plan/madswan)
expect_ok crew state init madswan
has "$out" "adopted plan/madswan of afterthought/blueprints"; has "$out" "joined plan/madswan of agentplot/blueprints at $joined"
has "$out" "added moves.rec with 1 moves of afterthought/blueprints at $moved"
git --git-dir "$as" merge-base --is-ancestor "$first" madswan/main || fail "madswan/main does not reach the plan's first commit"
eq "$(git --git-dir "$as" log --reverse --format=%s madswan/main | head -1)" "plan: start plan/madswan (chuck@mac-studio)"
git --git-dir "$as" show madswan/main:plan.rec > "$T/plan.rec"; recfix --check "$T/plan.rec" || fail "the joined plan fails recfix --check"
eq "$(recsel -C -t Bolt -P Bolt "$T/plan.rec")" $'site-refresh\nflywheel-loop'
eq "$(recsel -C -t Unit -P Unit "$T/plan.rec")" $'the-home-page-loads-fast\nthe-loop-turns'
eq "$(recsel -t Unit -e "Unit = 'the-home-page-loads-fast'" -P Source "$T/plan.rec")" "books/site.md"
eq "$(recsel -t Unit -e "Unit = 'the-loop-turns'" -P Source "$T/plan.rec")" "agentplot/blueprints:design/loop.md"
eq "$(recsel -t Bolt -e "Bolt = 'flywheel-loop'" -P Source "$T/plan.rec")" "agentplot/blueprints:design/loop.md"
has "$(git --git-dir "$as" log --format=%s madswan/main)" "state(madswan): join plan/madswan of agentplot/blueprints at $joined"
git --git-dir "$as" show madswan/main:moves.rec > "$T/moves.rec"; recfix --check "$T/moves.rec" || fail "moves.rec fails recfix --check"
eq "$(recsel -t Move -P Signal,Move "$T/moves.rec")" $'2026-10-01-standup/01-noise\ndrop'
has "$(git --git-dir "$as" log -1 --format=%s madswan/main)" "afterthought/blueprints's signals/moves.rec at $moved"
ok "madswan's branch adopts afterthought's plan with its history, joins agentplot's naming it, and copies the move"

# swancloud shares afterthought/crew-state on a branch of its own. Its moves step is refused once: the run stops with
# the plan written, and running it again finishes it.
cat > "$as/hooks/pre-receive" <<'HOOK'
#!/usr/bin/env bash
while read -r old new ref; do
  if [ "$ref" = refs/heads/swancloud/main ] && git cat-file -e "$new:moves.rec" 2>/dev/null && [ -f "$CREW_TEST_ROOT/refuse-once" ]; then
    rm "$CREW_TEST_ROOT/refuse-once"; echo "refused once" >&2; exit 1
  fi
done
exit 0
HOOK
chmod +x "$as/hooks/pre-receive"; touch "$T/refuse-once"
expect_fail "the push of swancloud/main to afterthought/crew-state failed" crew state init swancloud
eq "$(git --git-dir "$as" ls-tree --name-only swancloud/main)" "plan.rec"
expect_ok crew state init swancloud
has "$out" "added moves.rec"; lacks "$out" "started an empty plan"
eq "$(git --git-dir "$as" ls-tree --name-only swancloud/main)" $'moves.rec\nplan.rec'
expect_ok crew state init swancloud; has "$out" "nothing to do"
git --git-dir "$as" merge-base madswan/main swancloud/main >/dev/null 2>&1 && fail "madswan's and swancloud's branches share history"
eq "$(git --git-dir "$as" for-each-ref --format='%(refname:short)' refs/heads)" $'madswan/main\nswancloud/main'
ok "a run stopped between steps is finished by running it again, and two flywheels in one repository share no history"

# Every step is in the run record, each commit naming its entry.
eid=$(git --git-dir "$ws" log -1 --format='%(trailers:key=Crew-Entry,valueonly)' wldn/main | head -1)
rec=$(cat "$(home_of mac-studio)"/.local/state/crew/wldn/runs/mac-studio/*.rec)
has "$rec" "Id: $eid"; has "$rec" "Act: state.init"; has "$rec" "Commit: WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
ok "each init commit's Crew-Entry trailer names the entry that names the commit"
