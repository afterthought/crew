# A partition's main level and its console through the crew command on the stubs (tests.11, record 0022), in the
# journeys' world (tests/journeys.sh): crew main up starts the main level, its operator among it, and nothing else,
# no dispatcher on any host, each greeted once, one waiting on a question holding back no other; main status lists
# them; a tell records its length and never its text; crew send reaches the partition named by its label's operator,
# marked with whom it was for, and records its length, and a team's name from before teams left is refused; a word from the board, piped to crew tell --board as the board's
# listener pipes it, reaches the agent its item's kind goes to marked as the user's from the board and naming the item,
# and records its length, and one for an agent its kind does not go to types nothing; the console opens its shell tab
# alone while the host's job follows, a tab named beside it and the rail tab of itself while no follower runs, keeps
# what is open, and starts no agent; a tell reaches an agent whose pane herdr names no session for, refused while the
# session crew recorded in its pane has a question open; crew revive brings back what a restart left empty, resumed or,
# with no conversation to pick up, fresh, leaving down what was taken down; crew revive and crew main up open again a
# pane herdr brought back dead; a role its partition names a session for comes up there (record 0035); and a role its
# partition runs as its kind is started by none of them, its role record written and a standing agent of it left from
# before ended, and main status says whether a run of it stands and what waits.
# What each agent is greeted with, where it runs and whether a pane is dead are logic cases (tests/py/test_teams.py).
# Reads: plugin/hooks/ plugin/lib/board.py plugin/roles/ tests/journeys.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/journeys.sh"

# The main level, with the planner stopped on a question as it starts: the others are greeted meanwhile.
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
answer() {
  local i
  for i in $(seq 6000); do
    grep -q "agent prompt wldn-design '" "$CREW_TEST_LOG" && grep -q "agent prompt wldn-ops '" "$CREW_TEST_LOG" &&
      grep -q "^$box wldn-3 agent get wldn-planner\$" "$CREW_TEST_LOG" && break
    /bin/sleep 0.1
  done
  as $box herdr --session wldn-3 stub status wldn-planner idle
}
answer &
CREW_TEST_BLOCKED=wldn-planner expect_ok crew main up wldn
wait
for a in wldn-design wldn-planner wldn-ops wldn-operator; do has "$out" "$a started"; has "$out" "$a greeted"; done
lacks "$out" "dispatch"
has "$out" "wldn-planner is waiting on a question in its pane; answer it there and it will be greeted"
eq "$(herdr_state $box wldn-3 '[.workspaces[].label] | join(",")')" "wldn"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops,operator"
eq "$(herdr_state mac-studio wldn-5 '[.agents[].name] | map(select(startswith("wldn-"))) | join(",")' 2>/dev/null)" ""
eq "$(jq -r 'select(.agent == "wldn-design") | "\(.host) \(.argv[1]) \(.argv[3])"' "$CREW_TEST_CLAUDE_LOG")" "$box claude-fable-5-1 xhigh"
grep -q " ssh mac-studio " "$CREW_TEST_LOG" && fail "crew main up reached another host"
at() { grep -n "$1" "$CREW_TEST_LOG" | head -1 | cut -d: -f1; }
answered=$(at "stub status wldn-planner idle")
(( $(at "agent prompt wldn-design '") < answered && answered < $(at "agent prompt wldn-planner '") )) ||
  fail "the planner's question held back the design agent, or the planner was greeted before it was answered"
eq "$(field $box main.up On agent/wldn-design)" "agent/wldn-design agent/wldn-planner agent/wldn-ops agent/wldn-operator"
expect_ok crew main up wldn
has "$out" "wldn-design is already up"; lacks "$out" "greeted"
eq "$(count $box main.up)" "1"
ok "crew main up starts the main level, its operator among it, on its host and no dispatcher on any host, greeting each once, one waiting on a question once it is answered and holding back no other; a second starts and records nothing"

