# A verified unit fixed in its one round, settled and merged, through the crew command on the stubs (tests.11, record
# 0022), a part of the units journey (t-journey-units): a forecast against the bolt starts the settle stage of a unit
# verified and then fixed once (teams.14, teams.17); a dependent holding that unit's work as its place took it is not
# forecast against the unit for the settle's revision of it; a stop-short of the unit's merge for an archive it can
# make itself is refused once in the stage, and a second is passed on; the unit merges through sluice once its change
# is archived; the merge's wait rebases a dependent onto the bolt, leaving out that work as it took it, and undoes a
# rebase that conflicts; the next read frees the merged unit's slot and removes its place; the dependent whose rebase
# conflicted is told how to make that rebase's upstream again, its older forecast against the bolt dropped; and of two
# unmerged units forecast to conflict, the later's settle that stops short lifts the order a forecast wrote before
# (plan.13, teams.12), and its next settle, taking the earlier's work, puts it after the earlier, holding its merge.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world 'unit("a", "tenant-environments"); unit("b", "tenant-environments", "a"); unit("c", "tenant-environments", "a")'
export CREW_AGENT=swb-1-conductor
crew unit run a construct >/dev/null
change "$kd/places/a" a 3 3; commit_all "$kd/places/a" "feat(a): its change, done"
crew unit wait a >/dev/null; crew unit run a verify >/dev/null
mkdir -p "$reports"; echo "the report" > "$reports/verify-a-20261008-1412.md"; crew unit wait a >/dev/null
crew unit run b construct >/dev/null; change "$kd/places/b" b 0 2; commit_all "$kd/places/b" "docs(b): the change"; crew unit wait b >/dev/null
crew unit run a code "Fix every finding the verify report at $reports/verify-a-20261008-1412.md marks fix." >/dev/null
printf 'one\ntwo, as a has it\nthree\n' > "$kd/places/a/shared.txt"; commit_all "$kd/places/a" "fix(a): its line, as its report marked"
crew unit wait a >/dev/null
crew unit run c construct >/dev/null; change "$kd/places/c" c 0 2
printf 'one\ntwo, as c has it\nthree\n' > "$kd/places/c/shared.txt"; commit_all "$kd/places/c" "docs(c): the change"; crew unit wait c >/dev/null
# The bolt takes a line of shared.txt that a, verified, fixed and waiting to merge, also changed: the next wait forecasts it,
# and starts a's settle stage.
on_branch "$k" bolt/tenant-environments "feat: the bolt's own line" shared.txt $'one\ntwo, as the bolt has it\nthree\n'
: > "$CREW_TEST_LOG"
expect_ok crew unit wait b --timeout 0
eq "$(field $box forecast Reached unit/a bolt/tenant-environments)" "settle"
has "$(prompt_to swb-1-unit-1)" "'Settle a: Your branch is forecast to conflict with bolt/tenant-environments on shared.txt. Rebase your place onto the bolt (git rebase bolt/tenant-environments)"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(field $box stage.start By stage/a/settle)" "swb-1-conductor"
git -C "$kd/places/a" rebase -q bolt/tenant-environments >/dev/null 2>&1 && fail "a's rebase onto the bolt did not conflict"
printf 'one\ntwo, as a has it, and as the bolt has it\nthree\n' > "$kd/places/a/shared.txt"; git -C "$kd/places/a" add shared.txt
GIT_EDITOR=true git -C "$kd/places/a" rebase --continue >/dev/null 2>&1 || fail "a's rebase did not continue"
# The settle also revises a's design into its change, which b's place holds as it took it: from the bolt both started
# on, git sees b and a change it two ways; from the head b took, b adds nothing to it, and b, after a, is forecast
# nothing against a.
printf '# Design\n\nz, as it stands on the bolt\n' > "$kd/places/a/openspec/changes/a/design.md"
git -C "$kd/places/a" commit -qam "fixup! feat(a): its change, done"
GIT_SEQUENCE_EDITOR=true git -C "$kd/places/a" rebase -q -i --autosquash bolt/tenant-environments >/dev/null 2>&1 || fail "a's settle did not fold its design in"
expect_ok crew unit wait a
has "$out" "swb-1-unit-1 delivered settle on a: its branch is at $(short unit/a), ready to merge"
eq "$(field $box forecast Heads unit/b unit/a)" ""
expect_ok crew unit run a merge
eq "$(prompt_to swb-1-unit-1)" "'Merge a into bolt/tenant-environments: sluice submit bolt/tenant-environments --no-wait --json'"
lacks "$out" "Pending You card"
# a's place holds a change no unit has, every task ticked and touching a's specs, as main's left open: a's merge
# archives it first, and a stop-short for it is refused, the stage still owed.
change "$kd/places/a" left 3 3; commit_all "$kd/places/a" "docs(left): a change main left open"
CREW_AGENT=swb-1-unit-1 expect_fail "merge on a does not stop short for archives it can make: unit/a holds left open" \
  crew needs "openspec archive a refuses: its delta modifies a requirement left adds"
