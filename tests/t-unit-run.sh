# Unit slots and crew unit run <unit> construct|code|verify|merge: a free slot is taken, refused when every slot
# is in flight; construct makes places/<unit> on unit/<unit> from the bolt; each stage ends the slot's agent and
# starts a fresh one from that stage's definition, then sends its prompt; code waits for the approval and
# verify for every task ticked.
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
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v "/exit" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }

expect_fail "bolt tenant-environments is held by no team yet" crew unit run a construct
CREW_AGENT= crew bolt give swb-1 >/dev/null 2>&1
expect_fail "unit queued-one is queued" crew unit run queued-one construct

expect_ok crew unit run a construct
has "$out" "swb-1-unit-1 has a: construct, in $kd/places/a"
eq "$(cat "$slots")" "unit-1 unit a $kd/places/a"
eq "$(git -C "$kd/places/a" branch --show-current)" "unit/a"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/a)" "bolt/tenant-environments"
eq "$(cat "$kd/places/a/.prepared")" "$k"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/a"
p1=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-1") | .key')
eq "$(prompt_to "$p1")" "'/opsx:propose a Unit a. Sources: books/x.md; switchboard-kit:docs/y.md.'"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1 units"
ok "construct takes a free slot, makes the unit's place from the bolt, and starts a fresh agent at high effort"

expect_fail "unit b is waiting: it comes after a, not yet merged into its bolt" crew unit run b construct
eq "$(wc -l < "$slots" | tr -d ' ')" "1"
[[ ! -d $kd/places/b ]] || fail "b's place was made"
ok "a unit waiting on another is refused, and takes no slot"

change "$kd/places/a" a 0 3; commit_all "$kd/places/a" "docs(a): the change"
expect_fail "unit a is in review: code waits until the user approves it (crew unit approve a)" crew unit run a code
crew unit approve a >/dev/null
: > "$CREW_TEST_LOG"
expect_ok crew unit run a code
has "$out" "swb-1-unit-1 has a: code"
grep -q "^$box wldn-1 agent prompt $p1 /exit" "$CREW_TEST_LOG" || fail "the construct agent was not ended"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to "$p1")" "'/opsx:apply a'"
ok "code is refused before the approval, then starts fresh in the same slot at xhigh"

sed -i '' 's/- \[ \] 1.1/- [x] 1.1/' "$kd/places/a/openspec/changes/a/tasks.md"; commit_all "$kd/places/a" "feat(a): task 1"
expect_fail "unit a is in code, with these tasks still open: 1.2 task 2; 1.3 task 3" crew unit run a verify
sed -i '' 's/- \[ \]/- [x]/' "$kd/places/a/openspec/changes/a/tasks.md"; commit_all "$kd/places/a" "feat(a): tasks 2 and 3"
expect_ok crew unit run a verify
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to "$p1")" "'/opsx:verify a'"
expect_ok crew unit run a code "Fix these findings from the verify: the error names no unit."
eq "$(prompt_to "$p1")" "'/opsx:apply a Fix these findings from the verify: the error names no unit.'"
expect_ok crew unit run a merge
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to "$p1")" "'Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
ok "verify is refused until every task is ticked; verify and merge start fresh at their efforts"

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
