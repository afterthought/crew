# A bolt landed through sluice, through the crew command on the stubs (tests.11, record 0022), every team's work built
# in Flume places (Decision 1 of the-team-machinery-leaves): each place, cut here as Flume cuts it, lands on its bolt
# through the stub sluice and the runner on the box carries it landed, and a unit's change is recorded read in a
# batch. crew bolts reads the bolt's verification from sluice's verdict on it; crew bolt land refuses a bolt whose
# unit's change is on its bolt and not on main; crew bolt submit lands the bolt by a submission to main from a
# short-lived worktree, a conflict landing nothing, its pull request into main, in a kit whose main takes pull
# requests, left a draft and said so, and the bolt's take-main fix launched (bolt-teams). Once that fix's place has
# merged, the rail's read on the partition's main machine raises the kit's landings card in main-level ops's name, the
# bolt its one row, with the row's reading started first, tried a second time when its first start fails, and linked
# from it, which crew card session gives again, and what brings a preview of its head up, which the kit's policy there
# declares, sluice asked for nothing (record 0043); ops's crew card preview, on the user's words on the card, brings it
# up through sluice and the card, changed in place, lists its address while it comes up, its stack failing said on the
# card, and its --done releases it; a fix launched on the bolt holds its row, so the card, with no row left that can
# land, is withdrawn naming it, the row's reading ended, and once the fix's place merges the rail's read posts a new
# card, following nothing, raised without its reading when both its starts fail, naming crew card session, whose read
# then finds no reading running and which then starts it, changing the card to carry its link. On the user's send a
# landing whose checks the host could not run takes up the place a stopped landing left on the bolt's branch, levels
# the host's copy, which the fix's merge sluice landed on GitHub left behind, to GitHub's head first and says so
# (plan.19), and is stopped, nothing of the bolt's, recorded with no refusal, its row keeping its box, the card the user
# answered left as it is and crew card read naming it with what stopped it beside the command that lands it; the next
# submission on the same send readies the bolt's pull request and lands it at GitHub's head, sluice answering with the
# pull request and crew waiting on the submission it made from it, leaving the kit's detached main checkout as it was,
# and closes it as it lands, recording the commit main holds, sluice deleting its branch from GitHub (plan.19), the
# kit's landings card closed with where GitHub's main holds it, the row's reading ended and the preview released. A
# bolt landed with a chore of its own not yet built has its close refused, said by the landing and recorded once, in
# main-level ops's name, and its head line on the board says it landed on main and was not closed, in those words;
# once the planner drops the chore, the drop's read of the bolt closes it, its branch, holding a commit main lacks after
# the landing, kept on GitHub, sluice refusing its delete, and on the host, named, its mark unset and the keeping
# recorded. A landing outlives the crew bolt submit that queued it (plan.21): killed once sluice has queued the landing,
# its waiter on the box calls sluice wait again while sluice is undecided, then reads the landing from sluice's record,
# recording it landed and closing the bolt; and with the waiter stopped too, ops's crew bolt land reads it from sluice's
# record first, records it landed and closes it. A bolt no team holds lands once its unit's change is on main; a
# delete sluice refuses is named in its words, the branch kept on GitHub; a bolt made before gives went through sluice
# is deleted there once its landing's pull request put it there, no create run for it; dropping a held bolt has sluice
# delete its branch, and one holding a merge main lacks is kept on GitHub and the host, marked, named and recorded,
# until a landing brings its tip into main and the next landing's sweep has sluice delete it. Then two bolts of one kit
# proven at once are one landings card of two boxes in the plan's order, the lower forecast to conflict with the one
# above, changed in place when a head moves and when a third joins it; one crew bolt submit lands the three the user
# ticked in that order, each queued behind the one before and closed as it lands, the second refused for its conflict,
# recorded at its head and its take-main fix launched, the third landing all the same, the command exiting non-zero
# naming the held one, and the card the user answered left as it is, their send standing for the one taking main in;
# once its take-main fix's place merges, no card asks for it, and crew bolt submit of it, run again after its landing
# stood in sluice when ops's session ended, waits on that landing again, submits nothing and lands it, closing the
# card with what the send landed (record 0031 as amended 2026-10-24). Last, main moving under a proven row makes crew
# rail on the main level's host raise the kit's landings card again, holding the row taking main first, and a second
# crew rail, main not having moved, raises nothing; and a bolt the user left keeps its box when main moves under it,
# the card changed in place saying it would take main first, and a send ticking it, read by crew card read, submits
# nothing of it (rail-cards, bolt-teams). No agent starts. Every decision on the way is a logic case (tests/py/); how
# git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the command's wiring once.
# Reads: plugin/lib/board.py
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
flume_world
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
short() { git -C "$k" rev-parse --short "$1"; }
# field <host> <act> <field> [object...]: a field of that host's last entry of the act naming every object given
field() {
  local h=$1 a=$2 f=$3; shift 3
  as "$h" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and all(o in e["On"] for o in sys.argv[3:])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$a" "$@" | jq -r --arg f "$f" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
record_of() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null'; }
# flume_place <place> <branch> <bolt>: a Flume place, cut on its branch from the bolt where it lives, GitHub's, after a
# fetch
flume_place() { git -C "$k" fetch -q origin && git -C "$k" worktree add -q -b "$2" "$1" "origin/bolt/$3"; }
# landed <place> <work> <bolt>: Flume's end of a place it submitted to the bolt and sluice landed there: the place
# removed, and the runner on the box carrying Flume's status of it, landed at the bolt's head on GitHub, which the
# fleet's timer has fetched to the box
landed() {
  git -C "$k" fetch -q origin; git -C "$k" worktree remove --force "$1"
  runner_writes $box "$(request_of "$2")" "$1" "$(landed_status "$1" "$(git -C "$k" rev-parse "origin/bolt/$3")")"
}
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew unit add a "Unit a." --bolt tenant-environments >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew unit add c "Unit c." --bolt console-pages >/dev/null
crew bolt give swb-1 tenant-environments >/dev/null
crew bolt give swb-2 console-pages >/dev/null
# sluice forecasts tenant-environments against main with no conflict (teams.21)
printf '{"conflict":null,"head":"%s","onto":"%s","ahead":[]}\n' "$(git -C "$k" rev-parse origin/bolt/tenant-environments)" \
  "$(git -C "$k" rev-parse main)" > "$T/sluice-check-bolt-tenant-environments.json"
# a's change written and archived in its Flume place and submitted to the bolt, which sluice lands there; the bolt's
# policy, as a's place commits it, declares a preview with one address; the bolt and main each change the title.
pa=$T/flume/a
flume_place "$pa" unit/a tenant-environments
change "$pa" a 1 1; commit_all "$pa" "feat(a): its change, done"
{ printf '[preview]\ncommand = ["sh", "-c", "true"]\n\n[preview.addresses]\nweb = "http://{name.web}"\n\n'; cat "$pa/.config/sluice.toml"; } > "$pa/sluice.toml"
mv "$pa/sluice.toml" "$pa/.config/sluice.toml"
commit_all "$pa" "chore: the kit declares a preview"
echo "# switchboard-kit, the bolt's" > "$pa/README.md"; commit_all "$pa" "docs(a): the bolt's title"
mkdir -p "$pa/openspec/changes/archive"; git -C "$pa" mv openspec/changes/a openspec/changes/archive/2026-10-13-a
git -C "$pa" commit -qm "docs(openspec): archive a"
merge_as flume "$pa" bolt/tenant-environments || fail "a's submission failed"
landed "$pa" unit/a tenant-environments
# batched <n> <unit> <bolt>: the unit's change, at its bolt's head on GitHub, read in batch n and the batch closed, as
# crew review and the user's read of its card record them (t-journey-review proves those), so the bolt's landing waits
# on no batch
batched() {
  local w; w=$(git -C "$k" rev-parse "origin/bolt/$3")
  as $box env CREW_AGENT=wldn-planner python3 "$CREW/plugin/lib/record.py" emit --label wldn --act review.batch --on "batch/$1" \
    --on "unit/$2" --why "batch($1): reviewed" --field "Batch=$1" --field "Units=$2:swb-1@$w" >/dev/null
  as $box env CREW_AGENT=wldn-planner python3 "$CREW/plugin/lib/record.py" emit --label wldn --act batch.close --on "batch/$1" \
    --why "batch($1): read" --field "Batch=$1" --field "Key=batch/$1" >/dev/null
}
batched 1 a tenant-environments
echo "# switchboard-kit, main's" > "$k/README.md"
# From here main takes pull requests, as crew's own does: a landing opens one from the bolt's branch (bolt-teams).
rewrite "$k/.config/sluice.toml" '/^\[branches.main\]$/,/^remote/ s/^remote = "origin"$/&\n\n[branches.main.pull_requests]\nreviews = 0/'
commit_all "$k" "docs: main's title, and main takes pull requests"; push "$k"
expect_ok crew bolts --label wldn
has "$out" "verification: green, sluice's verdict on its last landing, $(short origin/bolt/tenant-environments): passed (stub)"
ok "a unit's place merges into the bolt by a submission, and crew bolts reads the bolt's verification from sluice's verdict on it"

# The bolt lands once its units have: submitted to main, which conflicts on the title.
expect_fail "unit a has not landed on switchboard-kit's main: its place landed on bolt/tenant-environments at $(short origin/bolt/tenant-environments), which main does not hold" \
  crew bolt land tenant-environments
land=$kd/places/land-tenant-environments
main_before=$(git -C "$k" rev-parse main)
gh_repo=WilldanGroup/switchboard-kit
pr=$(pull $gh_repo bolt/tenant-environments false)  # the pull request sluice's submission opens, ready for review
: > "$CREW_TEST_LOG"
expect_fail "bolt/tenant-environments did not land: sluice refused it or found a conflict, and main is where it was" crew bolt submit tenant-environments
has "$out" "sluice's verdict: #"; has "$out" " conflict: README.md. "
eq "$(calls | grep "^$box wt submit ")" "$box wt submit main --no-wait --json --no-remove from $land as $me@mac-studio"
has "$out" "tenant-environments did not land, as said above; none landed"
eq "$(git -C "$k" rev-parse main)" "$main_before"
[[ ! -e $land ]] || fail "the landing's worktree is still there"
has "$out" "Its pull request https://github.com/$gh_repo/pull/$pr is a draft, so no merge into bolt/tenant-environments lands it; the next crew bolt submit tenant-environments, on the user's word, makes it live again."
eq "$(drafted "$pr")" true
eq "$(calls | grep -A100 "^$box wt submit " | grep -c "^$box gh pr ready $pr -R $gh_repo --undo$")" 1
m=$(git -C "$k" rev-parse --short=7 origin/main)
tm=fix/tenant-environments/take-main-$m
has "$out" "bolt tenant-environments takes main first: the runner on $box launches fix tenant-environments--take-main-$m (request $(request_of "$tm")), taking origin/main at $m into the bolt"
ok "crew bolt submit lands a bolt by a submission to main from a short-lived worktree, and a conflict lands nothing, leaves its pull request a draft, said with its link, and launches the bolt's take-main fix"

# The take-main fix's Flume place merges main in, resolving the title, and is submitted to the bolt, which sluice lands
# there.
tmp=$T/flume/take-main
flume_place "$tmp" "$tm" tenant-environments
git -C "$tmp" merge -q origin/main >/dev/null 2>&1 && fail "taking main did not stop on the title"
echo "# switchboard-kit, main's and the bolt's" > "$tmp/README.md"; git -C "$tmp" add README.md
GIT_EDITOR=true git -C "$tmp" commit -q --no-edit || fail "the merge of main did not commit"
merge_as flume "$tmp" bolt/tenant-environments || fail "the fix's submission failed"
landed "$tmp" "$tm" tenant-environments
# The box gives a plannotator session a link on its tailnet name, as swancloud sets it.
export PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
reading=$(home_of $box)/.local/state/crew/cards/wldn/land/tenant-environments
refusals=$(home_of $box)/.stub-plannotator/refuse-starts
mkdir -p "${refusals%/*}"; echo 1 > "$refusals"  # the reading's first start fails
on_box() { HOST=$box crew "$@"; }
: > "$CREW_TEST_LOG"
expect_ok on_box rail --label wldn
# The rail's read on the partition's main machine finds the bolt proven and raises the kit's landings card in
# main-level ops's name, keyed by the kit, the bolt its one row, carrying what brings a preview of its head up, sluice
# asked for nothing.
card=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $card ]] || fail "the rail raised no landings card:"$'\n'"$out"
has "$out" "call get_request (requestId $card, name wldn-ops)"
has "$out" "land/switchboard-kit (wldn), wldn-ops's $card: posted: its row had none open"
posted=$(calls | grep "^$box pendingyou post_request ")
has "$posted" '"idempotencyKey": "land/switchboard-kit@wldn"'
has "$posted" '"label": "wldn-ops"'
has "$posted" "\"title\": \"Land the bolt tenant-environments on switchboard-kit's main\""
h1=$(git -C "$k" rev-parse origin/bolt/tenant-environments)
eq "$(calls | grep -c "^$box sluice preview ")" "0"
has "$posted" "Try it running from bolt/tenant-environments at ${h1:0:7}: write on this card to bring it up, and that you are done to put it away. It is not held while the card waits."
lacks "$posted" "web: http://"
ok "once the take-main fix's place has merged, the rail's read raises the kit's landings card in main-level ops's name, keyed by the kit, printing the line that adopts it, with what brings a preview of its head up and sluice asked for nothing"

