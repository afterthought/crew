# Constructed changes reach the user in batches that span the partition, wired through the command: a batch due on a
# conductor's wait at the partition's setting, counted across its teams from the run record, is told to the planner
# once (which changes are due, and when a batch is, are logic cases: tests/py/test_batches.py); crew review starts
# the reviewer fresh in a review tab beside the planner, its prompt the due changes and how to read each at its commit;
# its summary file ends the batch, recorded with each unit at its commit, and its tab closes; the rail lists each
# batch as one row, keyed batch/<n>, however many units it holds, and a batch posted as cards of five before a batch was
# one card as a row for each card posted, until it closes, the planner refused batch/<n> for it; and a bolt with every
# unit merged is offered for landing only once every unit's latest change has been in a batch. Each scenario of the review-batches and rail-cards specs crew holds.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new b1 "One." --repo switchboard-kit >/dev/null
crew bolt new b2 "Two." --repo switchboard-kit >/dev/null
crew unit add x1 "Unit x1." --bolt b1 >/dev/null
crew unit add y1 "Unit y1." --bolt b2 >/dev/null
crew bolt give swb-1 b1 >/dev/null 2>&1; crew bolt give swb-2 b2 >/dev/null 2>&1
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"
crew main up wldn >/dev/null 2>&1
edit teams "$(part wldn)['review'] = {'every': 2, 'hours': 4}"
planner_told() { grep -c "^$box wldn-3 agent prompt wldn-planner '\[crew\] A batch of wldn" "$CREW_TEST_LOG" || true; }
entries() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))):
    for e in record.parse(open(f).read()):
        if e["Act"] == sys.argv[2]:
            print(json.dumps(e))' "$CREW/plugin/lib" "$2"
}
# build <team> <unit>: the unit's construct run by its conductor, its change committed, and the wait that records its end
build() {
  CREW_AGENT=$1-conductor crew unit run $2 construct >/dev/null; change "$kd/places/$2" $2 0 2; commit_all "$kd/places/$2" "docs($2): the change"
  CREW_AGENT=$1-conductor crew unit wait $2 >/dev/null
}
: > "$CREW_TEST_LOG"
build swb-1 x1
eq "$(planner_told)" "0"
eq "$(entries $box batch.due | wc -l | tr -d ' ')" "0"
build swb-2 y1
eq "$(planner_told)" "1"
has "$(grep "agent prompt wldn-planner" "$CREW_TEST_LOG")" "s changes is due: x1 (swb-1), y1 (swb-2); 2 changes are due, and a batch is every 2. Start its reviewer with crew review wldn"
eq "$(entries $box batch.due | jq -r '[.Count, (.On | join(" "))] | join(" ")')" "2 agent/wldn-planner unit/x1 unit/y1"
CREW_AGENT=swb-2-conductor crew unit wait y1 >/dev/null
eq "$(planner_told)" "1"
ok "a batch due across the partition's teams, at its setting, is told to its planner once, with the count"

expect_fail "invalid choice" crew unit approve x1
: > "$CREW_TEST_CLAUDE_LOG"
CREW_AGENT=wldn-planner expect_ok crew review wldn
has "$out" "wldn-reviewer is reviewing batch 1 of wldn, into $(home_of $box)/.local/state/crew/wldn-main/reports/batch-wldn-1.md"
eq "$(jq -r '"\(.agent) \(.argv[1]) \(.argv[3])"' "$CREW_TEST_CLAUDE_LOG")" "wldn-reviewer claude-opus-5-5[1m] high"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops,review"
rpane=$(herdr_state $box wldn-3 '.agents | to_entries[] | select(.value.name == "wldn-reviewer") | .key')
p=$(grep "agent prompt $rpane " "$CREW_TEST_LOG" | tail -1)
sha=$(git -C "$k" rev-parse --short unit/x1)
has "$p" "Review batch 1 of wldn, 2 changes, and write its summary to $(home_of $box)/.local/state/crew/wldn-main/reports/batch-wldn-1.md."
has "$p" "x1 (swb-1, switchboard-kit on $box, at $sha): list its files with \`git -C $k ls-tree -r --name-only $sha openspec/changes/x1/\`"
has "$p" "y1 (swb-2, switchboard-kit on $box, at $(git -C "$k" rev-parse --short unit/y1))"
lacks "$p" "[crew]"
grep -q "agent prompt \($rpane\|wldn-reviewer\) '\[crew\]" "$CREW_TEST_LOG" && fail "the reviewer was greeted"
eq "$(entries $box review.start | jq -r '[.Batch, .Units] | join(" ")')" "1 x1:swb-1@$sha y1:swb-2@$(git -C "$k" rev-parse --short unit/y1)"
CREW_AGENT=wldn-planner expect_fail "wldn-reviewer is still reviewing a batch" crew review wldn
ok "the planner starts the reviewer fresh in a review tab beside it, sent the due changes and how to read each at its commit, and not greeted"

