# After holds a dependent's construct and its merge, never its code, and the dependent builds on its After units'
# work as it stands: a unit after one whose change is not committed is waiting and refused construct; once that change
# is committed, construct is accepted and the dependent's new place takes its head; an After unit constructed again
# reaches its dependents, which are not held; when it merges, each dependent's place is rebased onto the bolt while its
# agent is idle, the bolt's commits dropping out; and the dependent's merge is refused, naming it, until it has
# merged. Each scenario of the bolt-plan and bolt-teams specs on After.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew unit add a "Unit a." --bolt tenant-environments >/dev/null
crew unit add b "Unit b." --bolt tenant-environments --after a >/dev/null
crew unit add c "Unit c." --bolt tenant-environments --after a >/dev/null
crew unit add d "Unit d." --bolt tenant-environments --after a >/dev/null
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
bolt=$kd/bolts/tenant-environments
pane() { herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key"; }
told() { grep "^$box wldn-1 agent prompt $1 '\[crew\]" "$CREW_TEST_LOG" || true; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v "/exit" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
entry() {  # entry <act> <object> <jq>: of the last entry of the act on the object, on the box
  as $box python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and sys.argv[3] in e["On"]]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$1" "$2" | jq -r "$3"
}
short() { git -C "$k" rev-parse --short=7 "$1"; }

expect_ok crew unit run a construct
eq "$(stage b)" "waiting"
expect_fail "unit b is waiting: it comes after a, whose change is not committed yet" crew unit run b construct
[[ ! -d $kd/places/b ]] || fail "b's place was made"
ok "a dependency still in construct holds its dependent's construct"

change "$kd/places/a" a 0 2; commit_all "$kd/places/a" "docs(a): the change"; crew unit wait a >/dev/null
echo a > "$kd/places/a/a-work"; rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \] 1.1/- [x] 1.1/'
commit_all "$kd/places/a" "feat(a): task 1"
eq "$(stage a)" "code"; eq "$(stage b)" "ready"
expect_ok crew unit run b construct
has "$out" "has b: construct, in $kd/places/b"
git -C "$k" merge-base --is-ancestor unit/a unit/b || fail "b's place does not hold a's work"
eq "$(entry stage.start stage/b/construct .Took)" "a@$(short unit/a)"
crew unit run c construct >/dev/null
git -C "$k" merge-base --is-ancestor unit/a unit/c || fail "c's place does not hold a's work"
crew unit run d construct >/dev/null
change "$kd/places/d" d 0 2; echo "a, as d has it" > "$kd/places/d/a-work"; commit_all "$kd/places/d" "docs(d): the change, and a's file its way"
crew unit wait d >/dev/null
ok "a dependency whose change is committed, in code and not merged, lets its dependents' construct start, and each new place takes its head"

change "$kd/places/b" b 2 2; commit_all "$kd/places/b" "feat(b): done"; crew unit wait b >/dev/null
change "$kd/places/c" c 0 2; commit_all "$kd/places/c" "docs(c): the change"; crew unit wait c >/dev/null
crew unit run c code >/dev/null
eq "$(stage b)" "verify"
expect_fail "unit b merges after a, not yet merged into bolt/tenant-environments" crew unit run b merge
ok "a dependent's merge is refused, naming the unit it comes after, while that unit has not merged"

# a is constructed again with the user's words, while its dependents are in code and in verify.
crew unit run a construct "Say what the tenant sees." >/dev/null
echo "Say more." >> "$kd/places/a/openspec/changes/a/design.md"; commit_all "$kd/places/a" "docs(a): written again"
crew unit wait a >/dev/null
: > "$CREW_TEST_LOG"
expect_ok crew unit wait c --timeout 0
has "$(told swb-1-unit-3)" "a, which you come after, was constructed again, and you are not held for it"
has "$(told swb-1-unit-3)" "change is $kd/places/a/openspec/changes/a/."
eq "$(entry amendment unit/b .Reached)" "prompt"
eq "$(entry amendment unit/c .Reached)" "told"
eq "$(stage c)" "planned"
: > "$CREW_TEST_LOG"
expect_ok crew unit wait c --timeout 0
eq "$(told swb-1-unit-3)" ""
expect_ok crew unit run b verify
has "$(prompt_to "$(pane swb-1-unit-2)")" "'/opsx:verify b a, which you come after, was constructed again"
ok "an After unit constructed again reaches each dependent once, told or in its next prompt, and holds neither"

# a merges as wt merge does: rebased onto a bolt that has moved, then fast-forwarded.
echo bolt > "$bolt/bolt-work"; commit_all "$bolt" "feat: the bolt moves"
echo "a, done" > "$kd/places/a/a-work"; rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/a" "feat(a): done"
git -C "$kd/places/a" rebase -q bolt/tenant-environments; git -C "$bolt" merge -q --ff-only unit/a
eq "$(stage a)" "merged"
as $box herdr --session wldn-1 stub status "$(pane swb-1-unit-3)" working
cb=$(git -C "$k" rev-parse unit/c)
HOST=$box expect_ok crew status swb-1
has "$out" "c waits to be rebased onto bolt/tenant-environments, now that a merged: its agent is working"
has "$out" "b is rebased onto bolt/tenant-environments, now that a merged"
eq "$(git -C "$k" rev-parse unit/c)" "$cb"
git -C "$k" merge-base --is-ancestor bolt/tenant-environments unit/b || fail "b was not rebased onto the bolt"
eq "$(git -C "$k" log --format=%s bolt/tenant-environments..unit/b | tr '\n' ';')" "feat(b): done;"
eq "$(entry unit.rebase unit/b '.From | join(" ")')" "unit/a"
as $box herdr --session wldn-1 stub status "$(pane swb-1-unit-3)" idle
HOST=$box expect_ok crew status swb-1
has "$out" "c is rebased onto bolt/tenant-environments, now that a merged"
git -C "$k" merge-base --is-ancestor bolt/tenant-environments unit/c || fail "c was not rebased onto the bolt"
HOST=$box expect_ok crew status swb-1
lacks "$out" "rebased"
ok "once the dependency merges, each dependent's place is rebased onto the bolt while its agent is idle, the bolt's commits dropping out, and once"

dh=$(git -C "$k" rev-parse unit/d)
has "$out" "rebasing d onto bolt/tenant-environments conflicts: its place is as it was, and it is told"
eq "$(git -C "$k" rev-parse unit/d)" "$dh"; eq "$(git -C "$kd/places/d" status --porcelain)" ""
: > "$CREW_TEST_LOG"
expect_ok crew unit wait c --timeout 0
eq "$(entry forecast unit/d '[(.On | join(" ")), .Paths, .Reached] | join(" | ")')" "unit/d bolt/tenant-environments | a-work | prompt"
eq "$(git -C "$k" rev-parse unit/d)" "$dh"
ok "a rebase that conflicts is undone, the place as it was, and reaches the dependent as a conflict does"

expect_ok crew unit run b merge
has "$(prompt_to "$(pane swb-1-unit-2)")" "'Merge b into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
ok "a dependent merges once the unit it comes after has merged"