# The landing card's reading, started with it on the box: one session on the head's folder, the bolt's page
# first and its diff against main last, its link on the card, and crew card session giving it again.
listed() { as $box plannotator sessions --json | jq -r '[.[].pid] | sort | map(tostring) | join(" ")'; }
gone() { until_ok python3 -c 'import os, sys
try:
    os.kill(int(sys.argv[1]), 0)
except ProcessLookupError:
    sys.exit(0)
sys.exit(1)' "$1"; }
# ended: a reading crew sent SIGTERM is gone and took its session's file with it, as plannotator does, so no pid the
# host gives another process later reads as its session
ended() { gone "$1"; [[ ! -e $(home_of $box)/.stub-plannotator/$1.json ]] || fail "plannotator pid $1 ended and left its session's file"; }
url=$(jq -r .url "$reading/session.json"); pid=$(jq -r .pid "$reading/session.json")
[[ $url =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "the landing's reading is not on the box's tailnet name: $url"
eq "$(listed)" "$pid"
eq "$(cat "$refusals")" "0"
has "$out" "card land/tenant-environments: its reading could not be opened on the tailnet: plannotator ended before land/tenant-environments's session was ready: stub: refused to start; crew fetches switchboard-kit's main and tries once more"
lacks "$(field $box card.post Unread kit/switchboard-kit)" "refused"
folder=$(cd "$reading/${h1:0:7}" && pwd -P)
eq "$(jq -r '.argv | map(select(startswith("/") and (endswith("/result.json") | not))) | map(sub(".*/"; "")) | join(" ")' \
  "$(home_of $box)/.stub-plannotator/$pid.json")" \
  "00-tenant-environments.md 01-a-proposal.md 01-a-design.md 01-a-specs-x-spec.md 01-a-tasks.md 02-tenant-environments-diff.txt"
eq "$(jq -r '.argv[1]' "$(home_of $box)/.stub-plannotator/$pid.json")" "$folder/00-tenant-environments.md"
has "$(cat "$folder/02-tenant-environments-diff.txt")" "+# switchboard-kit, main's and the bolt's"
lacks "$(cat "$folder/02-tenant-environments-diff.txt")" "openspec/changes"
has "$(calls | grep "^$box pendingyou post_request " | tail -1)" "\"url\": \"$url\""
expect_ok on_box card session land/tenant-environments
eq "$out" "$url"; eq "$(listed)" "$pid"
ok "the landing card's reading is started with it on the box, a second time when its first start fails, the bolt's page, each unit's change and the bolt's diff against main as one review, its link on the card, and crew card session gives it again, starting nothing"

# The user writes on the card asking to try it running: ops's crew card preview brings it up through sluice on the
# box, its stack taking its time, and the card, changed in place, lists its address while it comes up.
ops() { (export CREW_AGENT=wldn-ops; HOST=$box crew "$@"); }
previews=$(home_of $box)/.local/state/crew/previews/wldn/land-switchboard-kit
touch "$CREW_TEST_ROOT/sluice-preview-holds"  # the preview's stack takes its time to come up
: > "$CREW_TEST_LOG"
out=$(ops card preview land/switchboard-kit tenant-environments 2>&1) || fail "ops could not bring the preview up:"$'\n'"$out"
eq "$(calls | grep "^$box sluice preview ")" "$box sluice preview bolt/tenant-environments $h1 --wait --json in $(cd "$k" && pwd -P)"
has "$out" "tenant-environments: Its preview of ${h1:0:7} is coming up: web http://web-${h1:0:7}--bolt-tenant-environments--kit"
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"changeNote\": \"tenant-environments: Its preview of ${h1:0:7} is coming up\""
has "$changed" "web: http://web-${h1:0:7}--bolt-tenant-environments--kit"
ok "ops's crew card preview, on the user's words, brings the row's preview up through sluice on the box, and the card, changed in place, lists its address while it comes up"

# The preview's stack fails: the process crew handed the ask to changes the card in place while it waits on the user.
touch "$CREW_TEST_ROOT/sluice-preview-fails"; rm "$CREW_TEST_ROOT/sluice-preview-holds"
until_ok grep -q "^card land/switchboard-kit: $card changed" "$previews/tenant-environments.log" ||
  fail "the card was not changed for its preview's end:"$'\n'"$(cat "$previews/tenant-environments.log")"
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"changeNote\": \"tenant-environments: Its preview of ${h1:0:7} did not come up\""
has "$changed" "A preview of ${h1:0:7} was asked for and is not there: starting web / stub: the preview command failed: web did not come up."
lacks "$changed" "web: http://"
rm "$CREW_TEST_ROOT/sluice-preview-fails"
ok "a preview whose stack fails is said on the card, changed in place while it waits on the user"

# The user writes that they are done with it: ops's --done releases it, sluice lists none, and the card, changed in
# place, carries what brings it up again.
: > "$CREW_TEST_LOG"
out=$(ops card preview land/switchboard-kit tenant-environments --done 2>&1) || fail "ops could not put the preview away:"$'\n'"$out"
has "$out" "released tenant-environments's preview of ${h1:0:7} from land/switchboard-kit"
eq "$(ls "$CREW_TEST_ROOT/sluice-previews")" ""
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"changeNote\": \"tenant-environments: Its preview of ${h1:0:7} is put away\""
has "$changed" "Try it running from bolt/tenant-environments at ${h1:0:7}: write on this card to bring it up"
ok "ops's --done, on the user's words, releases the preview, and the card carries what brings it up again"

# A defect noted on the card: a fix launched on the bolt holds its row, ending its reading, and the card, with no row
# left that can land, is withdrawn naming the fix's words.
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 gap "The zone list misses one zone."
has "$out" "the runner on $box launches fix tenant-environments--gap on bolt/tenant-environments (request $(request_of fix/tenant-environments/gap)) in stream wldn"
has "$out" "card land/switchboard-kit: $card withdrawn"
has "$out" "ended land/tenant-environments's session, plannotator pid $pid"
ended "$pid"; eq "$(listed)" ""
has "$(calls | grep "^$box pendingyou cancel_request ")" '"reason": "every bolt waiting to land is held: tenant-environments, held for a fix: The zone list misses one zone. (fix/tenant-environments/gap)"'
eq "$(calls | grep "^$box sluice release " | grep -vc " --worktree ")" "0"
# The fix's Flume place lands on GitHub's bolt, sluice pushing as its app, which leaves the host's copy without its
# merge (plan.19).
gp=$T/flume/gap
flume_place "$gp" fix/tenant-environments/gap tenant-environments
echo four >> "$gp/zones.txt"; commit_all "$gp" "fix(a): the zone list holds every zone"
lag=$(git -C "$k" rev-parse bolt/tenant-environments)
touch "$T/sluice-leaves-copy"
merge_as flume "$gp" bolt/tenant-environments || fail "the gap fix's submission failed"
rm "$T/sluice-leaves-copy"
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$lag"
landed "$gp" fix/tenant-environments/gap tenant-environments
: > "$CREW_TEST_LOG"
echo 2 > "$refusals"  # both of the reading's starts fail
expect_ok on_box rail --label wldn
again=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $again && $again != "$card" ]] || fail "the landings card was not raised again:"$'\n'"$out"
h2=$(git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse bolt/tenant-environments)  # GitHub's, where it lives
git -C "$k" merge-base --is-ancestor "$h2" "$lag" && fail "the host's copy holds the gap fix's merge"
posted=$(calls | grep "^$box pendingyou post_request " | tail -1)
lacks "$posted" '"follows"'
refused="plannotator ended before land/tenant-environments's session was ready: stub: refused to start"
has "$posted" "Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and "
has "$posted" " starts it with crew card session land/tenant-environments; this card then carries its link."
has "$posted" "The reading could not be opened on the tailnet: $refused"
has "$out" "card land/tenant-environments: its reading could not be opened on the tailnet: $refused; crew card session land/tenant-environments starts it"
[[ ! -e $reading/session.json ]] || fail "a reading is recorded though both its starts failed"
eq "$(listed)" ""; eq "$(cat "$refusals")" "0"
eq "$(field $box card.post Card kit/switchboard-kit) $(field $box card.post Unread kit/switchboard-kit)" "$again $refused"
has "$posted" "Try it running from bolt/tenant-environments at ${h2:0:7}: write on this card to bring it up"
eq "$(calls | grep -c "^$box sluice preview ")" "0"
ok "a fix launched on the bolt holds its row, ending its reading, the card withdrawn with no row left that can land, and once the fix's place merges the rail's read posts a new card with what brings a preview of the new head up, raised without its row's reading when both its starts fail, naming crew card session, and why is kept in the box's run record"

# The read of the bolt's row finds no reading running, and its crew card session starts it, changing the card to carry
# its link; the reading runs until the landing's close ends it, with nothing of crew's waiting on it. crew card read
# reads a bolt's reading in the name of the conductor of the team holding it, though no conductor runs.
reader() { (export CREW_AGENT=swb-1-conductor; HOST=$box crew "$@"); }
out=$(reader card read land/tenant-environments 2>&1) || fail "the bolt's reading could not be read:"$'\n'"$out"
eq "$out" "land/tenant-environments: no reading of it runs on this host: crew card session land/tenant-environments starts it"
out=$(ops card session land/tenant-environments 2>&1) || fail "ops could not start the bolt's reading:"$'\n'"$out"
pid2=$(jq -r .pid "$reading/session.json"); url2=$(jq -r .url "$reading/session.json")
eq "$(head -1 <<<"$out")" "$url2"
[[ $pid2 != "$pid" ]] || fail "the landing card raised again has its old reading"
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"requestId\": \"$again\""; has "$changed" "\"changeNote\": \"tenant-environments: Its reading is open again at a new link\""; has "$changed" "$url2"
eq "$(listed)" "$pid2"
out=$(reader card read land/tenant-environments 2>&1) || fail "the bolt's reading could not be read:"$'\n'"$out"
eq "$out" "land/tenant-environments: its reading waits on the user, who has sent nothing from it"
ok "a read of the bolt's row with no reading says so, and ops's crew card session starts it, prints its link and changes the kit's card to carry it"

# The user asks on the card raised again to try it running, and ops brings it up at the new head; then the user
# approves the card, and main-level ops submits the bolt: it lands, the kit's detached main checkout left as it was,
# and is closed as it lands, the preview released. A landing stopped before it removed its worktree left one on the
# bolt's branch, its process gone, which the submission takes up and removes.
out=$(ops card preview land/switchboard-kit tenant-environments 2>&1) || fail "ops could not bring the preview up again:"$'\n'"$out"
has "$out" "tenant-environments: Its preview of ${h2:0:7} is up: web http://web-${h2:0:7}--bolt-tenant-environments--kit"
mkdir -p "$(home_of $box)/.stub-pendingyou/answered"
echo '{"answer": {"approved": true}}' > "$(home_of $box)/.stub-pendingyou/answered/$again.json"
git -C "$k" worktree add -q "$land" bolt/tenant-environments
sh -c 'echo $$' > "$(git -C "$land" rev-parse --absolute-git-dir)/crew-landing"
git -C "$k" switch -q --detach  # the kit's main checkout as the anchor the fleet's timer moves (plan.18)
bolt_tip=$h2 tip=${h2:0:7}
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$lag"
# The host can't run main's checks: the landing is stopped, nothing of the bolt's, recorded with its head and no
# refusal; its row keeps its box, the card the user answered is left as it is, and crew card read names the bolt with
# what stopped it beside the command that lands it (rail-cards "Checks that never ran").
echo "check-full: the Dagger engine did not answer" > "$CREW_TEST_ROOT/sluice-could-not-run"
stop="check-full could not run: the Dagger engine did not answer"
: > "$CREW_TEST_LOG"
out=$(on_box bolt submit tenant-environments 2>&1) && fail "a landing whose checks could not run landed:"$'\n'"$out"
# The host's copy lags GitHub's by the gap fix's merge: the landing levels it to GitHub's head first, says so, and
# submits that head, the worktree a stopped landing left on the copy brought along (bolt-teams "The host's copy lags
# GitHub's").
has "$out" "levelled $box's copy of bolt/tenant-environments from ${lag:0:7} to GitHub's $tip, 1 merge it lacked"
has "$out" "bolt/tenant-environments did not land, and nothing of the bolt's stopped it: $stop, and main is where it was. Its row keeps its box and the user's word stands: report what stopped it, and once it is cleared crew bolt submit tenant-environments submits it again, with no new word."
has "$out" "card land/switchboard-kit: $again is left as it is, the user having answered it"
eq "$(field $box bolt.submit Outcome bolt/tenant-environments)|$(field $box bolt.submit Refused bolt/tenant-environments)" "stopped|"
eq "$(field $box bolt.submit Head bolt/tenant-environments) $(git -C "$k" rev-parse bolt/tenant-environments)" "$bolt_tip $bolt_tip"
[[ ! -e $land ]] || fail "the stopped landing's worktree is still there"
has "$(field $box bolt.submit Why bolt/tenant-environments)" "$stop. Its pull request https://github.com/$gh_repo/pull/$pr is a draft"
eq "$(drafted "$pr")" true
row=$(on_box _land-row wldn tenant-environments --json 2>/dev/null | tail -1)
eq "$(jq -r '.box' <<<"$row") $(jq -r '.facts.stopped[1]' <<<"$row" | cut -c1-${#stop})" "true $stop"
out=$(ops card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
has "$out" "  to land, in the card's order: tenant-environments"
has "$out" "  tenant-environments's last landing at $(short bolt/tenant-environments) was stopped, nothing of the bolt's: $stop"
has "$out" "lands them: crew bolt submit tenant-environments --label wldn"
rm "$CREW_TEST_ROOT/sluice-could-not-run"
ok "a landing whose checks the host could not run takes up the place a stopped landing left, levels the host's lagging copy to GitHub's head first and says so, and is stopped, nothing of the bolt's: recorded with no refusal, its row keeps its box, the card the user answered is left as it is, and crew card read names it with what stopped it"
# Once the host runs them, the next submission lands it on the same send, with no new word, at GitHub's head, the
# host's copy already level with it.
: > "$CREW_TEST_LOG"
expect_ok crew bolt submit tenant-environments
lacks "$out" "levelled $box's copy"
has "$out" "bolt/tenant-environments landed on switchboard-kit's main at $(short main): now crew bolt land tenant-environments."
has "$out" "Its pull request https://github.com/$gh_repo/pull/$pr is ready for review again, so sluice takes it at the head bolt/tenant-environments has now."
eq "$(drafted "$pr")" false
# sluice answers with the pull request, as on a main that takes them: crew waits on the submission it made from it,
# told from any made before by sluice's record of main read before the pull request is readied, and read again after.
has "$out" "bolt/tenant-environments submitted to switchboard-kit's main, sluice's #"
has "$out" " from pull request #$pr"
eq "$(calls | grep -c "^exec sluice status main --all --json$")" 2
eq "$(calls | grep -E "^$box (gh pr ready|wt submit) " | cut -d' ' -f2-4)" $'gh pr ready\nwt submit main'
eq "$(calls | grep -c "^$box gh pr ready .* --undo$")" 0
grep -v "copy of bolt/tenant-environments" <<<"$out" | grep -q level && fail "the landing spoke of levelling a detached checkout:"$'\n'"$out"
eq "$(git -C "$k" log -1 --format='%an %P' main)" "sluice $main_before $bolt_tip"
git -C "$k" merge-base --is-ancestor "$bolt_tip" main || fail "main lacks the merge the host's copy lacked"
eq "$(git -C "$k" rev-parse HEAD) $(cat "$k/README.md")" "$main_before # switchboard-kit, main's"
eq "$(git -C "$k" status --porcelain)" ""
[[ ! -e $land ]] || fail "the landing's worktree is still there"
# Recorded queued where it was submitted, and its outcome where it was read, the box (plan.21).
eq "$(field mac-studio bolt.submit Outcome bolt/tenant-environments) $(field mac-studio bolt.submit Head bolt/tenant-environments)" "queued $bolt_tip"
n=$(field mac-studio bolt.submit Submission bolt/tenant-environments)
eq "$(field $box bolt.submit Outcome bolt/tenant-environments) $(field $box bolt.submit Submission bolt/tenant-environments) $(field $box bolt.submit Head bolt/tenant-environments)" \
  "landed $n $bolt_tip"
git -C "$k" switch -q main  # the timer's move, for the steps below that commit on the kit's main
has "$out" "tenant-environments has landed at switchboard-kit's $(git -C "$k" rev-parse --short=7 main)"
has "$(calls | grep "^$box pendingyou ack_answer ")" "\"outcome\": \"Landed on GitHub's main: tenant-environments at $(short main); every host's folder follows by swancloud's timer within minutes.\""
has "$out" "card land/switchboard-kit: $again closed"
has "$out" "released tenant-environments's preview of ${h2:0:7} from land/switchboard-kit"
eq "$(ls "$CREW_TEST_ROOT/sluice-previews")" ""
has "$out" "ended land/tenant-environments's session, plannotator pid $pid2"
ended "$pid2"; eq "$(listed)" ""
[[ ! -e $reading ]] || fail "the landing's reading outlived its card"
has "$out" "sluice deleted bolt/tenant-environments from GitHub at $tip"
git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still on GitHub"
eq "$(git -C "$k" config branch.bolt/tenant-environments.crew || true)" ""
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -c)" "0"
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still there"
eq "$(field $box bolt.land On bolt/tenant-environments) $(field $box bolt.land Commit bolt/tenant-environments)" "bolt/tenant-environments unit/a WilldanGroup/crew-state@$(act_tip)"
eq "$(field $box bolt.land Repo bolt/tenant-environments) $(field $box bolt.land Head bolt/tenant-environments)" "switchboard-kit $(git -C "$k" rev-parse main)"
eq "$(field $box bolt.land By bolt/tenant-environments)" "wldn-ops"  # closed by the landing's read in main-level ops's name
# The stub's record of a submission keeps no time it was submitted or told, so the bolt's age and split can't be told
# and the entry carries neither, the landing going on (run-record "sluice's record can't be read at the landing").
eq "$(field $box bolt.land Age bolt/tenant-environments)$(field $box bolt.land Split bolt/tenant-environments)" ""
ok "the bolt, submitted again on the user's word once its checks can run, lands at GitHub's head, its worktree removed and the detached main checkout left as it was, and is closed as it lands, recording the commit main holds, sluice deleting its branch from GitHub and the host, closing the kit's landings card with where GitHub's main holds it and the timer, ending its row's reading and releasing its preview"

# A bolt landed with a chore of its own not yet built (plan.21, plan.8's reading of 2026-10-27): its close is refused,
# said by the landing, and recorded once in main-level ops's name, though the waiter's read and the submission's own
# each tried it; its head line on the board says it landed on main and was not closed, in those words.
crew bolt new zone-lists "The zone list grows." --repo switchboard-kit >/dev/null
crew bolt give swb-1 zone-lists >/dev/null
crew chore add tidy-zones "Tidy the zone list." --bolt zone-lists >/dev/null
# on_bolt <bolt> <line> <subject>: a commit on the bolt's branch, pushed as sluice pushes a landing on a bolt on GitHub
on_bolt() { git -C "$k" worktree add -q "$T/$1" "bolt/$1" && echo "$2" >> "$T/$1/zones.txt" &&
  commit_all "$T/$1" "$3" && git -C "$k" worktree remove "$T/$1" && git -C "$k" push -q origin "bolt/$1"; }
on_bolt zone-lists north "feat: the zone list" || fail "the bolt took no commit"
out=$(export CREW_AGENT=wldn-ops; crew bolt submit zone-lists 2>&1) || fail "the landing did not land:"$'\n'"$out"
ready="chore tidy-zones has not merged into bolt/zone-lists: it is launching"
has "$out" "bolt/zone-lists landed on switchboard-kit's main at"
has "$out" "bolt/zone-lists landed and was not closed: $ready; crew's next read of the bolt closes it once that is mended"
eq "$(git -C "$k" config branch.bolt/zone-lists.crew)" "landed"
eq "$(plan -t Bolt -e "Bolt = 'zone-lists'" -c)" "1"
eq "$(record_of $box | grep -c "^Refused: $ready$")" "1"
eq "$(field $box bolt.land By bolt/zone-lists) | $(field $box bolt.land Refused bolt/zone-lists)" "wldn-ops | $ready"
expect_ok crew board --label wldn
has "$out" "  landed on main, not closed: $ready  "
has "$out" "bolt zone-lists: it landed on main and was not closed: $ready"
ok "a bolt landed with a chore not yet built has its close refused, said and recorded once in main-level ops's name over the two reads that tried it, and its head line on the board says it landed on main and was not closed, in those words"

# The branch takes a commit after its landing, and the planner drops the chore: the drop's read of the bolt that
# follows closes it, sluice refusing its branch's delete, so it is kept on GitHub and, at its commit, on the host,
# named, its mark unset and the keeping recorded.
on_bolt zone-lists south "feat: one zone more, after the landing" || fail "the bolt took no commit after its landing"
at=$(short bolt/zone-lists)
expect_ok crew chore drop tidy-zones "folded into the next"
eq "$(plan -t Bolt -e "Bolt = 'zone-lists'" -c)" "0"
eq "$(field $box bolt.land By bolt/zone-lists) | $(field $box bolt.land Refused bolt/zone-lists) | $(field $box bolt.land Repo bolt/zone-lists)" \
  "wldn-ops |  | switchboard-kit"
has "$out" "bolt/zone-lists is kept on GitHub: sluice did not delete it: bolt/zone-lists at $(git -C "$k" rev-parse bolt/zone-lists) has not landed into main"
has "$out" "bolt/zone-lists is kept at $at: bolt zone-lists has landed, and it holds 1 commit whose patch origin/main lacks (git cherry), the user's to keep or delete"
eq "$(git -C "$k" config branch.bolt/zone-lists.crew)" ""
eq "$(field $box branch.kept Head bolt/zone-lists) $(field $box branch.kept Count bolt/zone-lists)" "$at 1"
eq "$(field $box branch.kept From bolt/zone-lists) | $(field $box branch.kept Why bolt/zone-lists)" \
  "bolt/zone-lists | bolt zone-lists has landed, and origin/main lacks its patches"
eq "$(short bolt/zone-lists)" "$at"
git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q bolt/zone-lists >/dev/null || fail "the refused delete removed bolt/zone-lists from GitHub"
ok "once the planner drops the chore the drop's read closes the bolt, its branch, holding a commit main lacks, kept on GitHub, sluice refusing its delete, and at its commit on the host, named, its mark unset and the keeping recorded"

# A landing outlives its submitter (plan.21): crew bolt submit is killed once sluice has queued the landing, sluice still
# undecided; the waiter it left on the box calls sluice wait again, a call at a time, while it exits 5, and then
# reads the landing from sluice's record, records it landed and closes the bolt, no one running crew bolt land.
# queued <bolt>: the bolt's landing is recorded queued where it was submitted, and its entry is on the branch, where
# every host reads it (read.5)
queued() { [[ $(field mac-studio bolt.submit Outcome "bolt/$1") == queued ]] &&
  grep -q "^runs(mac-studio): bolt.submit bolt/$1 " <<<"$(git --git-dir "$ws" log --format=%s wldn/main)"; }
# closed <bolt>: the plan holds the bolt no more
closed() { [[ $(plan -t Bolt -e "Bolt = '$1'" -c) == 0 ]]; }
# submitters <pid> <bolts>: the python of each crew bolt submit <bolts> among the processes <pid> started, this run's
# alone: a pattern matched across the host ends another run's of this test, as sluice runs it side by side (tests.9)
submitters() {
  local c re="lib/plan\.py bolt submit $2\$"
  for c in $(pgrep -P "$1"); do
    [[ $(ps -ww -o command= -p "$c") =~ $re ]] && echo "$c"
    submitters "$c" "$2"
  done
}
# killed <bolt> <pid>: crew bolt submit of the bolt, run in the background as <pid>, killed with the python it runs
killed() {
  local p; p=$(submitters "$2" "$1"); [[ -n $p ]] || fail "crew bolt submit $1 was not running under $2"
  kill $p 2>/dev/null || true; wait "$2" 2>/dev/null || true
  until_ok bash -c 'for p; do ! kill -0 "$p" 2>/dev/null || exit 1; done' _ $p || fail "crew bolt submit $1 was not stopped"
}
# decoy: another run's landing on the host, started outside this run's processes, its command line crew bolt submit
# far-reach's, its pid in $decoy; it ends with this run's scratch folder, or in thirty minutes. spared <what>: the decoy
# outlived what this run just ended, and is ended. Each lives only around one of this run's ends, since a copy of this
# test from before its kills were its own ends it from anywhere on the host.
mkdir -p "$T/decoy/lib"
printf '%s\n' 'import pathlib, time' 'end = time.time() + 1800' \
  'while pathlib.Path(__file__).exists() and time.time() < end:' '    time.sleep(1)' > "$T/decoy/lib/plan.py"
decoy=
decoy() {
  (python3 "$T/decoy/lib/plan.py" bolt submit far-reach </dev/null >/dev/null 2>&1 & echo $! > "$T/decoy.pid")
  decoy=$(cat "$T/decoy.pid")
  until_ok bash -c '[[ $(ps -ww -o command= -p "$1") == *"/decoy/lib/plan.py bolt submit far-reach" ]]' _ "$decoy" ||
    fail "the decoy did not start"
}
spared() {
  kill -0 "$decoy" 2>/dev/null || fail "$1 ended another run's crew bolt submit far-reach on the host"
  kill "$decoy" 2>/dev/null || true; decoy=
}
# A test that stops before it lets sluice decide leaves no waiter of its own calling sluice wait, nor a submitter.
leave() { rm -f "$T/sluice-wait-holds"; kill $(submitters $$ "((far|near)-reach|north south east)") 2>/dev/null || true; }
trap 'leave; [[ -z $decoy ]] || kill "$decoy" 2>/dev/null || true' EXIT
crew bolt new far-reach "The zones reach far." --repo switchboard-kit >/dev/null
crew bolt give swb-1 far-reach >/dev/null 2>&1
on_bolt far-reach far "feat: far zones" || fail "the bolt took no commit"
touch "$T/sluice-wait-holds"  # sluice has not decided
(export CREW_AGENT=wldn-ops; crew bolt submit far-reach > "$T/far-reach.out" 2>&1) &
submitter=$!
until_ok queued far-reach || fail "the landing was not recorded queued:"$'\n'"$(cat "$T/far-reach.out")"
decoy
killed far-reach "$submitter"
spared "ending this run's crew bolt submit far-reach"
n=$(field mac-studio bolt.submit Submission bolt/far-reach)
far=$kd/places/land-far-reach
waiter=$(cat "$(git -C "$far" rev-parse --absolute-git-dir)/crew-landing")
kill -0 "$waiter" 2>/dev/null || fail "no waiter runs on the landing's submission #$n"
echo 2 > "$T/sluice-wait-$n-fives"  # two waits more that sluice is undecided on, once it is no longer held
: > "$CREW_TEST_LOG"
rm "$T/sluice-wait-holds"
until_ok closed far-reach || fail "the waiter's read did not close far-reach:"$'\n'"$(calls)"
# sluice undecided on two more waits: the waiter spent both and called again after each (teams.5)
eq "$(cat "$T/sluice-wait-$n-fives")" "0"
(( $(calls | grep -c "^$box sluice wait main --timeout 9m --json in $(cd "$kd" && pwd -P)/places/land-far-reach$") >= 2 )) ||
  fail "the waiter did not wait a call at a time:"$'\n'"$(calls)"
until_ok bash -c '! kill -0 "$1" 2>/dev/null' _ "$waiter" || fail "the waiter outlived its read"
eq "$(field $box bolt.submit Outcome bolt/far-reach) $(field $box bolt.submit Submission bolt/far-reach)" "landed $n"
eq "$(field $box bolt.land By bolt/far-reach) $(field $box bolt.land Head bolt/far-reach)" "wldn-ops $(git -C "$k" rev-parse main)"
[[ ! -e $far ]] || fail "the landing's worktree is still there"
ok "a landing outlives the submitter that queued it: its waiter on the box calls sluice wait again while sluice is undecided, then reads the landing from sluice's record, records it landed and closes the bolt"

# The waiter stopped as well before sluice decided: nothing records the landing until crew's next act on the bolt,
# main-level ops's crew bolt land, whose read of it from sluice's record comes first, recording it landed and closing
# the bolt, so that close is said and no second one made.
crew bolt new near-reach "The zones reach near." --repo switchboard-kit >/dev/null
crew bolt give swb-1 near-reach >/dev/null 2>&1
on_bolt near-reach near "feat: near zones" || fail "the bolt took no commit"
touch "$T/sluice-wait-holds"
(export CREW_AGENT=wldn-ops; crew bolt submit near-reach > "$T/near-reach.out" 2>&1) &
submitter=$!
until_ok queued near-reach || fail "the landing was not recorded queued:"$'\n'"$(cat "$T/near-reach.out")"
killed near-reach "$submitter"
near=$kd/places/land-near-reach
waiter=$(cat "$(git -C "$near" rev-parse --absolute-git-dir)/crew-landing")
# stopped <pid>: the process and everything it started, its children first, so the waiter's loop does not outlive the
# process crew-landing names and read the landing itself
stopped() { local c; for c in $(pgrep -P "$1"); do stopped "$c"; done; kill -KILL "$1" 2>/dev/null || true; }
loop=$(pgrep -P "$waiter")
stopped "$waiter"
until_ok bash -c 'for p; do ! kill -0 "$p" 2>/dev/null || exit 1; done' _ "$waiter" $loop || fail "the waiter was not stopped"
rm "$T/sluice-wait-holds"
eq "$(plan -t Bolt -e "Bolt = 'near-reach'" -c) $(field $box bolt.submit Outcome bolt/near-reach)" "1 "
out=$(export CREW_AGENT=wldn-ops; crew bolt land near-reach 2>&1) || fail "ops's crew bolt land near-reach failed:"$'\n'"$out"
has "$out" "bolt/near-reach landed on switchboard-kit's main at"
has "$out" "bolt near-reach is closed: crew's read of its landing closed it"
eq "$(plan -t Bolt -e "Bolt = 'near-reach'" -c)" "0"
eq "$(field $box bolt.submit Outcome bolt/near-reach) $(field $box bolt.land By bolt/near-reach)" "landed wldn-ops"
has "$(field $box bolt.land Why bolt/near-reach)" "read from sluice's record by wldn-ops"
ok "a landing whose submitter and waiter were both stopped before sluice decided is read by ops's crew bolt land, which records it landed from sluice's record and closes the bolt, saying so"

# A bolt built outside a team: no team holds it, and it lands once its unit's change is on the kit's main.
crew bolt new done-outside "Built outside a team." --repo switchboard-kit >/dev/null
crew unit add done-x "Unit done-x." --bolt done-outside >/dev/null
expect_fail "unit done-x has not landed on main: it is ready" crew bolt land done-outside
mkdir -p "$k/openspec/changes/archive/2026-10-12-done-x"; echo "# done-x" > "$k/openspec/changes/archive/2026-10-12-done-x/proposal.md"
commit_all "$k" "chore(openspec): archive done-x"; push "$k"
expect_ok crew bolt land done-outside
eq "$(tail -1 <<<"$out")" "done-outside has landed at switchboard-kit's $(git -C "$k" rev-parse main | cut -c1-7); no team held it"
eq "$(field mac-studio bolt.land Head bolt/done-outside) $(plan -t Bolt -e "Bolt = 'done-outside'" -c)" "$(git -C "$k" rev-parse main) 0"
ok "a bolt no team holds lands once its unit's change is on its kit's main, recording the commit main holds"

# A delete sluice refuses, a submission still queued on the bolt: the bolt leaves the plan, its branch kept on GitHub and
# named in sluice's words. Its chore's Flume place landed on the bolt, and a landing carried the bolt's work to main.
crew bolt new queued-one "Landed with a submission queued." --repo switchboard-kit >/dev/null
crew chore add q1 "Chore q1." --bolt queued-one >/dev/null
crew bolt give swb-1 queued-one >/dev/null 2>&1
flume_lands $box chore q1 queued-one
git -C "$k" merge -q --no-edit origin/bolt/queued-one && push "$k"
echo 3 > "$T/sluice-queued-bolt-queued-one"
expect_ok crew bolt land queued-one
has "$out" "bolt/queued-one is kept on GitHub: sluice did not delete it: #3 still queued on bolt/queued-one; wait for them to land, or withdraw them"
eq "$(plan -t Bolt -e "Bolt = 'queued-one'" -c)" "0"
git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q bolt/queued-one >/dev/null || fail "the refused delete removed bolt/queued-one from GitHub"
rm "$T/sluice-queued-bolt-queued-one"
ok "a delete sluice refuses leaves the bolt out of the plan and its branch on GitHub, named in sluice's words"

# A bolt made before gives went through sluice: its branch made with git on the kit's host, its policy naming no remote
# for bolts, until its last merge brings main's, which names origin; its landing's pull request puts it on GitHub, and
# crew bolt land has sluice delete it there, no create run for it.
hands=0
# by_hand <python>: plan.rec changed on the branch in one commit, the python statement changing p, a plan.Plan
by_hand() {
  local w=$T/hand-$((hands += 1)); git clone -q -b wldn/main "$ws" "$w"
  python3 - "$CREW/plugin/lib" "$w/plan.rec" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
exec(sys.argv[3])
open(f, "w").write(p.text())
PY
  commit_all "$w" "plan: by hand"; push_state "$w"
}
by_hand 'p.insert(plan.Rec("Bolt", [("Bolt", "made-before"), ("Repo", "switchboard-kit"), ("Goal", "Made before."), ("Team", "swb-1")]))
p.insert(plan.Rec("Unit", [("Unit", "mb"), ("Repo", "switchboard-kit"), ("Bolt", "made-before"), ("Intent", "Unit mb.")]))'
git -C "$k" branch -q --no-track bolt/made-before main; git -C "$k" config branch.bolt/made-before.crew given
on_branch "$k" bolt/made-before "chore: bolts kept on the host" .config/sluice.toml $'[branches."bolt/*"]\nrequired = ["#check-full"]\n'
mkdir -p "$k/openspec/changes/archive/2026-10-22-mb"; echo "# mb" > "$k/openspec/changes/archive/2026-10-22-mb/proposal.md"
commit_all "$k" "chore(openspec): archive mb"; push "$k"
git -C "$k" update-ref refs/heads/bolt/made-before "$(git -C "$k" commit-tree "main^{tree}" -p bolt/made-before -p main -m "chore(land): #20 chore/bolts-on-github")"
git -C "$k" push -q origin bolt/made-before  # as sluice pushes the branch its landing's pull request opens from
: > "$CREW_TEST_LOG"
expect_ok crew bolt submit made-before
has "$out" "sluice deleted bolt/made-before from GitHub at"
git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q bolt/made-before >/dev/null && fail "bolt/made-before is still on GitHub"
git -C "$k" rev-parse --verify -q bolt/made-before >/dev/null && fail "bolt/made-before is still on the host"
calls | grep -q " sluice branch create bolt/made-before " && fail "crew ran a create for a bolt made before"
ok "a bolt made before lands through its pull request, and sluice deletes its branch from GitHub with no create run for it"

github() { git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q "$1" >/dev/null; }
console=$(short origin/bolt/console-pages)
expect_ok crew bolt drop console-pages "the portal lists them"
has "$out" "sluice deleted bolt/console-pages from GitHub at $console"
github bolt/console-pages && fail "bolt/console-pages is still on GitHub"
git -C "$k" rev-parse --verify -q bolt/console-pages >/dev/null && fail "bolt/console-pages is still on the host"
eq "$(git --git-dir "$ws" log -1 --format=%b "$(act_tip)" | head -1)" "the portal lists them"
ok "dropping a held bolt has sluice delete its branch from GitHub and the host, with the reason in the commit"

# A dropped bolt holding a merge main lacks: sluice refuses its delete, and the branch is kept on GitHub and the host,
# marked dropped, named as the drop's unmerged work in sluice's words and recorded once.
crew bolt new kept-work "Work dropped before it landed." --repo switchboard-kit >/dev/null
crew bolt give swb-2 kept-work >/dev/null
on_bolt kept-work kept "feat: work merged into the bolt" || fail "the bolt took no merge"
tip=$(git -C "$k" rev-parse bolt/kept-work)
expect_ok crew bolt drop kept-work "not this quarter"
has "$out" "bolt/kept-work is kept on GitHub at ${tip:0:7}: bolt kept-work was dropped, and sluice did not delete it: bolt/kept-work at $tip has not landed into main; submit it there first; it is the drop's unmerged work, the user's to keep or delete, and crew asks sluice again once main holds its tip"
github bolt/kept-work || fail "the refused delete removed bolt/kept-work from GitHub"
eq "$(git -C "$k" rev-parse bolt/kept-work) $(git -C "$k" config branch.bolt/kept-work.crew)" "$tip dropped"
eq "$(field $box branch.kept Head bolt/kept-work team/swb-2) | $(field $box branch.kept Why bolt/kept-work)" \
  "${tip:0:7} | bolt kept-work was dropped, and main does not hold its tip (sluice)"
eq "$(record_of $box | grep -c "^On: bolt/kept-work")" "1"
ok "a dropped bolt holding a merge main lacks is kept on GitHub and the host, marked, named in sluice's words and recorded once"
git -C "$k" merge -q --no-edit bolt/kept-work && push "$k"  # a landing that carried its work

# Two bolts of one kit proven at once: one landings card in main-level ops's name, on the partition's main machine, a
# box a bolt in the plan's order, the lower row forecast to conflict with the one above it; a merge that moves the
# second's head changes the card in place, naming it. Each bolt's work is a chore Flume builds, writing the file it
# names, and lands on the bolt, so the bolt reads proven at sluice's green head.
for b in north south east; do crew bolt new "$b" "The $b regions." --repo switchboard-kit >/dev/null; done
crew chore add north-regions "North's regions." --bolt north >/dev/null; crew chore add south-regions "South's regions." --bolt south >/dev/null
crew bolt give swb-1 north >/dev/null 2>&1; crew bolt give swb-2 south >/dev/null 2>&1
flume_lands $box chore north-regions north regions.txt
flume_lands $box chore south-regions south regions.txt
: > "$CREW_TEST_LOG"
expect_ok on_box _land-card wldn switchboard-kit
kit=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $kit ]] || fail "no landings card was raised for north and south:"$'\n'"$out"
posted=$(calls | grep "^$box pendingyou post_request " | tail -1)
eq "$(jq -c '[.idempotencyKey, .session.label, .kind, .highStakes, [.options[].label], .recommendedIds]' <<<"${posted#* post_request }")" \
  '["land/switchboard-kit@wldn:3","wldn-ops","multi",true,["1. north","2. south"],["land:north","land:south"]]'  # two closed before it
has "$posted" "It is forecast to conflict with north on regions.txt."
eq "$(field $box card.post Heads kit/switchboard-kit)" "north@$(short origin/bolt/north) south@$(short origin/bolt/south)"
crew chore add south-more "More of south." --bolt south >/dev/null
flume_lands $box chore south-more south south.txt
: > "$CREW_TEST_LOG"
expect_ok on_box _land-card wldn switchboard-kit
has "$out" "card land/switchboard-kit: $kit changed"
changed=$(calls | grep "^$box pendingyou update_request ")
has "$changed" "\"changeNote\": \"south's head is now $(short origin/bolt/south)\""
calls | grep -q "^$box pendingyou post_request " && fail "the card was posted again rather than changed in place"
ok "two proven bolts of one kit are one landings card in main-level ops's name, a box each in the plan's order, the lower forecast to conflict with the one above, and a merge moving the second's head changes it in place"

# A third bolt proven joins the card in place; the user sends it with all three ticked, and one crew bolt submit lands
# them in the card's order, each queued behind the one before on the one host, each closed as it lands: south, which
# conflicts with north on main once north has landed, is refused, recorded at its head in sluice's words and held on
# its row taking main first, its take-main fix launched, and east lands all the same; the command exits non-zero
# naming south, and the card the user answered is left as it is, their send standing for south as it takes main in.
# The landings' sweep has sluice delete the dropped bolt's branch kept before, main holding its tip.
crew chore add east-files "East's files." --bolt east >/dev/null
crew bolt give swb-1 east >/dev/null 2>&1
flume_lands $box chore east-files east east.txt
: > "$CREW_TEST_LOG"
expect_ok on_box _land-card wldn switchboard-kit
has "$out" "card land/switchboard-kit: $kit changed"
has "$(calls | grep "^$box pendingyou update_request ")" "\"changeNote\": \"east reads proven and joins the card\""
echo '{"answer": {"choiceIds": ["land:north", "land:south", "land:east"]}}' > "$(home_of $box)/.stub-pendingyou/answered/$kit.json"
out=$(ops card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
has "$out" "lands them: crew bolt submit north south east --label wldn"
south=$(git -C "$k" rev-parse origin/bolt/south)
: > "$CREW_TEST_LOG"
# sluice decides none of them until all three are queued, as it decides a chain each queued behind the one before, so
# each outcome is read once east has landed, whether the landing's waiter or the command reads it first
touch "$T/sluice-wait-holds"
(crew bolt submit north south east > "$T/group.out" 2>&1) &
submitter=$!
until_ok queued east || fail "east's landing was not recorded queued:"$'\n'"$(cat "$T/group.out")"
rm "$T/sluice-wait-holds"
wait "$submitter" && fail "expected failure: crew bolt submit north south east"$'\n'"$(cat "$T/group.out")"
out=$(cat "$T/group.out")
# the landings' waiters on the box end once each has read its landing, so none levels the kit's main checkout after
waiters_gone() { ! pgrep -f -- "_landing-read.*$k" >/dev/null; }
until_ok waiters_gone || fail "the group's landing waiters outlived their reads"
has "$out" "south did not land, as said above; north and east landed"
eq "$(calls | grep "^$box wt submit " | sed 's/.* from //; s/ as .*//; s/.*land-//')" $'north\nsouth\neast'
has "$out" "bolt/north landed on switchboard-kit's main at"
has "$out" "bolt/south did not land: sluice refused it or found a conflict; switchboard-kit's main moved to"
has "$out" "bolt/east landed on switchboard-kit's main at"
eq "$(plan -t Bolt -e "Bolt = 'north' || Bolt = 'east'" -c) $(plan -t Bolt -e "Bolt = 'south'" -c)" "0 1"
eq "$(field $box bolt.submit Head bolt/south)" "$south"
has "$(field $box bolt.submit Refused bolt/south)" " conflict: regions.txt"
st=$(git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request -e "Act = 'launch' && Work ~ '^fix/south/take-main-'" -P Work)
sm=${st##*-}
eq "$(git -C "$k" rev-parse --short=7 "$sm")" "$sm"
has "$out" "bolt south takes main first: the runner on $box launches fix south--take-main-$sm (request $(request_of "$st")), taking origin/main at $sm into the bolt"
has "$out" "card land/switchboard-kit: $kit is left as it is, the user having answered it"
calls | grep -q "^$box pendingyou \(post\|update\|cancel\)_request " && fail "the answered card was changed though the user's send stands for each bolt it ticked"
has "$out" "bolt/kept-work is removed: main now holds bolt kept-work's tip, and sluice deleted it from GitHub at ${tip:0:7}"
github bolt/kept-work && fail "bolt/kept-work is still on GitHub"
git -C "$k" rev-parse --verify -q bolt/kept-work >/dev/null && fail "bolt/kept-work is still on the host"
ok "one crew bolt submit lands the ticked bolts in the card's order, each queued behind the one before and closed as it lands, the second refused for its conflict, recorded at its head and its take-main fix launched, the third landing all the same; it exits non-zero naming the one held, and the card the user answered is left as it is, their send standing for the bolt taking main in; and the landings' sweep has sluice delete the dropped bolt's kept branch, main holding its tip"

# The send stands for south's work (record 0031 as amended 2026-10-24): its take-main fix's Flume place merges main
# in, and once that merges south's row can land again on the same send, the card left as it is.
sp=$T/flume/south-take-main
flume_place "$sp" "$st" south
git -C "$sp" merge -q origin/main >/dev/null 2>&1 && fail "taking main into south did not stop on regions.txt"
printf 'north-regions\nsouth-regions\n' > "$sp/regions.txt"; git -C "$sp" add regions.txt
GIT_EDITOR=true git -C "$sp" commit -q --no-edit || fail "the merge of main into south did not commit"
merge_as flume "$sp" bolt/south || fail "south's take-main submission failed"
landed "$sp" "$st" south
[[ $(git -C "$k" rev-parse origin/bolt/south) != "$south" ]] || fail "south's head did not move with its fix's merge"
: > "$CREW_TEST_LOG"
expect_ok on_box _land-card wldn switchboard-kit
has "$out" "card land/switchboard-kit: $kit is left as it is, the user having answered it"
calls | grep -q "^$box pendingyou \(post\|update\|cancel\)_request " && fail "a landings card asked for south again though its own work is unchanged"
# Not asserted: crew card read prints a submit naming bolts already landed while south takes main by a fix (a defect).
# Ops's session ended while its crew bolt submit south waited on the landing, #90, still queued on main at south's head
# (bolt-teams "Ops restarted while its landing stood"): run again, it reads sluice's queue, submits nothing and waits on
# #90 again, and once sluice lands it south is landed and closed as any landing is, the card closed with what its send
# landed.
sh=$(git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse bolt/south)
jq -n --arg h "$sh" '{schema: "sluice/overview@1", at: "2026-10-28T16:00:00Z", host: "chuck-herdr-alpha", hosts: [], previews: [],
  sessions: [], repository: "/kit/.git", branches: [{branch: "main", submissions: [{schema: "sluice/submission@1", id: 90,
  branch: "main", head: $h, state: "queued", from: {agent: "wldn-ops", worktree: "pull/9", head: "bolt/south"}}]}]}' \
  > "$CREW_TEST_ROOT/sluice-overview.json"
echo "$kd/places/land-south" > "$CREW_TEST_ROOT/sluice-stands-90"
: > "$CREW_TEST_LOG"
expect_ok crew bolt submit south
rm "$CREW_TEST_ROOT/sluice-overview.json"
has "$out" "bolt/south's landing #90 stands in sluice at ${sh:0:7}, its head: crew waits on #90 again and submits nothing"
grep -q "^$box wt submit main" "$CREW_TEST_LOG" && fail "crew submitted south again though its landing stood in sluice:"$'\n'"$(calls)"
[[ ! -e $CREW_TEST_ROOT/sluice-stands-90 ]] || fail "crew's wait on #90 again did not reach sluice"
has "$out" "bolt/south landed on switchboard-kit's main at"
eq "$(plan -t Bolt -e "Bolt = 'south'" -c)" "0"
eq "$(field $box bolt.land Repo bolt/south)" "switchboard-kit"
has "$out" "card land/switchboard-kit: $kit closed"
has "$(calls | grep "^$box pendingyou ack_answer ")" "\"outcome\": \"Landed on GitHub's main: north at"
closed=$(field $box card.close Outcome kit/switchboard-kit)  # whole in the run record, cut on the card
has "$closed" ", south at $(git -C "$k" rev-parse --short=7 origin/main) and east at"
case $closed in *"words above"*) fail "the card's close points at words above, which are in ops's terminal, not on the card" ;; esac
calls | grep -q "^$box pendingyou post_request " && fail "a landings card was posted for south's landing"
ok "a ticked bolt taking main in keeps the user's send through its take-main fix, no card asking for it again, and crew bolt submit of it, run again after its landing stood in sluice, waits on that landing again, submitting nothing, lands it and closes the card with what its send landed"

# Main moving under a proven row: GitHub's main lands a change to the file far's chore added, and the builder's host
# has it as origin/main, as the fleet's timer fetches it; crew rail on the main level's host, the partition's main
# machine, raises the kit's landings card again, which forecasts far against main after a fetch, holds far taking main
# first, so a list of two becomes an approval of west alone, followed; a second crew rail, main not having moved,
# raises nothing.
crew bolt new west "The west regions." --repo switchboard-kit >/dev/null
crew chore add west-files "West's files." --bolt west >/dev/null; crew bolt give swb-1 west >/dev/null 2>&1
flume_lands $box chore west-files west west.txt
crew bolt new far "The far regions." --repo switchboard-kit >/dev/null
crew chore add far-files "Far's files." --bolt far >/dev/null; crew bolt give swb-1 far >/dev/null 2>&1
flume_lands $box chore far-files far far.txt
expect_ok on_box _land-card wldn switchboard-kit
kit=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $kit ]] || fail "no landings card was raised for west and far:"$'\n'"$out"
kept=$(home_of $box)/.local/state/crew/cards/wldn/land/switchboard-kit/main
eq "$(cat "$kept")" "$(git -C "$k" rev-parse origin/main)"
was=$(cat "$kept")
echo "main's far" > "$k/far.txt"; commit_all "$k" "feat: main's own far"; push "$k"
: > "$CREW_TEST_LOG"
expect_ok on_box rail --label wldn
has "$out" "land/switchboard-kit (wldn): main is at $(short origin/main), its rows forecast at ${was:0:7}: raised again"
eq "$(cat "$kept")" "$(git -C "$k" rev-parse origin/main)"
has "$(calls | grep "^$box pendingyou cancel_request ")" "far takes main first: forecast to conflict with main on far.txt at $(short origin/main)"
posted=$(calls | grep "^$box pendingyou post_request " | tail -1)
eq "$(jq -c '[.kind, .follows, .title]' <<<"${posted#* post_request }")" "[\"approve\",\"$kit\",\"Land the bolt west on switchboard-kit's main\"]"
has "$posted" "**far**: takes main first: forecast to conflict with main on far.txt at $(short origin/main)"
: > "$CREW_TEST_LOG"
expect_ok on_box rail --label wldn
lacks "$out" "landings cards forecast again"
calls | grep -q "^$box pendingyou \(post\|update\|cancel\)_request " && fail "a second rail read changed the landings card:"$'\n'"$(calls)"
ok "main moving under a proven row makes crew rail on the main level's host raise the kit's landings card again, holding the row taking main first; a second crew rail raises nothing"

# A bolt the user left: near joins west on a card of two boxes, and the user sends it ticking none, which ops's crew
# card read acts on at once, closing it and following it with both rows unticked as left, the set recorded. Main then
# lands a change to the file west's chore added: crew rail's raise keeps west's box, changes the waiting card in place
# saying it would take main first, and records the forecast as found while left. The user ticks west on the card that
# follows: crew card read leaves west out of the command that lands, saying it takes main first, its send standing.
crew bolt new near "The near regions." --repo switchboard-kit >/dev/null
crew chore add near-files "Near's files." --bolt near >/dev/null; crew bolt give swb-2 near >/dev/null 2>&1
flume_lands $box chore near-files near near.txt
expect_ok on_box _land-card wldn switchboard-kit
two=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | tail -1 | cut -d' ' -f3)
eq "$(field $box card.post Heads kit/switchboard-kit)" "west@$(short origin/bolt/west) near@$(short origin/bolt/near)"
echo '{"answer": {"choiceIds": []}}' > "$(home_of $box)/.stub-pendingyou/answered/$two.json"
out=$(ops card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
has "$out" "no bolt ticked: nothing lands"
eq "$(field $box landing.left Heads kit/switchboard-kit)" "west@$(short origin/bolt/west) near@$(short origin/bolt/near)"
eq "$(field $box card.post Heads kit/switchboard-kit)" "west@$(short origin/bolt/west):left near@$(short origin/bolt/near):left"
left=$(field $box card.post Card kit/switchboard-kit)
[[ $left != "$two" ]] || fail "no card followed the send that left west and near"
echo "main's west" > "$k/west.txt"; commit_all "$k" "feat: main's own west"; push "$k"
: > "$CREW_TEST_LOG"
expect_ok on_box rail --label wldn
changed=$(calls | grep "^$box pendingyou update_request ")
has "$changed" "\"changeNote\": \"west, which you left, would take main first: forecast to conflict with main on west.txt at $(short origin/main)\""
has "$changed" "It would take main first if you tick it: forecast to conflict with main on west.txt"
eq "$(jq -c '.recommendedIds' <<<"${changed#* update_request }")" "[]"
eq "$(field $box forecast Heads bolt/west) | $(field $box forecast Reached bolt/west)" "bolt/west@$(short origin/bolt/west) main@$(short origin/main) | left"
echo '{"answer": {"choiceIds": ["land:west"]}}' > "$(home_of $box)/.stub-pendingyou/answered/$left.json"
: > "$CREW_TEST_LOG"
out=$(ops card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
has "$out" "west takes main first: its team takes main in by a fix, and the user's send stands for it"
lacks "$out" "crew bolt submit"
eq "$(field $box landing.left Heads kit/switchboard-kit)" "near@$(short origin/bolt/near)"
ok "a bolt the user left keeps its box when main moves under it, the card saying it would take main first and the forecast recorded as found while left; a send ticking it, read by ops, submits nothing of it"

# No agent started all along: every team's work ran in Flume places.
eq "$(launches)" ""
# This run's end stops its own landings' submitters and nothing of another run's on the host.
decoy
leave
spared "this run's end"
ok "the test's end stops its own landings' submitters and none of another run's beside it on the host"
