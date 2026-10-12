# A fix, a proof and the plan moving under a team, through the crew command on the stubs (tests.11, record 0022), a part
# of the units journey (t-journey-units): a fix takes a slot in its own place from the bolt, writes no plan and merges
# as a stage does; crew prove asks ops for the proof and its wait returns with the file ops saved; a moved unit's branch
# is rebased onto its new bolt; and the team's reads free the slots a moved unit, a merged fix and a dropped unit leave,
# keeping a place that holds a stray file.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abcd"]
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
export CREW_AGENT=swb-1-conductor
for u in a b c d; do crew unit run $u construct >/dev/null; done
CREW_AGENT= crew unit drop a "not this one" >/dev/null; mkdir -p "$reports"
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
