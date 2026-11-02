# A flywheel's state and its run record, through the crew command on the stubs (tests.11, record 0022): a plan command
# names recutils when it is missing; crew state init starts a branch, adopts a partition's old plans with their history
# and its moves, finishes a run stopped partway, and keeps two flywheels' branches apart; a record that can't be written
# changes nothing else; a write's commit changes its own files and names its entry, which follows as a commit of its
# own, and every entry is on the branch when the command that wrote it returns; a push the branch refuses is said and
# goes with the host's next entry, crew events --push pushes what is left, and an entry cut short stops the record's
# push, not the write; an agent's entry names its session as herdr has it; a refused write is an entry and a read none;
# crew events and crew trace read the branch alone, a host that does not answer hiding nothing it pushed, and --follow
# prints what another host pushes once it fetches, at its start and on its clock, which a signal moves; none of them
# asks a host. What an entry holds, which entries a push takes and how their commits are worded, how a
# trace walks and what events shows, the act and objects of each plan write, and how plans are joined are logic cases
# (tests/py/test_record.py); two processes appending at once, and a chain of entries landing on a moved branch, contract
# cases (tests/contract/test_record.py); each step here checks a command's wiring once.
# Reads: plugin/lib/board.py plugin/lib/sites.py
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
eq "$(git --git-dir "$as" ls-tree --name-only swancloud/main)" $'plan.rec\nruns'
expect_ok crew state init swancloud
has "$out" "added moves.rec"; lacks "$out" "started an empty plan"
git --git-dir "$as" merge-base madswan/main swancloud/main >/dev/null 2>&1 && fail "madswan's and swancloud's branches share history"
ok "state init adopts a partition's first old plan with its history, joins another naming where it came from, copies its moves, finishes a stopped run, and keeps two flywheels' branches apart"

export CREW_LABEL=wldn
crew bolt new tenants "Tenants." --repo switchboard-kit >/dev/null
rec=$(home_of mac-studio)/.local/state/crew/wldn/runs/mac-studio/$day.rec
eid=$(git --git-dir "$ws" log -1 --format='%(trailers:key=Crew-Entry,valueonly)' wldn/main~1 | head -1)
eq "$(recsel -t Entry -e "Id = '$eid'" -P Act,Commit "$rec")" $'bolt.new\n'"WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main~1)"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main~1)" "plan.rec"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" "runs/mac-studio/$day.rec"
eq "$(git --git-dir "$ws" log -1 --format='%(trailers:key=Crew-Entry,valueonly)' wldn/main | head -1)" "$eid"
has "$(onbranch mac-studio)" "$eid"
ok "a plan write's commit changes its own files alone, and its entry, which names it, follows as the next commit"
n=$(commits)
tell=$(emit mac-studio --act tell --on agent/wldn-planner --field Chars=5)
has "$(onbranch mac-studio)" "$tell"; eq "$(commits)" "$((n + 1))"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" "runs/mac-studio/$day.rec"
eq "$(git --git-dir "$ws" log -1 --format='%s%n%(trailers:key=Crew-Entry,valueonly)' wldn/main | sed '/^$/d')" "runs(mac-studio): tell agent/wldn-planner ($me@mac-studio)"$'\n'"$tell"
ok "an entry is on the branch when the command that wrote it returns, in a commit of its own changing its day's file alone and naming it"

# The state repository refuses a push of the run record while refuse-runs is there, as GitHub out of reach would.
cat > "$ws/hooks/pre-receive" <<'HOOK'
#!/usr/bin/env bash
while read -r old new ref; do
  if [ -f "$CREW_TEST_ROOT/refuse-runs" ] && git log -1 --format=%s "$new" | grep -q '^runs('; then
    echo "github.com could not be reached" >&2; exit 1
  fi
