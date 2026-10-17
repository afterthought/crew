# crew's Pending You cards on the stub pendingyou (the rail-cards spec, briefs.16, record 0031), the journey each change
# of the card series adds its card to. crew card post, change, close and read, each command's wiring once: a conductor's
# card posted as the asking assistant through `pendingyou mcp`, whoami first, filed in its kit's area made under the
# kit's key, under the card key with its session, recorded from Pending You's reply, and printed with the line that
# adopts it; posted again, the same card; a key not the conductor's refused by the card hook's check with nothing sent;
# Pending You's refusal and a host with no sign-in refused in their words, the first recorded; a change at the version
# Pending You reports; the user's answer read; a close by outcome and a withdrawal by reason, each recorded; and after
# the host signs in again, a card read as lost, and posted again under its key. Then the act that sends crew's own
# cards, as a raise of the series calls it: a landing card raised outside its owner's turn, asked in the owner's name,
# told to the owner with the line that adopts it, and closed by the owner's crew card read once the user declines it,
# with their words; raised again, a new card under the key's revision, changed in place while it waits, and once the
# user answers it, acked with the change note and followed by its new version. Then crew record, as the design agent
# runs it at each turn of a record's status: the record read on the kit's main, its status recorded with its commit and
# its card raised in the design agent's name under record/<kit>/<number>; a status the file does not hold, an
# alternatives file crew can't read and another host refused with nothing recorded; the card changed in place at a new
# commit, closed with the accepting commit, a choice when a rule decided, and none raised when the user settled it in
# the pane. Then a batch's card, raised by crew in the planner's name once the reviewer's summary is there, with its one
# reading session on the main level's host linked from it, and, lost to its owner, raised again by the sweep's entry
# under its key, saying its older copy is dead, on the same session; crew card session giving that link again and
# refusing a unit, a landing's key and a short proposal's; crew card wait closing the card on the tap, with its note,
# and on the session's send, with every annotation, each ending the session; a session whose link only the host could
# open ended, and the card raised all the same, saying so; and a wait with neither card nor session refused. Then the
# rail read's sweep of the box's cards: a card whose row is gone withdrawn, or recorded lost when Pending You no longer
# finds it, and a question whose asker ended withdrawn, a question whose asker runs listed with its asker and age, crew
# board acting on none; a deploy's card, raised by crew ops offer, read not found, recorded lost and raised again through
# its kind's raise; a row whose post was refused showing the refusal, left while the refusal is under ten minutes old and
# raised through its kind's raise after, a proposal's and a step's that crew ops step raised. Which card a key names, what crew sets on a card, the area, how a reply, a refusal and an answer
# read, and what the act sends and records for each are logic cases (tests/py/test_card_commands.py); whose key and what
# form, each card's builder, a record's facts, and the session's start and end in the act and what a batch's wait
# returns, test_cards.py; a batch card's facts, test_batches.py; what the sweep judges and does, test_rail.py.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
stub=$(home_of $box)/.stub-pendingyou
v1=land/b1/abc1001
entries() {
  as $box python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))):
    for e in record.parse(open(f).read()):
        if e["Act"] == sys.argv[2]:
            print(json.dumps(e))' "$CREW/plugin/lib" "$1"
}
# The conductor's worktree: a checkout whose origin is switchboard-kit's on GitHub, where its card commands run.
wd=$T/conductor-work; git init -q "$wd"; git -C "$wd" remote add origin git@github.com:WilldanGroup/switchboard-kit.git
# card <command...>: crew card as swb-1-conductor on the box, in its worktree, standard input passed on
card() { (export CREW_TEST_HOST=$box CREW_AGENT=swb-1-conductor HOME; HOME=$(home_of $box); cd "$wd" && "$CREW/plugin/bin/crew" card "$@"); }
py_calls() { grep " pendingyou " "$CREW_TEST_LOG" | cut -d' ' -f3- || true; }

# The plan, by hand: b1 holds v1, and swb-1 holds b1, whose landing card the conductor posts.
w=$T/hand; git clone -q -b wldn/main "$ws" "$w"
python3 - "$CREW/plugin/lib" "$w/plan.rec" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
p.insert(plan.Rec("Bolt", [("Bolt", "b1"), ("Repo", "switchboard-kit"), ("Goal", "Goal of b1.")]))
p.insert(plan.Rec("Unit", [("Unit", "v1"), ("Repo", "switchboard-kit"), ("Bolt", "b1"), ("Intent", "Unit v1.")]))
open(f, "w").write(p.text())
PY
commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
crew bolt give swb-1 b1 >/dev/null 2>&1

landing='{"kind": "approve", "title": "Land b1", "summary": "b1 is ready to land.", "blocking": false, "urgency": "today",
  "highStakes": true, "approve": {"action": "Land b1", "risk": "high", "reversible": false}}'
: > "$CREW_TEST_LOG"
out=$(card post $v1 <<<"$landing")
eq "$out" "card $v1: req_stub-1 https://www.pendingyou.com/app/r/req_stub-1
call get_request (requestId req_stub-1, name swb-1-conductor)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area create_area post_request "
eq "$(py_calls | sed -n 1p)" 'whoami {"name": "swb-1-conductor"}'
has "$(py_calls | sed -n 2p)" '"remote": "github.com/WilldanGroup/switchboard-kit"'
has "$(py_calls | sed -n 3p)" '"group": "wldn", "idempotencyKey": "create-area:WilldanGroup/switchboard-kit", "name": "switchboard-kit"'
posted=$(py_calls | sed -n 4p | cut -d' ' -f2-)
eq "$(jq -c '[.idempotencyKey, .areaId, .session, .kind, (.options | length)]' <<<"$posted")" \
  "[\"$v1\",\"prj_stub-1\",{\"cwd\":\"$wd\",\"label\":\"swb-1-conductor\",\"machine\":\"$box\"},\"approve\",0]"
