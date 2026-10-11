# Unit slots and crew unit run <unit> construct|code|verify|merge: a free slot is taken, refused when every slot
# is in flight; construct makes places/<unit> on unit/<unit> from the bolt; each stage ends the slot's agent and
# starts a fresh one from that stage's definition, then sends its prompt; construct waits for each After unit's change,
# code for the unit's own change to be committed, with no review between, and verify for every task ticked. A stage
# that ends a rail row names the row's card to the conductor that owns it. A stage begins only once its agent's
# transcript shows its prompt, sent once more when it does not; else it never started, and when crew cannot tell,
# nothing more is sent or pressed.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
mkdir -p "$k/.devenv/profile/bin"
printf '#!/usr/bin/env bash\necho "$KIT" > .prepared\n' > "$k/.devenv/profile/bin/crew-prepare"; chmod +x "$k/.devenv/profile/bin/crew-prepare"
printf '.devenv/\n.prepared\n' > "$k/.gitignore"; commit_all "$k" "chore: ignore what preparing makes"
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew unit add a "Unit a." --bolt tenant-environments --source books/x.md --source switchboard-kit:docs/y.md >/dev/null
crew unit add b "Unit b." --bolt tenant-environments --after a >/dev/null
for u in c d e f; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew unit add queued-one "Later." --repo switchboard-kit >/dev/null
export CREW_AGENT=swb-1-conductor
slots=$(home_of $box)/.local/state/swb-1-team/slots
last_launch() { tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '([.argv | to_entries[] | select(.value == "--name") | .key][0]) as $i | "\(.argv[0:4] | join(" ")) | \(.argv[$i + 1]) | \(.cwd)"'; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }

expect_fail "bolt tenant-environments is held by no team yet" crew unit run a construct
CREW_AGENT= crew bolt give swb-1 >/dev/null 2>&1
expect_fail "unit queued-one is queued" crew unit run queued-one construct

expect_ok crew unit run a construct
has "$out" "swb-1-unit-1 has a: construct, in $kd/places/a"
lacks "$out" "Pending You"
eq "$(cat "$slots")" "unit-1 unit a $kd/places/a"
eq "$(git -C "$kd/places/a" branch --show-current)" "unit/a"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/a)" "bolt/tenant-environments"
eq "$(cat "$kd/places/a/.prepared")" "$k"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/a"
p1=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-1") | .key')
eq "$(prompt_to swb-1-unit-1)" "'/opsx:propose a Unit a. Sources: books/x.md; switchboard-kit:docs/y.md.'"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1 units"
ok "construct takes a free slot, makes the unit's place from the bolt, and starts a fresh agent at high effort"

expect_fail "unit b is waiting: it comes after a, whose change is not committed yet" crew unit run b construct
eq "$(wc -l < "$slots" | tr -d ' ')" "1"
[[ ! -d $kd/places/b ]] || fail "b's place was made"
ok "a unit after one whose change is not committed is refused construct, and takes no slot"

expect_fail "unit a is in construct: code waits until its change is committed" crew unit run a code
change "$kd/places/a" a 0 3; commit_all "$kd/places/a" "docs(a): the change"
eq "$(stage a)" "planned"; eq "$(stage b)" "ready"
: > "$CREW_TEST_LOG"
expect_ok crew unit run a code
has "$out" "swb-1-unit-1 has a: code"
grep -q "^$box wldn-1 agent prompt $p1 /exit" "$CREW_TEST_LOG" || fail "the construct agent was not ended"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:apply a'"
ok "code is refused until the change is committed, then starts fresh in the same slot at xhigh with nobody asked to approve"

