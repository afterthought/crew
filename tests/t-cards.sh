# crew's Pending You cards on the stub pendingyou (the rail-cards spec, briefs.16, record 0031), the journey each
# change of the card series adds its card to, on a plan whose bolt b1 swb-1 builds through Flume (Decision 1 of
# the-team-machinery-leaves). An agent's own question, through Pending You's own tools, with crew's card hook before and
# after each call: the operator's post refused, naming why, with nothing sent; the planner's question posted in a kit's
# area made under the kit's key, recorded on the planner with its id and key; crew card read printing where it stands
# and the user's answer, recording nothing; the planner's close and withdrawal recorded under its key; a post under a
# bolt's landing key refused as crew's card; and after the host signs in again, a question read as lost, saying to ask
# it again, and asked again under its key. Then the act that sends crew's own cards, as a raise of the series calls it:
# a landing card raised outside its owner's turn, asked in main-level ops's name, told to ops with the line that adopts
# it, and closed by ops's crew card read once the user declines it, with their words; raised again, a new card under
# the key's revision, changed in place while it waits, and once the user answers it and its head moves, acked with the
# change note and followed by its new version. Then
# crew record, as the design agent runs it at each turn of a record's status: the record read on the kit's main, its
# status recorded with its commit and its card raised in the design agent's name under record/<kit>/<number>; a
# status the file does not hold, an alternatives file crew can't read and another host refused with nothing recorded; the card changed in place
# at a new commit, closed with the accepting commit, a choice when a rule decided, and none raised when the user
# settled it in the pane, in words crew reads in the design agent's transcript as theirs, the record refused with
# nothing recorded when the words are another agent's tell of them; and posted saying an older copy was lost when one
# stands on a host this one's sign-in can't reach. Then a batch's card, raised by crew in the planner's name once the reviewer's summary is
# there, with its one reading session on the main level's host linked from it, and, lost to its owner, raised again by
# the sweep's entry under its key, saying its older copy is dead, on the same session; crew card session giving that
# link again and refusing a unit, a bolt's key while it is no row of its kit's landings card, the kit's card, which
# has no reading of its own, and a short proposal's, and, started from a shell naming no port while another session
# holds 19432, a link on the next port of crew's range; crew card wait refused, naming crew card read; the planner's
# crew card read closing the card on the tap, with its note, and on the session's send, with every annotation, each
# ending the session; a session whose link only the host could open ended, and the card raised all the same, saying
# so; a read with neither card nor session refused; and a session sent with no card held, or with its card's close
# refused, recording crew's close of the batch, read, in the planner's name. Then the rail read's sweep of the box's cards: a card whose row is gone withdrawn, or recorded lost when
# Pending You no longer finds it, and a question whose asker ended withdrawn, a question whose asker runs listed with
# its asker and age, crew board acting on none; a deploy's card, raised by crew ops offer, read not found, recorded
# lost and raised again through its kind's raise; a row whose post was refused showing the refusal, left while the
# refusal is under ten minutes old and raised through its kind's raise after, a proposal's and a step's that crew ops
# step raised. Then Pending You's notice of a change on a card, crew _answered as `pendingyou watch` runs it: one ask of
# a role that runs as its kind, keyed by the card's request and version, and none for a card of a role that stands.
# Which card a key names, what crew sets on a card, the area, how a reply, a refusal and an answer read,
# and what the act sends and records for each are logic cases (tests/py/test_card_commands.py); who may post under
# which key, what the hook records, each card's builder, a record's facts, and the session's start and end in the act
# and what a batch's read returns, test_cards.py; a batch card's facts, test_batches.py; what the sweep judges and
# does, test_rail.py.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
stub=$(home_of $box)/.stub-pendingyou
entries() {
  as $box python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))):
    for e in record.parse(open(f).read()):
        if e["Act"] == sys.argv[2]:
            print(json.dumps(e))' "$CREW/plugin/lib" "$1"
}
# The main level's folder on the box, where its agents' card commands run.
wd=$(space $box willdan)
# card <command...>: crew card as wldn-ops on the box, in the main level's folder, standard input passed on
card() { (export CREW_TEST_HOST=$box CREW_AGENT=wldn-ops HOME; HOME=$(home_of $box); cd "$wd" && "$CREW/plugin/bin/crew" card "$@"); }
# card2 <command...>: the same, as wldn-planner, whose questions the hook's and crew card read's wiring is shown on
card2() { (export CREW_TEST_HOST=$box CREW_AGENT=wldn-planner HOME; HOME=$(home_of $box); cd "$wd" && "$CREW/plugin/bin/crew" card "$@"); }
py_calls() { grep " pendingyou " "$CREW_TEST_LOG" | cut -d' ' -f3- || true; }

# The plan, by hand: b1 holds v1, and swb-1 builds it through Flume, whose landing card crew raises below.
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
commit_all "$w" "plan: by hand"; push_state "$w"
flume_world
crew bolt start b1 >/dev/null

# ask <agent> <tool> <args as JSON>: a Pending You call from the agent's session through Pending You's own tools, as
# Claude Code makes it on the box: crew's card hook before it, which may deny it, then the stub's answer, then the hook
# after it, which records it. Prints the answer, or "denied: <why>".
ask() {
  as $box env CREW_AGENT=$1 python3 - "$CREW/plugin/lib" "$CREW/plugin/hooks/cards" "$2" "$3" <<'PY'
import json, subprocess, sys
sys.path.insert(0, sys.argv[1])
import cards
hook, tool, given = sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
call = {"session_id": None, "tool_name": f"mcp__pendingyou__{tool}", "tool_input": given}
said = subprocess.run([sys.executable, hook, "--before"], input=json.dumps(call), capture_output=True, text=True).stdout
if said.strip():
    print("denied: " + json.loads(said)["hookSpecificOutput"]["permissionDecisionReason"])
    sys.exit(0)
with cards.Bridge(given.get("name") or "nobody", "") as py:
    got = py.call(tool, given)
subprocess.run([sys.executable, hook], input=json.dumps(dict(call, tool_response={"structuredContent": got})), text=True, check=True)
print(json.dumps(got))
PY
}