eq "$(entries card.post | jq -r '[(.On | join(" ")), .Card, .Key, .By] | join(" ")')" "bolt/b1 req_stub-1 $v1 swb-1-conductor"
ok "crew card post posts a conductor's card as it, whoami first, in its kit's area made under the kit's key, under the card key with its session, records it from Pending You's reply, and prints the line that adopts it"

: > "$CREW_TEST_LOG"
eq "$(card post $v1 <<<"$landing" | head -1)" "card $v1: req_stub-1 https://www.pendingyou.com/app/r/req_stub-1"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
eq "$(jq 'length' "$stub/cards.json")" "1"
ok "posted again, the card comes back under its key, filed in the area that now matches, and no second card is made"

: > "$CREW_TEST_LOG"
expect_fail "swb-1-conductor posts a card only under a rail row's key of its own" card post proposal/9 <<<"$landing"
eq "$(py_calls)" ""
refused_key=$out
ok "a key that is not the conductor's is refused by the card hook's own check, and nothing reaches Pending You"

echo "post_request Approve requests give their risk in approve.risk." > "$stub/refuse"
expect_fail "Pending You refused post_request: Approve requests give their risk in approve.risk." card post land/b1/abc1100 <<<"$landing"
eq "$(entries card.post | jq -r 'select(.Refused) | [(.On | join(" ")), .Refused] | join(" ")')" \
  "proposal/9 $(sed -n 1p <<<"$refused_key")
bolt/b1 Pending You refused post_request: Approve requests give their risk in approve.risk."
: > "$stub/refuse"
touch "$stub/signed-out"
expect_fail "this host can't ask through Pending You: Claude Code on this computer isn’t signed in to Pending You (https://www.pendingyou.com). The user signs it in with pendingyou-signin. Post it again later." \
  card post land/b1/abc1100 <<<"$landing"
lacks "$out" "npx"
mv "$stub/signed-out" "$stub/signed-out.was"
ok "a refusal, crew's or Pending You's in its words, is recorded as the post refused, and a host with no sign-in is refused saying whose it is to sign in, never npx"

: > "$CREW_TEST_LOG"
eq "$(card change $v1 <<<'{"changeNote": "Its fix merged", "summary": "b1 is ready to land, its fix merged."}')" \
  "card $v1: req_stub-1 changed, now version 2"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request update_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.requestId, .expectedVersion, .name]')" '["req_stub-1",1,"swb-1-conductor"]'
eq "$(entries card.update | jq -r '[(.On | join(" ")), .Card, .Key] | join(" ")')" "bolt/b1 req_stub-1 $v1"
ok "crew card change changes the conductor's card at the version Pending You reports, and records it"

eq "$(card read $v1)" "card $v1: req_stub-1, pending, waiting on the user
  https://www.pendingyou.com/app/r/req_stub-1"
mkdir -p "$stub/answered"; echo '{"answer": {"approved": true, "note": {"text": "Land it once the box has pulled."}}}' > "$stub/answered/req_stub-1.json"
eq "$(card read $v1)" "card $v1: req_stub-1, answered, your turn: the user has answered
  approved: yes
  note: Land it once the box has pulled.
  https://www.pendingyou.com/app/r/req_stub-1"
eq "$(card read $v1 --json | jq -r .version)" "3"
eq "$(entries card.read)" ""
ok "crew card read prints where the card stands, the user's answer and words once they answer, records nothing"

: > "$CREW_TEST_LOG"
eq "$(card close $v1 --outcome "Told wldn-ops to land b1.")" "card $v1: req_stub-1 closed
no session was running for $v1"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.expectedVersion, .outcome]')" '[3,"Told wldn-ops to land b1."]'
eq "$(entries card.close | jq -r '[(.On | join(" ")), .Card, .Key] | join(" ")')" "bolt/b1 req_stub-1 $v1"
expect_fail "swb-1-conductor holds no open card under $v1 on $box: post one with crew card post $v1" card read $v1
ok "crew card close acks the answer at its version, records the close, ends no session that was not running, and the key then names no card"

v2=land/b1/abc1200
card post $v2 <<<"$landing" >/dev/null
: > "$CREW_TEST_LOG"
eq "$(card close $v2 --reason "A fix moved the bolt's head." | head -1)" "card $v2: req_stub-2 withdrawn"
eq "$(py_calls | sed -n 2p)" 'cancel_request {"name": "swb-1-conductor", "reason": "A fix moved the bolt'"'"'s head.", "requestId": "req_stub-2"}'
eq "$(entries card.close | jq -r .Card | tr '\n' ' ')" "req_stub-1 req_stub-2 "
ok "crew card close --reason withdraws the card with why, and records it"

# The host signs in to Pending You again: every card posted before reads "not found" to its owner.
v3=land/b1/abc1300
card post $v3 <<<"$landing" >/dev/null
mv "$stub/cards.json" "$stub/cards.before-sign-in.json"
expect_fail "card req_stub-3 under $v3 is lost to its owner (Pending You: \"Not found: request:req_stub-3.\")" card read $v3
has "$out" "post its card again with crew card post $v3, its summary saying an older copy is dead"
eq "$(card post $v3 <<<"$landing" | head -1)" "card $v3: req_stub-4 https://www.pendingyou.com/app/r/req_stub-4"
eq "$(card read $v3 | head -1)" "card $v3: req_stub-4, pending, waiting on the user"
ok "after the host signs in again a card reads as lost to its owner, saying to post the row's card again, and posted again under its key it is the key's card"

