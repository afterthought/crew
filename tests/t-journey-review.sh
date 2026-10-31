# What reaches the user, through the crew command on the stubs (tests.11, record 0022): constructed changes make a batch
# due, told to the planner once, and crew review starts the reviewer, while a host of the partition does not answer,
# since both read the run record from the partition's branch (read.5); the reviewer's summary ends the batch, raising
# its card with its reading session in the planner's name, tried twice when its first start fails, and raised without
# it, naming crew card session, when both fail, the planner's crew card session then starting it and changing the
# card to carry its link; crew rail lists what waits, with each row's card; crew's card hook refuses an agent's card
# under crew's own key; a batch card's one reading session is written from every team's host and started on the main
# level's, an old batch card's on its unit's team's host, and none for a verify report, which no row has; the rail's
# refresh tells the planner once that the user sent the reading, its crew card read returns the user's words and
# closes the batch's card, ending its session, and a reading approved with no words is recorded read at the refresh;
# crew card end ends an old card's, and a rail read sweeps what is dead; writes and tells reach the agents they should,
# never one waiting on a question; and a reviewer that runs as its kind is asked its batch and hands it back, asking the
# planner. Which changes are due,
# what each row and card says, whose key a card may take and in what form, and what a session does are logic cases
# (tests/py/test_batches.py, test_rail.py, test_cards.py, test_review.py); each step here checks a command's wiring
# once.
# Reads: plugin/hooks/ plugin/roles/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
ak=$(kit mac-studio willdan atlas-kit); akd=$(dirname "$ak")
export CREW_LABEL=wldn PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
now=$(date +%s)
shown() { python3 -c 'import sys, time; print(time.strftime(sys.argv[2], time.localtime(int(sys.argv[1]))))' "$((now - $1 * 60))" "$2"; }
commit_at() { git -C "$2" add -A && GIT_COMMITTER_DATE="@$((now - $1 * 60)) +0000" git -C "$2" commit -qm "$3"; }
real() { (cd "$1" && pwd -P); }
entries() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))):
    for e in record.parse(open(f).read()):
        if e["Act"] == sys.argv[2]:
            print(json.dumps(e))' "$CREW/plugin/lib" "$2"
}
cards=.local/state/crew/cards/wldn
rec() { jq -r "$3" "$(home_of "$1")/$cards/$2/session.json"; }
stub() { jq -r "$3" "$(home_of "$1")/.stub-plannotator/$2.json"; }
listed() { as "$1" plannotator sessions --json | jq -r '[.[].pid] | sort | map(tostring) | join(" ")'; }
gone() { python3 -c 'import os, sys, time
pid, give_up = int(sys.argv[1]), time.monotonic() + 600
while True:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        break
    if time.monotonic() > give_up:
        sys.exit(f"pid {pid} is still running")
    time.sleep(0.05)' "$1"; }
decide() { printf '%s\n' "$3" > "$(home_of "$1")/.stub-plannotator/$2.decision"; gone "$2"; }
# The plan, by hand: b1 on swb-1 (the box) holds x1 and v1; m1 on atl-1 (mac-studio) holds z1.
w=$T/hand; git clone -q -b wldn/main "$ws" "$w"
python3 - "$CREW/plugin/lib" "$w/plan.rec" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
for b, kit in (("b1", "switchboard-kit"), ("m1", "atlas-kit")):
    p.insert(plan.Rec("Bolt", [("Bolt", b), ("Repo", kit), ("Goal", f"Goal of {b}.")]))
for u, b, kit in (("x1", "b1", "switchboard-kit"), ("v1", "b1", "switchboard-kit"), ("z1", "m1", "atlas-kit")):
    p.insert(plan.Rec("Unit", [("Unit", u), ("Repo", kit), ("Bolt", b), ("Intent", f"Unit {u}.")]))
open(f, "w").write(p.text())
PY
commit_all "$w" "plan: by hand"; push_state "$w"
crew bolt give swb-1 b1 >/dev/null 2>&1; crew bolt give atl-1 m1 >/dev/null 2>&1
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"
crew main up wldn >/dev/null 2>&1
edit teams "$(part wldn)['review'] = {'every': 2, 'hours': 4}"
planner_told() { grep -c "^$box wldn-3 agent prompt wldn-planner '\[crew\] A batch of wldn" "$CREW_TEST_LOG" || true; }
build() {  # build <team> <unit> <kit dir>: its construct run by its conductor, its change committed, and the wait that ends it
  CREW_AGENT=$1-conductor crew unit run $2 construct >/dev/null; change "$3/places/$2" $2 0 2; commit_all "$3/places/$2" "docs($2): the change"
  CREW_AGENT=$1-conductor crew unit wait $2 >/dev/null
}
: > "$CREW_TEST_LOG"
build atl-1 z1 "$akd"
eq "$(planner_told)" "0"
# mac-studio, which holds a wldn operator session and z1's entries, does not answer the box from here on: the batch is
# reckoned from wldn/main, which holds them.
echo mac-studio > "$T/down"
build swb-1 x1 "$kd"
eq "$(planner_told)" "1"
has "$(grep "agent prompt wldn-planner" "$CREW_TEST_LOG")" "s changes is due: x1 (swb-1), z1 (atl-1); 2 changes are due, and a batch is every 2. Start its reviewer with crew review wldn"
eq "$(entries $box batch.due | jq -r '[.Count, (.On | join(" "))] | join(" ")')" "2 agent/wldn-planner unit/x1 unit/z1"
ok "changes constructed by two teams make a batch due at the partition's setting, told to its planner once, on a conductor's wait, while a host of the partition does not answer"

: > "$CREW_TEST_CLAUDE_LOG"
CREW_AGENT=wldn-planner expect_ok crew review wldn
lacks "$(grep " ssh mac-studio " "$CREW_TEST_LOG")" "ssh mac-studio"
rm "$T/down"
summary=$(home_of $box)/.local/state/crew/wldn-main/reports/batch-wldn-1.md
has "$out" "wldn-reviewer is reviewing batch 1 of wldn, into $summary"
eq "$(jq -r '"\(.agent) \(.argv[3])"' "$CREW_TEST_CLAUDE_LOG")" "wldn-reviewer high"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops,operator,review"
rpane=$(herdr_state $box wldn-3 '.agents | to_entries[] | select(.value.name == "wldn-reviewer") | .key')
grep -q "agent prompt \($rpane\|wldn-reviewer\) '\[crew\]" "$CREW_TEST_LOG" && fail "the reviewer was greeted"
CREW_AGENT=wldn-planner expect_fail "wldn-reviewer is still reviewing a batch" crew review wldn
CREW_AGENT=wldn-planner expect_fail "batch 1's review is still running after the wait's 0 ms" crew review wldn --wait --timeout 0
has "$(grep "agent prompt $rpane " "$CREW_TEST_LOG" | tail -1)" "z1 (atl-1, atlas-kit on mac-studio, at $(git -C "$ak" rev-parse --short unit/z1)): list its files with \`ssh -o BatchMode=yes mac-studio git -C $ak"
mkdir -p "$(dirname "$summary")"; printf '# Batch 1\n' > "$summary"
refusals=$(home_of $box)/.stub-plannotator/refuse-starts
mkdir -p "${refusals%/*}"; echo 1 > "$refusals"  # the reading's first start fails, and its second opens
CREW_AGENT=wldn-planner expect_ok crew review wldn --wait
has "$out" "card batch/1: its reading could not be opened on the tailnet: plannotator ended before batch/1's session was ready: stub: refused to start; crew tries once more"
eq "$(grep -v '^card batch/1: its reading' <<<"$out")" "card batch/1: req_stub-1 https://www.pendingyou.com/app/r/req_stub-1
call get_request (requestId req_stub-1, name wldn-planner)
batch summary: $summary"
eq "$(entries $box review.batch | jq -r '[.Batch, (.On | join(" "))] | join(" ")')" "1 batch/1 unit/x1 unit/z1"
eq "$(entries $box card.post | jq -r '[(.On | join(" ")), .Card, .Key, .By, .Unread // "opened"] | join(" ")')" "batch/1 req_stub-1 batch/1 wldn-planner opened"
CREW_AGENT=wldn-planner expect_ok crew review wldn --wait
eq "$out" "batch summary: $summary"
eq "$(entries $box card.post | jq -r .Card)" "req_stub-1"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops,operator"
ok "the planner starts the reviewer fresh in a review tab, not greeted, sent each change and how to read it on its team's host, while a host of the partition does not answer, and no second while it reviews; its summary ends the batch, recorded, raises its card in the planner's name once, its reading tried twice, and closes its tab"

# v1 is in verify, its report newer than its last commit, and waits on nobody (teams.17).
pv=$(place "$k" b1 v1); change "$pv" v1 2 2; commit_at 60 "$pv" "feat(v1): done"
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
stamp=$(shown 50 %Y%m%d-%H%M); report=$reports/verify-v1-$stamp.md
echo "# Verify v1" > "$report"; touch -t "$(shown 50 %Y%m%d%H%M.%S)" "$report"
records() { cat "$(home_of mac-studio)"/.local/state/crew/wldn/runs/*/*.rec "$(home_of $box)"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null | wc -l || true; }
tip=$(git --git-dir "$ws" rev-parse wldn/main) n=$(records)
expect_ok crew rail --label wldn; r=$out
eq "$(git --git-dir "$ws" rev-parse wldn/main) $(records)" "$tip $n"
eq "$(grep -E '^[a-z]+$' <<<"$r" | tr '\n' ' ')" "proposals batches land operations "
has "$r" "batch 1 (wldn): x1 (swb-1), z1 (atl-1)"
has "$r" "    card:   batch/1, open, asked by wldn-planner (req_stub-1)"
lacks "${r//crew-test.??????/}" "v1"  # the scratch folder's random name can hold v1
ok "crew rail lists a batch as one row with its card key, no verify report waits, and it writes nothing"

# The planner's own Pending You calls: refused under crew's own key, or one the hook can't check.
deny=$(jq -nc '{session_id: "sid-1", hook_event_name: "PreToolUse", cwd: "/work", tool_name: "mcp__pendingyou__post_request",
  tool_input: {name: "wldn-planner", title: "Batch", idempotencyKey: "proposal/9"}}' | CREW_AGENT=wldn-planner as $box python3 "$CREW/plugin/hooks/cards" --before)
eq "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$deny")" "deny"
has "$(jq -r '.hookSpecificOutput.permissionDecisionReason' <<<"$deny")" "crew refuses wldn-planner's post of the card under proposal/9: a proposal's card is crew's"
eq "$(echo 'not json' | CREW_AGENT=wldn-planner as $box python3 "$CREW/plugin/hooks/cards" 2>&1 >/dev/null)" "crew cards: Expecting value: line 1 column 1 (char 0)"
has "$(echo 'not json' | CREW_AGENT=wldn-planner as $box python3 "$CREW/plugin/hooks/cards" --before | jq -r .hookSpecificOutput.permissionDecisionReason)" \
  "crew could not check this call:"
ok "crew's card hook refuses a card under crew's own key, or one it can't check, before it is posted, and never fails the tool"

# The batch card's one reading session, started with its card on the main level's host: the summary, then each unit's
# change as the batch read it, from each team's host.
HOST=$box CREW_AGENT=wldn-planner expect_ok crew card session batch/1; u1=$out
eq "$(jq -r '.["req_stub-1"].posted.context.links[0].url' "$(home_of $box)/.stub-pendingyou/cards.json")" "$u1"
[[ $u1 =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on the main level's host's tailnet name: $u1"
p1=$(rec $box batch/1 .pid)
folder=$(real "$(dirname "$summary")")/batch-wldn-1
order="00-summary.md 01-x1-proposal.md 01-x1-design.md 01-x1-specs-x-spec.md 01-x1-tasks.md 02-z1-proposal.md 02-z1-design.md 02-z1-specs-x-spec.md 02-z1-tasks.md"
eq "$(stub $box "$p1" '.argv | map(select(endswith(".md"))) | join(" ")')" "$(for f in $order; do printf '%s ' "$folder/$f"; done | sed 's/ $//')"
eq "$(cat "$folder/02-z1-tasks.md")" "$(git -C "$akd/places/z1" show HEAD:openspec/changes/z1/tasks.md)"
eq "$(stub $box "$p1" .skip_browser)" "true"
HOST=$box CREW_AGENT=wldn-planner expect_ok crew card session batch/1; eq "$out" "$u1"; eq "$(listed $box)" "$p1"
notes=$'# Annotations\n\n1. Say what z means.'
decide $box "$p1" "$(jq -nc --arg f "$notes" '{decision: "annotated", feedback: $f, annotationCount: 1}')"
told() { grep -c "^$box wldn-3 agent prompt wldn-planner '\[crew\] The user sent batch/1'\"'\"'s reading. Run crew card read batch/1 for what they sent.'\$" "$CREW_TEST_LOG" || true; }
: > "$CREW_TEST_LOG"
expect_ok crew rail --label wldn
has "$out" "readings sent:"$'\n'"  batch/1 (wldn) on $box: its reading was sent; the user sent its reading, and wldn-planner was told to run crew card read batch/1"
lacks "$(grep "agent prompt wldn-planner" "$CREW_TEST_LOG")" "Say what z means"
expect_ok crew rail --label wldn
lacks "$out" "readings sent:"
eq "$(told)" "1"
HOST=$box CREW_AGENT=wldn-planner expect_fail "crew card wait is gone: crew keeps no process waiting on a card or its reading. Run crew card read batch/1" crew card wait batch/1
HOST=$box CREW_AGENT=wldn-planner expect_ok crew card read batch/1
eq "$out" "batch/1: annotated
$notes
card batch/1: req_stub-1 withdrawn
batch/1's session had ended as the user sent it, and batch/1 is forgotten"
[[ ! -e $(home_of $box)/$cards/batch/1 ]] || fail "batch/1's session folder outlived its card"
eq "$(entries $box card.close | jq -r '[.Card, .Key, .State, .Outcome] | join(" ")')" "req_stub-1 batch/1 withdrawn Read; 1 note sent to its team"
ok "a batch card's one session reads the summary and every unit's change from each team's host, the link on its card and the same again while it serves; the rail's refresh tells the planner once that it was sent, with none of the user's words, crew card wait is refused naming the read, and the planner's crew card read returns the words and closes the card, which forgets the session"

# A batch posted as cards of five before a batch was one card: its sessions are its units', each on its team's host.
CREW_AGENT=wldn-reviewer as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act review.batch --on batch/2 --field Batch=2 \
  --field "Units=x1:swb-1@$(git -C "$k" rev-parse unit/x1) z1:atl-1@$(git -C "$ak" rev-parse unit/z1)" >/dev/null
CREW_AGENT=wldn-planner as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act card.post --on batch/2 \
  --field Card=req_bat-2 --field Key=batch/2-1 >/dev/null  # as the card hook recorded the planner's post then
HOST=$box CREW_AGENT=wldn-planner expect_ok crew card session batch/2-1 z1
p3=$(rec mac-studio batch/2-1/z1 .pid)
c=$(real "$akd/places/z1")/openspec/changes/z1
eq "$(stub mac-studio "$p3" '.argv | map(select(endswith(".md"))) | join(" ")')" "$c/proposal.md $c/design.md $c/specs/x/spec.md $c/tasks.md"
HOST=$box CREW_AGENT=wldn-planner expect_ok crew card end batch/2-1 z1
gone "$p3"
ok "an old batch card's session of a unit is started on that unit's team's host, on its change's files, and crew card end ends it there"

# A later batch whose reading will not open at either start: its card is raised without it, saying so and naming crew
# card session, with why in the run record; the planner's crew card session then starts the reading and changes the
# card to carry its link, and the user's approval with no words is recorded read at the next refresh.
for act in review.start review.batch; do
  CREW_AGENT=wldn-planner as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act $act --on batch/3 --field Batch=3 \
    --field "Units=x1:swb-1@$(git -C "$k" rev-parse unit/x1)" >/dev/null
done
printf '# Batch 3\n\n## x1 (swb-1)\n\nx1 gives each tenant its own zone.\n' > "$(dirname "$summary")/batch-wldn-3.md"
echo 2 > "$refusals"
: > "$CREW_TEST_LOG"
CREW_AGENT=wldn-planner expect_ok crew review wldn --wait
c3=$(grep -o "^card batch/3: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $c3 ]] || fail "crew review --wait raised no card for batch 3:"$'\n'"$out"
has "$out" "card batch/3: its reading could not be opened on the tailnet: plannotator ended before batch/3's session was ready: stub: refused to start; crew card session batch/3 starts it"
posted=$(jq -r --arg c "$c3" '.[$c].posted' "$(home_of $box)/.stub-pendingyou/cards.json")
has "$(jq -r .summary <<<"$posted")" "Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and the planner starts it with crew card session batch/3; this card then carries its link."
eq "$(jq -r '.context.links | length' <<<"$posted")" "0"
eq "$(entries $box card.post | jq -r --arg c "$c3" 'select(.Card == $c) | .Unread')" "plannotator ended before batch/3's session was ready: stub: refused to start"
[[ ! -e $(home_of $box)/$cards/batch/3/session.json ]] || fail "a session of batch/3 is recorded though neither start opened"
ok "a batch's card whose reading will not open at either start is raised without it, saying so and naming crew card session as the planner's, with why in the run record"
rm "$refusals"
HOST=$box CREW_AGENT=wldn-planner expect_ok crew card session batch/3
p6=$(rec $box batch/3 .pid); u3=$(rec $box batch/3 .url)
eq "$(head -1 <<<"$out")" "$u3"
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"requestId\": \"$c3\""; has "$changed" "\"changeNote\": \"Its reading is open again at a new link\""; has "$changed" "$u3"
eq "$(entries $box card.reading | jq -r '[.Key, .Card, .Refused // "done"] | join(" ")')" "batch/3 $c3 done"
decide $box "$p6" '{"decision": "approved", "annotationCount": 0}'
: > "$CREW_TEST_LOG"
expect_ok crew rail --label wldn
has "$out" "  batch/3 (wldn) on $box: its reading was sent; the user approved its reading with no notes, so crew recorded it read, Read; no notes: card batch/3: $c3 withdrawn"
lacks "$(grep "agent prompt wldn-planner" "$CREW_TEST_LOG")" "batch/3"
eq "$(entries $box card.close | jq -r --arg c "$c3" 'select(.Card == $c) | [.Key, .State, .Outcome] | join(" ")')" "batch/3 withdrawn Read; no notes"
[[ ! -e $(home_of $box)/$cards/batch/3 ]] || fail "batch/3's reading outlived its card"
ok "the planner's crew card session on a batch card raised without its reading starts the reading, records the try and changes the card to carry its link; the user's approval with no words is recorded read at the next refresh, its card closed, with nobody told"

# A verify report's card, whose row went with record 0027: crew refuses the conductor's post, and its key starts no session.
deny=$(jq -nc --arg k "verify/v1/$stamp" '{session_id: "sid-1", hook_event_name: "PreToolUse", cwd: "/work", tool_name: "mcp__pendingyou__post_request",
  tool_input: {name: "swb-1-conductor", title: "Verify v1", idempotencyKey: $k}}' | CREW_AGENT=swb-1-conductor as $box python3 "$CREW/plugin/hooks/cards" --before)
eq "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$deny")" "deny"
has "$(jq -r '.hookSpecificOutput.permissionDecisionReason' <<<"$deny")" "crew refuses swb-1-conductor's post of the card under verify/v1/$stamp: a verify report has no card"
HOST=$box CREW_AGENT=swb-1-conductor expect_fail "verify/v1/$stamp is not a card key" crew card session "verify/v1/$stamp"
ok "a verify report's card is refused before it is posted, and its key starts no session, since it is no row's"

# A proposal of more than fifteen new units: its page opened, its session started, and its row gone once approved:
# the next rail read sweeps it.
{ printf '%s\n' 'Case: The console gets a bolt of its own.' 'Do: bolt new console-pages "The console lists them." --repo switchboard-kit'
  for i in $(seq 1 16); do echo "Do: unit add page-$i \"Page $i.\" --bolt console-pages"; done; } > "$T/p.rec"
crew plan propose "$T/p.rec" >/dev/null
f=$(home_of mac-studio)/.local/state/crew/proposals/wldn-1.md
: > "$CREW_TEST_LOG"
HERDR_ENV=1 expect_ok crew plan proposed 1 --label wldn --open
grep -qx "mac-studio plannotator-tui herdr open $f" "$CREW_TEST_LOG" || fail "plannotator did not open $f beside the caller:"$'\n'"$(calls)"
expect_ok crew card session proposal/1; p5=$(rec mac-studio proposal/1 .pid)
eq "$(cat "$(stub mac-studio "$p5" .target)")" "$(crew plan proposed 1)"
s=$(home_of mac-studio)/$cards/proposal/1/session.json
jq -c '.started = "2026-01-01T00:00:00Z"' "$s" > "$s.new" && mv "$s.new" "$s"
crew plan approve 1 >/dev/null
expect_ok crew rail --label wldn
has "$out" "card sessions ended:"$'\n'"  proposal/1 (wldn) on mac-studio: its row is gone; ended proposal/1's session, plannotator pid $p5"
gone "$p5"
ok "a proposal opens in plannotator beside the caller; its card's session is on its page, and once its row is gone a rail read ends it on its host"

# Writes and tells reach the agents they should: the conductor and the dispatcher up on the box.
p=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$p" swb-1-conductor
p=$(as $box herdr --session wldn-3 workspace create --cwd / --label "wldn dispatch" | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-3 stub agent "$p" wldn-dispatch-chuck-herdr-alpha
: > "$CREW_TEST_LOG"
crew unit add y1 "Unit y1." --bolt b1 >/dev/null
eq "$(grep "^$box wldn-1 agent prompt swb-1-conductor " "$CREW_TEST_LOG")" "$box wldn-1 agent prompt swb-1-conductor '[crew] plan(b1): add y1 ($me@mac-studio)'"
crew bolt new edge-signins "Sign-ins at the edge." --repo switchboard-kit >/dev/null
has "$(grep "^$box wldn-3 agent prompt wldn-dispatch-chuck-herdr-alpha " "$CREW_TEST_LOG")" "plan(edge-signins): add the bolt ($me@mac-studio). Give a free team its next bolt."
CREW_AGENT=wldn-design expect_ok crew tell swb-1-conductor "The tenant's zone is its own."
grep -q "^$box wldn-1 agent prompt swb-1-conductor '\[crew tell from wldn-design\] The tenant'\"'\"'s zone is its own.'" "$CREW_TEST_LOG" || fail "crew tell sent nothing"
as $box herdr --session wldn-1 stub status swb-1-conductor blocked
: > "$CREW_TEST_LOG"
expect_fail "swb-1-conductor is waiting on a question in its pane: nothing was sent" crew tell swb-1-conductor "Hold the zone work."
grep -q "agent prompt swb-1-conductor" "$CREW_TEST_LOG" && fail "a tell was typed to an agent herdr reads blocked"
as $box herdr --session wldn-1 stub status swb-1-conductor idle
# The conductor opens a question for the user, which crew's own hook marks though herdr reads it idle.
sid=$(as $box herdr --session wldn-1 agent get swb-1-conductor | jq -r .result.agent.agent_session.value)
tx=$(transcript $box "$sid" <<<'{"type":"user","message":{"role":"user","content":"Which zone first?"}}')
printf '{"session_id":"%s","transcript_path":"%s","tool_name":"AskUserQuestion","tool_use_id":"toolu_q1","tool_input":{}}' "$sid" "$tx" |
  as $box env CREW_AGENT=swb-1-conductor python3 "$CREW/plugin/hooks/questions"
expect_fail "swb-1-conductor is waiting on a question in its pane: nothing was sent" crew tell swb-1-conductor "Hold the zone work."
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"toolu_q1","content":"User has answered your questions"}]}}' >> "$tx"
: > "$CREW_TEST_LOG"
expect_ok crew tell swb-1-conductor "Hold the zone work."
eq "$(grep "^$box wldn-1 agent prompt swb-1-conductor " "$CREW_TEST_LOG")" "$box wldn-1 agent prompt swb-1-conductor '[crew tell from $me@mac-studio] Hold the zone work.'"
ok "a write to a held bolt tells its conductor and a bolt added the dispatcher; crew tell marks its sender, types nothing to an agent herdr reads blocked or crew's hook saw open a question, and is delivered once the question is answered"

# wldn's reviewer and planner run as their kinds: crew review asks the reviewer the batch, opening no tab; the
# reviewer's run takes it with crew role start and hands it back with crew review delivered once its summary is
# written, which records the batch, raises its card in the planner's name and asks the planner, typing into no pane.
role_stream wldn reviewer wldn-main; role_stream wldn planner wldn-main
build swb-1 y1 "$kd"
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
CREW_AGENT=wldn-planner expect_ok crew review wldn
summary4=$(dirname "$summary")/batch-wldn-4.md
has "$out" "wldn-reviewer is asked batch 4 of wldn, into $summary4"
asks() { git --git-dir "$ws" show wldn/main:asks.rec | recsel -t Ask "$@"; }
eq "$(asks -e "Role = 'reviewer'" -P What,Names,Key | tr '\n' ' ')" "batch batch/4 batch/4 "
has "$(asks -e "Role = 'reviewer'" -P Words)" "Review batch 4 of wldn, 1 change, and write its summary to $summary4. y1 (swb-1, switchboard-kit on $box"
[[ -s $CREW_TEST_CLAUDE_LOG ]] && fail "crew review started a reviewer that runs as its kind"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops,operator"
CREW_AGENT=wldn-planner expect_fail "wldn runs its reviewer as its kind, so crew review --wait waits on nothing" crew review wldn --wait
reviewer() { HOST=$box FLUME_PLACE=$T/flume/places/crew-reviewer--wldn "$@"; }
reviewer expect_fail "wldn-reviewer has no open turn: crew role start takes the batches asked of it first" crew review delivered
reviewer expect_ok crew role start
has "$out" "ask $(asks -e "Role = 'reviewer'" -P Id): batch from wldn-planner on batch/4"
reviewer expect_fail "batch 4's summary $summary4 is not written since its start, so it is not delivered" crew review delivered
printf '# Batch 4\n\n## y1 (swb-1)\n\ny1 does its part.\n' > "$summary4"
reviewer expect_ok crew review delivered
has "$out" "batch 4 of wldn is delivered: $summary4"
eq "$(entries $box review.batch | jq -r 'select(.Batch == "4") | [(.On | join(" ")), .By] | join(" ")')" "batch/4 unit/y1 wldn-reviewer"
c4=$(entries $box card.post | jq -r 'select(.Key == "batch/4") | .Card')
[[ -n $c4 ]] || fail "no card of batch 4 was raised"
eq "$(entries $box card.post | jq -r 'select(.Key == "batch/4") | .By')" "wldn-planner"
eq "$(asks -e "Role = 'planner' && What = 'delivered'" -P From,Names,Key | tr '\n' ' ')" "wldn-reviewer batch/4 delivered/4 "
has "$(asks -e "Role = 'planner' && What = 'delivered'" -P Words)" "call get_request (requestId $c4, name wldn-planner)"
grep -q "agent prompt wldn-planner" "$CREW_TEST_LOG" && fail "the delivery typed into the planner's pane"
ok "a reviewer that runs as its kind is asked its batch with no tab, crew review --wait refuses for it, and its run hands the batch its turn took back once its summary is written, recorded, its card raised in the planner's name and the planner asked with the line that adopts it"
