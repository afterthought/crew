# The operations on a partition's environments, a deploy being one kind (plan.14), through crew ops as swancloud's
# deployer calls it, on the stubs (tests.11, record 0022): an offer is a rail row, and crew raises its card in
# main-level ops's name on the stub pendingyou, with the release notes and steps it was handed on its face, keeping
# those files beside it and none of their text in the run record, telling ops the line that adopts it; the same offer
# again writes nothing, a file it can't read is refused with nothing offered, and a newer offer changes the card in
# place; crew ops approve records the user's word, refusing an approval of another commit, and crew ops word answers
# it until that deploy's end is recorded, which closes the card with its outcome; a deploy's start, step and end are
# entries as it runs; an operation's states are recorded and crew ops steps gives each one's latest, one the user is to
# take, or an agent's held for the user's word, a rail row whose card crew raises one at a time, each following the
# one before, and closes when it is marked; an offer on a host not signed in stands with no card; main-level ops may
# post a card under an open operations row's key; quiet reads the host's agents and test slots; and an ops command
# run away from the partition's main level runs there. Which offer is open, the word, each step's latest state, the
# rows and their words, each card's facts, whether it is posted or changed and which step's card is raised are logic
# cases (tests/py/test_ops.py); each step here checks a command's wiring once.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints afterthought/blueprints >/dev/null; blueprints WilldanGroup/willdan-blueprints >/dev/null
crew state init swancloud >/dev/null; crew state init wldn >/dev/null
box=chuck-herdr-alpha
s1=$(printf 'a%.0s' $(seq 40)); s2=$(printf 'b%.0s' $(seq 40)); s3=$(printf 'c%.0s' $(seq 40))
runs() { cat "$(home_of "${1:-mac-studio}")/.local/state/crew/${2:-swancloud}/runs/${1:-mac-studio}"/*.rec 2>/dev/null || true; }
acts() { runs "$@" | grep -c "^Act: $3\$" || true; }
dep() { crew ops "$@" --label swancloud; }
stub=$(home_of mac-studio)/.stub-pendingyou
py_calls() { grep " pendingyou " "$CREW_TEST_LOG" | cut -d' ' -f3- || true; }
py_arg() { py_calls | grep "^$1 " | sed -n "${2:-1}p" | cut -d' ' -f2-; }
# Main-level ops is up, so the line that adopts a card raised outside its turn can be told.
o=$(as mac-studio herdr --session swancloud-1 workspace create --cwd / --label swancloud | jq -r .result.root_pane.pane_id)
as mac-studio herdr --session swancloud-1 stub agent "$o" swancloud-ops >/dev/null

printf '## swancloud-srv-v0.3.0 (2026-10-15)\n### Fixes\n- deployer: crew reaches the boxes with the peer key (e5b8322)\n' > "$T/notes.md"
printf "step\t1\tuser\t\tmac-studio\tOnly you hold the vault.\trotate the kanidm admin password\nstep\t2\tmain-ops\tquiet held\t\tIt ends a stage.\trestart crew's teams\nstep\t3\tuser\t\tswancloud-srv\tNot here.\tcheck srv's backups\n" > "$T/steps.txt"
: > "$CREW_TEST_LOG"
expect_ok dep offer mac-studio --from none --to "$s1" --notes "$T/notes.md" --steps "$T/steps.txt"
has "$out" "card deploy/mac-studio: req_stub-1 https://www.pendingyou.com/app/r/req_stub-1"
has "$out" "call get_request (requestId req_stub-1, name swancloud-ops)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area create_area post_request "
eq "$(jq -c '[.idempotencyKey, .session.label, .kind, .approve.risk, .approve.reversible, .title]' <<<"$(py_arg post_request)")" \
  '["deploy/mac-studio","swancloud-ops","approve","high",false,"Deploy main aaaaaaa to mac-studio"]'
eq "$(jq -c '[.artifacts[0].lang, .artifacts[0].title, .artifacts[0].lines[2]]' <<<"$(py_arg post_request)")" \
  '["markdown","What'"'"'s in it: swancloud-srv-v0.3.0","- deployer: crew reaches the boxes with the peer key (e5b8322)"]'
eq "$(jq -c '.artifacts[1].lines' <<<"$(py_arg post_request)")" \
  '["1  rotate the kanidm admin password","   you","2  restart crew'"'"'s teams","   swancloud-ops, held for your word"]'
has "$(grep "agent prompt swancloud-ops" "$CREW_TEST_LOG")" \
  "[crew] Your card deploy/mac-studio is up for the user: call get_request (requestId req_stub-1, name swancloud-ops), to hear their answer."
kept=$(home_of mac-studio)/.local/state/crew/swancloud/ops/mac-studio/$s1
eq "$(cat "$kept/notes.md")" "$(cat "$T/notes.md")"; eq "$(cat "$kept/steps.txt")" "$(cat "$T/steps.txt")"
lacks "$(runs)" "peer key"; lacks "$(runs)" "kanidm"
eq "$(runs | grep -B4 -A6 '^Act: card.post' | grep -E '^(On|Key|Card|By):' | tr '\n' ' ')" \
  "By: swancloud-ops On: env/mac-studio Card: req_stub-1 Key: deploy/mac-studio "
: > "$CREW_TEST_LOG"
expect_ok dep offer mac-studio --from none --to "$s1"
eq "$(acts mac-studio swancloud ops.offer)" "1"; eq "$(py_calls)" ""
expect_ok crew rail --label swancloud
has "$out" "deploy mac-studio (swancloud) to ${s1:0:7}, from nothing deployed: crew raises its card in swancloud-ops's name"
has "$out" "answer: crew ops approve mac-studio --to $s1 --label swancloud"
has "$out" "card:   deploy/mac-studio, open, asked by swancloud-ops (req_stub-1)"
ok "an offer is a rail row whose card crew raises in main-level ops's name with the notes and steps it was handed, kept beside it and out of the run record, telling ops the line that adopts it; the same offer again writes nothing"

printf 'step\t1\tthe-user\t\t\twhy\trotate it\n' > "$T/bad.txt"
expect_fail "the steps file $T/bad.txt can't be read: line 1 is no step crew reads" dep offer mac-studio --from none --to "$s2" --steps "$T/bad.txt"
expect_fail "the release notes file $T/none.md can't be read" dep offer mac-studio --from none --to "$s2" --notes "$T/none.md"
eq "$(acts mac-studio swancloud ops.offer)" "1"
ok "an offer handed a file crew can't read is refused, naming it, and nothing is offered"

: > "$CREW_TEST_LOG"
expect_ok dep offer mac-studio --from none --to "$s2"
has "$out" "card deploy/mac-studio: req_stub-1 changed, now version 2"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request update_request "
eq "$(jq -c '[.changeNote, .title, .artifacts[0].title]' <<<"$(py_arg update_request)")" \
  '["Now offering bbbbbbb, which includes aaaaaaa","Deploy main bbbbbbb to mac-studio","What'"'"'s in it"]'
has "$(py_arg update_request)" "Which landings it carries in the first deploy to mac-studio can't be read: bbbbbbb is no landing's commit in the record."
has "$(py_arg update_request)" "The kit handed no release notes."
ok "a newer offer changes the one card in place, with a note naming the head it now offers and the one it replaces"

rc=0; out=$(dep word mac-studio 2>&1) || rc=$?
eq "$rc" "1"; has "$out" "no word is given for a deploy of mac-studio"
expect_fail "the deploy of mac-studio offered is to ${s2:0:7}, not ${s1:0:7}" dep approve mac-studio --to "$s1"
has "$(runs)" "Refused: the deploy of mac-studio offered is to ${s2:0:7}, not ${s1:0:7}"
mkdir -p "$stub/answered"; echo '{"answer": {"approved": true}}' > "$stub/answered/req_stub-1.json"
expect_ok dep approve mac-studio --to "$s2"
has "$out" "the deploy of mac-studio to ${s2:0:7} is approved"
expect_ok dep word mac-studio; eq "$out" "$s2"
expect_ok crew rail --label swancloud; lacks "$out" "deploy mac-studio (swancloud)"
ok "there is no word until the user approves the offer the rail shows, which leaves the rail; another commit's approval is refused and recorded"

: > "$CREW_TEST_LOG"
expect_ok dep offer mac-studio --from "$s2" --to "$s3"
has "$out" "card deploy/mac-studio: its card asks for the deploy of ${s2:0:7}, approved, and the offer of ${s3:0:7} is raised once that deploy ends"
eq "$(py_calls)" ""
expect_ok dep word mac-studio; eq "$out" "$s2"
expect_ok crew rail --label swancloud; has "$out" "deploy mac-studio (swancloud) to ${s3:0:7}"
lacks "$out" "open cards whose row is gone"; eq "$(py_calls | cut -d' ' -f1 | sort -u | tr '\n' ' ')" "get_request whoami "
: > "$CREW_TEST_LOG"
echo '[{"name":"deployer","state":"ok","detail":"","before":"warn","verdict":"better"}]' > "$T/rows.json"
expect_ok dep record mac-studio --to "$s2" --act start --from none
expect_ok dep record mac-studio --to "$s2" --act step --step suite --outcome ok --log /tmp/suite.log --rows "$T/rows.json"
expect_ok dep word mac-studio; eq "$out" "$s2"
eq "$(py_calls)" ""
expect_ok dep record mac-studio --to "$s2" --act end --outcome ok
has "$out" "card deploy/mac-studio: req_stub-1 closed"
eq "$(py_calls | cut -d' ' -f1 | head -3 | tr '\n' ' ')" "whoami get_request ack_answer "
eq "$(jq -r .outcome <<<"$(py_arg ack_answer)")" "Deployed ${s2:0:7} to mac-studio: suite ok."
eq "$(py_calls | grep -c '^post_request ')" "1"
eq "$(jq -c '[.idempotencyKey, .title]' <<<"$(py_arg post_request)")" '["deploy/mac-studio:2","Deploy main ccccccc to mac-studio"]'
rc=0; dep word mac-studio >/dev/null 2>&1 || rc=$?; eq "$rc" "1"
has "$(runs)" 'Rows: [{"name":"deployer","state":"ok","detail":"","before":"warn","verdict":"better"}]'
eq "$(runs | grep -c '^Phase: ')" "3"; eq "$(runs | grep '^Phase: ' | tr '\n' ' ')" "Phase: start Phase: step Phase: end "
expect_ok crew rail --label swancloud; has "$out" "deploy mac-studio (swancloud) to ${s3:0:7}"
ok "a newer offer waits beside an approved one, whose card the rail's sweep leaves open, its own card raised once that deploy ends under the key's revision; a deploy's start, step and end are recorded, and its end ends the word and closes its card with each step's outcome"

: > "$CREW_TEST_LOG"
printf 'Restart the herdr server\nonce the teams are quiet.\n- where: a terminal on mac-studio\n- command: launchctl kickstart -k gui/501/herdr\n- done: herdr answers herdr status.\n' > "$T/step.txt"
expect_ok dep step mac-studio --to "$s2" --key restart-herdr/1 --state waiting --doer user --text "$T/step.txt"
has "$out" "card op/mac-studio/1: req_stub-"
step1=$(grep -o 'card op/mac-studio/1: req_stub-[0-9]*' <<<"$out" | cut -d' ' -f3)
deploy_card=$(runs | grep -B1 -A3 '^Key: deploy/mac-studio$' | grep '^Card: ' | tail -1 | cut -d' ' -f2)
eq "$(jq -c '[.idempotencyKey, .kind, .intent, .follows, .action.where, .action.steps[0].command, .action.done]' <<<"$(py_arg post_request)")" \
  "[\"op/mac-studio/1\",\"action\",\"do\",\"$deploy_card\",\"a terminal on mac-studio\",\"launchctl kickstart -k gui/501/herdr\",\"herdr answers herdr status.\"]"
expect_ok dep step mac-studio --to "$s2" --key restart-teams/1 --state handed --doer dispatcher --agent swancloud-dispatch-mac-studio --when quiet
printf "Restart crew's teams.\n- why: It ends a stage mid-unit.\n" > "$T/held.txt"
expect_ok dep step mac-studio --to "$s2" --key restart-crew/1 --state waiting --doer main-ops --agent swancloud-ops --when quiet --held --text "$T/held.txt"
has "$out" "card op/mac-studio/1 is open: the next step's card is raised when it closes"
eq "$(py_calls | grep -c '^post_request ')" "1"
expect_ok crew rail --label swancloud
has "$out" "an operation after the deploy of mac-studio to ${s2:0:7} (swancloud), yours to do: Restart the herdr server"
has "$out" "done:   crew ops step mac-studio --to $s2 --key restart-herdr/1 --state done --label swancloud"
has "$out" "an operation after the deploy of mac-studio to ${s2:0:7} (swancloud), swancloud-ops's, held for your word: Restart crew's teams."
lacks "$out" "restart-teams"
expect_ok dep steps mac-studio --json
eq "$(jq -r '[.[] | "\(.key) \(.state) \(.to[:7])"] | join(", ")' <<<"$out")" \
  "restart-herdr/1 waiting ${s2:0:7}, restart-teams/1 handed ${s2:0:7}, restart-crew/1 waiting ${s2:0:7}"
: > "$CREW_TEST_LOG"
expect_ok dep step mac-studio --to "$s2" --key restart-herdr/1 --state done --note "restarted at 10:02"
has "$out" "card op/mac-studio/1: $step1 withdrawn"
eq "$(jq -r .reason <<<"$(py_arg cancel_request)")" "Done."
has "$out" "card op/mac-studio/3: req_stub-"
eq "$(jq -c '[.idempotencyKey, .kind, .follows, .recommendedIds, [.options[].id], .options[1].consequence]' <<<"$(py_arg post_request)")" \
  "[\"op/mac-studio/3\",\"choice\",\"$step1\",[\"quiet\"],[\"quiet\",\"now\",\"skip\"],\"It runs at once; no stage is working on mac-studio now\"]"
expect_ok dep steps mac-studio --json
eq "$(jq -r '[.[] | "\(.key) \(.state)"] | join(", ")' <<<"$out")" "restart-teams/1 handed, restart-crew/1 waiting, restart-herdr/1 done"
eq "$(jq -r '.[] | select(.key == "restart-herdr/1") | .note' <<<"$out")" "restarted at 10:02"
expect_ok crew rail --label swancloud; lacks "$out" "yours to do"
expect_ok dep step mac-studio --key rotate-tailnet-key --state waiting --doer user --note "due this week"
has "$out" "card op/mac-studio/3 is open: the next step's card is raised when it closes"
expect_ok crew rail --label swancloud
has "$out" "an operation on mac-studio (swancloud), yours to do: rotate-tailnet-key"
has "$out" "done:   crew ops step mac-studio --key rotate-tailnet-key --state done --label swancloud"
key=$(grep -o 'op/mac-studio/4' <<<"$out" | head -1); [[ -n $key ]] || fail "the operation's row has no op/ key"
expect_ok dep steps mac-studio --json
eq "$(jq -r '.[] | select(.key == "rotate-tailnet-key") | "\(.to)|\(.state)"' <<<"$out")" "|waiting"
: > "$CREW_TEST_LOG"
expect_ok dep step mac-studio --to "$s2" --key restart-crew/1 --state declined
has "$out" "card op/mac-studio/3: req_stub-"; has "$out" "withdrawn"
has "$out" "card op/mac-studio/4: req_stub-"
eq "$(jq -r '.title' <<<"$(py_arg post_request)")" "After mac-studio's deploy: rotate-tailnet-key"
expect_ok dep step mac-studio --key rotate-tailnet-key --state declined
has "$out" "card op/mac-studio/4: req_stub-"; has "$out" "withdrawn"
expect_ok crew rail --label swancloud; lacks "$out" "yours to do"; lacks "$out" "held for your word"
ok "an operation's states are recorded after a deploy or on its own, steps gives each one's latest, and one the user is to take, or held for their word, is a rail row whose card crew raises one at a time, each following the one before, and closes when it is marked"

touch "$stub/signed-out"
rc=0; out=$(dep offer swancloud-srv --from none --to "$s1" 2>&1) || rc=$?
rm "$stub/signed-out"
eq "$rc" "0"; eq "$(acts mac-studio swancloud ops.offer)" "4"
has "$out" "card deploy/swancloud-srv not posted: this host can't ask through Pending You: Claude Code on this computer isn"
has "$(runs | grep -B8 '^Key: deploy/swancloud-srv$')" "Refused: this host can't ask through Pending You"
ok "an offer on a host not signed in to Pending You stands, its card not posted, said and recorded"

refusal() { as mac-studio python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import crew, plan
print(plan.card_refusal(crew.load(), sys.argv[2], "swancloud", "post_request", sys.argv[3]))' "$CREW/plugin/lib" "$@"; }
eq "$(refusal swancloud-ops deploy/mac-studio)" "None"
has "$(refusal swancloud-ops "deploy/mac-studio/${s1:0:7}")" "swancloud-ops posts a card only under an operations row's key of swancloud open now, deploy/mac-studio"
has "$(refusal swancloud-ops land/x/abcdef1)" "operations row's key"
ok "main-level ops may post a card under an open operations row's key, and no other"

expect_ok dep quiet mac-studio
slot=$(home_of mac-studio)/.cache/crew/test-slots/slot-0; mkdir -p "$(dirname "$slot")"
python3 -c 'import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDWR | os.O_CREAT); fcntl.flock(fd, fcntl.LOCK_EX); open(sys.argv[2], "w").close(); time.sleep(600)' \
  "$slot" "$T/held" & holder=$!
held() { [[ -e $T/held ]]; }; until_ok held || fail "the test slot was never held"
rc=0; out=$(dep quiet mac-studio 2>&1) || rc=$?
kill "$holder"; wait "$holder" 2>/dev/null || true
eq "$rc" "1"; has "$out" "1 of crew's tests are running on mac-studio"
p=$(as mac-studio herdr --session wldn-5 workspace create --cwd / --label atl-1 | jq -r .result.root_pane.pane_id)
as mac-studio herdr --session wldn-5 stub agent "$p" atl-1-unit-2 >/dev/null
as mac-studio herdr --session wldn-5 stub status atl-1-unit-2 working >/dev/null
rc=0; out=$(dep quiet mac-studio 2>&1) || rc=$?
eq "$rc" "1"; has "$out" "atl-1-unit-2 is working"
ok "quiet answers whether the host's teams have a stage working or a test running"

expect_ok crew ops offer "$box" --label wldn --from none --to "$s1"
eq "$(acts "$box" wldn ops.offer)" "1"
eq "$(acts mac-studio wldn ops.offer)" "0"
expect_fail "no word is given for a deploy of $box" crew ops word "$box" --label wldn
ok "an ops command run away from the partition's main level is run there"