done
exit 0
HOOK
chmod +x "$ws/hooks/pre-receive"; touch "$T/refuse-runs"
n=$(commits)
out=$(crew bolt new billing "Billing." --repo switchboard-kit 2>&1) || fail "a write failed when its entry could not be pushed: $out"
missed=$(sed -n "s/^crew: entry \([^ ]*\) did not reach wldn\/main of WilldanGroup\/crew-state: .*github.com could not be reached.*; mac-studio keeps it and pushes it with its next entry\$/\1/p" <<<"$out")
[[ -n $missed ]] || fail "the refused push was not said:"$'\n'"$out"
eq "$(grep -c 'did not reach' <<<"$out")" "1"
has "$(git --git-dir "$ws" show wldn/main:plan.rec)" "Bolt: billing"; eq "$(commits)" "$((n + 1))"
lacks "$(onbranch mac-studio)" "$missed"; has "$(cat "$rec")" "Id: $missed"
rm "$T/refuse-runs"
next=$(emit mac-studio --act tell --on agent/wldn-planner --field Chars=7)
eq "$(commits)" "$((n + 3))"
eq "$(git --git-dir "$ws" log -2 --format='%(trailers:key=Crew-Entry,valueonly)' wldn/main | sed '/^$/d' | tr '\n' ' ')" "$next $missed "
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main~1) $(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" \
  "runs/mac-studio/$day.rec runs/mac-studio/$day.rec"
ok "an entry whose push is refused is said once and the write it records stands; the host's next entry pushes it first, each its own commit"

touch "$T/refuse-runs"
left=$(emit mac-studio --act tell --on agent/wldn-planner --field Chars=9 2>/dev/null)
rm "$T/refuse-runs"
lacks "$(onbranch mac-studio)" "$left"
expect_ok crew events --push; eq "$out" "wldn/main: pushed 1 of mac-studio's entries"
has "$(onbranch mac-studio)" "$left"
expect_ok crew events --push; eq "$out" "wldn/main: nothing of mac-studio's run record left to push"
ok "crew events --push pushes what a refused push left in the host's record, then says nothing is left"

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
emit $box --act unit.drop --on unit/x --on queue/switchboard-kit --why "plan(queue): drop x" >/dev/null
echo "$box" > "$T/down"; : > "$CREW_TEST_LOG"
expect_ok crew events --about unit/x
eq "$(acts "$out")" "unit.add unit.drop "
expect_ok crew trace unit/x
has "$out" "unit.add"; has "$out" "unit.drop"; lacks "$out" "did not answer"
rm "$T/down"
expect_ok crew events --json
eq "$(jq -r '[.entries[].Host] | unique | join(" ")' <<<"$out")" "$box mac-studio"; eq "$(jq -c .unreachable <<<"$out")" "{}"
lacks "$(calls)" " ssh "
ok "crew events and crew trace read the branch alone: a host that does not answer hides none of what it pushed, and no host is asked"

carried=$(onbranch $box)
mv "$(home_of $box)/.local/state/crew/wldn" "$T/box-record-lost"
emit $box --act unit.add --on unit/y --on queue/switchboard-kit --why "plan(queue): add y" >/dev/null
HOST=$box expect_ok crew events --push
eq "$(onbranch $box | wc -l | tr -d ' ')" "$(( $(wc -w <<<"$carried") + 1 ))"
ok "a host that lost its run record after pushing it keeps its entries on the branch, and adds new ones beside them"

# The follow, with no follower on mac-studio, fetches wldn's branch at its start and on its own clock, which the test
# sets past the test's length so only its signal moves it (tests.8); a shim on git counts its fetches of the branch.
cache=$(home_of mac-studio)/.cache/crew/git/WilldanGroup/crew-state.git
rm -f "$cache/FETCH_HEAD"; : > "$CREW_TEST_LOG"; : > "$T/fetches"; mkdir -p "$T/shim"
printf '#!/usr/bin/env bash\nif [[ " $* " == *" fetch "*refs/crew/wldn/main* ]]; then echo fetch >> %q; fi\nexec %q "$@"\n' \
  "$T/fetches" "$(command -v git)" > "$T/shim/git"; chmod +x "$T/shim/git"
fetches() { wc -l < "$T/fetches" | tr -d ' '; }
( export CREW_TEST_HOST=mac-studio HOME=$(home_of mac-studio) CREW_TEST_PERIOD=3600 PATH="$T/shim:$PATH"
  cd "$HOME" && exec "$CREW/plugin/bin/crew" events --follow ) > "$T/follow" 2>&1 &
fpid=$!
# Its first read is made once it has fetched the branch: what the branch held then is not printed.
fetched() { [[ -f $cache/FETCH_HEAD ]]; }
until_ok fetched || fail "crew events --follow never read the branch"
emit $box --act stage.start --on stage/a/construct --on unit/a --why "unit(a): start construct" >/dev/null
eq "$(fetches)" "1"
lacks "$(cat "$T/follow")" "stage.start"
kill -USR1 "$fpid"
follows() { grep -q "stage.start" "$T/follow"; }; until_ok follows || true
kill "$fpid"; wait "$fpid" 2>/dev/null || true
has "$(cat "$T/follow")" "stage/a/construct unit/a"; lacks "$(cat "$T/follow")" "unit.add"
eq "$(fetches)" "2"
lacks "$(calls)" " ssh "
ok "crew events --follow prints an entry another host pushes once it is told to tick, fetching at its start and once per tick and never otherwise, and asks no host for it"

# An entry cut short in the host's run record fails recfix --check: the record's push is refused, naming the file, with
# nothing of it pushed, while the write whose entry it held back lands; once the entry is gone the record is pushed.
printf 'Id: 20991231T235959Z-mac-studio-1-1\nAt: 2099-12-31T23:59:59Z\n\n' >> "$rec"
expect_ok crew bolt new portals "Portals." --repo switchboard-kit
has "$out" "did not reach wldn/main of WilldanGroup/crew-state: runs/mac-studio/$day.rec fails recfix --check"
has "$(git --git-dir "$ws" show wldn/main:plan.rec)" "Bolt: portals"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" "plan.rec"
rewrite "$rec" '/^Id: 20991231T235959Z-mac-studio-1-1$/,/^At: 2099-12-31T23:59:59Z$/d'
expect_ok crew events --push; has "$out" "wldn/main: pushed"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" "runs/mac-studio/$day.rec"
ok "an entry cut short in the host's run record refuses the record's push, naming the file, and the write it followed lands"