# A stage begins only when its agent takes its prompt (teams.15): sent once more when it was left typed, and when the
# second is not taken either, the stage never started, and the same command run again starts it.
export CREW_TAKEN_WITHIN=1
stages=$(home_of $box)/.local/state/swb-1-team/stages
starts() {  # starts <object>: each stage.start on it in the box's run record, "started" or "refused: <why>", one a line
  as $box python3 -c 'import glob, os, sys; sys.path.insert(0, sys.argv[1]); import record
for e in sorted((e for f in glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec")) for e in record.parse(open(f).read())
                 if e["Act"] == "stage.start" and sys.argv[2] in e["On"]), key=lambda e: (e["At"], e["Id"])):
    print("refused: " + e["Refused"] if e.get("Refused") else "started")' "$CREW/plugin/lib" "$1"
}
sent() { grep -c "^$box wldn-1 agent prompt swb-1-unit-1 '/opsx:apply a'$" "$CREW_TEST_LOG" || true; }
n=$(starts stage/a/code | wc -l)
as $box herdr --session wldn-1 stub leave swb-1-unit-1 1
: > "$CREW_TEST_LOG"
expect_ok crew unit run a code
has "$out" "swb-1-unit-1 has a: code"
eq "$(sent)" "2"
eq "$(starts stage/a/code | wc -l | tr -d ' ')" "$((n + 1))"
eq "$(starts stage/a/code | tail -1)" "started"
has "$(cat "$stages")" "unit-1 a code "
ok "a code stage whose prompt was left typed is sent it once more, and starts once"

never="swb-1-unit-1 never took its code prompt for a, sent twice; the stage never started and nothing is left typed in its pane: run it again with crew unit run a code"
as $box herdr --session wldn-1 stub leave swb-1-unit-1 2
: > "$CREW_TEST_LOG"
expect_fail "$never" crew unit run a code
lacks "$out" "swb-1-unit-1 has a: code"
eq "$(sent)" "2"
eq "$(starts stage/a/code | tail -1)" "refused: $never"
lacks "$(cat "$stages")" "unit-1 a code "
eq "$(cat "$slots")" "unit-1 unit a $kd/places/a"
eq "$(herdr_state $box wldn-1 '.agents[] | select(.name == "swb-1-unit-1") | .typed // ""')" ""
expect_ok crew unit wait a --timeout 0
has "$out" "code on a has ended"
expect_ok crew unit run a code
has "$out" "swb-1-unit-1 has a: code"
eq "$(starts stage/a/code | tail -1)" "started"
has "$(cat "$stages")" "unit-1 a code "
unset CREW_TAKEN_WITHIN
ok "a code stage whose prompt was not taken twice never started: refused, owed nothing, its slot held; run again, it starts"

rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \] 1.1/- [x] 1.1/'; commit_all "$kd/places/a" "feat(a): task 1"
expect_fail "unit a is in code, with these tasks still open: 1.2 task 2; 1.3 task 3" crew unit run a verify
rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/a" "feat(a): tasks 2 and 3"
expect_ok crew unit run a verify
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:verify a'"
expect_ok crew unit run a code "Fix these findings from the verify: the error names no unit."
eq "$(prompt_to swb-1-unit-1)" "'/opsx:apply a Fix these findings from the verify: the error names no unit.'"
expect_ok crew unit run a merge
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
ok "verify is refused until every task is ticked; verify and merge start fresh at their efforts"

# A merge whose prompt crew cannot tell was taken (teams.15): the prompt is left typed and the agent goes on a question,
# so once the time passes crew reads it waiting there, sends nothing more and presses nothing; the stage never started.
export CREW_TAKEN_WITHIN=1
merge="'Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
cant="crew could not tell whether swb-1-unit-1 took its merge prompt for a: it is waiting on a question in its pane; nothing more was sent, and the stage is taken as never started: run it again with crew unit run a merge"
as $box herdr --session wldn-1 stub leave swb-1-unit-1 1 blocked
: > "$CREW_TEST_LOG"
expect_fail "$cant" crew unit run a merge
lacks "$out" "swb-1-unit-1 has a: merge"
eq "$(grep -cxF "$box wldn-1 agent prompt swb-1-unit-1 $merge" "$CREW_TEST_LOG")" "1"
grep -q "agent send-keys swb-1-unit-1 ctrl+c" "$CREW_TEST_LOG" && fail "crew pressed ctrl+c in a pane it could not read:"$'\n'"$(calls)"
eq "$(starts stage/a/merge | tail -1)" "refused: $cant"
lacks "$(cat "$stages")" "unit-1 a merge "
eq "$(cat "$slots")" "unit-1 unit a $kd/places/a"
as $box herdr --session wldn-1 stub status swb-1-unit-1 idle
unset CREW_TAKEN_WITHIN
ok "a merge crew cannot tell was taken is neither sent again nor pressed, and is refused, owed nothing, its slot held"