# crew's own card, raised as a raise of the series raises it: the landing of b1, read on the user's rail at the box,
# not in its conductor's turn. The conductor is up, so the line that adopts it can be told.
c=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$c" swb-1-conductor
: > "$CREW_TEST_LOG"
raised=$(as $box python3 - "$CREW/plugin/lib" "$wd" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import cards, crew, plan
facts = dict(bolt="b1", kit="switchboard-kit", units=["v1"], chores=[], batches={"v1": 1}, head="abc1400", at=None, moved=0, pr=None)
plan.row_card_post(crew.load(), "wldn", "swb-1-conductor", cards.landing_card, facts,
                   (sys.argv[2], "github.com/WilldanGroup/switchboard-kit"))
PY
)
eq "$raised" "card land/b1: req_stub-5 https://www.pendingyou.com/app/r/req_stub-5
call get_request (requestId req_stub-5, name swb-1-conductor)
told swb-1-conductor: call get_request (requestId req_stub-5, name swb-1-conductor)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
eq "$(py_calls | sed -n 1p)" 'whoami {"name": "swb-1-conductor"}'
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
eq "$(jq -c '[.idempotencyKey, .session.label, .kind, .approve.risk, .approve.reversible, (.highStakes // "none"), .artifacts[0].lines]' <<<"$posted")" \
  '["land/b1","swb-1-conductor","approve","high",false,"none",["v1"]]'
has "$(grep "agent prompt swb-1-conductor" "$CREW_TEST_LOG")" \
  "[crew] Your card land/b1 is up for the user: call get_request (requestId req_stub-5, name swb-1-conductor), to hear their answer."
eq "$(entries card.post | jq -r 'select(.Key == "land/b1") | [(.On | join(" ")), .Card, .By] | join(" ")')" "bolt/b1 req_stub-5 swb-1-conductor"
ok "crew's own card is posted in its owner's name under its row's key, prints the line that adopts it, and is told to its owner when raised outside its turn"

echo '{"answer": {"approved": false, "note": {"text": "Not before the box pulls."}}}' > "$stub/answered/req_stub-5.json"
: > "$CREW_TEST_LOG"
eq "$(card read land/b1)" "card land/b1: req_stub-5, answered, your turn: the user has answered
  approved: no
  note: Not before the box pulls.
  https://www.pendingyou.com/app/r/req_stub-5
card land/b1: req_stub-5 closed, as the user declined it"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.name, .outcome]')" '["swb-1-conductor","Declined: Not before the box pulls."]'
eq "$(entries card.close | jq -r 'select(.Key == "land/b1") | [.Card, .State, .Outcome] | join(" ")')" "req_stub-5 declined Declined: Not before the box pulls."
expect_fail "swb-1-conductor holds no open card under land/b1 on $box" card read land/b1
ok "the owner's crew card read finds the approval the user declined and closes it with their words"

# crew record (briefs.15, record 0031 §1): the design agent's record at each turn of its status, read on switchboard-kit's
# main as this host's checkout of it holds it, raising, changing and closing the record's one card in its name.
# adr <status> <subject> [<number>]: a record committed on the kit's main, as sluice lands the design agent's
adr() {
  local n=${3:-32}
  mkdir -p "$k/docs/adr"
  printf -- '---\nnumber: %s\ntitle: switchboard runs the workflows\nstatus: %s\n---\n\n# switchboard runs the workflows\n\nStatus: %s.\n\nDeciders: the user (“no fleet”); wldn-design.\n\n## Context and problem statement\n\nThe runners cost. %s\n' \
    "$n" "$1" "$1" "$2" > "$k/docs/adr/00$n-switchboard-runs-the-workflows.md"
  git -C "$k" add docs/adr; git -C "$k" commit -qm "$2"
  sha=$(git -C "$k" rev-parse --short=7 HEAD)
}
# design <args...>: crew record as wldn-design on the box, in its pane's folder
design() { (export CREW_TEST_HOST=$box CREW_AGENT=wldn-design HOME; HOME=$(home_of $box); cd "$(space $box willdan)" && "$CREW/plugin/bin/crew" record "$@"); }

adr proposed "docs(adr): 0032 switchboard runs the workflows"
: > "$CREW_TEST_LOG"
eq "$(design switchboard-kit 32 --proposed)" "record 0032 in switchboard-kit: proposed at $sha
card record/switchboard-kit/0032: req_stub-6 https://www.pendingyou.com/app/r/req_stub-6
call get_request (requestId req_stub-6, name wldn-design)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
eq "$(jq -c '[.idempotencyKey, .session.label, .session.cwd, .kind, .approve.risk, .approve.reversible, .artifacts[0].lines[0]]' <<<"$posted")" \
  "[\"record/switchboard-kit/0032\",\"wldn-design\",\"$k\",\"approve\",\"low\",true,\"# switchboard runs the workflows\"]"
has "$(jq -r .summary <<<"$posted")" "Your own words, recorded as your decision: “no fleet”"
eq "$(entries record.proposed | jq -r '[(.On | join(" ")), (.Commit | join(" ")), .By] | join(" ")')" \
  "record/switchboard-kit/0032 WilldanGroup/switchboard-kit@$(git -C "$k" rev-parse HEAD) wldn-design"
eq "$(entries card.post | jq -r 'select(.Key == "record/switchboard-kit/0032") | [(.On | join(" ")), .Card, .By] | join(" ")')" \
  "record/switchboard-kit/0032 req_stub-6 wldn-design"
ok "crew record --proposed records the status with its commit, and raises the record's card in the design agent's name under its key, the record whole and the user's own words on it"

: > "$CREW_TEST_LOG"
expect_fail "crew refuses record 0032 in switchboard-kit as accepted: its file on main says proposed" design switchboard-kit 32 --accepted
expect_fail "crew can't read the alternatives file $T/none.md" design switchboard-kit 32 --proposed --alternatives "$T/none.md"
expect_fail "crew record runs on chuck-herdr-alpha, where wldn's design agent holds its records' cards" \
  as mac-studio env CREW_AGENT=wldn-design "$CREW/plugin/bin/crew" record switchboard-kit 32 --proposed
