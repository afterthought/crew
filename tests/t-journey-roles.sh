# A partition's main-level roles that run as their kinds, through the crew command on the stubs (tests.11, record
# 0022; record 0047 move 6): with madswan's planner and operator named a stream, a tell to the planner with no
# standing agent of it up is an ask of the role from its sender on madswan's flywheel branch, its role record written in
# the same commit, nothing typed into any pane and one ask entry holding the words' length and never their text, which
# crew trace of the run lists; a send to madswan is an ask of its operator carrying whom it was for; and a tell to wldn's
# planner, which stands, is refused as today with nothing asked. The planner's run, named from its place: crew role start
# takes both asks of it in one turn, writes its brief to the host's file and prints it, each ask and the card the user
# answered in its name, read from Pending You as madswan-planner; an ask written after the start is not the turn's; crew
# role end, as the turn's prompt names it, answers the turn and writes the report; and outside a run each is refused.
# What a tell decides, the ask's fields and what a start takes and prints are logic cases (tests/py/test_tell_asks.py,
# test_asks.py); each step here checks a command's wiring once.
# Reads: plugin/flume/ plugin/roles/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints afterthought/blueprints >/dev/null; blueprints agentplot/blueprints >/dev/null
crew state init madswan >/dev/null
role_stream madswan planner madswan-main; role_stream madswan operator madswan-main
ms=$(remote afterthought/crew-state)
at() { git --git-dir "$ms" show "madswan/main:$1"; }
asks() { at asks.rec | recsel -t Ask "$@"; }

# A tell to the planner, which runs as its kind with no standing agent up: an ask, nothing typed.
: > "$CREW_TEST_LOG"
t0=$(act_tip madswan/main "$ms")
CREW_AGENT=madswan-design expect_ok crew tell madswan-planner "Record 0053 is accepted ZQXR"
has "$out" "asked madswan-planner"
eq "$(asks -p Role,From,What,Words | tr '\n' ' ')" "Role: planner From: madswan-design What: tell Words: Record 0053 is accepted ZQXR "
eq "$(at roles.rec | recsel -t Role -P Address,Stream,Kind,Name,Intent | tr '\n' ' ')" "madswan/planner madswan-main crew-planner madswan madswan-planner "
eq "$(acts_since "$t0" madswan/main "$ms")" "1"
grep -q "agent prompt" "$CREW_TEST_LOG" && fail "a tell to a role that runs as its kind typed into a pane"
expect_ok crew trace agent/madswan-planner --label madswan
has "$out" "agent/madswan-planner (28 characters)"
[[ $(git --git-dir "$ms" log -p madswan/main -- runs/) != *ZQXR* ]] || fail "an ask's words are in the run record"
ok "a tell to a role that runs as its kind is an ask from its sender with its role record in one commit, typing nothing, and its entry holds no words"

# A send to madswan: an ask of its operator, which runs as its kind, carrying whom it was for.
CREW_AGENT=swancloud-planner expect_ok crew send madswan "The zone check fails"
has "$out" "asked madswan-operator"
eq "$(asks -e "Role = 'operator'" -p From,What,Words | tr '\n' ' ')" "From: swancloud-planner What: send Words: (sent to madswan) The zone check fails "
ok "a send to a partition whose operator runs as its kind is an ask of the operator carrying whom it was for"

# wldn's planner stands: a tell to it, not up, is refused as today, and nothing is asked.
blueprints WilldanGroup/willdan-blueprints >/dev/null; crew state init wldn >/dev/null
CREW_AGENT=madswan-design expect_fail "could not tell wldn-planner on chuck-herdr-alpha: it is not up" crew tell wldn-planner "hello"
git --git-dir "$(remote WilldanGroup/crew-state)" show wldn/main:asks.rec >/dev/null 2>&1 && fail "a tell to a role that stands wrote an ask"
ok "a tell to a role that stands is today's, and asks nothing"

# madswan's planner's run, in its place: its start takes both tells of it and the card the user answered in its name.
run() { FLUME_PLACE=$T/flume/places/crew-planner--madswan "$@"; }
CREW_AGENT=madswan-design expect_ok crew tell madswan-planner "Batch 4 is due"
stub=$(home_of mac-studio)/.stub-pendingyou; mkdir -p "$stub/answered"
echo '{"req_stub-90": {"key": "zone-question-1", "posted": {"name": "madswan-planner", "title": "Which zone?"}, "status": "pending", "turn": "you", "version": 1}}' > "$stub/cards.json"
echo '{"answer": {"text": "eu-west-1"}}' > "$stub/answered/req_stub-90.json"
: > "$CREW_TEST_LOG"
t0=$(act_tip madswan/main "$ms")
run expect_ok crew role start
brief=$(home_of mac-studio)/.local/state/crew/madswan/turns/planner.md
has "$out" "Read $brief whole first: it is your brief as madswan-planner, filled for madswan."
has "$out" "ask 1: tell from madswan-design"$'\n'"  Record 0053 is accepted ZQXR"$'\n'"ask 3: tell from madswan-design"$'\n'"  Batch 4 is due"
has "$out" "card card/req_stub-90/2: Which zone?"$'\n'"  words: eu-west-1"
has "$(cat "$brief")" "You run as your kind"; lacks "$(cat "$brief")" "{{"
grep -q '^mac-studio pendingyou list_pending {"name": "madswan-planner"}$' "$CREW_TEST_LOG" || fail "the start did not read its cards as madswan-planner"
eq "$(at asks.rec | recsel -t Turn -p Turn,Run,Place,Took | tr '\n' ' ')" "Turn: 1 Run: madswan-planner Place: crew-planner--madswan Took: ask/1 Took: ask/3 "
eq "$(acts_since "$t0" madswan/main "$ms")" "1"
expect_ok crew trace agent/madswan-planner --label madswan
has "$out" "(took 2)"
ok "a role's run, named from its place, takes what waits in one turn, writes and prints its brief, its asks and the card the user answered in its name"

# An ask after the start waits for the next run; the end, as the turn's prompt names it, answers the turn and writes the report.
CREW_AGENT=madswan-design expect_ok crew tell madswan-planner "One more thing"
end=$(grep -o 'crew role end --report {{report}}' "$CREW/plugin/flume/turn.md" | head -1)
report=$T/flume/state/crew-planner--madswan/turn.md
read -ra endcmd <<< "${end//\{\{report\}\}/$report}"
run expect_ok "${endcmd[@]}" "proposed the fix bolt"
has "$out" "turn 1 of madswan-planner is ended, and its report is $report."
eq "$(at asks.rec | recsel -t Turn -P Said)" "proposed the fix bolt"
has "$(cat "$report")" "# Turn 1 of madswan-planner"; has "$(cat "$report")" "- ask/3: tell from madswan-design"
eq "$(at asks.rec | recsel -C -t Ask -e "Role = 'planner'" -P Id | tr '\n' ' ')" "1 3 4 "
lacks "$(at asks.rec | recsel -t Turn -P Took)" "ask/4"
ok "an ask written during a run is not its turn's, and the end answers the turn and writes the report at the prompt's path"

# Outside a run, the start and the end are refused and write nothing.
t0=$(git --git-dir "$ms" rev-parse madswan/main)
CREW_AGENT=madswan-planner expect_fail "crew role start runs only in a run of a crew role" crew role start
expect_fail "crew role end runs only in a run of a crew role" crew role end --report "$T/elsewhere.md" "done"
eq "$(git --git-dir "$ms" rev-parse madswan/main)" "$t0"; [[ -e $T/elsewhere.md ]] && fail "an end outside a run wrote a report"
ok "a start and an end outside a role's run are refused and write nothing"
