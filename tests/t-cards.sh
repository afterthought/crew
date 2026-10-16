# crew's Pending You cards on the stub pendingyou (the rail-cards spec, briefs.16, record 0031), the journey each change
# of the card series adds its card to. crew card post, change, close and read, each command's wiring once: a
# conductor's card posted as the asking assistant through `pendingyou mcp`, whoami first, filed in its kit's area made
# under the kit's key, under the card key with its session, recorded from Pending You's reply, and printed with the
# line that adopts it; posted again, the same card; a key not the conductor's refused by the card hook's check with
# nothing sent; Pending You's refusal and a host with no sign-in refused in their words, the first recorded; a change
# at the version Pending You reports; the user's answer read; a close by outcome and a withdrawal by reason, each
# recorded; and after the host signs in again, a card read as lost, and posted again under its key. Then the act that
# sends crew's own cards, as a raise of the series calls it: a landing card raised outside its owner's turn, asked in
# the owner's name, told to the owner with the line that adopts it, and closed by the owner's crew card read once the
# user declines it, with their words. Which card a key names, what crew sets on a card, the area, how a reply, a
# refusal and an answer read, and what the act sends and records for each are logic cases
# (tests/py/test_card_commands.py); whose key and what form, and each card's builder, test_cards.py.
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
