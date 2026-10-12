# A batch card's session: crew card session batch/<n> starts one plannotator session on the whole batch, on the
# partition's main level's host, with no browser, kept under batch/<n>: crew first writes the batch's folder beside its
# summary, 00-summary.md and then each unit's Markdown files as the batch read them at their commits, from every
# team's host, each named <kk>-<unit>-<its path>, and gives plannotator those files in that order as one review, never
# a folder. Run again while it serves, it prints the same link and writes nothing. It refuses a unit with that key,
# another host than the main level's, and a batch crew can't read whole, naming the unit and the host, with nothing
# started. crew card wait and end act on the one session, and the card's close through crew's hook ends it. A batch
# posted as cards of five before a batch was one card has its sessions started, waited on and ended under the
# batch/<n>-<k> key it was posted under, one per unit on its team's host, each given its change's Markdown files,
# proposal first, and none under batch/<n>. Each scenario of the card-sessions spec on batch cards.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
ak=$(kit mac-studio willdan atlas-kit); akd=$(dirname "$ak")
export CREW_LABEL=wldn PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
crew bolt new b1 "One." --repo switchboard-kit >/dev/null
crew bolt new m1 "Maps." --repo atlas-kit >/dev/null
for u in x1 x2; do crew unit add $u "Unit $u." --bolt b1 >/dev/null; done
crew unit add z1 "Unit z1." --bolt m1 >/dev/null
crew bolt give swb-1 b1 >/dev/null 2>&1; crew bolt give atl-1 m1 >/dev/null 2>&1
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"
crew main up wldn >/dev/null 2>&1
real() { (cd "$1" && pwd -P); }
build() {  # build <team> <unit> <kit dir> [<command run in the change's folder before its commit>]
  CREW_AGENT=$1-conductor crew unit run $2 construct >/dev/null; change "$3/places/$2" $2 0 2
  [[ -z ${4:-} ]] || (cd "$3/places/$2/openspec/changes/$2" && eval "$4")
  commit_all "$3/places/$2" "docs($2): the change"
  CREW_AGENT=$1-conductor crew unit wait $2 >/dev/null
}
# x1's change holds metadata and a Markdown file of its own beside the four a change has.
build swb-1 x1 "$kd" 'printf "schema: spec-driven\n" > .openspec.yaml; printf "# Notes\n" > notes.md'
build swb-1 x2 "$kd"; build atl-1 z1 "$akd"
sx1=$(git -C "$kd/places/x1" rev-parse HEAD); sx2=$(git -C "$kd/places/x2" rev-parse HEAD)
CREW_AGENT=wldn-planner crew review wldn >/dev/null
reports=$(home_of $box)/.local/state/crew/wldn-main/reports; mkdir -p "$reports"; echo "# Batch 1" > "$reports/batch-wldn-1.md"
CREW_AGENT=wldn-planner crew review wldn --wait >/dev/null
# x1's change moves on after the batch read it.
printf '# Design\n\nrewritten\n' > "$kd/places/x1/openspec/changes/x1/design.md"; commit_all "$kd/places/x1" "docs(x1): the design again"
rec() { jq -r "$3" "$(home_of "$1")/.local/state/crew/cards/wldn/$2/session.json"; }
stub() { jq -r "$3" "$(home_of "$1")/.stub-plannotator/$2.json"; }
given() { stub "$1" "$2" '.argv | map(select(endswith(".md"))) | join(" ")'; }
listed() { as "$1" plannotator sessions --json | jq -r '[.[].pid] | sort | map(tostring) | join(" ")'; }
gone() { python3 -c 'import os, sys, time
pid, give_up = int(sys.argv[1]), time.monotonic() + 10
while True:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        break
    if time.monotonic() > give_up:
        sys.exit(f"pid {pid} is still running")
    time.sleep(0.05)' "$1"; }
export CREW_AGENT=wldn-planner

: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew card session batch/1; u1=$out
[[ $u1 =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "not a link on the main level's host's tailnet name: $u1"
p1=$(rec $box batch/1 .pid)
folder=$(real "$reports")/batch-wldn-1
order="00-summary.md 01-x1-proposal.md 01-x1-design.md 01-x1-specs-x-spec.md 01-x1-tasks.md 01-x1-notes.md 02-x2-proposal.md
02-x2-design.md 02-x2-specs-x-spec.md 02-x2-tasks.md 03-z1-proposal.md 03-z1-design.md 03-z1-specs-x-spec.md 03-z1-tasks.md"
eq "$(given $box "$p1")" "$(for f in $order; do printf '%s ' "$folder/$f"; done | sed 's/ $//')"
eq "$(stub $box "$p1" .target)" "$(for f in $order; do printf '%s, ' "$folder/$f"; done | sed 's/, $//')"
eq "$(rec $box batch/1 .document)" "$(stub $box "$p1" .target)"
eq "$(stub $box "$p1" .label)" "annotate-14 files: $(echo $order | sed 's/ /, /g')"
eq "$(ls -A "$folder" | sort | tr '\n' ' ')" "$(echo $order | tr ' ' '\n' | sort | tr '\n' ' ')"
eq "$(cat "$folder/00-summary.md")" "# Batch 1"
eq "$(cat "$folder/01-x1-design.md")" $'# Design\n\nz'
eq "$(cat "$folder/03-z1-tasks.md")" "$(git -C "$akd/places/z1" show HEAD:openspec/changes/z1/tasks.md)"
has "$(calls)" "$box ssh mac-studio bash -c 'set -eo pipefail"
grep -qE "^' crew .*/atlas-kit/main [0-9a-f]+ z1$" "$CREW_TEST_LOG" || fail "z1's change was not read on its team's host:"$'\n'"$(calls)"
eq "$(stub $box "$p1" .skip_browser)" "true"
lacks "$(calls)" "opened a browser"
eq "$(listed mac-studio)" ""
ok "a batch card's session is one, on the main level's host: the summary, then each unit's Markdown files as the batch read them, from each team's host, each named for its unit, given as files in that order, with no browser"

echo "Read by the user." >> "$folder/00-summary.md"
HOST=$box expect_ok crew card session batch/1; eq "$out" "$u1"; eq "$(listed $box)" "$p1"
has "$(cat "$folder/00-summary.md")" "Read by the user."
ok "run again while it serves, it prints the same link, starts nothing and does not write the batch's folder again"

HOST=$box expect_fail "a batch has one reading session, on the whole batch: crew card session batch/1" crew card session batch/1 x1
HOST=$box expect_fail "a batch has one reading session, on the whole batch: crew card wait batch/1" crew card wait batch/1 x1
HOST=$box expect_fail "a batch has one reading session, on the whole batch: crew card end batch/1" crew card end batch/1 x1
HOST=mac-studio expect_fail "batch/1's reading session runs on chuck-herdr-alpha, where wldn's main level writes the batch's summary" \
  crew card session batch/1
HOST=$box expect_fail "only an old batch card's key, batch/<n>-<k>, takes a unit" crew card session proposal/1 x1
eq "$(listed $box)" "$p1"; eq "$(listed mac-studio)" ""
ok "a unit with a batch's key, the batch's session on another host than the main level's, and a unit with another key are refused, with nothing started"

notes=$'# Annotations\n\n1. Say what z means.'
printf '%s\n' "$(jq -nc --arg f "$notes" '{decision: "annotated", feedback: $f}')" > "$(home_of $box)/.stub-plannotator/$p1.decision"
gone "$p1"
HOST=$box expect_ok crew card wait batch/1
eq "$out" "batch/1: annotated
$notes"
HOST=mac-studio expect_fail "no session was started for card batch/1" crew card wait batch/1
ok "a wait on the batch's session returns the user's annotations in their words, on the main level's host"

HOST=$box expect_ok crew card end batch/1
HOST=$box expect_ok crew card session batch/1; p2=$(rec $box batch/1 .pid)
HOST=$box expect_ok crew card end batch/1
eq "$out" "ended batch/1's session, plannotator pid $p2"
gone "$p2"; eq "$(listed $box)" ""
ok "crew card end ends the batch's one session"

# A batch crew can't read whole starts nothing: a team's host that does not answer, and a commit not in a kit.
echo mac-studio > "$T/down"
HOST=$box expect_fail "mac-studio did not answer" crew card session batch/1
rm "$T/down"
batched() { CREW_AGENT=wldn-reviewer as $box python3 "$CREW/plugin/lib/record.py" emit --label wldn --act review.batch --on batch/$1 \
  --field Batch=$1 --field "Units=$2" >/dev/null; echo "# Batch $1" > "$reports/batch-wldn-$1.md"; }
batched 2 "x1:swb-1@$sx1 x2:swb-1@abc1234 z1:atl-1@abc1234"
HOST=$box expect_fail "crew can't read x2's change at abc1234 in $k on chuck-herdr-alpha: abc1234 is not a commit of" crew card session batch/2
batched 3 "x1:swb-1@$sx1 x2:swb-1@$sx2 z1:atl-1@abc1234"
HOST=$box expect_fail "crew can't read z1's change at abc1234 in $ak on mac-studio: abc1234 is not a commit of" crew card session batch/3
for n in 2 3; do [[ ! -e $reports/batch-wldn-$n ]] || fail "batch $n's folder was written from part of the batch: $(ls -A "$reports/batch-wldn-$n")"; done
eq "$(listed $box)" ""
ok "a batch whose team's host does not answer is refused naming the host, and one whose unit's change can't be read at its commit naming the unit and its host, with nothing written or started"

# The card's close, through crew's hook, ends its session.
HOST=$box expect_ok crew card session batch/1; p3=$(rec $box batch/1 .pid)
call() { jq -nc --arg t "mcp__pendingyou__$1" --argjson i "$2" --argjson r "$3" \
  '{session_id: "sid-1", hook_event_name: "PostToolUse", cwd: "/work", tool_name: $t, tool_input: $i, tool_response: $r}'; }
call post_request '{"name": "wldn-planner", "idempotencyKey": "batch/1"}' '{"structuredContent": {"requestId": "req_bat-1"}}' | as $box python3 "$CREW/plugin/hooks/cards"
said=$(call ack_answer '{"name": "wldn-planner", "requestId": "req_bat-1", "outcome": "noted"}' '{"structuredContent": {"status": "resolved"}}' \
  | as $box python3 "$CREW/plugin/hooks/cards")
eq "$said" ""
gone "$p3"
eq "$(listed $box)" ""
[[ ! -e $(home_of $box)/.local/state/crew/cards/wldn/batch/1 ]] || fail "batch/1's session folder outlived its card"
HOST=$box expect_fail "no row of wldn's rail has the card key batch/1: its row is gone" crew card session batch/1
ok "a batch card's close through crew's hook ends its one session there, and the closed card starts none"

# Batch 2, posted as cards of five before a batch was one card: its card under batch/2-1 holds its three units.
call post_request '{"name": "wldn-planner", "idempotencyKey": "batch/2-1"}' '{"structuredContent": {"requestId": "req_bat-2"}}' | as $box python3 "$CREW/plugin/hooks/cards"
HOST=$box expect_fail "no row of wldn's rail has the card key batch/2: its row is gone" crew card session batch/2
HOST=$box expect_fail "a batch card posted as cards of five has a session for each of its units: crew card session batch/2-1 <unit>" \
  crew card session batch/2-1
HOST=$box expect_ok crew card session batch/2-1 x1; p4=$(rec $box batch/2-1/x1 .pid)
c=$(real "$kd/places/x1")/openspec/changes/x1
eq "$(given $box "$p4")" "$c/proposal.md $c/design.md $c/specs/x/spec.md $c/tasks.md $c/notes.md"
eq "$(stub $box "$p4" '.argv | map(select(endswith("/x1") or endswith("/x1/"))) | length')" "0"
HOST=$box expect_ok crew card session batch/2-1 z1; p5=$(rec mac-studio batch/2-1/z1 .pid)
c=$(real "$akd/places/z1")/openspec/changes/z1
eq "$(given mac-studio "$p5")" "$c/proposal.md $c/design.md $c/specs/x/spec.md $c/tasks.md"
HOST=$box expect_ok crew card session batch/2-1 x1; eq "$(listed $box)" "$p4"
printf '%s\n' "$(jq -nc --arg f "$notes" '{decision: "annotated", feedback: $f}')" > "$(home_of mac-studio)/.stub-plannotator/$p5.decision"
gone "$p5"
HOST=$box expect_ok crew card wait batch/2-1 z1
eq "$out" "batch/2-1 z1: annotated
$notes"
call ack_answer '{"name": "wldn-planner", "requestId": "req_bat-2", "outcome": "noted"}' '{"structuredContent": {"status": "resolved"}}' | as $box python3 "$CREW/plugin/hooks/cards"
gone "$p4"
eq "$(listed $box)" ""
HOST=$box expect_fail "no row of wldn's rail has the card key batch/2-1: its row is gone" crew card session batch/2-1 x1
ok "a batch posted as cards of five before has its sessions started on each unit's change as its Markdown files, proposal first and never its folder, waited on and ended under the key it was posted under, and none under batch/<n>"