for u in c d e; do crew unit run $u construct >/dev/null; done
expect_fail "all 4 of swb-1's slots are in flight: unit-1 holds a; unit-2 holds c; unit-3 holds d; unit-4 holds e" crew unit run f construct
[[ ! -d $kd/places/f ]] || fail "f's place was made"
units_ws=$(herdr_state $box wldn-1 '.workspaces | to_entries[] | select(.value.label == "swb-1 units") | .key')
eq "$(herdr_state $box wldn-1 "[.panes[] | select(.workspace == \"$units_ws\")] | length")" "4"
ok "a fifth unit is refused while all four slots are in flight, naming the units they hold"

p2=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-2") | .key')
as $box herdr --session wldn-1 stub status "$p2" working
expect_fail "swb-1-unit-2 is working; add --force to end it anyway." crew unit run c construct
expect_ok crew unit run c construct "Use the words the user gave." --force
ok "a working stage is ended only with --force"

# The stage that ends a rail row names its card: construct, code or merge on a unit in verify ends its verify
# report's row. Construct again on a planned unit marks it amended and ends no row.
change "$kd/places/d" d 0 2; commit_all "$kd/places/d" "docs(d): the change"
eq "$(stage d)" "planned"
# A construct refused because the slot's agent is working starts nothing, so it names no card, to anyone.
p3=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-3") | .key')
as $box herdr --session wldn-1 stub status "$p3" working
: > "$CREW_TEST_LOG"
for who in swb-1-conductor ""; do
  CREW_AGENT=$who expect_fail "swb-1-unit-3 is working; add --force to end it anyway." crew unit run d construct "Name the tenant in the title."
  lacks "$out" "Pending You"
done
grep -q "agent prompt swb-1-conductor" "$CREW_TEST_LOG" && fail "the conductor was told to close a card for a stage that never started"
as $box herdr --session wldn-1 stub status "$p3" idle
expect_ok crew unit run d construct "Name the tenant in the title."
lacks "$out" "Pending You"
eq "$(stage d)" "construct"
expect_fail "unit d was amended and its change is being written again, and has not been committed" crew unit run d code
change "$kd/places/e" e 2 2; commit_all "$kd/places/e" "feat(e): done"
eq "$(stage e)" "verify"
expect_ok crew unit run e verify
lacks "$out" "Pending You"
for s in code merge; do
  expect_ok crew unit run e $s
  has "$out" "Close your Pending You card for verify/e, if one is open, with what was done."
done
p=$(as chuck-herdr-alpha herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as chuck-herdr-alpha herdr --session wldn-1 stub agent "$p" swb-1-conductor  # up, so it can be told
: > "$CREW_TEST_LOG"
CREW_AGENT= expect_ok crew unit run e code
lacks "$out" "Pending You"
grep -qF "agent prompt swb-1-conductor '[crew] $me@mac-studio ran code on unit e. Close your Pending You card for verify/e, if one is open, with what was done.'" \
  "$CREW_TEST_LOG" || fail "the conductor was not told to close its verify card:"$'\n'"$(calls)"
ok "construct again on a planned unit names no card, and code or merge on one in verify name the verify row's card: shown to its conductor, told to it otherwise"