eq "$(field $box stage.end Ended stage/a/merge)" ""
# Told, it stops short again in the same stage only when openspec refuses one of them: that stop-short is passed on,
# and the conductor runs the merge again, crew having ended the agent.
HOST=$box CREW_AGENT=swb-1-unit-1 expect_ok crew needs "openspec archive left refuses: a requirement it modifies is not in the specs ZQXP"
eq "$out" "merge on a is ended, stopped short: swb-1-conductor is told what you need. crew ends this session once your turn ends: end it now."
until_ok grep -qF "swb-1-unit-1 is ended: its stage stopped short" "$(home_of $box)/.local/state/swb-1-team/short/unit-1.log" \
  || fail "crew never ended the agent whose merge stopped short"
grep -qF "agent prompt swb-1-conductor '[crew tell from swb-1-unit-1] swb-1-unit-1 stopped short in merge on a. It needs: openspec archive left refuses: a requirement it modifies is not in the specs ZQXP'" "$CREW_TEST_LOG" \
  || fail "the conductor was not told the merge's second stop-short"
eq "$(field $box stage.end Ended stage/a/merge)" "short"
expect_ok crew unit run a merge
mkdir -p "$kd/places/a/openspec/changes/archive"; git -C "$kd/places/a" mv openspec/changes/left openspec/changes/archive/2026-10-13-left
git -C "$kd/places/a" commit -qm "docs(openspec): archive left"
git -C "$kd/places/a" mv openspec/changes/a openspec/changes/archive/2026-10-13-a
git -C "$kd/places/a" commit -qm "docs(openspec): archive a"
merge_as swb-1-unit-1 "$kd/places/a" bolt/tenant-environments || fail "a's submission failed"
eq "$(git -C "$k" log -1 --format='%an %(trailers:key=Sluice-Result,valueonly)' bolt/tenant-environments)" "sluice passed (stub)"
b_before=$(git -C "$k" rev-parse unit/b) c_before=$(git -C "$k" rev-parse unit/c)
expect_ok crew unit wait a
has "$out" "swb-1-unit-1 delivered merge on a: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
has "$out" "rebasing c onto bolt/tenant-environments conflicts: its place is as it was, and it is told"
git -C "$k" merge-base --is-ancestor bolt/tenant-environments unit/b || fail "b was not rebased onto the bolt: $out"
[[ $(git -C "$k" rev-parse unit/b) != "$b_before" ]] || fail "b did not move"
# b's rebase leaves out a's change as b's place took it, which a's settle rewrote: only b's own commit is replayed.
has "$out" "b is rebased onto bolt/tenant-environments, now that a merged"
eq "$(git -C "$k" log --format=%s bolt/tenant-environments..unit/b)" "docs(b): the change"
eq "$(git -C "$k" rev-parse unit/c)" "$c_before"
eq "$(field $box unit.rebase From unit/b)" "unit/a"
# c's own line meets a's settled one: its rebase, which left out a's work as c's place took it, conflicts there.
c_took=$(field $box stage.start Took stage/c/construct); c_took=${c_took#a@}
eq "$(field $box forecast Took unit/c bolt/tenant-environments)" "a@$c_took"
# The merge's wait frees its slot and removes its place and branch as it lands, not at the conductor's next read.
has "$out" "swb-1-unit-1 is free: a has merged into its bolt"
has "$out" "$kd/places/a and unit/a are removed; the branch was at"
[[ ! -d $kd/places/a ]] || fail "a's place is still there"
ok "a forecast against the bolt starts the settle stage of a unit verified and fixed once, a dependent is forecast nothing for the unit's own work its place took, and the unit merges with its change archived, each a fresh agent ended at its deliverable; no card is named, and the merge's wait rebases a dependent onto the bolt, leaving out the unit's work as it took it, undoes a rebase that conflicts, and frees the slot and removes the place and branch"

expect_ok crew status swb-1
lacks "$out" "swb-1-unit-1 is free"; lacks "$out" "places/a"
ok "the next read finds a merged unit's slot freed and its place gone already"

# c's next prompt carries its rebase's conflict, naming the upstream that rebase used, made again by the command given,
# and not c's older forecast against the bolt, read before a merged, which this one replaces.
expect_ok crew unit run c code
has "$(prompt_to swb-1-unit-3)" "work as your place took it, which the bolt holds as merged (git rebase --onto bolt/tenant-environments \$(git commit-tree -p bolt/tenant-environments -p $c_took -m upstream"
lacks "$(prompt_to swb-1-unit-3)" "(git rebase bolt/tenant-environments)"
ok "a dependent whose rebase conflicts is told the upstream crew's rebase used, as a command that makes it again, and only its newest forecast against the bolt"

# d and e, ahead of b and c in the file and after nothing, each add other.txt, d once e is verified and waits to merge.
# e stands after d as a forecast's own write put it before a forecast stopped ordering two units: the plan's After and
# its unit.after entry under that write's subject, both written here. The next wait forecasts e against d and starts
# e's settle, which stops short, nothing to change: its wait lifts the order, in the conductor's name.
by_hand 'unit("d", "tenant-environments"); unit("e", "tenant-environments")
p.insert(p.unit("d"), before=p.unit("b")); p.insert(p.unit("e"), before=p.unit("b"))'
slot_of() { awk -v u="$1" '$3 == u {print $1}' "$slots"; }
crew unit run d construct >/dev/null; change "$kd/places/d" d 3 3; commit_all "$kd/places/d" "feat(d): its change, done"
crew unit wait d >/dev/null
crew unit run e construct >/dev/null; change "$kd/places/e" e 3 3
printf 'e\n' > "$kd/places/e/other.txt"; commit_all "$kd/places/e" "feat(e): its change, done"; crew unit wait e >/dev/null
crew unit run e verify >/dev/null; echo "the report" > "$reports/verify-e-20261008-1500.md"; crew unit wait e >/dev/null
e_agent=swb-1-$(slot_of e)
printf 'd\n' > "$kd/places/d/other.txt"; commit_all "$kd/places/d" "feat(d): its line"
by_hand 'p.unit("e").add("After", "d", after="Intent")'
CREW_SESSION= as $box python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import record
record.emit("wldn", "unit.after", ["unit/e", "bolt/tenant-environments"], why="plan(tenant-environments): e after d, forecast to conflict")' "$CREW/plugin/lib"
: > "$CREW_TEST_LOG"
expect_ok crew unit wait d --timeout 0
eq "$(field $box forecast Reached unit/e unit/d)" "settle"
has "$(prompt_to "$e_agent")" "'Settle e: Your merge after d, ahead of you in the bolt and not merged, is forecast to conflict on other.txt."
looks() { grep -c " agent get $e_agent$" "$CREW_TEST_LOG" || true; }
n=$(looks)
crew unit wait e --stuck 3600000 --timeout 1800000 > "$T/wait.out" 2>&1 &
waiting=$!
until_ok eval '(( $(looks) > n ))' || fail "the wait never looked at e"
HOST=$box CREW_AGENT=$e_agent expect_ok crew needs "nothing needs to change ZQXL"
until_ok grep -qF "$e_agent is ended: its stage stopped short" "$(home_of $box)/.local/state/swb-1-team/short/$(slot_of e).log" \
  || fail "crew never ended the agent whose settle stopped short"
wait $waiting || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(tail -1 "$T/wait.out")" "$e_agent stopped short in settle on e. It needs: nothing needs to change ZQXL. e no longer comes after d: its settle found nothing to change."
has "$(cat "$T/wait.out")" "plan(tenant-environments): e no longer after d, its settle found nothing to change (swb-1-conductor)"
eq "$(plan -t Unit -e "Unit = 'e'" -P After)" ""
eq "$(field $box unit.after Lifted unit/e) $(field $box unit.after Settle unit/e)" "d $(field $box stage.end Id stage/e/settle)"
ok "an order a forecast wrote is lifted by the wait on the settle that found nothing to change, in the conductor's name, with no proposal"

# d moves on, and the next forecast on the new heads starts e's settle again; this time it takes d's work, and the wait
# that sees it deliver puts e after d, once, so e's merge waits for d's.
printf 'd, again\n' > "$kd/places/d/other.txt"; commit_all "$kd/places/d" "feat(d): its line again"
expect_ok crew unit wait d --timeout 0
eq "$(plan -t Unit -e "Unit = 'e'" -P After)" ""
has "$(prompt_to "$e_agent")" "'Settle e: Your merge after d, ahead of you in the bolt and not merged, is forecast to conflict on other.txt."
git -C "$kd/places/e" merge -q unit/d >/dev/null 2>&1 && fail "e's merge of d's work did not conflict"
printf 'e, with d again\n' > "$kd/places/e/other.txt"; git -C "$kd/places/e" add other.txt
git -C "$kd/places/e" commit -qm "merge d's work into e" || fail "e's merge of d's work was not committed"
expect_ok crew unit wait e
has "$out" "$e_agent delivered settle on e: its branch is at $(short unit/e), ready to merge. e now comes after d, whose work its settle took: it merges after d."
eq "$(plan -t Unit -e "Unit = 'e'" -P After)" "d"
eq "$(field $box unit.after After unit/e) $(field $box unit.after Settle unit/e)" "d $(field $box stage.end Id stage/e/settle)"
expect_fail "unit e merges after d, not yet merged into bolt/tenant-environments" crew unit run e merge
ok "a settle that takes the other unit's work puts it after that unit in the conductor's name, after crew's own lift, and its merge waits for the other's"
