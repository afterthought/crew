# Four units in swb-1's four slots, through the crew command on the stubs (tests.11, record 0022), a part of the units
# journey (t-journey-units): a construct fetches and gathers once on each host; its wait forecasts a conflict with an
# unmerged unit ahead of it and tells only it, ordering neither; an agent's stop-short ends its stage, tells its
# conductor and ends the agent, though it works on, so the slot's next start needs no --force; and with --force a
# working agent is ended and a prompt left typed is sent again.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/): a unit run refused with every slot in flight, on a working agent without --force, or for a prompt
# never taken is tests/py/test_slots.py's (tests.12). How git and worktrunk behave for them, contract cases
# (tests/contract/). Each step checks the command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abcde"]'
export CREW_AGENT=swb-1-conductor
crew unit run a construct >/dev/null; crew unit run b construct >/dev/null
# c and a meet on shared.txt: the conductor's wait forecasts it and tells c, putting c after nothing.
: > "$T/reads.log"
PATH="$T/shim:$PATH" CREW_TEST_READS=$T/reads.log expect_ok crew unit run c construct
eq "$(reads fetch) $(reads gather) $(reads openspec)" "1 1 0"
eq "$(grep -c "^mac-studio fetch$" "$T/reads.log") $(grep -c "^mac-studio gather$" "$T/reads.log")" "1 0"
change "$kd/places/c" c 0 2; printf 'one\ntwo, as c has it\nthree\n' > "$kd/places/c/shared.txt"; commit_all "$kd/places/c" "docs(c): the change"
printf 'one\ntwo, as a has it\nthree\n' > "$kd/places/a/shared.txt"; commit_all "$kd/places/a" "feat(a): its line"
: > "$CREW_TEST_LOG"
expect_ok crew unit wait c
[[ $out != *"c after a"* ]] || fail "the forecast put c after a: $out"
has "$out" "swb-1-unit-3 delivered construct on c: its change is committed at $(short unit/c)"
has "$(told swb-1-unit-3)" "Your merge after a, ahead of you in the bolt and not merged, is forecast to conflict on shared.txt."
eq "$(told swb-1-unit-1)" ""
eq "$(plan -t Unit -e "Unit = 'c'" -P After)" ""
eq "$(field $box forecast Reached unit/c)" "told"
ok "a unit run fetches once on each host and reads the kit once; a wait forecasts a conflict between two unmerged units and tells only the later, giving it no After"

expect_ok crew unit run d construct
status swb-1-unit-4 working  # it goes on working after its needs, as crw-5-unit-4 did (signal 2026-10-23-crw-5-conductor-ff91959f/01)
HOST=$box CREW_AGENT=swb-1-unit-4 expect_ok crew needs "a decision on which table holds tenants ZQXN"  # on its own host, as an agent runs it
eq "$out" "construct on d is ended, stopped short: swb-1-conductor is told what you need. crew ends this session once your turn ends: end it now."
grep -qF "agent prompt swb-1-conductor '[crew tell from swb-1-unit-4] swb-1-unit-4 stopped short in construct on d. It needs: a decision on which table holds tenants ZQXN'" "$CREW_TEST_LOG" \
  || fail "the conductor was not told the agent's words, marked as from it"
eq "$(field $box stage.end Ended stage/d/construct)" "short"
[[ $(record_of $box) != *ZQXN* ]] || fail "a stop-short's words are in the run record"
until_ok grep -qF "swb-1-unit-4 is ended: its stage stopped short" "$(home_of $box)/.local/state/swb-1-team/short/unit-4.log" \
  || fail "crew never ended the agent whose stage stopped short"
eq "$(pane swb-1-unit-4)" ""
expect_ok crew unit run d construct
has "$out" "swb-1-unit-4 has d: construct"
ok "an agent's stop-short ends its stage and tells its conductor its words, which the run record never holds; crew ends the agent, though it works on, and the slot's next start needs no --force"

units_ws=$(herdr_state $box wldn-1 '.workspaces | to_entries[] | select(.value.label == "swb-1 units") | .key')
eq "$(herdr_state $box wldn-1 "[.panes[] | select(.workspace == \"$units_ws\")] | length")" "4"
status swb-1-unit-4 working
export CREW_TAKEN_WITHIN=1
as $box herdr --session wldn-1 stub leave swb-1-unit-4 1
: > "$CREW_TEST_LOG"
expect_ok crew unit run d construct "Name the tenant." --force
eq "$(sent swb-1-unit-4 "'/opsx:propose d Unit d. Name the tenant.'")" "2"
eq "$(field $box stage.start Refused stage/d/construct)" ""
has "$(cat "$stages")" "unit-4 d construct "
unset CREW_TAKEN_WITHIN
ok "the units workspace holds a pane for each slot in flight, and with --force a working agent is ended and a prompt left typed is sent again"