eq "$(py_calls)" ""
eq "$(entries record.accepted)" ""; eq "$(entries record.proposed | wc -l | tr -d ' ')" "1"
ok "a status the record's file does not hold on main, an alternatives file crew can't read and another host than the main level's are refused, with nothing recorded or raised"

adr proposed "docs(adr): 0032 says what the runners cost"
: > "$CREW_TEST_LOG"
eq "$(design switchboard-kit 32 --proposed)" "record 0032 in switchboard-kit: proposed at $sha
card record/switchboard-kit/0032: req_stub-6 changed, now version 2"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request update_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .changeNote)" "Revised at $sha: docs(adr): 0032 says what the runners cost"
ok "a record revised and run again changes its one card in place, the change note naming the new commit"

echo '{"answer": {"approved": true}}' > "$stub/answered/req_stub-6.json"
adr accepted "docs(adr): 0032 accepted by the user"
: > "$CREW_TEST_LOG"
eq "$(design switchboard-kit 32 --accepted)" "record 0032 in switchboard-kit: accepted at $sha
card record/switchboard-kit/0032: req_stub-6 closed"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .outcome)" "Accepted at $sha"
eq "$(entries card.close | jq -r 'select(.Key == "record/switchboard-kit/0032") | [(.On | join(" ")), .State, .Outcome] | join(" ")')" \
  "record/switchboard-kit/0032 closed Accepted at $sha"
ok "a record accepted on its card records its status and closes the card with the accepting commit"

printf -- '---\nrules: ops.3, ops.7\nother: switchboard runs the workflows itself\n---\n\n## Where your rules decided\n\nops.3 chose a fleet.\n' > "$T/alternatives.md"
adr proposed "docs(adr): 0033 a fleet runs the workflows" 33
: > "$CREW_TEST_LOG"
design switchboard-kit 33 --proposed --alternatives "$T/alternatives.md" >/dev/null
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.idempotencyKey, .kind, .recommendedIds, [.options[].id], .artifacts[0].lines[0]]')" \
  '["record/switchboard-kit/0033","choice",["accept"],["loosen","accept","back"],"## Where your rules decided"]'
ok "a record a rule decided is raised as one choice, loosen the rules as drafted, accept as ruled or send back, its alternatives on its face"

adr proposed "docs(adr): 0034 settled beside the user" 34
: > "$CREW_TEST_LOG"
eq "$(design switchboard-kit 34 --proposed --settled-in-pane)" \
  "record 0034 in switchboard-kit: proposed at $sha, the user's yes given in the pane; no card is raised"
eq "$(py_calls)" ""
eq "$(entries record.proposed | jq -r 'select(.On[0] == "record/switchboard-kit/0034") | .State')" "settled in the pane"
ok "a record settled with the user in the pane records their yes there, and no card is raised"

# The act's change of crew's own card (record 0031 §3): b1's landing card raised again after the user declined it is a
# new card under the key's revision, changed in place while it waits, and once the user answers it, acked with the
# change note and followed by its new version, which crew card read then finds as the row's card.
# land <change|post> <head>: b1's landing card raised by the act as a raise of the series calls it, on the box
land() {
  as $box python3 - "$CREW/plugin/lib" "$wd" "$1" "$2" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import cards, crew, plan
facts = dict(bolt="b1", kit="switchboard-kit", units=["v1"], chores=[], batches={"v1": 1}, head=sys.argv[4], at=None, moved=0, pr=None)
where = (sys.argv[2], "github.com/WilldanGroup/switchboard-kit")
if sys.argv[3] == "post":
    plan.row_card_post(crew.load(), "wldn", "swb-1-conductor", cards.landing_card, facts, where)
else:
    plan.row_card_change(crew.load(), "wldn", "swb-1-conductor", cards.landing_card, facts, f"Head is now {sys.argv[4]}", where)
PY
}
: > "$CREW_TEST_LOG"
eq "$(land post abc1500 | head -1)" "card land/b1: req_stub-8 https://www.pendingyou.com/app/r/req_stub-8"
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .idempotencyKey)" "land/b1:2"
ok "a row's card raised again after its last card closed is posted under the key with its revision, a new card rather than the closed one given back"

: > "$CREW_TEST_LOG"
eq "$(land change abc1600)" "card land/b1: req_stub-8 changed, now version 2"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request update_request "
echo '{"answer": {"approved": false, "note": {"text": "Not with that head."}}}' > "$stub/answered/req_stub-8.json"
: > "$CREW_TEST_LOG"
raised=$(land change abc1700)
eq "$(head -2 <<<"$raised")" "card land/b1: req_stub-8 closed, the user having answered it, and its new version follows it
card land/b1: req_stub-9 https://www.pendingyou.com/app/r/req_stub-9"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer whoami match_area post_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .outcome)" "Head is now abc1700"
eq "$(py_calls | sed -n 6p | cut -d' ' -f2- | jq -c '[.idempotencyKey, .follows]')" '["land/b1:3","req_stub-8"]'
eq "$(jq -r '.["req_stub-8"].status' "$stub/cards.json")" "resolved"
eq "$(entries card.close | jq -r 'select(.Card == "req_stub-8") | [.Key, .State] | join(" ")')" "land/b1 closed"
eq "$(entries card.post | jq -r 'select(.Card == "req_stub-9") | [(.On | join(" ")), .Key, .By] | join(" ")')" "bolt/b1 land/b1 swb-1-conductor"
eq "$(card read land/b1 | head -1)" "card land/b1: req_stub-9, pending, waiting on the user"
ok "a card waiting on the user is changed in place; once they answer it, it is acked with the change note and its new version posted following it, recorded under the row's key, and crew card read finds that one"

