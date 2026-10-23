# What reaches a unit's agent, through the crew command on the stubs (tests.11, record 0022), a part of the units journey
# (t-journey-units): a conflict with the bolt forecast for a unit with no stage running reaches its next stage's prompt,
# once; a second wait on a stage is refused, and a stop-short's words are the running wait's answer; and the user's
# amendment marks a unit and hands its construct to the team's host, which runs it again in their name, its wait
# clearing the mark.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abc"]'
export CREW_AGENT=swb-1-conductor
crew unit run a construct >/dev/null
crew unit run b construct >/dev/null; change "$kd/places/b" b 0 2; commit_all "$kd/places/b" "docs(b): the change"; crew unit wait b >/dev/null
crew unit run c construct >/dev/null; change "$kd/places/c" c 0 2
printf 'one\ntwo, as c has it\nthree\n' > "$kd/places/c/shared.txt"; commit_all "$kd/places/c" "docs(c): the change"; crew unit wait c >/dev/null
on_branch "$k" bolt/tenant-environments "feat: the bolt's own line" shared.txt $'one\ntwo, as the bolt has it\nthree\n'
git -C "$k" push -q origin bolt/tenant-environments  # landed on GitHub's bolt, where crew reads it (plan.19)
: > "$CREW_TEST_LOG"
expect_ok crew unit wait c --timeout 0
eq "$(field $box forecast Reached unit/c bolt/tenant-environments)" "prompt"
expect_ok crew unit run c code
has "$(prompt_to swb-1-unit-3)" "'/opsx:apply c "
has "$(prompt_to swb-1-unit-3)" " Your branch is forecast to conflict with bolt/tenant-environments on shared.txt."
has "$(field $box stage.start Forecast stage/c/code)" "$(field $box forecast Id unit/c bolt/tenant-environments)"
looks() { grep -c " agent get swb-1-unit-3$" "$CREW_TEST_LOG" || true; }
n=$(looks)
crew unit wait c --stuck 3600000 --timeout 1800000 > "$T/wait.out" 2>&1 &
waiting=$!
lock=$(home_of $box)/.local/state/swb-1-team/waits/unit-3.lock
until_ok eval '! python3 -c "import fcntl, sys; f = open(sys.argv[1], \"a\"); fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)" "$lock" 2>/dev/null' \
  || fail "the wait never took its lock"
expect_fail "a wait on swb-1-unit-3's stage is already running: its answer is the one to read" crew unit wait c
# The stop-short is said once the wait looks at its stage: a wait still forecasting and reckoning the batch, which a
# loaded host can stretch past crew needs' minute, has not reached its first look (tests.8).
until_ok eval '(( $(looks) > n ))' || fail "the wait never looked at c"
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
has "$out" "construct on unit b is handed to $box, where it starts again: swb-1-conductor is told what started, and crew unit wait b waits for it"
lacks "$out" "swb-1-unit-2 has b"
until_ok eval '[[ $(told swb-1-conductor) == *"construct runs again on it in swb-1-unit-2"* ]]' || fail "the handed construct never told the conductor"
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
handed=$(home_of $box)/.local/state/swb-1-team/handed/b
printf '{"by": "the user", "at": 0, "pid": %s}' $$ > "$handed"
expect_fail "construct on unit b is starting on this host, handed there by the user: crew unit wait b waits for it" crew unit run b code
printf '{"by": "the user", "at": 0, "pid": %s, "failed": "swb-1 is down; crew up swb-1 brings it back"}' $$ > "$handed"
expect_fail "construct did not start on unit b: swb-1 is down; crew up swb-1 brings it back" crew unit wait b
[[ ! -e $handed ]] || fail "the wait that said the handed construct failed left its marker"
expect_ok crew unit wait b
has "$out" "swb-1-unit-2 delivered construct on b"
eq "$(plan -t Unit -e "Unit = 'b'" -P Amended)" ""
eq "$(subject)" "plan(tenant-environments): b constructed again, its mark cleared (swb-1-conductor)"
git --git-dir "$ws" show "wldn/main:runs/$box/$(date -u +%F).rec" | grep -q "^Act: stage.end" || fail "the write that clears the mark carries no construct end"
ok "the user's amendment marks the unit and answers once its construct is handed to the team's host, which runs it again in their name and tells the conductor; a stage is refused while it starts, a wait says why it did not, and the wait that ends it clears the mark"