# The operator asks nothing on a card: crew's hook refuses its post before it reaches Pending You, since the user is in
# its pane.
: > "$CREW_TEST_LOG"
out=$(ask wldn-operator post_request '{"name": "wldn-operator", "idempotencyKey": "ask/wldn-operator/zones", "title": "Which zone?"}')
eq "$out" "denied: crew refuses a card from wldn-operator: only a conductor, the planner, main-level ops and the design agent ask the user on a card. The user is in your pane: ask them there."
eq "$(py_calls)" ""
ok "crew's card hook refuses the operator's card before it reaches Pending You, saying the user is in its pane"

# The planner asks the user a question of its own, through Pending You's own tools, filed in a kit's area, under a key
# of its own; the hook records it on the planner. crew card read then reads it, and the planner closes it.
q1=ask/wldn-planner/hold-the-macs
: > "$CREW_TEST_LOG"
area=$(ask wldn-planner match_area '{"cwd": "/work", "remote": "github.com/WilldanGroup/switchboard-kit", "task": "wldn-planner"}' | jq -r '.proposedName')
eq "$area" "switchboard-kit"
area=$(ask wldn-planner create_area '{"name": "switchboard-kit", "group": "wldn", "idempotencyKey": "create-area:WilldanGroup/switchboard-kit", "repo": {"remote": "github.com/WilldanGroup/switchboard-kit"}}' | jq -r .areaId)
eq "$area" "prj_stub-1"
asked=$(ask wldn-planner post_request "{\"name\": \"wldn-planner\", \"idempotencyKey\": \"$q1\", \"areaId\": \"$area\", \"kind\": \"choice\",
  \"title\": \"Hold the Macs for the demo?\", \"summary\": \"The demo is Friday.\", \"options\": [{\"id\": \"hold\", \"label\": \"Hold them\"}, {\"id\": \"go\", \"label\": \"Go on\"}],
  \"recommendedIds\": [\"hold\"], \"blocking\": false, \"session\": {\"label\": \"wldn-planner\", \"machine\": \"$box\", \"cwd\": \"$wd\"}}")
eq "$(jq -r .requestId <<<"$asked")" "req_stub-1"
eq "$(entries card.post | jq -r '[(.On | join(" ")), .Card, .Key, .By] | join(" ")')" "agent/wldn-planner req_stub-1 $q1 wldn-planner"
ok "the planner asks a question of its own through Pending You's own tools, in a kit's area, and crew's hook records it on the planner with its id and key"

eq "$(card2 read $q1)" "card $q1: req_stub-1, pending, waiting on the user
  https://www.pendingyou.com/app/r/req_stub-1"
mkdir -p "$stub/answered"; echo '{"answer": {"approved": true, "note": {"text": "Hold them until Monday."}}}' > "$stub/answered/req_stub-1.json"
eq "$(card2 read $q1)" "card $q1: req_stub-1, answered, your turn: the user has answered
  approved: yes
  note: Hold them until Monday.
  https://www.pendingyou.com/app/r/req_stub-1"
eq "$(card2 read $q1 --json | jq -r .version)" "2"
eq "$(entries card.read)" ""
: > "$CREW_TEST_LOG"
eq "$(ask wldn-planner ack_answer '{"name": "wldn-planner", "requestId": "req_stub-1", "expectedVersion": 2, "outcome": "Held until Monday."}' | jq -r .status)" "resolved"
eq "$(entries card.close | jq -r '[(.On | join(" ")), .Card, .Key] | join(" ")')" "agent/wldn-planner req_stub-1 $q1"
expect_fail "wldn-planner holds no open card under $q1 on $box" card2 read $q1
ok "crew card read prints where the question stands and the user's answer, recording nothing, and the planner's close is recorded under its key"

# Crew's own cards are crew's: the planner's post under a bolt's landing key is refused, naming the card as crew's.
: > "$CREW_TEST_LOG"
out=$(ask wldn-planner post_request '{"name": "wldn-planner", "idempotencyKey": "land/b1", "title": "Land b1"}')
eq "$out" "denied: crew refuses wldn-planner's post of the card under land/b1: a kit's landings card is crew's, raised in main-level ops's name when a bolt of the kit reads proven, and closed when nothing waits to land on the kit's main. Ask a question of your own under a key of your own, ask/wldn-planner/<what it is about>."
eq "$(py_calls)" ""
ok "the planner's post under a bolt's landing key is refused before it reaches Pending You, naming the card as crew's"

# A second question, withdrawn by its asker; a third, lost when the host signs in to Pending You again, and asked again.
q2=ask/wldn-planner/zones q3=ask/wldn-planner/cutover
ask wldn-planner post_request "{\"name\": \"wldn-planner\", \"idempotencyKey\": \"$q2\", \"kind\": \"fyi\", \"title\": \"Zones\"}" >/dev/null
eq "$(ask wldn-planner cancel_request '{"name": "wldn-planner", "requestId": "req_stub-2", "reason": "Settled in the pane."}' | jq -r .status)" "cancelled"
eq "$(entries card.close | jq -r .Card | tr '\n' ' ')" "req_stub-1 req_stub-2 "
ask wldn-planner post_request "{\"name\": \"wldn-planner\", \"idempotencyKey\": \"$q3\", \"kind\": \"fyi\", \"title\": \"Cutover\"}" >/dev/null
mv "$stub/cards.json" "$stub/cards.before-sign-in.json"
expect_fail "card req_stub-3 under $q3 is lost to its owner (Pending You: \"Not found: request:req_stub-3.\")" card2 read $q3
has "$out" "Ask it again if it still matters, saying in it that an older copy is dead"
eq "$(ask wldn-planner post_request "{\"name\": \"wldn-planner\", \"idempotencyKey\": \"$q3\", \"kind\": \"fyi\", \"title\": \"Cutover\"}" | jq -r .requestId)" "req_stub-4"
eq "$(card2 read $q3 | head -1)" "card $q3: req_stub-4, pending, waiting on the user"
ok "a question withdrawn by its asker is recorded closed; one lost after the host signs in again reads as lost, saying to ask it again, and asked again it is the key's card"