CREW_AGENT=wldn-planner expect_fail "batch 1's review is still running after the wait's 0 ms" crew review wldn --wait --timeout 0
eq "$(entries $box review.batch | wc -l | tr -d ' ')" "0"
summary=$(home_of $box)/.local/state/crew/wldn-main/reports/batch-wldn-1.md
mkdir -p "$(dirname "$summary")"; printf '# Batch 1\n\n## x1 (swb-1)\n' > "$summary"
CREW_AGENT=wldn-planner expect_ok crew review wldn --wait
eq "$out" "batch summary: $summary"
eq "$(entries $box review.batch | jq -r '[.Batch, (.On | join(" "))] | join(" ")')" "1 batch/1 unit/x1 unit/y1"
eq "$(herdr_state $box wldn-3 '[.agents[].name] | map(select(. == "wldn-reviewer")) | length')" "0"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops"
CREW_AGENT=wldn-planner expect_fail "no change of wldn is due for a batch" crew review wldn
ok "the summary file ends the batch: the run record names its units at their commits, the reviewer is ended and its tab closed"

expect_ok crew rail --label wldn; r=$out
eq "$(grep -E '^[a-z]+$' <<<"$r" | tr '\n' ' ')" "proposals batches verify land operations "
has "$r" "batch 1 (wldn): x1 (swb-1), y1 (swb-2)"
has "$r" "    card:   batch/1, none open"
has "$r" "    answer: crew tell wldn-planner \"On batch 1: \""
# A batch of seven, as the run record would hold one: one row, holding all seven.
units7=$(for u in a b c d e f g; do printf '%s:swb-1@abc1234 ' "u$u"; done)
emit() { CREW_AGENT=$1 as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn "${@:2}" >/dev/null; }
emit wldn-reviewer --act review.batch --on batch/2 --field Batch=2 --field "Units=$units7"
expect_ok crew rail --label wldn; r=$out
has "$r" "batch 2 (wldn): ua (swb-1), ub (swb-1), uc (swb-1), ud (swb-1), ue (swb-1), uf (swb-1), ug (swb-1)"
has "$r" "    card:   batch/2, none open"
lacks "$r" "card 1 of"; lacks "$r" "batch/2-"
ok "the rail lists each batch as one row, keyed batch/<n>, however many units it holds"

# A batch of seven posted as cards of five before a batch was one card: a row for each card posted, until it closes.
emit wldn-reviewer --act review.batch --on batch/3 --field Batch=3 --field "Units=$units7"
emit wldn-planner --act card.post --on batch/3 --field Card=req_b-1 --field Key=batch/3-1
emit wldn-planner --act card.post --on batch/3 --field Card=req_b-2 --field Key=batch/3-2
expect_ok crew rail --label wldn; r=$out
has "$r" "batch 3 (wldn), card 1 of 2: ua (swb-1), ub (swb-1), uc (swb-1), ud (swb-1), ue (swb-1)"
has "$r" "batch 3 (wldn), card 2 of 2: uf (swb-1), ug (swb-1)"
has "$r" "    card:   batch/3-1, open, asked by wldn-planner"; has "$r" "    card:   batch/3-2, open, asked by wldn-planner"
lacks "$r" "batch/3,"
emit wldn-planner --act card.close --on batch/3 --field Card=req_b-2 --field Key=batch/3-2
expect_ok crew rail --label wldn
lacks "$out" "batch 3 (wldn), card 2 of 2"; has "$out" "batch 3 (wldn), card 1 of 2"
before() { jq -nc --arg k "$1" '{session_id: "sid-1", hook_event_name: "PreToolUse", cwd: "/work", tool_name: "mcp__pendingyou__post_request",
  tool_input: {name: "wldn-planner", title: "Batch", idempotencyKey: $k}}' | CREW_AGENT=wldn-planner as $box python3 "$CREW/plugin/hooks/cards" --before |
  jq -r '.hookSpecificOutput.permissionDecisionReason'; }
