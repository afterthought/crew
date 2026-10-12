# Four units in swb-1's four slots, through the crew command on the stubs (tests.11, record 0022), a part of the units
# journey (t-journey-units): a construct fetches and gathers once on each host; its wait forecasts a conflict with an
# unmerged unit ahead of it, puts it after that unit and tells only it; an agent's stop-short ends its stage and tells
# its conductor; a fifth unit is refused with every slot in flight; a working agent is ended only with --force; a
# prompt left typed is sent again, and one never taken starts nothing.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abcde"]'
export CREW_AGENT=swb-1-conductor
crew unit run a construct >/dev/null; crew unit run b construct >/dev/null
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