# A batch's card and its one reading session, raised by crew in the planner's name once the reviewer's summary is
# there, on the main level's host, the box: v1's change read at its commit in switchboard-kit.
export PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
change "$k" v1 0 2; commit_all "$k" "docs(v1): the change"; sha=$(git -C "$k" rev-parse HEAD)
reports=$(home_of $box)/.local/state/crew/wldn-main/reports; mkdir -p "$reports"
cards_dir=$(home_of $box)/.local/state/crew/cards/wldn
batch() {  # batch <n>: batch n of v1 recorded on the box, and its summary written
  CREW_AGENT=wldn-reviewer as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act review.batch --on "batch/$1" \
    --field "Batch=$1" --field "Units=v1:swb-1@$sha" >/dev/null
  printf '# Batch %s of wldn\n\n## v1 (swb-1)\n\nv1 gives each tenant its own zone. The user sees it in the console.\n\n**Its risks**: none.\n' "$1" \
    > "$reports/batch-wldn-$1.md"
}
raise() { CREW_AGENT=wldn-planner as $box python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import crew, plan
plan.raise_batch(crew.load(), {"label": "wldn", "key": f"batch/{sys.argv[2]}", "group": "batches"})' "$CREW/plugin/lib" "$1"; }
planner() { (export CREW_AGENT=wldn-planner; HOST=$box crew card "$@"); }
listed() { as $box plannotator sessions --json | jq -r '[.[].pid] | sort | map(tostring) | join(" ")'; }
gone() { until_ok python3 -c 'import os, sys
try:
    os.kill(int(sys.argv[1]), 0)
except ProcessLookupError:
    sys.exit(0)
sys.exit(1)' "$1"; }
decide() { printf '%s\n' "$2" > "$(home_of $box)/.stub-plannotator/$1.decision"; gone "$1"; }
batch 1
expect_ok raise 9
eq "$out" ""
: > "$CREW_TEST_LOG"
expect_ok raise 1
eq "$out" "card batch/1: req_stub-10 https://www.pendingyou.com/app/r/req_stub-10
call get_request (requestId req_stub-10, name wldn-planner)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
s1=$cards_dir/batch/1/session.json; u1=$(jq -r .url "$s1"); p1=$(jq -r .pid "$s1")
[[ $u1 =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on the box's tailnet name: $u1"
eq "$(jq -c '[.idempotencyKey, .session.label, .kind, .title, .context.links[0].url]' <<<"$posted")" \
  "[\"batch/1\",\"wldn-planner\",\"fyi\",\"Goal of b1 (batch 1)\",\"$u1\"]"
has "$(jq -r .summary <<<"$posted")" "1 change to read, nothing to approve."
has "$(jq -r '.artifacts[0].lines | join("\n")' <<<"$posted")" "**swb-1 · v1**"$'\n\n'"v1 gives each tenant its own zone."
folder=$(cd "$reports" && pwd -P)/batch-wldn-1
eq "$(jq -r '.argv | map(select(endswith(".md"))) | join(" ")' "$(home_of $box)/.stub-plannotator/$p1.json")" \
  "$folder/00-summary.md $folder/01-v1-proposal.md $folder/01-v1-design.md $folder/01-v1-specs-x-spec.md $folder/01-v1-tasks.md"
eq "$(entries card.post | jq -r 'select(.Key == "batch/1") | [(.On | join(" ")), .Card, .By] | join(" ")')" "batch/1 req_stub-10 wldn-planner"
: > "$CREW_TEST_LOG"
ok "a batch's card is raised once its summary is there, in the planner's name, its one reading session on the main level's host started first and linked from it"

# The host signs in to Pending You again: batch 1's card reads "not found" to the planner, and the sweep's raise posts
# it again under its key, on the session that still runs.
mv "$stub/cards.json" "$stub/cards.before-batch-sign-in.json"
expect_ok raise 1
has "$out" "card batch/1: req_stub-10 is lost to wldn-planner (Pending You: \"Not found: request:req_stub-10.\")"
has "$out" "card batch/1: req_stub-11 https://www.pendingyou.com/app/r/req_stub-11"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request whoami match_area post_request "
posted=$(py_calls | sed -n 5p | cut -d' ' -f2-)
has "$(jq -r .summary <<<"$posted")" "An older copy of this card was lost: dismiss it in the app."
eq "$(jq -r .idempotencyKey <<<"$posted")" "batch/1:2"
eq "$(jq -r '.context.links[0].url' <<<"$posted")" "$u1"; eq "$(listed)" "$p1"
eq "$(entries card.close | jq -r 'select(.Key == "batch/1") | [.Card, .State] | join(" ")')" "req_stub-10 lost"
ok "a batch's card lost to the planner is raised again by the sweep's entry under its key, saying its older copy is dead, its link the session's that still runs"

expect_ok planner session batch/1; eq "$out" "$u1"; eq "$(listed)" "$p1"
expect_fail "a batch has one reading session, on the whole batch: crew card session batch/1" planner session batch/1 v1
expect_fail "a landing card has nothing to read" planner session land/b1/abc1001
printf '%s\n' 'Case: The console gets a bolt of its own.' 'Do: bolt new console-pages "The console lists them." --repo switchboard-kit' > "$T/p.rec"
crew plan propose "$T/p.rec" >/dev/null
expect_fail "proposal/1's card has nothing to read: it holds the proposal whole" crew card session proposal/1
ok "crew card session gives a running session's link again, and refuses a unit with a batch's key, a landing's key and a short proposal's"

echo '{"answer": {"note": {"text": "v1: say what the zone is."}}}' > "$stub/answered/req_stub-11.json"
: > "$CREW_TEST_LOG"
expect_ok planner wait batch/1
eq "$out" "batch/1: sent back on its card, with a note:
v1: say what the zone is.
card batch/1: req_stub-11 closed
ended batch/1's session, plannotator pid $p1"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request whoami get_request ack_answer "
eq "$(py_calls | sed -n 5p | cut -d' ' -f2- | jq -r .outcome)" "Read; 1 note sent to its team"
gone "$p1"
[[ ! -e $cards_dir/batch/1 ]] || fail "batch/1's session folder outlived its card"
eq "$(entries card.close | jq -r 'select(.Key == "batch/1" and .State == "closed") | [.Card, .Outcome] | join(" ")')" "req_stub-11 Read; 1 note sent to its team"
ok "the card sent back while nobody waited ends the planner's wait at once with its note, and crew closes it and ends its session"

batch 2
raise 2 >/dev/null; p2=$(jq -r .pid "$cards_dir/batch/2/session.json")
notes=$'# Annotations\n\n1. 01-v1-design.md: say why one zone.\n2. 01-v1-tasks.md: a task for the console.'
decide "$p2" "$(jq -nc --arg f "$notes" '{decision: "annotated", feedback: $f, annotationCount: 2}')"
: > "$CREW_TEST_LOG"
expect_ok planner wait batch/2
eq "$out" "batch/2: annotated
$notes
card batch/2: req_stub-12 withdrawn
batch/2's session had ended as the user sent it, and batch/2 is forgotten"
eq "$(py_calls | tail -1 | cut -d' ' -f2- | jq -r .reason)" "Read; 2 notes sent to their teams"
ok "the session sent with its annotations ends the wait with every one as the user wrote it, and crew closes the card and forgets the session"

batch 3
: > "$CREW_TEST_LOG"
out=$(CREW_AGENT=wldn-planner as $box env -u PLANNOTATOR_URL_HOST python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import crew, plan
plan.raise_batch(crew.load(), {"label": "wldn", "key": "batch/3", "group": "batches"})' "$CREW/plugin/lib" 2>&1) || fail "batch 3's raise failed: $out"
has "$out" "card batch/3: its reading could not be opened on the tailnet: plannotator gave batch/3's session the link http://localhost:"
has "$out" "card batch/3: req_stub-13 https://www.pendingyou.com/app/r/req_stub-13"
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
has "$(jq -r .summary <<<"$posted")" "Its reading could not be opened on the tailnet."
eq "$(jq -c '.context.links' <<<"$posted")" "[]"
eq "$(listed)" ""
echo '{"answer": {}}' > "$stub/answered/req_stub-13.json"
expect_ok planner wait batch/3
eq "$out" "batch/3: sent back on its card, with no note
card batch/3: req_stub-13 closed"
expect_fail "no card and no session of batch/4 is open on $box" planner wait batch/4
ok "a session whose link only the host could open is ended and the card raised all the same, saying so, its wait on the card alone; a wait with neither is refused"

# A proposal's card, crew's own (plan-proposals, record 0031 §1, change crew-raises-a-proposals-card): raised by crew plan
# propose in the planner's name on its own host, changed in place by a rewrite while it waits, followed by a new version
# when a rewrite comes after the user's note answered it, answered on the card and applied with its boxes as they stand,
# then closed with what was applied. Which act each step makes is a logic case
# (tests/py/test_proposal_life.py); the plan's side of each step, the proposals journey's (t-journey-plan).
as_planner() { HOST=$box CREW_AGENT=wldn-planner "$@"; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
opened() { sed -n 's/^proposal \([0-9]*\) is open,.*/\1/p' <<<"$out"; }  # the proposal crew plan propose just opened
raised() { sed -n "s|^card proposal/$1: \(req_stub-[0-9]*\) https.*|\1|p" <<<"$out"; }  # the card it posted under that key
: > "$CREW_TEST_LOG"
as_planner expect_ok crew plan propose "$(proposal 'Case: The page gets a bolt of its own.' \
  'Do: bolt new p1 "The page is drawn." --repo switchboard-kit' 'Do: unit add p-a "A page." --bolt p1' 'Do: unit add p-b "B page." --bolt p1')"
n=$(opened); c=$(raised "$n")
[[ -n $c ]] || fail "no card was raised for proposal $n:"$'\n'"$out"
eq "$(tail -1 <<<"$out")" "call get_request (requestId $c, name wldn-planner)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
eq "$(jq -c '[.idempotencyKey, .session.label, .title, .kind, [.options[].id], .recommendedIds]' <<<"$posted")" \
  "[\"proposal/$n\",\"wldn-planner\",\"Plan change to p1: 2 new\",\"multi\",[\"add:p-a\",\"add:p-b\"],[\"add:p-a\",\"add:p-b\"]]"
grep -q "agent prompt wldn-planner" "$CREW_TEST_LOG" && fail "the planner was told of the card its own command raised"
ok "crew plan propose raises the proposal's card in the planner's name under proposal/<n>, one checkbox list every row set as proposed, and prints the line that adopts it"

: > "$CREW_TEST_LOG"
as_planner expect_ok crew plan propose --replaces "$n" "$(proposal 'Case: The page gets a bolt of its own, with c in place of b.' \
  'Do: bolt new p2 "The page is drawn." --repo switchboard-kit' 'Do: unit add p-a "A page." --bolt p2' 'Do: unit add p-c "C page." --bolt p2')"
m=$(opened)
has "$out" "card proposal/$n: $c changed, now version 2"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request update_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.requestId, .changeNote, .title, [.options[].id]]')" \
  "[\"$c\",\"Rewritten as proposal $m after your note\",\"Plan change to p2: 2 new\",[\"add:p-a\",\"add:p-c\"]]"
eq "$(as_planner crew rail --label wldn | grep -A4 "proposal $m (wldn)" | grep 'card:' | sed 's/^ *//')" \
  "card:   proposal/$n, open, asked by wldn-planner ($c)"
ok "a rewrite changes the chain's one card in place with its note, and the rail's row for the successor carries the chain's key"

# The user sends the card with a note asking for a change, which answers it; the planner's rewrite follows it.
echo '{"answer": {"choiceIds": ["add:p-a", "add:p-c"], "note": {"text": "c before a."}}}' > "$stub/answered/$c.json"
: > "$CREW_TEST_LOG"
as_planner expect_ok crew plan propose --replaces "$m" "$(proposal 'Case: The page gets a bolt of its own, c before a.' \
  'Do: bolt new p3 "The page is drawn." --repo switchboard-kit' 'Do: unit add p-c "C page." --bolt p3' 'Do: unit add p-a "A page." --bolt p3')"
r=$(opened); c2=$(raised "$n")
has "$out" "card proposal/$n: $c closed, the user having answered it, and its new version follows it"
[[ -n $c2 && $c2 != "$c" ]] || fail "no new version of proposal/$n's card was posted:"$'\n'"$out"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer whoami match_area post_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .outcome)" "Rewritten as proposal $r after your note"
eq "$(py_calls | sed -n 6p | cut -d' ' -f2- | jq -c '[.idempotencyKey, .follows, .title, [.options[].id]]')" \
  "[\"proposal/$n:2\",\"$c\",\"Plan change to p3: 2 new\",[\"add:p-c\",\"add:p-a\"]]"
eq "$(entries card.post | jq -r "select(.Card == \"$c2\") | [(.On | join(\" \")), .Key, .By] | join(\" \")")" "proposal/$n proposal/$n wldn-planner"
eq "$(as_planner crew rail --label wldn | grep -A4 "proposal $r (wldn)" | grep 'card:' | sed 's/^ *//')" \
  "card:   proposal/$n, open, asked by wldn-planner ($c2)"
ok "a rewrite after the user's note, which answered the card, acks it with the note and posts the new version following it, under the row's key"

echo '{"answer": {"choiceIds": ["add:p-c"], "note": {"text": "a later."}}}' > "$stub/answered/$c2.json"
as_planner expect_ok crew card read "proposal/$n"
has "$out" "picked: add:p-c"
: > "$CREW_TEST_LOG"
as_planner expect_ok crew plan answer "$r" rows-1 add:p-c --note "a later."
has "$out" "proposal $r is approved and applied, without p-a"
has "$out" "card proposal/$n: $c2 closed"
eq "$(py_calls | sed -n 3p | cut -d' ' -f1)" "ack_answer"
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .outcome)" "Applied: added p-c; 1 other change. Left out on your word: p-a."
eq "$(entries card.close | jq -r "select(.Key == \"proposal/$n\") | [.Card, .State] | join(\" \")" | tail -1)" "$c2 closed"
ok "the user's boxes, sent on the card, are applied as they stand, and crew closes the card with what was applied"

# The rail read's sweep of the cards on the box, under its sign-in (record 0031 §1, §2, read.4). The landing cards
# posted before the batch's sign-in were recorded lost by the planner's rail reads above, their row gone; a landing card
# posted since, whose bolt has no row; and two questions asked through Pending You's own tools and recorded as crew's
# card hook records them: swb-2-conductor's, whose session has ended, and swb-1-conductor's, which runs. crew board
# reads them and acts on none.
question() {  # question <asker>: the question's id
  local id
  id=$(as $box python3 - "$CREW/plugin/lib" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import cards
who = sys.argv[2]
with cards.Bridge(who, "") as py:
    print(py.call("post_request", {"title": "Hold the Macs?", "summary": "Hold them.", "kind": "fyi", "idempotencyKey": f"ask/{who}/macs"})["requestId"])
PY
)
  CREW_AGENT=$1 as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act card.post --on "agent/$1" --field "Card=$id" >/dev/null
  echo "$id"
}
lc=$(card post land/b1/abc1900 <<<"$landing" | sed -n '1s/^card [^:]*: \([^ ]*\).*/\1/p')
q2=$(question swb-2-conductor); q1=$(question swb-1-conductor)
closes=$(entries card.close | wc -l)
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew board --label wldn
eq "$(py_calls)" ""; eq "$(entries card.close | wc -l)" "$closes"
HOST=$box expect_ok crew rail --label wldn; r=$out
eq "$(sed -n '/^cards swept:$/,/^$/p' <<<"$r")" "cards swept:
  land/b1/abc1900 (wldn), swb-1-conductor's $lc: withdrawn: its bolt no longer waits to land at abc1900
  a question (wldn), swb-2-conductor's $q2: withdrawn: swb-2-conductor ended"
asked=$(sed -n '/^questions waiting on you:$/,/^$/p' <<<"$r")
has "$asked" "a question (wldn), asked by swb-1-conductor on $box ($q1)"; lacks "$asked" "$q2"
eq "$(py_calls | sed -n 1p)" 'whoami {"name": "crew"}'
eq "$(py_calls | awk 'NR > 1 && $1 != "get_request" {exit} NR > 1 {print $1, $2, $3}' | sort -u)" 'get_request {"name": "crew",'
has "$(py_calls)" "cancel_request {\"name\": \"swb-1-conductor\", \"reason\": \"its bolt no longer waits to land at abc1900\", \"requestId\": \"$lc\"}"
has "$(py_calls)" "cancel_request {\"name\": \"swb-2-conductor\", \"reason\": \"swb-2-conductor ended; ask again if it still matters\", \"requestId\": \"$q2\"}"
eq "$(entries card.close | jq -r "select(.Card == \"req_stub-4\" or .Card == \"$lc\" or .Card == \"$q2\") | [.Card, .State, (.On | join(\" \"))] | join(\" \")" | tail -3)" \
  "req_stub-4 lost agent/swb-1-conductor
$lc withdrawn agent/swb-1-conductor
$q2 withdrawn agent/swb-2-conductor"
ok "the rail read, asking after each card in crew's own name, records lost a card whose row is gone and that Pending You no longer finds, withdraws one it finds and a question whose asker herdr no longer lists, keeps the one whose asker runs, and crew board acts on none"

# A deploy offered: crew ops offer raises its card in main-level ops's name on the box; the box signs in to Pending You
# again, so the card reads not found, and the read records it lost and raises it again through the deploy's raise,
# saying its older copy is dead.
s1=$(printf 'a%.0s' $(seq 40)); d=deploy/mac-studio
HOST=$box expect_ok crew ops offer mac-studio --label wldn --from none --to "$s1"
dc=$(sed -n "s|^card $d: \(req_stub-[0-9]*\) https.*|\1|p" <<<"$out")
[[ $dc == req_stub-* ]] || fail "the deploy's card was not raised:"$'\n'"$out"
mv "$stub/cards.json" "$stub/cards.signed-in-again.json"
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew rail --label wldn; r=$out
nc=$(sed -n "s|^card $d: \(req_stub-[0-9]*\) https.*|\1|p" <<<"$r")
[[ -n $nc && $nc != "$dc" ]] || fail "the read raised no new card for $d:"$'\n'"$r"
has "$r" "  $d (wldn), wldn-ops's $dc: lost: posted again as $nc"
has "$r" "    card:   $d, open, asked by wldn-ops ($nc)"
eq "$(entries card.close | jq -r "select(.Card == \"$dc\") | [.State, .By] | join(\" \")")" "lost wldn-ops"
eq "$(py_calls | grep '^post_request' | cut -d' ' -f2- | jq -r "select(.idempotencyKey | startswith(\"$d\")) | .summary" | head -1)" \
  "An older copy of this card was lost: dismiss it in the app."
ok "a row's card Pending You no longer finds is recorded lost by the rail read and raised again through its kind's raise, saying its older copy is dead"

# A proposal whose card Pending You refused at its raise: the row shows the refusal, and the rail read leaves it while
# the refusal is under ten minutes old (CARD_RETRY), so a refusal that stands is not tried at the rail tab's pace; once
# it is older, the read raises the card through the proposal's raise, in the planner's name.
echo "post_request Too many requests." > "$stub/refuse"
as_planner expect_ok crew plan propose "$(proposal 'Case: The console gets a bolt of its own.' 'Do: bolt new console-two "The console, again." --repo switchboard-kit')"
k=proposal/$(opened)
has "$out" "card $k not posted: Pending You refused post_request: Too many requests."
: > "$stub/refuse"
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew rail --label wldn
has "$out" "    card:   $k, none open; its last post was refused: Pending You refused post_request: Too many requests."
lacks "$(py_calls)" "post_request"
id=$(entries card.post | jq -r "select(.Key == \"$k\" and .Refused) | .Id" | tail -1)
old=$(python3 -c 'import datetime; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=11)).strftime("%Y-%m-%dT%H:%M:%SZ"))')
for f in "$(home_of $box)/.local/state/crew/wldn/runs/$box"/*.rec; do rewrite "$f" "/^Id: $id\$/,/^\$/s/^At: .*/At: $old/"; done
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew rail --label wldn; r=$out
pc=$(sed -n "s|^card $k: \(req_stub-[0-9]*\) https.*|\1|p" <<<"$r")
[[ -n $pc ]] || fail "the read raised no card for $k:"$'\n'"$r"
eq "$(py_calls | grep '^post_request' | cut -d' ' -f2- | jq -r '[.idempotencyKey, .session.label] | join(" ")')" "$k wldn-planner"
has "$r" "  $k (wldn), wldn-planner's $pc: posted: its row had none open"
has "$r" "    card:   $k, open, asked by wldn-planner ($pc)"
ok "a row whose card's post was refused shows the refusal, is left by a read while the refusal is under ten minutes old, and is raised through its kind's raise by the first read after"

# A step waiting on the user: crew ops step raises its card in main-level ops's name; refused, the row shows the
# refusal, and once that is over ten minutes old the read raises the card through the step's raise.
echo "post_request Too many requests." > "$stub/refuse"
HOST=$box expect_ok crew ops step mac-studio --label wldn --key rotate-key --state waiting --doer user --note "due this week"
op=$(grep -o 'op/mac-studio/[0-9]*' <<<"$out" | head -1); [[ -n $op ]] || fail "the step raised no op/ card:"$'\n'"$out"
has "$out" "card $op not posted: Pending You refused post_request: Too many requests."
: > "$stub/refuse"
id=$(entries card.post | jq -r "select(.Key == \"$op\" and .Refused) | .Id" | tail -1)
for f in "$(home_of $box)/.local/state/crew/wldn/runs/$box"/*.rec; do rewrite "$f" "/^Id: $id\$/,/^\$/s/^At: .*/At: $old/"; done
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew rail --label wldn; r=$out
sc=$(sed -n "s|^card $op: \(req_stub-[0-9]*\) https.*|\1|p" <<<"$r")
[[ -n $sc ]] || fail "the read raised no card for $op:"$'\n'"$r"
eq "$(py_calls | grep '^post_request' | cut -d' ' -f2- | jq -r "select(.idempotencyKey == \"$op\") | [.session.label, .kind, .intent] | join(\" \")")" "wldn-ops action do"
has "$r" "  $op (wldn), wldn-ops's $sc: posted: its row had none open"
has "$r" "    card:   $op, open, asked by wldn-ops ($sc)"
ok "a step waiting on the user has its card raised by crew ops step, and one whose post was refused raised through the step's raise by the first read after ten minutes"