# crew's own card, raised as a raise of the series raises it: the landing of b1, read on the user's rail at the box,
# not in its owner's turn, main-level ops's. ops is up, so the line that adopts it can be told.
mains=$(home_of $box)/.local/state/crew/wldn-main; mkdir -p "$mains"
c=$(as $box herdr --session wldn-3 workspace create --cwd / --label ops | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-3 stub agent "$c" wldn-ops
echo "ops $c" > "$mains/panes"
: > "$CREW_TEST_LOG"
raised=$(as $box python3 - "$CREW/plugin/lib" "$wd" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import cards, crew, plan
facts = dict(bolt="b1", kit="switchboard-kit", units=["v1"], chores=[], batches={"v1": 1}, head="abc1400", at=None, moved=0, pr=None)
plan.row_card_post(crew.load(), "wldn", "wldn-ops", cards.landing_card, facts,
                   (sys.argv[2], "github.com/WilldanGroup/switchboard-kit"))
PY
)
eq "$raised" "card land/b1: req_stub-5 https://www.pendingyou.com/app/r/req_stub-5
call get_request (requestId req_stub-5, name wldn-ops)
told wldn-ops: call get_request (requestId req_stub-5, name wldn-ops)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
eq "$(py_calls | sed -n 1p)" 'whoami {"name": "wldn-ops"}'
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
eq "$(jq -c '[.idempotencyKey, .session.label, .kind, .approve.risk, .approve.reversible, (.highStakes // "none"), .artifacts[0].lines]' <<<"$posted")" \
  '["land/b1@wldn","wldn-ops","approve","high",false,"none",["v1"]]'
has "$(grep "agent prompt wldn-ops" "$CREW_TEST_LOG")" \
  "[crew] Your card land/b1 is up for the user: call get_request (requestId req_stub-5, name wldn-ops), to hear their answer."
eq "$(entries card.post | jq -r 'select(.Key == "land/b1") | [(.On | join(" ")), .Card, .By] | join(" ")')" "bolt/b1 req_stub-5 wldn-ops"
ok "crew's own card is posted in its owner's name under its row's key, prints the line that adopts it, and is told to its owner when raised outside its turn"

echo '{"answer": {"approved": false, "note": {"text": "Not before the box pulls."}}}' > "$stub/answered/req_stub-5.json"
: > "$CREW_TEST_LOG"
eq "$(card read land/b1)" "card land/b1: req_stub-5, answered, your turn: the user has answered
  approved: no
  note: Not before the box pulls.
  https://www.pendingyou.com/app/r/req_stub-5
card land/b1: req_stub-5 closed, as the user declined it"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.name, .outcome]')" '["wldn-ops","Declined: Not before the box pulls."]'
eq "$(entries card.close | jq -r 'select(.Key == "land/b1") | [.Card, .State, .Outcome] | join(" ")')" "req_stub-5 declined Declined: Not before the box pulls."
# With no card of the bolt's own held, a read of its key reads the bolt's reading in its place, the user's here.
eq "$(as $box "$CREW/plugin/bin/crew" card read land/b1)" "land/b1: no reading of it runs on this host: crew card session land/b1 starts it"
ok "the owner's crew card read finds the approval the user declined and closes it with their words, and with no card of the bolt's own held a read of its key reads the bolt's reading in its place"

# crew record (briefs.15, record 0031 §1): the design agent's record at each turn of its status, read on switchboard-kit's
# main as this host's checkout of it holds it, raising, changing and closing the record's one card in its name.
# adr <status> <subject> [<number>]: a record committed on the kit's main and pushed, as sluice lands the design agent's
# on GitHub
adr() {
  local n=${3:-32}
  mkdir -p "$k/docs/adr"
  printf -- '---\nnumber: %s\ntitle: switchboard runs the workflows\nstatus: %s\n---\n\n# switchboard runs the workflows\n\nStatus: %s.\n\nDeciders: the user (“no fleet”); wldn-design.\n\n## Context and problem statement\n\nThe runners cost. %s\n' \
    "$n" "$1" "$1" "$2" > "$k/docs/adr/00$n-switchboard-runs-the-workflows.md"
  git -C "$k" add docs/adr; git -C "$k" commit -qm "$2"; push "$k"
  sha=$(git -C "$k" rev-parse --short=7 HEAD)
}
# design <args...>: crew record as wldn-design on the box, in its pane's folder and its Claude session s-design
design() { (export CREW_TEST_HOST=$box CREW_AGENT=wldn-design CREW_SESSION=$box:s-design HOME; HOME=$(home_of $box); cd "$(space $box willdan)" && "$CREW/plugin/bin/crew" record "$@"); }

adr proposed "docs(adr): 0032 switchboard runs the workflows"
: > "$CREW_TEST_LOG"
eq "$(design switchboard-kit 32 --proposed)" "record 0032 in switchboard-kit: proposed at $sha
card record/switchboard-kit/0032: req_stub-6 https://www.pendingyou.com/app/r/req_stub-6
call get_request (requestId req_stub-6, name wldn-design)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
eq "$(jq -c '[.idempotencyKey, .session.label, .session.cwd, .kind, .approve.risk, .approve.reversible, .artifacts[0].lines[0]]' <<<"$posted")" \
  "[\"record/switchboard-kit/0032@wldn\",\"wldn-design\",\"$k\",\"approve\",\"low\",true,\"# switchboard runs the workflows\"]"
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
  '["record/switchboard-kit/0033@wldn","choice",["accept"],["loosen","accept","back"],"## Where your rules decided"]'
eq "$(entries record.proposed | jq -r 'select(.On[0] == "record/switchboard-kit/0033") | .Form')" "alternatives"
eq "$(entries record.proposed | jq -r 'select(.On[0] == "record/switchboard-kit/0032") | .Form // "none"' | sort -u)" "none"
ok "a record a rule decided is raised as one choice, loosen the rules as drafted, accept as ruled or send back, its alternatives on its face, its status recording that its card offered them"

# The design agent's own session: the user's yes to record 34 in their own words, and the planner's tell of a yes to 35.
transcript $box s-design >/dev/null <<EOF
{"type":"user","uuid":"d34a0000-0000-4000-8000-000000000034","timestamp":"$(ago 2)","message":{"role":"user","content":"Yes, accept 34 as written"}}
{"type":"user","uuid":"d35a0000-0000-4000-8000-000000000035","timestamp":"$(ago 1)","message":{"role":"user","content":"[crew tell from wldn-planner] The user said: accept 35"}}
EOF
adr proposed "docs(adr): 0034 settled beside the user" 34
: > "$CREW_TEST_LOG"
eq "$(design switchboard-kit 34 --proposed --settled-in-pane --excerpt "Yes, accept 34 as written")" \
  "record 0034 in switchboard-kit: proposed at $sha, the user's yes given in the pane; no card is raised"
eq "$(py_calls)" ""
eq "$(entries record.proposed | jq -r 'select(.On[0] == "record/switchboard-kit/0034") | [.State, (.From | join(" ")), .Chars] | join(" ")')" \
  "settled in the pane session/s-design/d34a0000-0000-4000-8000-000000000034 25"
[[ $(cat "$(home_of $box)"/.local/state/crew/wldn/runs/*/*.rec) != *"accept 34"* ]] || fail "the run record holds the user's words"
ok "a record settled with the user in the pane, in their own words read in the design agent's transcript, records their yes there naming where the words are, and no card is raised"

adr proposed "docs(adr): 0035 settled on another agent's word" 35
: > "$CREW_TEST_LOG"
expect_fail "crew records record 0035 in switchboard-kit as settled in no pane: the words are wldn-planner's, passed on with crew tell, and not the user's; tell wldn-planner that the user settles a record in your pane or on its card; run crew record switchboard-kit 35 --proposed without --settled-in-pane, and the user answers on its card" \
  design switchboard-kit 35 --proposed --settled-in-pane --excerpt "accept 35"
eq "$(py_calls)" ""
eq "$(entries record.proposed | jq -r 'select(.On[0] == "record/switchboard-kit/0035") | .State')" ""
ok "a record settled on another agent's tell of the user's yes is refused naming who said it, with nothing recorded or raised"

# rail-cards, "The command raises it": record 34's card, posted from mac-studio in wldn-design's name, stands in the
# branch's run record where the box's sign-in can't reach it, so crew record on the box posts it saying the older copy
# was lost.
CREW_AGENT=wldn-design as mac-studio python3 "$CREW/plugin/lib/record.py" emit --label wldn --act card.post \
  --on record/switchboard-kit/0034 --field Card=req_old34 --field Key=record/switchboard-kit/0034 >/dev/null
HOST=mac-studio expect_ok crew events --push
: > "$CREW_TEST_LOG"
design switchboard-kit 34 --proposed >/dev/null
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
eq "$(jq -r .idempotencyKey <<<"$posted")" "record/switchboard-kit/0034@wldn"
[[ $(jq -r .summary <<<"$posted") == "An older copy of this card was lost: dismiss it in the app."* ]] ||
  fail "the summary does not open saying the older copy was lost: $posted"
ok "crew record --proposed, run where its record's card is held on a host this one's sign-in can't reach, posts it saying the older copy was lost"

# The act's change of crew's own card (record 0031 §3): b1's landing card raised again after the user declined it is a
# new card under the key's revision, changed in place while it waits, and once the user answers it and its head moves
# since, acked with the change note and followed by its new version saying the head moved since the approval, which
# crew card read then finds as the row's card.
# land <change|post> <head>: b1's landing card raised by the act as raise_land calls it, on the box, asked anew once
# the head the run record holds for the card is another
land() {
  as $box python3 - "$CREW/plugin/lib" "$wd" "$1" "$2" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import cards, crew, plan
facts = dict(bolt="b1", kit="switchboard-kit", units=["v1"], chores=[], batches={"v1": 1}, head=sys.argv[4], at=None, moved=0, pr=None)
where = (sys.argv[2], "github.com/WilldanGroup/switchboard-kit")
fleet = crew.load()
acts = plan.CardActs(fleet)
if sys.argv[3] == "post":
    plan.row_card_post(fleet, "wldn", "wldn-ops", cards.landing_card, facts, where, acts)
else:
    es = acts.entries("wldn")
    anew = cards.head_anew(es, cards.card_under(es, "land/b1", "wldn-ops"), sys.argv[4])
    plan.row_card_change(fleet, "wldn", "wldn-ops", cards.landing_card, facts, f"Head is now {sys.argv[4]}", where, acts, anew=anew)
PY
}
: > "$CREW_TEST_LOG"
eq "$(land post abc1500 | head -1)" "card land/b1: req_stub-9 https://www.pendingyou.com/app/r/req_stub-9"
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .idempotencyKey)" "land/b1@wldn:2"
ok "a row's card raised again after its last card closed is posted under the key with its revision, a new card rather than the closed one given back"

: > "$CREW_TEST_LOG"
eq "$(land change abc1600)" "card land/b1: req_stub-9 changed, now version 2"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request update_request "
echo '{"answer": {"approved": false, "note": {"text": "Not with that head."}}}' > "$stub/answered/req_stub-9.json"
: > "$CREW_TEST_LOG"
raised=$(land change abc1700)
eq "$(head -2 <<<"$raised")" "card land/b1: req_stub-9 closed, the user having answered it, and its new version follows it
card land/b1: req_stub-10 https://www.pendingyou.com/app/r/req_stub-10"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer whoami match_area post_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .outcome)" "Head is now abc1700"
eq "$(py_calls | sed -n 6p | cut -d' ' -f2- | jq -c '[.idempotencyKey, .follows]')" '["land/b1@wldn:3","req_stub-9"]'
has "$(py_calls | sed -n 6p | cut -d' ' -f2- | jq -r .summary)" "Its head moved since your approval, from abc1600 to abc1700"
eq "$(jq -r '.["req_stub-9"].status' "$stub/cards.json")" "resolved"
eq "$(entries card.close | jq -r 'select(.Card == "req_stub-9") | [.Key, .State] | join(" ")')" "land/b1 closed"
eq "$(entries card.post | jq -r 'select(.Card == "req_stub-10") | [(.On | join(" ")), .Key, .By] | join(" ")')" "bolt/b1 land/b1 wldn-ops"
eq "$(card read land/b1 | head -1)" "card land/b1: req_stub-10, pending, waiting on the user"
ok "a card waiting on the user is changed in place; once they answer it and its head moves, it is acked with the change note and its new version, saying so, posted following it, recorded under the row's key, and crew card read finds that one"

# A batch's card and its one reading session, raised by crew in the planner's name once the reviewer's summary is
# there, on the main level's host, the box: v1's change read at its commit in switchboard-kit.
export PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
change "$k" v1 0 2; commit_all "$k" "docs(v1): the change"; push "$k"; sha=$(git -C "$k" rev-parse HEAD)
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
eq "$out" "card batch/1: req_stub-11 https://www.pendingyou.com/app/r/req_stub-11
call get_request (requestId req_stub-11, name wldn-planner)"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami match_area post_request "
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
s1=$cards_dir/batch/1/session.json; u1=$(jq -r .url "$s1"); p1=$(jq -r .pid "$s1")
[[ $u1 =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on the box's tailnet name: $u1"
eq "$(jq -c '[.idempotencyKey, .session.label, .kind, .title, .context.links[0].url]' <<<"$posted")" \
  "[\"batch/1@wldn\",\"wldn-planner\",\"fyi\",\"Goal of b1 (batch 1)\",\"$u1\"]"
has "$(jq -r .summary <<<"$posted")" "1 change to read, nothing to approve."
has "$(jq -r '.artifacts[0].lines | join("\n")' <<<"$posted")" "**swb-1 · v1**"$'\n\n'"v1 gives each tenant its own zone."
folder=$(cd "$reports" && pwd -P)/batch-wldn-1
eq "$(jq -r '.argv | map(select(endswith(".md"))) | join(" ")' "$(home_of $box)/.stub-plannotator/$p1.json")" \
  "$folder/00-summary.md $folder/01-v1-proposal.md $folder/01-v1-design.md $folder/01-v1-specs-x-spec.md $folder/01-v1-tasks.md"
eq "$(entries card.post | jq -r 'select(.Key == "batch/1") | [(.On | join(" ")), .Card, .By] | join(" ")')" "batch/1 req_stub-11 wldn-planner"
: > "$CREW_TEST_LOG"
ok "a batch's card is raised once its summary is there, in the planner's name, its one reading session on the main level's host started first and linked from it"

# The host signs in to Pending You again: batch 1's card reads "not found" to the planner, and the sweep's raise posts
# it again under its key, on the session that still runs.
mv "$stub/cards.json" "$stub/cards.before-batch-sign-in.json"
expect_ok raise 1
has "$out" "card batch/1: req_stub-11 is lost to wldn-planner (Pending You: \"Not found: request:req_stub-11.\")"
has "$out" "card batch/1: req_stub-12 https://www.pendingyou.com/app/r/req_stub-12"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request whoami match_area post_request "
posted=$(py_calls | sed -n 5p | cut -d' ' -f2-)
has "$(jq -r .summary <<<"$posted")" "An older copy of this card was lost: dismiss it in the app."
eq "$(jq -r .idempotencyKey <<<"$posted")" "batch/1@wldn:2"
eq "$(jq -r '.context.links[0].url' <<<"$posted")" "$u1"; eq "$(listed)" "$p1"
eq "$(entries card.close | jq -r 'select(.Key == "batch/1") | [.Card, .State] | join(" ")')" "req_stub-11 lost"
ok "a batch's card lost to the planner is raised again by the sweep's entry under its key, saying its older copy is dead, its link the session's that still runs"

expect_ok planner session batch/1; eq "$out" "$u1"; eq "$(listed)" "$p1"
expect_fail "a batch has one reading session, on the whole batch: crew card session batch/1" planner session batch/1 v1
expect_fail "b1 is no row of switchboard-kit's landings card, so it has no reading: unit v1 has not merged: it is launching" \
  planner session land/b1
expect_fail "crew card wait is gone: crew keeps no process waiting on a card or its reading. Run crew card read land/b1 when" \
  planner wait land/b1
expect_fail "land/switchboard-kit is switchboard-kit's landings card, wldn-ops's, which has no reading of its own" \
  planner session land/switchboard-kit
eq "$(listed)" "$p1"
printf '%s\n' 'Case: The console gets a bolt of its own.' 'Do: bolt new console-pages "The console lists them." --repo switchboard-kit' > "$T/p.rec"
crew plan propose "$T/p.rec" >/dev/null
expect_fail "proposal/1's card has nothing to read: it holds the proposal whole" crew card session proposal/1
ok "crew card session gives a running session's link again, and refuses a unit with a batch's key, a bolt's key while it is no row of its kit's landings card, saying why, the kit's card, which has no reading of its own, and a short proposal's; crew card wait is refused, naming crew card read"

# A batch's session started from a shell naming no PLANNOTATOR_PORT, as on a Mac outside any agent, while batch 1's
# holds 19432, plannotator's one fixed port in remote mode: crew gives it its own range, so it takes the next port.
[[ $u1 == *:19432 ]] || fail "batch 1's session is not the one holding 19432: $u1"
batch 2
out=$(unset PLANNOTATOR_PORT; planner session batch/2 2>&1) || fail "batch 2's session with no port named failed: $out"
[[ $out =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:([0-9]+)$ ]] && (( BASH_REMATCH[1] > 19432 && BASH_REMATCH[1] <= 19451 )) \
  || fail "not a link on the next free port of 19432-19451: $out"
eq "$(jq -r .url "$cards_dir/batch/2/session.json")" "$out"
ok "a card's session started from a shell naming no port, while another holds 19432, takes the next free port of crew's range"

echo '{"answer": {"note": {"text": "v1: say what the zone is."}}}' > "$stub/answered/req_stub-12.json"
: > "$CREW_TEST_LOG"
expect_ok planner read batch/1
eq "$out" "batch/1: sent back on its card, with a note:
v1: say what the zone is.
card batch/1: req_stub-12 closed
ended batch/1's session, plannotator pid $p1"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request whoami get_request ack_answer "
eq "$(py_calls | sed -n 5p | cut -d' ' -f2- | jq -r .outcome)" "Read; 1 note sent to its team"
gone "$p1"
[[ ! -e $cards_dir/batch/1 ]] || fail "batch/1's session folder outlived its card"
eq "$(entries card.close | jq -r 'select(.Key == "batch/1" and .State == "closed") | [.Card, .Outcome] | join(" ")')" "req_stub-12 Read; 1 note sent to its team"
ok "the card sent back is read by the planner's crew card read with its note, and crew closes it and ends its session"

raise 2 >/dev/null; p2=$(jq -r .pid "$cards_dir/batch/2/session.json")
notes=$'# Annotations\n\n1. 01-v1-design.md: say why one zone.\n2. 01-v1-tasks.md: a task for the console.'
decide "$p2" "$(jq -nc --arg f "$notes" '{decision: "annotated", feedback: $f, annotationCount: 2}')"
: > "$CREW_TEST_LOG"
expect_ok planner read batch/2
eq "$out" "batch/2: annotated
$notes
card batch/2: req_stub-13 withdrawn
batch/2's session had ended as the user sent it, and batch/2 is forgotten"
eq "$(py_calls | tail -1 | cut -d' ' -f2- | jq -r .reason)" "Read; 2 notes sent to their teams"
ok "the session sent with its annotations is read with every one as the user wrote it, and crew closes the card and forgets the session"

batch 3
: > "$CREW_TEST_LOG"
out=$(CREW_AGENT=wldn-planner as $box env -u PLANNOTATOR_URL_HOST python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import crew, plan
plan.raise_batch(crew.load(), {"label": "wldn", "key": "batch/3", "group": "batches"})' "$CREW/plugin/lib" 2>&1) || fail "batch 3's raise failed: $out"
has "$out" "card batch/3: its reading could not be opened on the tailnet: plannotator gave batch/3's session the link http://localhost:"
has "$out" "card batch/3: req_stub-14 https://www.pendingyou.com/app/r/req_stub-14"
posted=$(py_calls | sed -n 3p | cut -d' ' -f2-)
has "$(jq -r .summary <<<"$posted")" "Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and the planner starts it with crew card session batch/3; this card then carries its link."
eq "$(jq -c '.context.links' <<<"$posted")" "[]"
eq "$(listed)" ""
echo '{"answer": {}}' > "$stub/answered/req_stub-14.json"
out=$(unset PLANNOTATOR_URL_HOST; planner read batch/3 2>&1) || fail "the planner's read of batch 3 failed: $out"
eq "$out" "batch/3: sent back on its card, with no note
card batch/3: req_stub-14 closed"
eq "$(listed)" ""
expect_fail "no card and no reading of batch/5 is open on $box" planner read batch/5
ok "a session whose link only the host could open is ended and the card raised all the same, saying so; the planner's read of its card starts no reading and closes it on the tap; a read with neither card nor reading is refused"

# A batch's session sent with no card of it held on the main level's host, as when its card was posted from a host the
# main level has left: the planner's read records crew's close of the batch, read, in the planner's name, and ends the
# session.
batch 4
expect_ok planner session batch/4; p4=$(jq -r .pid "$cards_dir/batch/4/session.json")
decide "$p4" '{"decision": "approved"}'
: > "$CREW_TEST_LOG"
expect_ok planner read batch/4
eq "$out" "batch/4: approved
batch/4: recorded read, Read; no notes
batch/4's session had ended as the user sent it, and batch/4 is forgotten"
eq "$(py_calls)" ""
eq "$(entries batch.close | jq -r 'select(.Key == "batch/4") | [.Key, .State, .Outcome, .By] | join(" ")')" "batch/4 read Read; no notes wldn-planner"
# Sent while Pending You refuses its card's close: the card stays open, and crew records the batch read all the same.
batch 6
raise 6 >/dev/null; c6=$(entries card.post | jq -r 'select(.Key == "batch/6") | .Card'); p6=$(jq -r .pid "$cards_dir/batch/6/session.json")
decide "$p6" '{"decision": "approved"}'
echo "cancel_request Too many requests." > "$stub/refuse"
expect_ok planner read batch/6
: > "$stub/refuse"
has "$out" "card batch/6 not closed: Pending You refused the close: Too many requests."
has "$out" "batch/6: recorded read, Read; no notes"
eq "$(entries card.close | jq -r "select(.Card == \"$c6\") | .Refused")" "Pending You refused the close: Too many requests."
eq "$(entries batch.close | jq -r 'select(.Key == "batch/6") | [.Key, .State, .Outcome, .By] | join(" ")')" "batch/6 read Read; no notes wldn-planner"
planner end batch/6 >/dev/null
ok "a batch's session sent with no card held, or with its card's close refused, records crew's close of the batch, read, in the planner's name"

# A proposal's card, crew's own (plan-proposals, record 0031 §1, change crew-raises-a-proposals-card): raised by crew plan
# propose in the planner's name on its own host, withdrawn by a rewrite that moves it from one list to lists of
# questions while it waits, a change of form update_request never makes, and followed by the new version, followed by
# a new version too when a rewrite comes after the user's note answered it, answered on the card and applied with its
# boxes as they stand, then closed with what was applied. Which act each step makes is a logic case
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
  "[\"proposal/$n@wldn\",\"wldn-planner\",\"Plan change to p1: 2 new\",\"multi\",[\"add:p-a\",\"add:p-b\"],[\"add:p-a\",\"add:p-b\"]]"
grep -q "agent prompt wldn-planner" "$CREW_TEST_LOG" && fail "the planner was told of the card its own command raised"
ok "crew plan propose raises the proposal's card in the planner's name under proposal/<n>, one checkbox list every row set as proposed, and prints the line that adopts it"

# A rewrite of six rows while the card waits: its one list becomes two, asked as questions (rows-1, rows-2), a form
# Pending You's update_request never changes into, so the waiting card is withdrawn with the note and the new version
# follows it.
: > "$CREW_TEST_LOG"
as_planner expect_ok crew plan propose --replaces "$n" "$(proposal 'Case: The page gets a bolt of its own, with c to g in place of b.' \
  'Do: bolt new p2 "The page is drawn." --repo switchboard-kit' 'Do: unit add p-a "A page." --bolt p2' 'Do: unit add p-c "C page." --bolt p2' \
  'Do: unit add p-d "D page." --bolt p2' 'Do: unit add p-e "E page." --bolt p2' 'Do: unit add p-f "F page." --bolt p2' \
  'Do: unit add p-g "G page." --bolt p2')"
m=$(opened); c1=$(raised "$n")
has "$out" "card proposal/$n: $c withdrawn, its kind having changed, and its new version follows it"
[[ -n $c1 && $c1 != "$c" ]] || fail "no new version of proposal/$n's card was posted:"$'\n'"$out"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request cancel_request whoami match_area post_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -c '[.requestId, .reason]')" "[\"$c\",\"Rewritten as proposal $m after your note\"]"
eq "$(py_calls | sed -n 6p | cut -d' ' -f2- | jq -c '[.idempotencyKey, .follows, .title, [.questions[] | [.id, [.options[].id]]]]')" \
  "[\"proposal/$n@wldn:2\",\"$c\",\"Plan change to p2: 6 new\",[[\"rows-1\",[\"add:p-a\",\"add:p-c\",\"add:p-d\"]],[\"rows-2\",[\"add:p-e\",\"add:p-f\",\"add:p-g\"]]]]"
eq "$(entries card.close | jq -r "select(.Card == \"$c\") | [.State, .Outcome] | join(\": \")")" "withdrawn: changed in kind: a new card follows it"
eq "$(as_planner crew rail --label wldn | grep -A4 "proposal $m (wldn)" | grep 'card:' | sed 's/^ *//')" \
  "card:   proposal/$n, open, asked by wldn-planner ($c1)"
ok "a rewrite that moves the card from one list to lists of questions withdraws the waiting card with its note and posts the new version following it, and the rail's row for the successor carries the chain's key"

# The user sends the card with a note asking for a change, which answers it; the planner's rewrite follows it.
echo '{"answer": {"answers": {"rows-1": {"choiceIds": ["add:p-a", "add:p-c"]}}, "note": {"text": "c before a, and only those."}}}' > "$stub/answered/$c1.json"
: > "$CREW_TEST_LOG"
as_planner expect_ok crew plan propose --replaces "$m" "$(proposal 'Case: The page gets a bolt of its own, c before a.' \
  'Do: bolt new p3 "The page is drawn." --repo switchboard-kit' 'Do: unit add p-c "C page." --bolt p3' 'Do: unit add p-a "A page." --bolt p3')"
r=$(opened); c2=$(raised "$n")
has "$out" "card proposal/$n: $c1 closed, the user having answered it, and its new version follows it"
[[ -n $c2 && $c2 != "$c1" ]] || fail "no new version of proposal/$n's card was posted:"$'\n'"$out"
eq "$(py_calls | cut -d' ' -f1 | tr '\n' ' ')" "whoami get_request ack_answer whoami match_area post_request "
eq "$(py_calls | sed -n 3p | cut -d' ' -f2- | jq -r .outcome)" "Rewritten as proposal $r after your note"
eq "$(py_calls | sed -n 6p | cut -d' ' -f2- | jq -c '[.idempotencyKey, .follows, .title, [.options[].id]]')" \
  "[\"proposal/$n@wldn:3\",\"$c1\",\"Plan change to p3: 2 new\",[\"add:p-c\",\"add:p-a\"]]"
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
# card hook records them: the design agent's, whose pane herdr lists with no agent in it, and the planner's, which
# runs. crew board reads them and acts on none.
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
lc=$(land post abc1900 | sed -n '1s/^card [^:]*: \([^ ]*\).*/\1/p')
qd=$(question wldn-design); qp=$(question wldn-planner)
pp=$(as $box herdr --session wldn-3 workspace create --cwd / --label planner | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-3 stub agent "$pp" wldn-planner
pd=$(as $box herdr --session wldn-3 workspace create --cwd / --label design | jq -r .result.root_pane.pane_id)
printf 'planner %s\ndesign %s\n' "$pp" "$pd" >> "$mains/panes"
closes=$(entries card.close | wc -l)
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew board --label wldn
eq "$(py_calls)" ""; eq "$(entries card.close | wc -l)" "$closes"
HOST=$box expect_ok crew rail --label wldn; r=$out
eq "$(sed -n '/^cards swept:$/,/^$/p' <<<"$r")" "cards swept:
  land/b1 (wldn), wldn-ops's $lc: withdrawn: its bolt no longer waits to land
  a question (wldn), wldn-design's $qd: withdrawn: wldn-design ended"
asked=$(sed -n '/^questions waiting on you:$/,/^$/p' <<<"$r")
has "$asked" "a question (wldn), asked by wldn-planner on $box ($qp)"; lacks "$asked" "$qd"
eq "$(py_calls | sed -n 1p)" 'whoami {"name": "crew"}'
eq "$(py_calls | awk 'NR > 1 && $1 != "get_request" {exit} NR > 1 {print $1, $2, $3}' | sort -u)" 'get_request {"name": "crew",'
has "$(py_calls)" "cancel_request {\"name\": \"wldn-ops\", \"reason\": \"its bolt no longer waits to land\", \"requestId\": \"$lc\"}"
has "$(py_calls)" "cancel_request {\"name\": \"wldn-design\", \"reason\": \"wldn-design ended; ask again if it still matters\", \"requestId\": \"$qd\"}"
eq "$(entries card.close | jq -r "select(.Card == \"req_stub-4\" or .Card == \"$lc\" or .Card == \"$qd\") | [.Card, .State, (.On | join(\" \"))] | join(\" \")" | tail -3)" \
  "req_stub-4 lost agent/wldn-planner
$lc withdrawn bolt/b1
$qd withdrawn agent/wldn-design"
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

# aged <id> <time>: the box's entry set back to the time, in its own file and on wldn/main, where the rail reads it (read.5)
aged() {
  local f w=$T/aged
  for f in "$(home_of $box)/.local/state/crew/wldn/runs/$box"/*.rec; do rewrite "$f" "/^Id: $1\$/,/^\$/s/^At: .*/At: $2/"; done
  rm -rf "$w"; git clone -q -b wldn/main "$ws" "$w"
  for f in "$w/runs/$box"/*.rec; do rewrite "$f" "/^Id: $1\$/,/^\$/s/^At: .*/At: $2/"; done
  commit_all "$w" "runs($box): an entry set back by hand"; push_state "$w"
}

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
aged "$id" "$old"
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew rail --label wldn; r=$out
pc=$(sed -n "s|^card $k: \(req_stub-[0-9]*\) https.*|\1|p" <<<"$r")
[[ -n $pc ]] || fail "the read raised no card for $k:"$'\n'"$r"
eq "$(py_calls | grep '^post_request' | cut -d' ' -f2- | jq -r '[.idempotencyKey, .session.label] | join(" ")')" "$k@wldn wldn-planner"
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
aged "$id" "$old"
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew rail --label wldn; r=$out
sc=$(sed -n "s|^card $op: \(req_stub-[0-9]*\) https.*|\1|p" <<<"$r")
[[ -n $sc ]] || fail "the read raised no card for $op:"$'\n'"$r"
eq "$(py_calls | grep '^post_request' | cut -d' ' -f2- | jq -r "select(.idempotencyKey == \"$op@wldn\") | [.session.label, .kind, .intent] | join(\" \")")" "wldn-ops action do"
has "$r" "  $op (wldn), wldn-ops's $sc: posted: its row had none open"
has "$r" "    card:   $op, open, asked by wldn-ops ($sc)"
ok "a step waiting on the user has its card raised by crew ops step, and one whose post was refused raised through the step's raise by the first read after ten minutes"

# Pending You's notice of a change on a card (design Decision 5 of roles-run-as-flume-kinds): with wldn's planner run as
# its kind, crew _answered, as `pendingyou watch` runs it on the box for each change on a card there, writes one card
# ask of the planner keyed by the card's request and version, from the notice's ids and asker alone, calling no Pending
# You tool; the same change handed again asks nothing more, and a later change on the card is asked again; a card of
# wldn-ops, which stands, asks nothing.
role_stream wldn planner wldn-main
# notice <asker> <request> <version>: crew _answered on the box as Pending You's watch runs it, the card on its input
notice() {
  jq -cn --arg n "$1" --arg r "$2" --argjson v "$3" '{requestId: $r, sessionLabel: $n, status: "answered", version: $v, title: "Approve 12?"}' |
    (export CREW_TEST_HOST=$box HOME PENDINGYOU_REQUEST_ID=$2 PENDINGYOU_VERSION=$3 PENDINGYOU_EVENT=answer_ready; HOME=$(home_of $box)
     unset CREW_AGENT CREW_LABEL; cd "$HOME" && "$CREW/plugin/bin/crew" _answered)
}
cask() { git --git-dir "$ws" show wldn/main:asks.rec | recsel -t Ask "$@"; }
: > "$CREW_TEST_LOG"
t0=$(act_tip)
expect_ok notice wldn-planner req_stub-77 3
eq "$(cask -p Role,From,What,Names,Key,Words | tr '\n' ' ')" \
  "Role: planner From: crew What: card Names: card/req_stub-77 Key: card/req_stub-77/3 Words: the user answered it "
eq "$(acts_since "$t0")" "1"
eq "$(py_calls)" ""
expect_ok notice wldn-planner req_stub-77 3
has "$out" "wldn-planner is already asked by card/req_stub-77/3; nothing written"
eq "$(cask -c)" "1"
expect_ok notice wldn-planner req_stub-77 4
eq "$(cask -P Key | grep . | tr '\n' ' ')" "card/req_stub-77/3 card/req_stub-77/4 "
expect_ok notice wldn-ops req_stub-78 2
eq "$(cask -c)" "2"
eq "$(py_calls)" ""
ok "a change on a card of a role that runs as its kind is one ask of the role, keyed by the card's request and version and read from the notice alone, and a card of a role that stands asks nothing"