expect_ok crew main status wldn
for a in wldn-design wldn-planner wldn-ops wldn-operator; do has "$(grep "^$a " <<<"$out")" "idle"; done
lacks "$out" "dispatch"
crew tell wldn-planner "Secret words ZQXR" >/dev/null
eq "$(field mac-studio tell Chars)" "17"
[[ $(as mac-studio bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec') != *ZQXR* ]] || fail "a tell's text is in the run record"
# crew send: another partition's agent and the user reach the partition's operator, the door, wherever it runs.
CREW_AGENT=swancloud-planner expect_ok crew send wldn "Words QVXJ for the partition"
grep -q "^$box wldn-3 agent prompt wldn-operator '\[crew tell from swancloud-planner\] (sent to wldn) Words QVXJ for the partition'" "$CREW_TEST_LOG" ||
  fail "crew send did not reach wldn-operator marked with its sender and whom it was for"
eq "$(field mac-studio send On agent/wldn-operator) $(field mac-studio send Chars agent/wldn-operator) $(field mac-studio send Why agent/wldn-operator)" "agent/wldn-operator 28 send wldn"
[[ $(as mac-studio bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec') != *QVXJ* ]] || fail "a send's text is in the run record"
expect_ok crew send wldn "For the partition"
grep -q "^$box wldn-3 agent prompt wldn-operator '\[crew tell from [^]]*@mac-studio\] (sent to wldn) For the partition'" "$CREW_TEST_LOG" ||
  fail "crew send from the user's shell did not reach wldn-operator"
eq "$(count mac-studio send) $(field mac-studio tell Chars)" "2 17"
expect_fail "crew send sends to a partition by its label, not 'swb-2': partitions madswan swancloud wldn" crew send swb-2 "x"
expect_fail "crew send sends to a partition by its label, not 'nosuch'" crew send nosuch "x"
eq "$(count mac-studio send)" "2"
# A word from a proposal's dock, as the board's listener pipes it: the planner is told it as the user's from the board,
# naming the item (record 0038 §3); one for another agent than the kind's types nothing.
board_word() { printf '%s' "$1" | crew tell --board; }
expect_ok board_word '{"label":"wldn","key":"proposal:4","to":"wldn-planner","text":"Words BRDW from the board"}'
eq "$out" "sent to wldn-planner"
grep -q "^$box wldn-3 agent prompt wldn-planner '\[crew tell from [^]@ ]*@board\] (on proposal 4) Words BRDW from the board'\$" "$CREW_TEST_LOG" ||
  fail "crew tell --board did not reach wldn-planner marked from the board and naming the item"
eq "$(field mac-studio tell Chars agent/wldn-planner)" "41"
[[ $(as mac-studio bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec') != *BRDW* ]] || fail "a word from the board's text is in the run record"
expect_fail "a word on a proposal goes to wldn-planner, not wldn-ops" \
  board_word '{"label":"wldn","key":"proposal:4","to":"wldn-ops","text":"Words BRDX for ops"}'
grep -q BRDX "$CREW_TEST_LOG" && fail "a word for an agent its kind does not go to was typed"
# herdr drops the planner's name in its pane, its session there the one crew started (briefs.17): a tell from another
# host finds it in the pane crew keeps for it, and its host's crew gives the name back.
p=$(as $box herdr --session wldn-3 agent get wldn-planner | jq -r .result.agent.pane_id)
as $box herdr --session wldn-3 stub agent "$p"
echo "CREW_AGENT=wldn-planner" > "$(home_of $box)/.local/state/crew/sessions/sid-${p/:/-}"
expect_ok crew tell wldn-planner "Words after the drop"
grep -q "^$box wldn-3 agent prompt wldn-planner '\[crew tell from [^]]*\] Words after the drop'" "$CREW_TEST_LOG" || fail "the tell did not reach the planner"
eq "$(as $box herdr --session wldn-3 agent get "$p" | jq -r .result.agent.name)" "wldn-planner"
ok "a tell reaches an agent whose name herdr dropped in its pane, its session the one crew started, and gives the name back"
# The operator agent mac-studio ran before record 0035, in an operator workspace beside a tab of the user's own: the
# console's up ends it and closes the panes crew recorded, leaving the user's tab.
as mac-studio herdr --session wldn workspace create --cwd /tmp --label operator --no-focus >/dev/null
op=$(as mac-studio herdr --session wldn pane list | jq -r '.result.panes[-1].pane_id')
as mac-studio herdr --session wldn stub agent "$op" wldn-operator-mac-studio >/dev/null
mine=$(as mac-studio herdr --session wldn tab create --workspace "$(as mac-studio herdr --session wldn workspace list | jq -r '.result.workspaces[-1].workspace_id')" --cwd /tmp --label mine --no-focus | jq -r .result.root_pane.pane_id)
as mac-studio bash -c "mkdir -p ~/.local/state/crew/wldn-operator && printf 'operator $op\n' > ~/.local/state/crew/wldn-operator/panes"
# mac-studio's follower runs as the host's job, swancloud's: a process holding its follower lock as the job until killed.
lock=$(home_of mac-studio)/.cache/crew/board/follower.lock
mkdir -p "$(dirname "$lock")"
python3 -c 'import fcntl, os, sys, time
f = open(sys.argv[1], "a+")
fcntl.flock(f, fcntl.LOCK_EX)
f.truncate(0)
f.write(f"job {os.getpid()} 2026-10-28T10:00:00Z\n")
f.flush()
open(sys.argv[2], "w").close()
while True:
    time.sleep(60)' "$lock" "$T/job-follows" &
job=$!
trap 'kill "$job" 2>/dev/null' EXIT
until_ok test -e "$T/job-follows" || fail "the job did not take mac-studio's follower lock"
tabs() { echo "$(herdr_state mac-studio wldn '[.workspaces[].label] | join(",")') $(herdr_state mac-studio wldn '[.tabs[].label] | join(",")')"; }
: > "$CREW_TEST_LOG"
expect_ok crew console up wldn
has "$out" "wldn-operator-mac-studio is ended and its operator tabs closed: the operator is wldn-operator, at wldn's main level"
eq "$(herdr_state mac-studio wldn '[.agents[].name] | map(select(. == "wldn-operator-mac-studio")) | length') $(herdr_state mac-studio wldn "[.panes | keys[] | select(. == \"$mine\")] | length")" "0 1"
as mac-studio herdr --session wldn pane close "$mine" >/dev/null
eq "$(tabs)" "console shell"
grep -q "^mac-studio wldn pane run [^ ]* 'export PATH=.*/plugin/bin:\$PATH'" "$CREW_TEST_LOG" || fail "the shell tab was not given crew on its path"
grep -q "_rail wldn" "$CREW_TEST_LOG" && fail "the console ran a rail tab while the host's job follows"
grep -q "crew-role\|agent prompt [^ ]* '\[crew\]" "$CREW_TEST_LOG" && fail "the console started or greeted an agent"
: > "$CREW_TEST_LOG"
expect_ok crew console up wldn rail
eq "$(tabs)" "console shell,rail"
grep -q "^mac-studio wldn pane run .*/crew _rail wldn'" "$CREW_TEST_LOG" || fail "the rail tab does not run wldn's rail"
expect_fail "crew console up opens the tabs flow, rail and board; there is no tab page" crew console up wldn page
: > "$CREW_TEST_LOG"
expect_ok crew console up wldn
grep -q "workspace create\|tab create\|pane run\|agent prompt" "$CREW_TEST_LOG" && fail "a second console up made, ran or greeted something"
eq "$(tabs)" "console shell,rail"
expect_ok crew operator up wldn
has "$out" "crew operator up is crew console up now; the operator is <label>-operator, at the main level"
# With no follower running, the rail tab opens of itself, since its loop is then the host's follower.
kill "$job"; wait "$job" 2>/dev/null || true; trap - EXIT
expect_ok crew console down wldn
: > "$CREW_TEST_LOG"
expect_ok crew console up wldn
eq "$(tabs)" "console shell,rail"
grep -q "^mac-studio wldn pane run .*/crew _rail wldn'" "$CREW_TEST_LOG" || fail "the rail tab opened while no one follows does not run wldn's rail"
ok "main status reaches every host, a tell and a send record their length and never their text, a send reaching the partition's operator, a word from the board its item's agent; the console comes up with no agent, its shell tab alone while the host's job follows, the rail tab beside it when named and kept by the next up, a word that is no tab refused, and the rail tab of itself while no one follows, crew operator up opening it too"

# herdr names no session for the planner's pane, as after its own restore: crew reads the session it recorded there.
as $box herdr --session wldn-3 stub nosession wldn-planner on
expect_ok crew tell wldn-planner "No session KWPD"
grep -q "^$box wldn-3 agent prompt wldn-planner '\[crew tell from [^]]*@mac-studio\] No session KWPD'" "$CREW_TEST_LOG" ||
  fail "a tell did not reach the planner whose pane herdr names no session for"
planner_pane=$(herdr_state $box wldn-3 '.agents | to_entries[] | select(.value.name == "wldn-planner") | .key')
planner_record=$(grep -lx "CREW_PANE=$planner_pane" $(grep -lx "CREW_AGENT=wldn-planner" "$(home_of $box)"/.local/state/crew/sessions/*))
sid=$(basename "$planner_record")
printf '{"session_id":"%s","transcript_path":"%s","tool_name":"AskUserQuestion","tool_use_id":"toolu_q1","tool_input":{}}' \
  "$sid" "$(ls "$(home_of $box)"/.claude/projects/*/"$sid.jsonl")" | as $box python3 "$CREW/plugin/hooks/questions"
expect_fail "wldn-planner is waiting on a question in its pane: nothing was sent" crew tell wldn-planner "Into a question JHTB"
grep -q "JHTB" "$CREW_TEST_LOG" && fail "a tell was typed into the question of the session crew recorded in the planner's pane"
rewrite "$planner_record" '/^CREW_HERDR_SESSION=/d; /^CREW_PANE=/d'
expect_ok crew tell wldn-planner "No record VNMC"
grep -q "^$box wldn-3 agent prompt wldn-planner '\[crew tell from [^]]*@mac-studio\] No record VNMC'" "$CREW_TEST_LOG" ||
  fail "a tell to the planner with no session herdr or crew names was refused"
rm "$(home_of $box)/.local/state/crew/questions/$sid"
as $box herdr --session wldn-3 stub nosession wldn-planner off
ok "a tell reaches an agent whose pane herdr names no session for, is refused while the session crew recorded in its pane has a question open, and with no record of its pane is guarded by herdr's reading alone"

# A restart: herdr brings each tab back as its shell alone. console up, which the fleet runs every five minutes, runs
# each tab's command there again, and leaves a pane running something else.
pane() { awk -v r="$1" '$1 == r {print $2}' "$(home_of mac-studio)/.local/state/crew/wldn-console/panes"; }
expect_ok crew console up wldn flow rail board
eq "$(herdr_state mac-studio wldn '[.tabs[].label] | sort | join(",")')" "board,flow,rail,shell"
for t in flow rail board; do as mac-studio herdr --session wldn stub restore "$(pane $t)"; done
as mac-studio herdr --session wldn pane run "$(pane board)" "less notes" >/dev/null
: > "$CREW_TEST_LOG"
expect_ok crew console up wldn
grep -q "^mac-studio wldn pane run $(pane flow) .*/crew events --follow --label wldn'" "$CREW_TEST_LOG" || fail "the flow tab's follow was not run again"
grep -q "^mac-studio wldn pane run $(pane rail) .*/crew _rail wldn'" "$CREW_TEST_LOG" || fail "the rail tab's loop was not run again"
grep -q "pane run $(pane board) " "$CREW_TEST_LOG" && fail "crew typed into a board tab running something else"
grep -q "workspace create\|tab create\|agent prompt" "$CREW_TEST_LOG" && fail "a restored console was opened again or greeted"
has "$out" "wldn's rail tab ($(pane rail)) held its shell alone; its rail runs there again"
has "$out" "wldn's board tab ($(pane board)) runs less notes, not crew's board; crew left it"
: > "$CREW_TEST_LOG"
expect_ok crew console up wldn
grep -q "pane run" "$CREW_TEST_LOG" && fail "console up ran a tab's command over one already running"
ok "after a restart, console up runs each tab's command again in the shell herdr brought back, once, and leaves a tab running something else"

# After a restart: panes back with no agent in them are revived, resumed or fresh; a main level taken down stays down.
gone() { local p; p=$(as $box herdr --session "$1" agent get "$2" | jq -r .result.agent.pane_id); as $box herdr --session "$1" agent prompt "$p" /exit >/dev/null; }
# wldn-ops's last session holds no conversation, as Claude Code keeps none for a session never spoken to.
ops_sid=$(basename "$(ls -t $(grep -lx "CREW_AGENT=wldn-ops" "$(home_of $box)"/.local/state/crew/sessions/*) | head -1)")
rm "$(home_of $box)"/.claude/projects/*/"$ops_sid.jsonl" || fail "wldn-ops's last session kept no transcript to remove"
gone wldn-3 wldn-design; gone wldn-3 wldn-ops
: > "$CREW_TEST_CLAUDE_LOG"; : > "$CREW_TEST_LOG"
HOST=$box expect_ok crew revive
has "$out" "wldn-design resumed"
has "$out" "wldn-ops has no conversation to resume; starting it fresh"
for a in wldn-planner wldn-operator; do eq "$(jq -r --arg a $a 'select(.agent == $a)' "$CREW_TEST_CLAUDE_LOG" | wc -l | tr -d ' ')" "0"; done
eq "$(launched wldn-design | cut -d' ' -f2) $(launched wldn-ops | cut -d' ' -f2)" "resumed fresh"
eq "$(greetings $box wldn-3 wldn-design)" "1"; eq "$(greetings $box wldn-3 wldn-ops)" "1"
grep -q "agent prompt wldn-planner '" "$CREW_TEST_LOG" && fail "an agent that came back by itself was greeted"
HOST=$box crew main down wldn >/dev/null
eq "$(herdr_state $box wldn-3 '.agents | length')" "0"
: > "$CREW_TEST_CLAUDE_LOG"
HOST=$box expect_ok crew revive
has "$out" "wldn was taken down; it stays down"
eq "$(wc -l < "$CREW_TEST_CLAUDE_LOG" | tr -d ' ')" "0"
echo mac-studio > "$T/down"
HOST=$box expect_ok crew main up wldn
lacks "$out" "dispatch"
rm "$T/down"
ok "crew revive brings back the agents whose panes came back empty and greets each it brought back once, one it had to start fresh among them; a main level taken down stays down; and main up reaches no other host, so one that does not answer fails nothing"

# herdr brings panes back dead, their folder gone at its restart, as it brought crw-2's back before test D (2026-10-18):
# crew revive closes each and opens it again in the main level's layout, and picks up its agent there; crew main up
# does the same and starts it.
mpane() { awk -v r="$1" '$1 == r {print $2}' "$(home_of $box)/.local/state/crew/wldn-main/panes"; }
o=$(mpane ops); d=$(mpane design)
as $box herdr --session wldn-3 stub dead "$o" "$T/trash/gone"
as $box herdr --session wldn-3 stub dead "$d"
HOST=$box expect_ok crew revive
has "$out" "wldn's ops pane $o is dead: herdr could not bring it back in $T/trash/gone (Saved directory is unavailable. Restore the directory and restart this session.); crew closes it and opens it again"
has "$out" "wldn's design pane $d is dead"
has "$out" "wldn-ops resumed"; has "$out" "wldn-design resumed"
eq "$(herdr_state $box wldn-3 '[.workspaces[].label] | join(",")')" "wldn"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "planner,operator,design,ops"
eq "$(herdr_state $box wldn-3 "[.panes | keys[] | select(. == \"$o\" or . == \"$d\")] | length")" "0"
HOST=$box crew main down wldn >/dev/null
d=$(mpane design); as $box herdr --session wldn-3 stub dead "$d"
HOST=$box expect_ok crew main up wldn
has "$out" "wldn's design pane $d is dead"; has "$out" "wldn-design started"; has "$out" "wldn-design greeted"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "planner,operator,ops,design"
eq "$(herdr_state $box wldn-3 "[.panes | keys[] | select(. == \"$d\")] | length")" "0"
ok "crew revive closes the main level's panes herdr brought back dead, opens each again in its layout and picks up its agent there, and crew main up does the same and starts it, each saying so"

# A role its partition names a session for comes up there, in a <label> workspace of its own; up refuses while the
# role's agent still runs where it stood, and down ends it there (record 0035).
edit teams "$(part wldn)['roles'] = {'planner': {'session': 'wldn-1'}}"
HOST=$box expect_fail "wldn-planner still runs in session wldn-3" crew main up wldn
has "$out" "crew main down wldn ends it, then crew main up wldn starts it there"
HOST=$box crew main down wldn >/dev/null
eq "$(herdr_state $box wldn-3 '[.agents[].name] | map(select(. == "wldn-planner")) | length')" "0"
HOST=$box expect_ok crew main up wldn
has "$out" "wldn-planner started"; has "$out" "wldn-planner greeted"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | map(select(startswith("wldn-"))) | join(",")')" "wldn-planner"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | map(select(. == "wldn")) | length')" "1"
HOST=$box expect_ok crew main status wldn
has "$(grep "^wldn-planner " <<<"$out")" "wldn-1"
ok "a role its partition names a session for comes up there, up refusing while it still runs where it stood and down ending it there"

# wldn's planner and reviewer run as their kinds: main up opens no tab for either and starts and greets neither,
# writes their role records to the flywheel's branch, and ends the standing planner left from before, idle; a second
# up does nothing of them; crew revive brings neither back; main status says each runs as its kind, in which stream,
# and how many asks wait (design Decision 14).
role_stream wldn planner wldn-main; role_stream wldn reviewer wldn-main
: > "$CREW_TEST_CLAUDE_LOG"
HOST=$box expect_ok crew main up wldn
has "$out" "wldn-planner's standing agent is ended: wldn's planner runs as its kind"
lacks "$out" "wldn-planner started"; lacks "$out" "wldn-planner greeted"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | map(select(. == "wldn-planner")) | length')" "0"
eq "$(git --git-dir "$ws" show wldn/main:roles.rec | recsel -t Role -P Address,Stream,Kind | tr -s '\n' ' ')" "wldn/planner wldn-main crew-planner wldn/reviewer wldn-main crew-reviewer "
HOST=$box expect_ok crew main up wldn
lacks "$out" "wldn-planner"
HOST=$box expect_ok crew revive
lacks "$out" "wldn-planner"
[[ $(launches) == *wldn-planner* ]] && fail "a planner that runs as its kind was started"
HOST=$box expect_ok crew main status wldn
has "$(grep "^wldn-planner " <<<"$out")" "runs as its kind in stream wldn-main; crew can't tell whether a run stands: no runner answers on $box: wldn/runner/$box does not exist; no ask waits"
has "$(grep "^wldn-reviewer " <<<"$out")" "runs as its kind in stream wldn-main; crew can't tell whether a run stands"
# Once the box's runner answers with no run of the planner, and the design agent's tell is an ask of it, main status
# says no run stands and the ask waits.
runner_rec=$(printf '%%rec: Runner\n%%key: Host\n%%type: Since date\n%%mandatory: Host Version Since\n%%allowed: Host Version Since\n\nHost: %s\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n' "$box")
tree=$(printf '100644 blob %s\trunner.rec\n' "$(printf '%s\n' "$runner_rec" | git --git-dir "$ws" hash-object -w --stdin)" | git --git-dir "$ws" mktree)
git --git-dir "$ws" update-ref "refs/heads/wldn/runner/$box" "$(git --git-dir "$ws" -c user.name=runner -c user.email=runner@example.com commit-tree "$tree" -m "runner: serve wldn on $box")"
CREW_AGENT=wldn-design expect_ok crew tell wldn-planner "Record 0012 is accepted"
has "$out" "asked wldn-planner"
HOST=$box expect_ok crew main status wldn
has "$(grep "^wldn-planner " <<<"$out")" "runs as its kind in stream wldn-main; no run stands; 1 ask waits, the oldest asked"
has "$(grep "^wldn-reviewer " <<<"$out")" "runs as its kind in stream wldn-main; no run stands; no ask waits"
ok "main up starts no role that runs as its kind, writes their role records and ends a standing agent of one left idle; revive passes them over and main status says how each runs, whether a run stands and what waits"