why=$(before batch/3)
has "$why" "crew refuses a card under batch/3: wldn-planner posts a card only under proposal/<n> for a proposal of wldn open now, or batch/<n> for one of its batches open now, batch/1, batch/2 or batch/3-1"
has "$(before batch/3-2)" "crew refuses a card under batch/3-2"
ok "a batch posted as cards of five before keeps a row for each card posted, keyed batch/<n>-<k>, until it closes, and the planner is refused batch/<n> for it"

# x1 constructed again with the user's notes: due again, and so is b1's landing once its units merge.
CREW_AGENT=swb-1-conductor crew unit run x1 construct "Say what the tenant sees." >/dev/null
echo notes >> "$kd/places/x1/openspec/changes/x1/design.md"; commit_all "$kd/places/x1" "docs(x1): the user's notes"
: > "$CREW_TEST_LOG"
CREW_AGENT=swb-1-conductor crew unit wait x1 >/dev/null
eq "$(planner_told)" "0"
for u in x1; do
  rewrite "$kd/places/$u/openspec/changes/$u/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/$u" "feat($u): done"
  git -C "$kd/bolts/b1" merge -q --no-ff -m "merge $u" "unit/$u"
done
eq "$(stage x1)" "merged"
expect_ok crew rail --label wldn
ld=$(awk '$0 == "land" {on = 1; next} /^[^ ]/ {on = 0} on' <<<"$out")
has "$ld" "bolt b1 (wldn), swb-1 on $box: every unit merged; wldn-ops lands it"
has "$ld" "lands once x1 has been in a batch, which is due for them"
lacks "$ld" "answer:"
has "$ld" "    card:   land/b1/"
CREW_AGENT=swb-1-conductor crew unit wait x1 >/dev/null
eq "$(planner_told)" "1"
has "$(grep "agent prompt wldn-planner" "$CREW_TEST_LOG")" "bolt b1 has every unit merged, and lands only once x1 has been in a batch"
ok "a change constructed again is due again; a bolt with every unit merged and one outside a batch is not offered for landing, and a batch is due at once"

CREW_AGENT=wldn-planner crew review wldn >/dev/null
printf '# Batch 4\n' > "$(home_of $box)/.local/state/crew/wldn-main/reports/batch-wldn-4.md"
CREW_AGENT=wldn-planner crew review wldn --wait >/dev/null
expect_ok crew rail --label wldn
has "$(awk '$0 == "land" {on = 1; next} /^[^ ]/ {on = 0} on' <<<"$out")" "    answer: crew tell wldn-ops \"Land bolt b1.\""
ok "once its last change has been in a batch, the bolt is offered for landing, though the batch's card is unanswered"

# y1 constructed again: due, so b2 does not land.
CREW_AGENT=swb-2-conductor crew unit run y1 construct "Again." >/dev/null
echo again >> "$kd/places/y1/openspec/changes/y1/design.md"; commit_all "$kd/places/y1" "docs(y1): again"
CREW_AGENT=swb-2-conductor crew unit wait y1 >/dev/null

for u in y1; do
  rewrite "$kd/places/$u/openspec/changes/$u/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/$u" "feat($u): done"
  git -C "$kd/bolts/b2" merge -q --no-ff -m "merge $u" "unit/$u"
done
git -C "$k" merge -q --no-ff -m "land b2" bolt/b2
eq "$(stage y1)" "landed"
expect_fail "bolt b2 lands only once every unit's latest change has been in a batch, and y1 has not: a batch is due for them (crew review wldn)" crew bolt land b2
ok "a landing is refused while a unit's latest change has been in no batch"
