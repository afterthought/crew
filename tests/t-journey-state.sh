# A flywheel's state and its run record, through the crew command on the stubs (tests.11, record 0022): a plan command
# names recutils when it is missing; crew state init starts a branch, adopts a partition's old plans with their history
# and its moves, finishes a run stopped partway, and keeps two flywheels' branches apart; a record that can't be written
# changes nothing else; a write's commit names its entry and carries what the host has not, crew events --push carries
# the rest, and a carried file that fails recfix refuses its write; an agent's entry names its session as herdr has it;
# a refused write is an entry and a read none; crew events and crew trace read the branch, then each host, naming a host
# that does not answer, and --follow prints what another host writes. What an entry holds, how a day is carried, how a
# trace walks and what events shows, the act and objects of each plan write, and how plans are joined are logic cases
# (tests/py/test_record.py); two processes appending at once, a contract case (tests/contract/test_record.py); each
# step here checks a command's wiring once.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
box=chuck-herdr-alpha
wb=$(blueprints WilldanGroup/willdan-blueprints); ws=$(remote WilldanGroup/crew-state)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
day=$(date -u +%F)
emit() { local h=$1; shift; as "$h" python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@"; }
# onbranch <host>: the ids that host's file of the day holds on the branch
onbranch() { git --git-dir "$ws" show "wldn/main:runs/$1/$day.rec" 2>/dev/null | sed -n 's/^Id: //p'; }
commits() { git --git-dir "$ws" rev-list --count wldn/main; }
acts() { awk '{print $3}' <<<"$1" | tr '\n' ' '; }

expect_fail "install the recutils package" env PATH="$(path_without recsel)" bash -c "$(declare -f as crew home_of); $(declare -p CREW T); HOST=$HOST crew bolts"
has "$out" "recsel is not on PATH"
ok "a plan command names recutils when recsel is missing"

st=$(home_of mac-studio)/.local/state/crew; mkdir -p "$st"; chmod 555 "$st"
out=$(crew state init wldn 2>"$T/err") || fail "state init failed when its record could not be written"
chmod 755 "$st"
eq "$out" "wldn/main of WilldanGroup/crew-state $(git --git-dir "$ws" rev-parse --short wldn/main): started an empty plan; added moves.rec with 0 moves of WilldanGroup/willdan-blueprints at $(git --git-dir "$wb" rev-parse --short main)"
eq "$(grep -c "crew: the run record at $st/wldn/runs/mac-studio/.* could not be written" "$T/err") $(wc -l < "$T/err" | tr -d ' ')" "2 2"
eq "$(git --git-dir "$ws" ls-tree --name-only wldn/main)" $'moves.rec\nplan.rec\nproposals.rec'
expect_ok crew state init wldn; has "$out" "nothing to do"
eq "$(commits)" "2"
ok "a new flywheel gets an empty plan, moves and proposals, a record that can't be written is said once an entry and changes nothing else, and a second run writes nothing"

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
  local w=$T/old-${1//\//-}-$2; git init -q "$w"; git -C "$w" checkout -q --orphan "plan/$2"
  planfile > "$w/plan.rec"; commit_all "$w" "plan: start plan/$2 (chuck@mac-studio)"
  planfile "$3" > "$w/plan.rec"; commit_all "$w" "plan: records (chuck@mac-studio)"
  git -C "$w" push -q "$(remote "$1")" "plan/$2"
}
ab=$(blueprints afterthought/blueprints); gb=$(blueprints agentplot/blueprints); as=$(remote afterthought/crew-state)
old_plan afterthought/blueprints madswan 'Bolt: site-refresh\nRepo: swancloud\nGoal: The site reads well.\n'
old_plan agentplot/blueprints madswan 'Bolt: flywheel-loop\nRepo: flywheel-next\nGoal: The loop runs.\nSource: design/loop.md\n'
first=$(git --git-dir "$ab" rev-list --max-parents=0 plan/madswan); joined=$(git --git-dir "$gb" rev-parse --short plan/madswan)
w=$T/abm; clone afterthought/blueprints "$w"
printf '\nSignal: 2026-10-01-standup/01-noise\nMove: drop\nReason: a greeting\nDate: 2026-10-01\nBy: madswan-design\n' >> "$w/signals/moves.rec"
commit_all "$w" "signals: a move"; git -C "$w" push -q origin main
expect_ok crew state init madswan
has "$out" "adopted plan/madswan of afterthought/blueprints"; has "$out" "joined plan/madswan of agentplot/blueprints at $joined"
has "$out" "added moves.rec with 1 moves of afterthought/blueprints"
git --git-dir "$as" merge-base --is-ancestor "$first" madswan/main || fail "madswan/main does not reach the plan's first commit"
has "$(git --git-dir "$as" show madswan/main:plan.rec)" "Source: agentplot/blueprints:design/loop.md"
has "$(git --git-dir "$as" show madswan/main:moves.rec)" "Signal: 2026-10-01-standup/01-noise"
# swancloud shares afterthought/crew-state on a branch of its own; its moves step is refused once, and a second run
# finishes it.
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
git --git-dir "$as" merge-base madswan/main swancloud/main >/dev/null 2>&1 && fail "madswan's and swancloud's branches share history"
ok "state init adopts a partition's first old plan with its history, joins another naming where it came from, copies its moves, finishes a stopped run, and keeps two flywheels' branches apart"

export CREW_LABEL=wldn
crew bolt new tenants "Tenants." --repo switchboard-kit >/dev/null
rec=$(home_of mac-studio)/.local/state/crew/wldn/runs/mac-studio/$day.rec
eid=$(git --git-dir "$ws" log -1 --format='%(trailers:key=Crew-Entry,valueonly)' wldn/main | head -1)
eq "$(recsel -t Entry -e "Id = '$eid'" -P Act,Commit "$rec")" $'bolt.new\n'"WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
tell=$(emit mac-studio --act tell --on agent/wldn-planner --field Chars=5)
crew bolt new consoles "Consoles." --repo switchboard-kit >/dev/null
has "$(onbranch mac-studio)" "$tell"; has "$(onbranch mac-studio)" "$eid"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" $'plan.rec\n'"runs/mac-studio/$day.rec"
n=$(commits)
emit mac-studio --act tell --on agent/wldn-planner --field Chars=7 >/dev/null
expect_ok crew events --push; has "$out" "carried mac-studio's run record"
expect_ok crew events --push; has "$out" "nothing of mac-studio's run record left to carry"
eq "$(commits)" "$((n + 1))"
ok "a write's commit names its entry and carries the host's uncarried record; crew events --push carries the rest in a commit of its own, and nothing when nothing is left"

crew unit add a "Unit a." --bolt tenants >/dev/null
before=$(grep -c '^Act: unit.drop$' "$rec" || true)
crew unit drop a "Gone." >/dev/null
expect_fail "no unit a in the plans of wldn" crew unit drop a "Gone again."
eq "$(grep -c '^Act: unit.drop$' "$rec")" "$((before + 2))"
eq "$(recsel -t Entry -e "Act = 'unit.drop' && Refused != ''" -P On "$rec")" "unit/a"
n=$(grep -c '^Id:' "$rec"); crew bolts >/dev/null; eq "$(grep -c '^Id:' "$rec")" "$n"
p=$(as $box herdr --session wldn-3 workspace create --cwd / --label wldn | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-3 stub agent "$p" wldn-planner
CREW_AGENT=wldn-planner emit $box --act test.agent >/dev/null
has "$(cat "$(home_of $box)"/.local/state/crew/wldn/runs/$box/$day.rec)" "Session: $box:sid-${p//:/-}"
ok "a refused write is one entry and a read none, and an agent's entry names its session as herdr has it"

emit $box --act unit.add --on unit/x --on queue/switchboard-kit --why "plan(queue): add x" >/dev/null
HOST=$box expect_ok crew events --push; has "$out" "carried $box's run record"
emit $box --act unit.drop --on unit/x --on queue/switchboard-kit --why "plan(queue): drop x" >/dev/null
echo "$box" > "$T/down"
expect_ok crew events --about unit/x
eq "$(acts "$(grep -v 'did not answer' <<<"$out")")" "unit.add "; has "$out" "$box did not answer"
expect_ok crew trace unit/x
has "$out" "unit.add"; lacks "$out" "unit.drop"; has "$out" "$box did not answer"
rm "$T/down"
expect_ok crew events --about unit/x
eq "$(acts "$out")" "unit.add unit.drop "
expect_ok crew events --json
eq "$(jq -r '[.entries[].Host] | unique | join(" ")' <<<"$out")" "$box mac-studio"
ok "crew events and crew trace read the branch, then each host: one that does not answer is shown as far as it had carried, and named"

carried=$(onbranch $box)
mv "$(home_of $box)/.local/state/crew/wldn" "$T/box-record-lost"
emit $box --act unit.add --on unit/y --on queue/switchboard-kit --why "plan(queue): add y" >/dev/null
HOST=$box expect_ok crew events --push
eq "$(onbranch $box | wc -l | tr -d ' ')" "$(( $(wc -w <<<"$carried") + 1 ))"
ok "a host that lost its run record after carrying keeps its entries on the branch, and adds new ones beside them"

( export CREW_TEST_HOST=mac-studio HOME=$(home_of mac-studio); cd "$HOME" && exec "$CREW/plugin/bin/crew" events --follow ) > "$T/follow" 2>&1 &
fpid=$!
# Its tails are up once one follows the box's files: an entry written before then is never followed.
tailing() { pgrep -f "tail -q -n 0 -F .*$T/hosts/$box/" >/dev/null; }
until_ok tailing || fail "crew events --follow never started its tails"
emit $box --act stage.start --on stage/a/construct --on unit/a --why "unit(a): start construct" >/dev/null
follows() { grep -q "stage.start" "$T/follow"; }; until_ok follows || true
kill "$fpid"; wait "$fpid" 2>/dev/null || true
has "$(cat "$T/follow")" "stage/a/construct unit/a"; lacks "$(cat "$T/follow")" "unit.add"
untailed() { ! pgrep -f "tail -q -n 0 -F .*$T/hosts" >/dev/null; }
until_ok untailed || fail "a tail outlived crew events --follow"
ok "crew events --follow prints an entry another host writes while it runs, and leaves no tail behind"

# An entry cut short in the host's run record fails recfix --check: a write that would carry it is refused, naming the
# file, with nothing pushed; once the entry is gone the same write lands.
printf 'Id: 20991231T235959Z-mac-studio-1-1\nAt: 2099-12-31T23:59:59Z\n\n' >> "$rec"
tip=$(git --git-dir "$ws" rev-parse wldn/main)
expect_fail "runs/mac-studio/$day.rec fails recfix --check" crew bolt new portals "Portals." --repo switchboard-kit
eq "$(git --git-dir "$ws" rev-parse wldn/main)" "$tip"
rewrite "$rec" '/^Id: 20991231T235959Z-mac-studio-1-1$/,/^At: 2099-12-31T23:59:59Z$/d'
expect_ok crew bolt new portals "Portals." --repo switchboard-kit
ok "a carried run-record file that fails recfix --check refuses the write it rides in, and nothing is pushed"
