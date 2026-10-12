# A bolt's units from its give to its landing, through the crew command on the stubs (tests.11, record 0022): give
# makes the bolt's worktree; each stage of a unit takes a slot, starts a fresh agent in the unit's place and sends its
# prompt, taken or sent again; the waits end each stage at its deliverable and record it; the team's reads record an
# end nobody waited on, free what merged, rebase a dependent and remove what is over; an amendment runs construct
# again; a fix and a proof run as stages do; and the bolt lands. Whether each stage may start, what it delivers, what
# its prompt says and every other decision on the way are logic cases (tests/py/); how git and worktrunk behave for
# them, contract cases (tests/contract/). Each step checks the command's wiring once.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
team_world
box=chuck-herdr-alpha
mkdir -p "$k/.devenv/profile/bin"
printf '#!/usr/bin/env bash\necho "$KIT" > .prepared\n' > "$k/.devenv/profile/bin/crew-prepare"; chmod +x "$k/.devenv/profile/bin/crew-prepare"
printf '.devenv/\n.prepared\n' > "$k/.gitignore"; printf 'one\ntwo\nthree\n' > "$k/shared.txt"
commit_all "$k" "chore: ignore what preparing makes, and a file the units share"
export CREW_LABEL=wldn
slots=$(home_of $box)/.local/state/swb-1-team/slots
stages=$(home_of $box)/.local/state/swb-1-team/stages
reports=$(home_of $box)/.local/state/swb-1-team/reports
bolt=$kd/bolts/tenant-environments
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
subject() { git --git-dir "$ws" log -1 --format=%s wldn/main; }
short() { git -C "$k" rev-parse --short "$1"; }
pane() { herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key"; }
status() { as $box herdr --session wldn-1 stub status "$(pane "$1")" "$2"; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v " /exit$" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
sent() { grep -cF "$box wldn-1 agent prompt $1 $2" "$CREW_TEST_LOG" || true; }
told() { grep "^$box wldn-1 agent prompt $1 '\[crew" "$CREW_TEST_LOG" || true; }
last_launch() { tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '([.argv | to_entries[] | select(.value == "--name") | .key][0]) as $i | "\(.argv[0:4] | join(" ")) | \(.argv[$i + 1]) | \(.cwd)"'; }
# field <host> <act> <field> [object...]: a field of that host's last entry of the act naming every object given
field() {
  local h=$1 a=$2 f=$3; shift 3
  as "$h" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and all(o in e["On"] for o in sys.argv[3:])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$a" "$@" | jq -r --arg f "$f" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
record_of() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null'; }
hands=0
# by_hand <python>: plan.rec changed on the branch in one commit, the python statement changing p, a plan.Plan
by_hand() {
  local w=$T/hand-$((hands += 1)); git clone -q -b wldn/main "$ws" "$w"
  python3 - "$CREW/plugin/lib" "$w/plan.rec" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
unit = lambda name, bolt, *after: p.insert(plan.Rec("Unit", [("Unit", name), ("Repo", "switchboard-kit"), ("Bolt", bolt),
                                                         ("Intent", f"Unit {name}.")] + [("After", x) for x in after]))
exec(sys.argv[3])
open(f, "w").write(p.text())
PY
  commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
}
# touches <unit> <entries...>: the unit's proposal ends with a Touches block holding the entries, committed in its place
touches() {
  local u=$1 f=$kd/places/$1/openspec/changes/$1/proposal.md; shift
  printf '# Proposal\n\n## Why\n\nx\n\n## What Changes\n\n- y\n\n## Touches\n\n```\n' > "$f"; printf '%s\n' "$@" >> "$f"; echo '```' >> "$f"
  commit_all "$kd/places/$u" "docs($u): touches"
}
tick() { rewrite "$kd/places/$1/openspec/changes/$1/tasks.md" "s/- \[ \] $2/- [x] $2/"; commit_all "$kd/places/$1" "feat($1): task $2"; }

expect_ok crew up swb-1
eq "$(field $box team.up On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
eq "$(field $box team.up By)" "$me@mac-studio"
expect_ok crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit --source books/x.md
has "$out" "plan(tenant-environments): add the bolt ($me@mac-studio)"
by_hand 'old = {plan.declares(q): q for q in plan.Plan(plan.HEADER.replace(" Amended", "")).paras if plan.declares(q)}
p.paras = [old.get(plan.declares(x), x) for x in p.paras]'
expect_ok crew unit add a "Unit a." --bolt tenant-environments --source books/x.md --source switchboard-kit:docs/y.md
has "$out" "plan(tenant-environments): add a ($me@mac-studio)"
eq "$(plan -t Unit -e "Unit = 'a'" -P Source)" $'books/x.md\nswitchboard-kit:docs/y.md'
has "$(grep '^%allowed: Unit' "$T/plan.rec")" "Amended"
by_hand 'unit("b", "tenant-environments", "a"); [unit(u, "tenant-environments") for u in "cde"]
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
expect_ok crew bolt give swb-1
has "$out" "swb-1 holds tenant-environments: bolt/tenant-environments at $bolt on $box"
eq "$(plan -t Bolt -e "Bolt = 'tenant-environments'" -P Team)" "swb-1"
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$(git -C "$k" rev-parse main)"
eq "$(cat "$bolt/.prepared")" "$k"
ok "crew up records the team's agents; bolt new and unit add each commit to the plan in the asker's name, a write bringing an older plan's descriptors in step; give makes the bolt's branch from main and its prepared worktree on the team's host"

# The conductor runs the stages on the team's host.
export CREW_AGENT=swb-1-conductor
expect_ok crew unit run a construct
has "$out" "swb-1-unit-1 has a: construct, in $kd/places/a"
eq "$(cat "$slots")" "unit-1 unit a $kd/places/a"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/a)" "bolt/tenant-environments"
eq "$(cat "$kd/places/a/.prepared")" "$k"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:propose a Unit a. Sources: books/x.md; switchboard-kit:docs/y.md.'"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1,swb-1 units"
eq "$(field $box stage.start On stage/a/construct)" "stage/a/construct unit/a agent/swb-1-unit-1"
eq "$(field $box stage.start By stage/a/construct)" "swb-1-conductor"
has "$(cat "$stages")" "unit-1 a construct "
ok "construct takes a free slot, makes the unit's prepared place from the bolt, starts a fresh agent sent its prompt in the units workspace, and records the start it owes an end"

expect_fail "unit b is waiting: it comes after a, whose change is not committed yet" crew unit run b construct
eq "$(wc -l < "$slots" | tr -d ' ')" "1"
[[ ! -d $kd/places/b ]] || fail "b's place was made"
has "$(field $box stage.start Refused stage/b/construct)" "unit b is waiting"
eq "$(ls -A "$(home_of $box)/.cache/crew/reads" "$(home_of mac-studio)/.cache/crew/reads" 2>/dev/null | grep -v '^/\|^$' || true)" ""
ok "a stage refused takes no slot, makes no place, leaves no reading, and is recorded refused"

change "$kd/places/a" a 0 3; commit_all "$kd/places/a" "docs(a): the change"
status swb-1-unit-1 working
expect_ok crew unit wait a --stuck 0 --timeout 0
eq "$out" "construct on a is still running after the wait's 0 ms: swb-1-unit-1 is working; nothing is recorded yet"
status swb-1-unit-1 idle
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered construct on a: its change is committed at $(short unit/a)"
eq "$(field $box stage.end Ended stage/a/construct)" "delivered"
eq "$(field $box stage.end Delivered stage/a/construct)" "unit/a@$(short unit/a)"
eq "$(field $box stage.end Result stage/a/construct)" "planned"
eq "$(cat "$stages")" ""
ok "a wait reads the stage still running while its agent works, then records its end with what it delivered"

echo a > "$kd/places/a/a-work"; commit_all "$kd/places/a" "feat(a): its own work"; tick a 1.1
expect_ok crew unit run b construct
has "$out" "swb-1-unit-2 has b: construct, in $kd/places/b"
git -C "$k" merge-base --is-ancestor unit/a unit/b || fail "b's place does not hold a's work"
eq "$(field $box stage.start Took stage/b/construct)" "a@$(git -C "$k" rev-parse --short=7 unit/a)"
expect_ok crew unit run a code
grep -q "^$box wldn-1 agent prompt $(pane swb-1-unit-1) /exit\|^$box wldn-1 agent prompt swb-1-unit-1 /exit" "$CREW_TEST_LOG" || fail "a's construct agent was not ended"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:apply a'"
ok "a dependent's construct takes its After unit's head; code ends the slot's agent and starts a fresh one at its own effort"

# The team's read on its host: an end nobody waited on recorded late, the state branch fetched and the kit gathered once.
tick a 1.2; tick a 1.3
mkdir -p "$T/shim"
shim() {  # shim <command> <bash test of "$@" that logs <what>> <what>
  printf '#!/usr/bin/env bash\nif %s; then echo "${CREW_TEST_HOST:-?} %s" >> %q; fi\nexec %q "$@"\n' "$2" "$3" "$T/reads.log" "$(command -v "$1")" > "$T/shim/$1"
  chmod +x "$T/shim/$1"
}
shim git '[[ " $* " == *" fetch "*refs/crew/* ]]' fetch
shim python3 '[[ ${1:-} == - && ${2:-} == "{"* ]]' gather
shim openspec true openspec
reads() { grep -c "^$box $1\$" "$T/reads.log" || true; }
stale=$(home_of $box)/.cache/crew/reads/OLDOLDOL; mkdir -p "$stale"; echo $box > "$stale/host"; touch -t 202601010000 "$stale"
: > "$T/reads.log"
PATH="$T/shim:$PATH" CREW_TEST_READS=$T/reads.log expect_ok crew status swb-1
for want in "swb-1-conductor" "swb-1-ops" "a  verify 3/3" "b  construct"; do has "$out" "$want"; done
eq "$(reads fetch) $(reads gather) $(reads openspec)" "1 1 0"
eq "$(ls -A "$(home_of $box)/.cache/crew/reads" 2>/dev/null)" ""
eq "$(field $box stage.end Ended stage/a/code)" "delivered"
eq "$(field $box stage.end Observed stage/a/code)" "late"
eq "$(field $box stage.end Tasks stage/a/code)" "3/3"
ok "crew status lists the roles and each slot's stage, fetches and gathers once, leaves no reading and removes one a day old, and records a delivered end nobody waited on, late"

expect_ok crew unit run a verify
eq "$(prompt_to swb-1-unit-1)" "'/opsx:verify a Changed and not declared in its Touches: a-work.'"
mkdir -p "$reports"; report=$reports/verify-a-20261008-1412.md; echo "the report" > "$report"
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered verify on a: the report is $report"
expect_ok crew trace report/verify-a-20261008-1412.md
has "$out" "stage/a/verify unit/a agent/swb-1-unit-1 → verify 3/3, delivered report/verify-a-20261008-1412.md"
ok "verify's prompt names what the unit changed and did not declare; the report it saves ends it, and crew trace finds it"

change "$kd/places/b" b 0 2; commit_all "$kd/places/b" "docs(b): the change"
touches b 'src/b/**' src/a/x
expect_ok crew unit run b code
eq "$(prompt_to swb-1-unit-2)" "'/opsx:apply b Its Touches overlap those of a, ahead of it in the bolt and not merged, on src/a/x against src/a/**; a'\"'\"'s change is $kd/places/a/openspec/changes/a/.'"
looks() { grep -c " agent get swb-1-unit-2$" "$CREW_TEST_LOG" || true; }
n=$(looks)
crew unit wait b --stuck 3600000 --timeout 1800000 > "$T/wait.out" 2>&1 &
waiting=$!
until_ok eval '(( $(looks) > n ))' || fail "the wait never looked at b"
kill -0 $waiting 2>/dev/null || fail "the wait returned before b's tasks were ticked: $(cat "$T/wait.out")"
tick b 1.1; tick b 1.2
wait $waiting || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(tail -1 "$T/wait.out")" "swb-1-unit-2 delivered code on b: every task is ticked (2/2) at $(short unit/b)"
ok "code's prompt names the Touches it overlaps of an unmerged unit ahead of it, and a wait that saw a task open sees it ticked at its next look"

# c and a meet on shared.txt: the conductor's wait forecasts it, puts c after a, and tells c.
: > "$T/reads.log"
PATH="$T/shim:$PATH" CREW_TEST_READS=$T/reads.log expect_ok crew unit run c construct
eq "$(reads fetch) $(reads gather) $(reads openspec)" "1 1 0"
eq "$(grep -c "^mac-studio fetch$" "$T/reads.log") $(grep -c "^mac-studio gather$" "$T/reads.log")" "1 0"
change "$kd/places/c" c 0 2; printf 'one\ntwo, as c has it\nthree\n' > "$kd/places/c/shared.txt"; commit_all "$kd/places/c" "docs(c): the change"
printf 'one\ntwo, as a has it\nthree\n' > "$kd/places/a/shared.txt"; commit_all "$kd/places/a" "feat(a): its line"
: > "$CREW_TEST_LOG"
expect_ok crew unit wait c
has "$out" "plan(tenant-environments): c after a, forecast to conflict (swb-1-conductor)"
has "$out" "swb-1-unit-3 delivered construct on c: its change is committed at $(short unit/c)"
has "$(told swb-1-unit-3)" "Your merge after a, ahead of you in the bolt and not merged, is forecast to conflict on shared.txt."
eq "$(told swb-1-unit-1)" ""
eq "$(plan -t Unit -e "Unit = 'c'" -P After)" "a"
eq "$(field $box forecast Reached unit/c)" "told"
ok "a unit run fetches once on each host and reads the kit once; a wait forecasts a conflict between two unmerged units, puts the later after the earlier, and tells only the later"

expect_ok crew unit run d construct
CREW_AGENT=swb-1-unit-4 expect_ok crew needs "a decision on which table holds tenants ZQXN"
eq "$out" "construct on d is ended, stopped short: swb-1-conductor is told what you need"
grep -qF "agent prompt swb-1-conductor '[crew tell from swb-1-unit-4] swb-1-unit-4 stopped short in construct on d. It needs: a decision on which table holds tenants ZQXN'" "$CREW_TEST_LOG" \
  || fail "the conductor was not told the agent's words, marked as from it"
eq "$(field $box stage.end Ended stage/d/construct)" "short"
[[ $(record_of $box) != *ZQXN* ]] || fail "a stop-short's words are in the run record"
ok "an agent's stop-short ends its stage and tells its conductor its words, which the run record never holds"

expect_fail "all 4 of swb-1's slots are in flight: unit-1 holds a; unit-2 holds b; unit-3 holds c; unit-4 holds d" crew unit run e construct
units_ws=$(herdr_state $box wldn-1 '.workspaces | to_entries[] | select(.value.label == "swb-1 units") | .key')
eq "$(herdr_state $box wldn-1 "[.panes[] | select(.workspace == \"$units_ws\")] | length")" "4"
has "$(field $box stage.start Refused stage/e/construct)" "all 4 of swb-1's slots are in flight"
status swb-1-unit-4 working
expect_fail "swb-1-unit-4 is working; add --force to end it anyway." crew unit run d construct
has "$(field $box stage.start Refused stage/d/construct)" "swb-1-unit-4 is working"
export CREW_TAKEN_WITHIN=1
as $box herdr --session wldn-1 stub leave swb-1-unit-4 1
: > "$CREW_TEST_LOG"
expect_ok crew unit run d construct "Name the tenant." --force
eq "$(sent swb-1-unit-4 "'/opsx:propose d Unit d. Name the tenant.'")" "2"
eq "$(field $box stage.start Refused stage/d/construct)" ""
has "$(cat "$stages")" "unit-4 d construct "
never="swb-1-unit-4 never took its construct prompt for d, sent twice; the stage never started and nothing is left typed in its pane: run it again with crew unit run d construct"
as $box herdr --session wldn-1 stub leave swb-1-unit-4 2
expect_fail "$never" crew unit run d construct
eq "$(field $box stage.start Refused stage/d/construct)" "$never"
lacks "$(cat "$stages")" "unit-4 d construct "
has "$(cat "$slots")" "unit-4 unit d"
unset CREW_TAKEN_WITHIN
ok "a fifth unit is refused with every slot in flight, a working agent is ended only with --force, a prompt left typed is sent again, and one never taken starts nothing and keeps its slot"

# The bolt takes a line of shared.txt that a, verified and waiting to merge, also changed: the next wait forecasts it,
# and starts a's settle stage.
printf 'one\ntwo, as the bolt has it\nthree\n' > "$bolt/shared.txt"; commit_all "$bolt" "feat: the bolt's own line"
: > "$CREW_TEST_LOG"
expect_ok crew unit wait b --timeout 0
eq "$(field $box forecast Reached unit/a bolt/tenant-environments)" "settle"
has "$(prompt_to swb-1-unit-1)" "'Settle a: Your branch is forecast to conflict with bolt/tenant-environments on shared.txt. Rebase your place onto the bolt (git rebase bolt/tenant-environments)"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(field $box stage.start By stage/a/settle)" "swb-1-conductor"
git -C "$kd/places/a" rebase -q bolt/tenant-environments >/dev/null 2>&1 && fail "a's rebase onto the bolt did not conflict"
printf 'one\ntwo, as a has it, and as the bolt has it\nthree\n' > "$kd/places/a/shared.txt"; git -C "$kd/places/a" add shared.txt
GIT_EDITOR=true git -C "$kd/places/a" rebase --continue >/dev/null 2>&1 || fail "a's rebase did not continue"
expect_ok crew unit wait a
has "$out" "swb-1-unit-1 delivered settle on a: its branch is at $(short unit/a), ready to merge"
expect_ok crew unit run a merge
eq "$(prompt_to swb-1-unit-1)" "'Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
has "$out" "Close your Pending You card for verify/a, if one is open, with what was done."
(cd "$kd/places/a" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge failed"
b_before=$(git -C "$k" rev-parse unit/b) c_before=$(git -C "$k" rev-parse unit/c)
expect_ok crew unit wait a
has "$out" "swb-1-unit-1 delivered merge on a: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
has "$out" "rebasing c onto bolt/tenant-environments conflicts: its place is as it was, and it is told"
git -C "$k" merge-base --is-ancestor bolt/tenant-environments unit/b || fail "b was not rebased onto the bolt"
[[ $(git -C "$k" rev-parse unit/b) != "$b_before" ]] || fail "b did not move"
eq "$(git -C "$k" rev-parse unit/c)" "$c_before"
eq "$(field $box unit.rebase From unit/b)" "unit/a"
ok "a forecast against the bolt starts a verified unit's settle stage, and the unit merges, each a fresh agent ended at its deliverable; the merge names the verify row's card, and its wait rebases a dependent onto the bolt and undoes a rebase that conflicts"

expect_ok crew status swb-1
has "$out" "swb-1-unit-1 is free: a has merged into its bolt"
has "$out" "$kd/places/a and unit/a are removed; the branch was at"
[[ ! -d $kd/places/a ]] || fail "a's place is still there"
ok "the next read frees a merged unit's slot and removes its place"

: > "$CREW_TEST_LOG"
expect_ok crew unit wait c --timeout 0
eq "$(field $box forecast Reached unit/c bolt/tenant-environments)" "prompt"
expect_ok crew unit run c code
has "$(prompt_to swb-1-unit-3)" "'/opsx:apply c "
has "$(prompt_to swb-1-unit-3)" " Your branch is forecast to conflict with bolt/tenant-environments on shared.txt."
has "$(field $box stage.start Forecast stage/c/code)" "$(field $box forecast Id unit/c bolt/tenant-environments)"
crew unit wait c --stuck 3600000 --timeout 1800000 > "$T/wait.out" 2>&1 &
waiting=$!
lock=$(home_of $box)/.local/state/swb-1-team/waits/unit-3.lock
until_ok eval '! python3 -c "import fcntl, sys; f = open(sys.argv[1], \"a\"); fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)" "$lock" 2>/dev/null' \
  || fail "the wait never took its lock"
expect_fail "a wait on swb-1-unit-3's stage is already running: its answer is the one to read" crew unit wait c
CREW_AGENT=swb-1-unit-3 expect_ok crew needs "the user's word ZQXM"
eq "$out" "code on c is ended, stopped short: swb-1-conductor's wait has what you need"
wait $waiting || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(tail -1 "$T/wait.out")" "swb-1-unit-3 stopped short in code on c. It needs: the user's word ZQXM"
grep -q "agent prompt swb-1-conductor .*ZQXM" "$CREW_TEST_LOG" && fail "the conductor was told words its wait already had"
[[ $(record_of $box) != *ZQXM* ]] || fail "a stop-short's words are in the run record"
ok "a conflict met at a rebase reaches a unit with no stage running in its next stage's prompt, once; a second wait on a stage is refused, and a stop-short's words are the running wait's answer"

unset CREW_AGENT
: > "$CREW_TEST_LOG"
expect_ok crew unit amend b "Unit b, said again."
has "$out" "swb-1-unit-2 has b: construct, in $kd/places/b"
eq "$(git --git-dir "$ws" log -2 --format=%s wldn/main)" "plan(tenant-environments): b amended, construct runs again ($me@mac-studio)
plan(tenant-environments): amend b ($me@mac-studio)"
eq "$(plan -t Unit -e "Unit = 'b'" -P Amended)" "$(git -C "$k" rev-parse unit/b)"
has "$(prompt_to swb-1-unit-2)" "'/opsx:propose b Unit b, said again. This unit'\"'\"'s intent was amended by the user; revise the existing change to it."
has "$(told swb-1-conductor)" "intent was amended by the user, and construct runs again on it in swb-1-unit-2: wait for it (crew unit wait b)"
eq "$(field $box stage.start By stage/b/construct)" "$me@mac-studio"
eq "$(field $box stage.start Amended stage/b/construct)" "yes"
eq "$(field $box stage.start Commit stage/b/construct)" "WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
has "$(git --git-dir "$ws" log -1 --format=%B wldn/main)" "Crew-Entry: $(field $box stage.start Id stage/b/construct)"
echo "Said again." >> "$kd/places/b/openspec/changes/b/design.md"; commit_all "$kd/places/b" "docs(b): written again"
export CREW_AGENT=swb-1-conductor
expect_ok crew unit wait b
has "$out" "swb-1-unit-2 delivered construct on b"
eq "$(plan -t Unit -e "Unit = 'b'" -P Amended)" ""
eq "$(subject)" "plan(tenant-environments): b constructed again, its mark cleared (swb-1-conductor)"
git --git-dir "$ws" show "wldn/main:runs/$box/$(date -u +%F).rec" | grep -q "^Act: stage.end" || fail "the write that clears the mark carries no construct end"
ok "the user's amendment marks the unit and runs its construct again in their name, tells the conductor, and the wait that ends it clears the mark"

fb=fix/tenant-environments/tidy fp=$kd/places/fix-tenant-environments--tidy
expect_ok crew fix swb-1 tidy "The banner flickers ZQXS."
has "$out" "swb-1-unit-1 has $fb: code, in $fp"
eq "$(prompt_to swb-1-unit-1)" "'Fix: The banner flickers ZQXS.'"
eq "$(field $box fix.start On)" "$fb bolt/tenant-environments agent/swb-1-unit-1"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' "refs/heads/$fb")" "bolt/tenant-environments"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $fp"
plan_tip=$(git --git-dir "$ws" rev-parse wldn/main)
expect_ok crew fix swb-1 tidy "It flickers still."
has "$out" "swb-1-unit-1 has $fb: code, in $fp"
has "$(cat "$slots")" "unit-1 fix $fb $fp"
eq "$(git --git-dir "$ws" rev-parse wldn/main)" "$plan_tip"
echo steady > "$fp/banner"; commit_all "$fp" "fix: the banner holds still"
expect_ok crew fix swb-1 tidy --wait
has "$out" "swb-1-unit-1 delivered fix $fb: its branch is at $(short $fb)"
expect_ok crew fix swb-1 tidy --merge
has "$out" "$fb does not carry the bolt onto main"
eq "$(prompt_to swb-1-unit-1)" "'Merge $fb into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
(cd "$fp" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge of the fix failed"
expect_ok crew fix swb-1 tidy --wait
has "$out" "swb-1-unit-1 delivered merge of $fb: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
[[ $(record_of $box) != *ZQXS* ]] || fail "a fix's words are in the run record"
ok "a fix takes a slot in its own place from the bolt and writes no plan, starts again there, ends at its commit, merges as a stage does and ends once the bolt holds it"

expect_ok crew prove swb-1
has "$out" "swb-1-ops is asked to prove bolt/tenant-environments"
grep -qF "agent prompt swb-1-ops '[crew tell from swb-1-conductor] Deploy the bolt and work the Proof in dev list of each of its units.'" "$CREW_TEST_LOG" \
  || fail "ops was not asked for the proof, marked as from the conductor"
proof=$reports/proof-tenant-environments-20261008-1630.md; echo "- ✅ sign-in: passed" > "$proof"
expect_ok crew prove swb-1 --wait
has "$out" "swb-1-ops delivered the proof of tenant-environments: $proof"
eq "$(field $box stage.end Delivered stage/tenant-environments/proof)" "proof/proof-tenant-environments-20261008-1630.md"
export CREW_TAKEN_WITHIN=1
as $box herdr --session wldn-1 stub leave swb-1-ops 2
expect_fail "the proof of tenant-environments never started, and no proof is owed: crew prove swb-1 asks ops again" crew prove swb-1
has "$out" "swb-1-ops did not take its prompt, sent twice; nothing is left typed"
eq "$(field $box stage.start Refused stage/tenant-environments/proof)" "swb-1-ops did not take its prompt, sent twice; nothing is left typed"
lacks "$(cat "$stages")" "ops tenant-environments proof"
unset CREW_TAKEN_WITHIN
ok "crew prove asks ops for the proof, owes its end, and its wait returns with the file ops saved; a request ops never took starts no proof"

# The user moves c to another team's bolt and drops d while its agent works, with the merged fix's place holding a file
# nobody committed: the reads that follow free each slot once its agent settles, remove d's place, and keep the fix's.
unset CREW_AGENT
echo stray > "$fp/note"
expect_ok crew bolt give swb-2 console-pages
said=$out
expect_ok crew unit move c console-pages
has "$out" "plan(console-pages): move c from tenant-environments"
said+=$'\n'$out
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/c)" "bolt/console-pages"
git -C "$k" merge-base --is-ancestor bolt/console-pages unit/c || fail "c was not rebased onto console-pages"
status swb-1-unit-4 working
expect_ok crew unit drop d "not wanted"
has "$out" "swb-1-unit-4 still holds d, dropped from the plan: its agent is working; it is freed once that settles"
said+=$'\n'$out
[[ -d $kd/places/d ]] || fail "d's place went with its agent working"
expect_fail "is working; add --force to end it anyway" crew unit free d --team swb-1
status swb-1-unit-4 idle
HOST=$box expect_ok crew unit free d
has "$out" "swb-1-unit-4 is free"
has "$out" "$kd/places/d and unit/d are removed; the branch was at"
export CREW_AGENT=swb-1-conductor
expect_ok crew status swb-1
said+=$'\n'$out
has "$said" "swb-1-unit-3 is free: c has left swb-1's bolt"
has "$said" "swb-1-unit-1 is free: $fb has merged into its bolt"
has "$said" "$fp is kept, and $fb with it: $fb has merged into bolt/tenant-environments, and it has uncommitted changes, which are the user's to keep or discard"
[[ -d $kd/places/c ]] || fail "c's place went with the slot it left"
[[ -d $fp ]] || fail "the fix's place went with its stray file"
eq "$(awk '{print $1, $3}' "$slots")" "unit-2 b"
rm "$fp/note"
ok "a moved unit's branch is rebased onto its new bolt; the team's reads free the slot it left and a merged fix's, keeping a merged place holding a stray file, and crew unit free a dropped unit's once its agent settles"

# The landing's rebase onto main conflicts on README.md, and a fix carries the bolt onto main: the bolt's commits
# replayed there with the conflict resolved. crew moves the bolt's branch to the fix's head and runs the kit's
# post-merge hooks on it, approved on the box.
echo "# switchboard-kit, the bolt's" > "$bolt/README.md"; commit_all "$bolt" "docs: the bolt's title"
mkdir -p "$k/.config"; printf '[post-merge]\nmark = "echo {{ target }} $(git rev-parse HEAD) > %s/hook-ran"\n' "$T" > "$k/.config/wt.toml"
echo "# switchboard-kit, main's" > "$k/README.md"; commit_all "$k" "docs: main's title, and a post-merge hook"
as $box bash -c 'cd "$1" && wt config approvals add --yes >/dev/null 2>&1' _ "$k" || fail "wt config approvals add failed"
n=$(git -C "$k" rev-list --count main..bolt/tenant-environments)
cm=fix/tenant-environments/carry-main cmp=$kd/places/fix-tenant-environments--carry-main
export CREW_AGENT=swb-1-conductor
expect_ok crew fix swb-1 carry-main "Carry the bolt onto main: the landing stopped on README.md."
has "$out" "$fp and $fb are removed; the branch was at"
git -C "$cmp" rebase main >/dev/null 2>&1 && fail "the replay did not stop on the title"
echo "# switchboard-kit, main's and the bolt's" > "$cmp/README.md"; git -C "$cmp" add README.md
GIT_EDITOR=true GIT_COMMITTER_DATE=$(ago -1) git -C "$cmp" rebase --continue >/dev/null 2>&1 || fail "the replay did not finish"
old=$(git -C "$k" rev-parse bolt/tenant-environments) new=$(git -C "$k" rev-parse "$cm")
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 carry-main --merge
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $cm carries the bolt's $n commits onto main (1 changed by the resolution)"
has "$out" "the bolt's checks are running on ${new:0:7}; prove the bolt again before it lands"
eq "$(git -C "$bolt" rev-parse HEAD)" "$new"
until_ok test -s "$T/hook-ran" || fail "the post-merge hook never ran"
eq "$(cat "$T/hook-ran")" "bolt/tenant-environments $new"
has "$(field $box fix.carry From "$cm")" "agent/swb-1-unit-"
grep -q "agent prompt .* 'Merge $cm" "$CREW_TEST_LOG" && fail "a carrying fix was sent a merge prompt"
has "$out" "is free: $cm has merged into its bolt"
has "$out" "$cmp and $cm are removed; the branch was at"
ok "a fix that carries the bolt onto main becomes its head, with no merge stage, and the kit's post-merge hooks run on it; the read after frees it, and removes a merged place once its stray file goes"

# The bolt lands once its units have: b and e are dropped, a's change reaches main, and a batch has held it.
unset CREW_AGENT
expect_fail "unit a has not landed on main: it is merged" crew bolt land tenant-environments
by_hand 'p.remove(p.unit("e"))'
expect_ok crew unit drop b "folded into a"
has "$out" "swb-1-unit-2 is free: b was dropped from the plan"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
git -C "$k" merge -q --ff-only bolt/tenant-environments
as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act review.batch --field Batch=1 \
  --field "Units=a:swb-1@$(field $box stage.end Delivered stage/a/construct | sed 's/.*@//')" >/dev/null
: > "$CREW_TEST_LOG"
expect_ok crew bolt land tenant-environments
has "$out" "tenant-environments has landed and swb-1 holds no bolt"
has "$out" "$bolt and bolt/tenant-environments are removed; the branch was at"
grep -qF "agent prompt swb-1-conductor '[crew] plan(tenant-environments): land the bolt ($me@mac-studio). Close any Pending You card you have open for verify/a or land/tenant-environments.'" \
  "$CREW_TEST_LOG" || fail "the conductor was not told to close its cards:"$'\n'"$(calls)"
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -c)" "0"
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still there"
ok "a drop frees the last slot and closes the units workspace; the bolt lands once every unit has, removing its worktree and what is over, and its conductor is told which cards to close"

expect_ok crew bolt drop console-pages "the portal lists them"
has "$out" "$kd/bolts/console-pages and bolt/console-pages are removed; the branch was at"
has "$out" "$kd/places/c and unit/c are removed; the branch was at"
eq "$(git --git-dir "$ws" log -1 --format=%b wldn/main | head -1)" "the portal lists them"
ok "dropping a held bolt removes its worktree and its units' places, with the reason in the commit"
