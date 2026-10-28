# A bolt landed through sluice, through the crew command on the stubs (tests.11, record 0022), a part of the units
# journey (t-journey-units): no unit starts on a bolt while its landing is in flight; a unit merges into the bolt by a
# submission, and crew bolts reads the bolt's verification from sluice's verdict on it; crew bolt submit lands the
# bolt by a submission to main from a short-lived worktree, naming a conflict for the team and moving nothing, its
# pull request into main, in a kit whose main takes pull requests, left a draft and said so (bolt-teams); a fix
# takes main into the bolt by a submission to the bolt, and its merge's end raises the kit's landings card, keyed by
# the kit, in main-level ops's name on the partition's main machine, the bolt its one row, with the row's reading of
# what the bolt brings to main started first on the team's host, tried a second time when its first start fails, and
# linked from it, which crew card session gives again, and the address of a preview of its head, which the
# kit's policy there declares, asked of sluice first; the preview's stack failing is said on the card, changed in
# place by the process that waited on it; a fix started on the bolt holds its row, so the card, with no row left that
# can land, is withdrawn naming it, the row's reading ended and its preview released, its pull request, ready again,
# drafted, and once the fix merges and the bolt reads proven again, the dispatcher told its team is free for its next
# bolt, a new card is posted, following nothing, with a preview of the new head, raised without its reading when both
# its starts fail, naming crew card session and keeping why in the run record, whose reading the conductor's read
# finds not running and its crew card session then starts, changing the card to carry its link, until the landing
# ends it; the bolt read proven, its team
# is given its next bolt beside it and refused a third (teams.16); on the user's send a landing whose checks the host
# could not run takes up the place a stopped landing left on the bolt's branch, levels the host's copy, which the
# fix's merge sluice landed on GitHub left behind, to GitHub's head first and says so (plan.19), and is stopped, nothing
# of the bolt's, recorded with no refusal, its row keeping its box, the card the user answered left as it is and crew
# card read naming it with what stopped it beside the command that lands it; once the host runs them, the next
# submission on the same send readies the bolt's pull request and lands it at GitHub's head, sluice answering with the
# pull request and crew waiting on the submission it made from it, leaving the kit's detached main
# checkout as it was, and closes it as it lands, recording the commit main holds, sluice deleting its branch from GitHub
# (plan.19), the kit's landings card closed with where GitHub's main holds it, the row's reading ended and its preview
# released, and its conductor told, the team still building its other bolt, whose branch its conductor carries; once
# that bolt is dropped too the team holds none and its conductor and ops start again at their next stop without it;
# a bolt landed with a chore of its own still at ready has its close refused, said by the landing and recorded once,
# in main-level ops's name, though the waiter's read and the submission's own each tried it, and its head line on the
# board says it landed on main and was not closed, in those words; once the planner drops the chore, the team's read
# that follows closes it, its branch, holding a commit main lacks after the landing, kept on GitHub, sluice refusing
# its delete, and on the host, named, its mark unset and the keeping recorded, and the team's next read leaves it; a
# landing outlives the crew bolt submit that queued it (plan.21): killed once sluice has queued the landing, its waiter
# on the team's host calls sluice wait again while sluice is undecided, then reads the landing from sluice's record,
# recording it landed and closing the bolt, and with the waiter stopped too, the conductor's next command reads and
# closes it; a bolt no team holds lands once
# its unit's change is on main; a delete sluice refuses is named in its words, the branch kept on GitHub; a bolt made
# before gives went through sluice is deleted there once its landing's pull request put it there, no create run for
# it; and dropping a held bolt removes its places and has sluice delete its branch, which holding a merge main lacks
# is kept on GitHub and the host, marked, named and recorded, the team's next read leaving it, until a landing brings
# its tip into main and the next read has sluice delete it. Then two bolts of one kit proven at once are one landings
# card of two boxes in the plan's order, the lower forecast to conflict with the one above, changed in place when a
# head moves and when a third joins it; and one crew bolt submit lands the three the user ticked in that order, each
# queued behind the one before and closed as it lands, the second refused for its conflict, recorded at its head and
# held, the third landing all the same, the command exiting non-zero naming the held one, and the card closed with
# what landed and what was held, keeping the user's send for the held one; its team's fix takes main into it, and once
# that merges no card asks for it, ops reads it under the earlier send with no card open, and the command that read
# prints lands it on that send (record 0031 as amended 2026-10-24), run again after its landing stood in sluice when
# ops's session ended, so it waits on that landing again and submits nothing (bolt-teams).
# Last, main moving under a proven row makes crew rail on the main level's host raise the kit's landings card again,
# holding the row taking main first and telling its conductor the take-main fix, recorded once, and a second crew
# rail, main not having moved, tells and raises nothing. And a bolt the user left on a send: main moving under it keeps
# its row's box, the card changed in place saying it would take main first, and tells its conductor nothing; a send
# ticking it, read by crew card read, tells the take-main fix and submits nothing of it (rail-cards, bolt-teams).
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ plugin/lib/board.py tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abe"]; unit("c", "console-pages")
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
# a's change archived and merged into the bolt by its submission, as its merge stage runs it, its place and branch
# gone; b built in a slot; c placed in console-pages. The bolt and main each change the title.
pa=$(place "$k" tenant-environments a); change "$pa" a 1 1; commit_all "$pa" "feat(a): its change, done"
# The kit's policy, as the bolt holds it, declares a preview with one address.
printf '\n[preview]\ncommand = ["sh", "-c", "true"]\n\n[preview.addresses]\nweb = "http://{name.web}"\n' >> "$pa/.config/sluice.toml"
commit_all "$pa" "chore: the kit declares a preview"
echo "# switchboard-kit, the bolt's" > "$pa/README.md"; commit_all "$pa" "docs(a): the bolt's title"
mkdir -p "$pa/openspec/changes/archive"; git -C "$pa" mv openspec/changes/a openspec/changes/archive/2026-10-13-a
git -C "$pa" commit -qm "docs(openspec): archive a"
merge_as swb-1-unit-1 "$pa" bolt/tenant-environments || fail "a's submission failed"
git -C "$k" worktree remove "$pa"; git -C "$k" branch -qD unit/a
# While the bolt's landing is in flight, its worktree standing with LANDING's process alive in it, no unit starts on it.
land=$kd/places/land-tenant-environments
git -C "$k" worktree add -q "$land" bolt/tenant-environments
echo $$ > "$(git -C "$land" rev-parse --absolute-git-dir)/crew-landing"
export CREW_AGENT=swb-1-conductor
expect_fail "bolt tenant-environments's landing is queued in sluice, submitted from $land: unit b's construct starts once it has landed or been refused" \
  crew unit run b construct
[[ ! -e $kd/places/b ]] || fail "a place was made for b while the landing was queued"
: > "$(git -C "$land" rev-parse --absolute-git-dir)/crew-landing"  # sluice's outcome is in
crew unit run b construct >/dev/null
unset CREW_AGENT
git -C "$k" worktree remove "$land"
ok "no unit starts on a bolt while its landing is in flight, and one starts once the outcome is in though the landing's worktree stands"
crew bolt give swb-2 console-pages >/dev/null 2>&1; place "$k" console-pages c >/dev/null
echo "# switchboard-kit, main's" > "$k/README.md"
# From here main takes pull requests, as crew's own does: a landing opens one from the bolt's branch (bolt-teams).
rewrite "$k/.config/sluice.toml" '/^\[branches.main\]$/,/^remote/ s/^remote = "origin"$/&\n\n[branches.main.pull_requests]\nreviews = 0/'
commit_all "$k" "docs: main's title, and main takes pull requests"; push "$k"
expect_ok crew bolts --label wldn
has "$out" "verification: green, sluice's verdict on its last landing, $(short bolt/tenant-environments): passed (stub)"
ok "a unit merges into the bolt by a submission, and crew bolts reads the bolt's verification from sluice's verdict on it"

# The bolt lands once its units have: b and e are dropped, and the bolt submitted to main, which conflicts on the title.
expect_fail "unit a has not landed on main: it is merged" crew bolt land tenant-environments
by_hand 'p.remove(p.unit("e"))'
expect_ok crew unit drop b "folded into a"
has "$out" "swb-1-unit-1 is free: b was dropped from the plan"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
main_before=$(git -C "$k" rev-parse main)
gh_repo=WilldanGroup/switchboard-kit
pr=$(pull $gh_repo bolt/tenant-environments false)  # the pull request sluice's submission opens, ready for review
: > "$CREW_TEST_LOG"
expect_fail "bolt/tenant-environments did not land: sluice refused it or found a conflict, and main is where it was" crew bolt submit tenant-environments
has "$out" "sluice's verdict: #"; has "$out" " conflict: README.md. Tell the bolt's conductor why"
eq "$(calls | grep "^$box wt submit ")" "$box wt submit main --no-wait --json --no-remove from $land as $me@mac-studio"
has "$out" "tenant-environments did not land, as said above; none landed"
eq "$(git -C "$k" rev-parse main)" "$main_before"
[[ ! -e $land ]] || fail "the landing's worktree is still there"
has "$out" "Its pull request https://github.com/$gh_repo/pull/$pr is a draft, so no merge into bolt/tenant-environments lands it; the next crew bolt submit tenant-environments, on the user's word, makes it live again."
eq "$(drafted "$pr")" true
eq "$(calls | grep -A100 "^$box wt submit " | grep -c "^$box gh pr ready $pr -R $gh_repo --undo$")" 1
ok "crew bolt submit lands a bolt by a submission to main from a short-lived worktree, and a conflict lands nothing, is named for the team and leaves its pull request a draft, said with its link"

# The team takes main into the bolt: a fix merges main in its place, resolving the title, and submits to the bolt.
# The team's host gives a plannotator session a link on its tailnet name, as swancloud sets it.
export PLANNOTATOR_URL_HOST=auto PLANNOTATOR_PORT=19432-19451
unset PLANNOTATOR_SKIP_BROWSER_OPEN PLANNOTATOR_REMOTE
reading=$(home_of $box)/.local/state/crew/cards/wldn/land/tenant-environments
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
tm=fix/tenant-environments/take-main tmp=$kd/places/fix-tenant-environments--take-main
export CREW_AGENT=swb-1-conductor
expect_ok crew fix swb-1 take-main "Take main into the bolt: the landing conflicts on README.md."
git -C "$tmp" merge -q main >/dev/null 2>&1 && fail "taking main did not stop on the title"
echo "# switchboard-kit, main's and the bolt's" > "$tmp/README.md"; git -C "$tmp" add README.md
GIT_EDITOR=true git -C "$tmp" commit -q --no-edit || fail "the merge of main did not commit"
expect_ok crew fix swb-1 take-main --wait
expect_ok crew fix swb-1 take-main --merge
merge_as swb-1-unit-1 "$tmp" bolt/tenant-environments || fail "the fix's submission failed"
: > "$CREW_TEST_LOG"
touch "$CREW_TEST_ROOT/sluice-preview-holds"  # the preview's stack takes its time to come up
refusals=$(home_of $box)/.stub-plannotator/refuse-starts
mkdir -p "${refusals%/*}"; echo 1 > "$refusals"  # the reading's first start fails
expect_ok crew fix swb-1 take-main --wait
has "$out" "delivered merge of $tm: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
# The merge's end finds the bolt proven, and raises the kit's landings card in main-level ops's name on the
# partition's main machine, keyed by the kit, the bolt its one row, with a preview of its head asked of sluice first,
# once, in the kit's main checkout on the team's host, and its address listed.
card=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $card ]] || fail "the merge's end raised no landings card:"$'\n'"$out"
has "$out" "call get_request (requestId $card, name wldn-ops)"
posted=$(calls | grep "^$box pendingyou post_request ")
has "$posted" '"idempotencyKey": "land/switchboard-kit@wldn"'
has "$posted" '"label": "wldn-ops"'
has "$posted" "\"title\": \"Land the bolt tenant-environments on switchboard-kit's main\""
h1=$(git -C "$k" rev-parse bolt/tenant-environments)
eq "$(calls | grep "^$box sluice preview ")" "$box sluice preview bolt/tenant-environments $h1 --wait --json in $(cd "$k" && pwd -P)"
has "$posted" "Try it running: a preview of ${h1:0:7} sluice brings up, at these addresses once it is up."
has "$posted" "web: http://web-${h1:0:7}--bolt-tenant-environments--kit"
ok "a fix takes main into the bolt by a submission to the bolt, and the merge's end raises the kit's landings card in main-level ops's name once the bolt reads proven, keyed by the kit, printing the line that adopts it, with the address of a preview of its head asked of sluice first"

# The landing card's reading, started with it on the team's host: one session on the head's folder, the bolt's page
# first and its diff against main last, its link on the card, and crew card session giving it again.
url=$(jq -r .url "$reading/session.json"); pid=$(jq -r .pid "$reading/session.json")
[[ $url =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "the landing's reading is not on the box's tailnet name: $url"
eq "$(listed)" "$pid"
eq "$(cat "$refusals")" "0"
has "$out" "card land/tenant-environments: its reading could not be opened on the tailnet: plannotator ended before land/tenant-environments's session was ready: stub: refused to start; crew fetches switchboard-kit's main and tries once more"
lacks "$(field $box card.post Unread kit/switchboard-kit)" "refused"
folder=$(cd "$reading/$(git -C "$k" rev-parse --short=7 bolt/tenant-environments)" && pwd -P)
eq "$(jq -r '.argv | map(select(startswith("/") and (endswith("/result.json") | not))) | map(sub(".*/"; "")) | join(" ")' \
  "$(home_of $box)/.stub-plannotator/$pid.json")" \
  "00-tenant-environments.md 01-a-proposal.md 01-a-design.md 01-a-specs-x-spec.md 01-a-tasks.md 02-tenant-environments-diff.txt"
eq "$(jq -r '.argv[1]' "$(home_of $box)/.stub-plannotator/$pid.json")" "$folder/00-tenant-environments.md"
has "$(cat "$folder/02-tenant-environments-diff.txt")" "+# switchboard-kit, main's and the bolt's"
lacks "$(cat "$folder/02-tenant-environments-diff.txt")" "openspec/changes"
has "$(calls | grep "^$box pendingyou post_request " | tail -1)" "\"url\": \"$url\""
on_box() { HOST=$box crew "$@"; }
expect_ok on_box card session land/tenant-environments
eq "$out" "$url"; eq "$(listed)" "$pid"
ok "the landing card's reading is started with it on the team's host, a second time when its first start fails, the bolt's page, each unit's change and the bolt's diff against main as one review, its link on the card, and crew card session gives it again, starting nothing"

# The preview's stack fails: the process crew handed the ask to changes the card in place while it waits on the user.
previews=$(home_of $box)/.local/state/crew/previews/wldn
touch "$CREW_TEST_ROOT/sluice-preview-fails"; rm "$CREW_TEST_ROOT/sluice-preview-holds"
until_ok grep -q "^card land/switchboard-kit: $card changed" "$previews/tenant-environments.log" ||
  fail "the card was not changed for its preview's end:"$'\n'"$(cat "$previews/tenant-environments.log")"
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"changeNote\": \"tenant-environments: Its preview of ${h1:0:7} did not come up\""
has "$changed" "A preview of ${h1:0:7} was asked for and is not there: starting web / stub: the preview command failed: web did not come up."
lacks "$changed" "web: http://"
rm "$CREW_TEST_ROOT/sluice-preview-fails"
ok "a preview whose stack fails is said on the card, changed in place while it waits on the user"

# A defect noted on the card: a fix started on the bolt holds its row, ending its reading and releasing its preview,
# its ready pull request drafted, and the card, with no row left that can land, is withdrawn naming the fix's words;
# once the fix merges and the bolt reads proven again, the merge's end raises a new card, following nothing, with a new
# reading and a preview of the new head.
as $box gh pr ready "$pr" -R $gh_repo 2>/dev/null  # ready again, as a refused landing crew could not draft leaves it
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 gap "The zone list misses one zone."
has "$out" "card land/switchboard-kit: $card withdrawn"
has "$out" "Its pull request https://github.com/$gh_repo/pull/$pr is a draft, so no merge into bolt/tenant-environments lands it"
eq "$(drafted "$pr")" true
has "$out" "ended land/tenant-environments's session, plannotator pid $pid"
has "$out" "released land/tenant-environments's preview of ${h1:0:7}"
ended "$pid"; eq "$(listed)" ""
has "$(calls | grep "^$box pendingyou cancel_request ")" '"reason": "every bolt waiting to land is held: tenant-environments, held for a fix: The zone list misses one zone. (fix/tenant-environments/gap)"'
eq "$(calls | grep "^$box sluice release " | grep -vc " --worktree ")" "1"
gp=$kd/places/fix-tenant-environments--gap
echo four >> "$gp/shared.txt"; commit_all "$gp" "fix(a): the zone list holds every zone"
expect_ok crew fix swb-1 gap --wait
expect_ok crew fix swb-1 gap --merge
# sluice lands the gap fix on GitHub's bolt pushing as its app, leaving the host's copy without its merge (plan.19).
lag=$(git -C "$k" rev-parse bolt/tenant-environments)
touch "$T/sluice-leaves-copy"
merge_as swb-1-unit-1 "$gp" bolt/tenant-environments || fail "the gap fix's submission failed"
rm "$T/sluice-leaves-copy"
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$lag"
(unset CREW_AGENT; crew bolt new ssh-fix "Hosts reach each other over ssh." --repo switchboard-kit >/dev/null)  # swb-1's next
p=$(as $box herdr --session wldn-3 workspace create --cwd / --label "wldn dispatch" | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-3 stub agent "$p" wldn-dispatch-chuck-herdr-alpha
: > "$CREW_TEST_LOG"
echo 2 > "$refusals"  # both of the reading's starts fail
expect_ok crew fix swb-1 gap --wait
again=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $again && $again != "$card" ]] || fail "the landings card was not raised again:"$'\n'"$out"
h2=$(git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse bolt/tenant-environments)  # GitHub's, where it lives
git -C "$k" merge-base --is-ancestor "$h2" "$lag" && fail "the host's copy holds the gap fix's merge"
posted=$(calls | grep "^$box pendingyou post_request " | tail -1)
lacks "$posted" '"follows"'
refused="plannotator ended before land/tenant-environments's session was ready: stub: refused to start"
has "$posted" "Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and swb-1-conductor starts it with crew card session land/tenant-environments; this card then carries its link."
has "$posted" "The reading could not be opened on the tailnet: $refused"
has "$out" "card land/tenant-environments: its reading could not be opened on the tailnet: $refused; crew card session land/tenant-environments starts it"
[[ ! -e $reading/session.json ]] || fail "a reading is recorded though both its starts failed"
eq "$(listed)" ""; eq "$(cat "$refusals")" "0"
eq "$(field $box card.post Card kit/switchboard-kit) $(field $box card.post Unread kit/switchboard-kit)" "$again $refused"
has "$posted" "web: http://web-${h2:0:7}--bolt-tenant-environments--kit"
eq "$(calls | grep "^$box sluice preview ")" "$box sluice preview bolt/tenant-environments $h2 --wait --json in $(cd "$k" && pwd -P)"
# The merge that makes the bolt proven frees its team for its next bolt, planned for it: the dispatcher is told (teams.16).
has "$(grep "^$box wldn-3 agent prompt wldn-dispatch-chuck-herdr-alpha " "$CREW_TEST_LOG")" \
  "swb-1 can take its next bolt: bolt tenant-environments reads proven. Give a free team its next bolt."
ok "a fix started on the bolt drafts its ready pull request and holds its row, ending its reading and releasing its preview, the card withdrawn with no row left that can land, and once the fix merges a new card is posted with a preview of the new head, raised without its row's reading when both its starts fail, naming crew card session, and why is kept in the box's run record; the merge tells the dispatcher its team is free for its next bolt"

# The conductor's read finds no reading running, and its crew card session starts it, changing the card to carry its
# link; the reading runs until the landing's close ends it, with nothing of crew's waiting on it.
HOST=$box expect_ok crew card read land/tenant-environments
eq "$out" "land/tenant-environments: no reading of it runs on this host: crew card session land/tenant-environments starts it"
HOST=$box expect_ok crew card session land/tenant-environments
pid2=$(jq -r .pid "$reading/session.json"); url2=$(jq -r .url "$reading/session.json")
eq "$(head -1 <<<"$out")" "$url2"
[[ $pid2 != "$pid" ]] || fail "the landing card raised again has its old reading"
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"requestId\": \"$again\""; has "$changed" "\"changeNote\": \"tenant-environments: Its reading is open again at a new link\""; has "$changed" "$url2"
eq "$(listed)" "$pid2"
HOST=$box expect_ok crew card read land/tenant-environments
eq "$out" "land/tenant-environments: its reading waits on the user, who has sent nothing from it"
ok "the conductor's read of its bolt's row with no reading says so, and its crew card session starts it, prints its link and changes the kit's card to carry it"
unset CREW_AGENT

# The bolt reads proven, so its team is free for its next bolt while it waits to land (teams.16): the give hands swb-1
# ssh-fix beside it, and a third is refused, naming the bolt whose landing frees the team.
: > "$CREW_TEST_LOG"
expect_ok crew bolt give swb-1
has "$out" "swb-1 holds ssh-fix: sluice made bolt/ssh-fix on GitHub (origin) from switchboard-kit's main at"
given=$out
expect_ok crew bolts --label wldn
eq "$(grep -c "  swb-1 @ $box  " <<<"$out")" "2"
has "$out" "tenant-environments  switchboard-kit  swb-1 @ $box  waits"
expect_ok crew status swb-1
has "$out" "swb-1 builds ssh-fix; tenant-environments waits to land"
crew bolt new third-one "The bolt after." --repo switchboard-kit >/dev/null
expect_fail "swb-1 holds tenant-environments and ssh-fix; tenant-environments waits to land, and its landing frees swb-1" crew bolt give swb-1
ok "a team whose bolt reads proven is given its next bolt beside it, and a third is refused, naming the bolt whose landing frees the team"

# The give restarts neither the conductor, which waits on its bolt's reading, nor ops at once: each starts again at its
# next stop, once idle, the conductor fresh and greeted with both bolts and the waiting one's row on the kit's card.
has "$given" "swb-1-conductor and swb-1-ops start again on bolt/ssh-fix at their next stop"
lacks "$given" "swb-1-conductor started"
for a in swb-1-conductor swb-1-ops; do
  log=$(home_of $box)/.local/state/crew/renew/$a.log
  until_ok grep -q "$a is restarted on crew" "$log" || fail "$a was not restarted at its next stop: $(cat "$log" 2>/dev/null)"
  eq "$(as $box herdr --session wldn-1 agent get "$a" | jq -r .result.agent.name)" "$a"  # found under its name at once, as crew restart leaves it
done
greeted=$(calls | grep "^$box wldn-1 agent prompt swb-1-conductor '\[crew\] crew restarted you")
has "$greeted" "bolt is now bolt/ssh-fix, which sluice"
has "$greeted" "Your team now builds the bolt ssh-fix. Bolt tenant-environments waits to land, a row of switchboard-kit"  # the log quotes each '
has "$greeted" "crew card read land/tenant-environments then gives its notes"
lacks "$greeted" "card wait"
lacks "$greeted" "get_request"
eq "$(jq -r 'select(.agent == "swb-1-conductor") | .branch' "$CREW_TEST_CLAUDE_LOG" | tail -1)" "bolt/ssh-fix"
ok "a give beside a waiting bolt restarts its conductor and ops at their next stop, the conductor greeted with both bolts and the waiting one's row"
# The user approves the landings card raised again, and main-level ops submits the bolt: it lands, the kit's detached main
# checkout left as it was, and is closed as it lands. A landing stopped before it removed its worktree left one on the
# bolt's branch, its process gone, which the submission takes up and removes.
mkdir -p "$(home_of $box)/.stub-pendingyou/answered"
echo '{"answer": {"approved": true}}' > "$(home_of $box)/.stub-pendingyou/answered/$again.json"
git -C "$k" worktree add -q "$land" bolt/tenant-environments
sh -c 'echo $$' > "$(git -C "$land" rev-parse --absolute-git-dir)/crew-landing"
git -C "$k" switch -q --detach  # the kit's main checkout as the anchor the fleet's timer moves (plan.18)
# The branch the conductor's pane tells sluice's plugins it works for (teams.20), "none" when it carries none.
branch() { herdr_state $box wldn-1 ".panes[\"$(awk '$1=="conductor"{print $2}' "$(home_of $box)/.local/state/swb-1-team/panes")\"].tokens.sluice_branch // \"none\""; }
eq "$(branch)" "bolt/ssh-fix"
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
out=$(export CREW_AGENT=wldn-ops; HOST=$box crew card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
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
# Recorded queued where it was submitted, and its outcome where it was read, the team's host (plan.21).
eq "$(field mac-studio bolt.submit Outcome bolt/tenant-environments) $(field mac-studio bolt.submit Head bolt/tenant-environments)" "queued $bolt_tip"
n=$(field mac-studio bolt.submit Submission bolt/tenant-environments)
eq "$(field $box bolt.submit Outcome bolt/tenant-environments) $(field $box bolt.submit Submission bolt/tenant-environments) $(field $box bolt.submit Head bolt/tenant-environments)" \
  "landed $n $bolt_tip"
git -C "$k" switch -q main  # the timer's move, for the steps below that commit on the kit's main
has "$out" "tenant-environments has landed at switchboard-kit's $(git -C "$k" rev-parse --short=7 main); swb-1 builds ssh-fix"
# The branch the conductor carries is the bolt it builds, so the landing makes no restart due.
eq "$(branch)" "bolt/ssh-fix"
eq "$(jq -r 'select(.agent == "swb-1-conductor") | .branch' "$CREW_TEST_CLAUDE_LOG" | tail -1)" "bolt/ssh-fix"
has "$(calls | grep "^$box pendingyou ack_answer ")" "\"outcome\": \"Landed on GitHub's main: tenant-environments at $(short main); every host's folder follows by swancloud's timer within minutes.\""
has "$out" "card land/switchboard-kit: $again closed"
has "$out" "released land/tenant-environments's preview of ${h2:0:7}"
eq "$(ls "$CREW_TEST_ROOT/sluice-previews")" ""
has "$out" "ended land/tenant-environments's session, plannotator pid $pid2"
ended "$pid2"; eq "$(listed)" ""
[[ ! -e $reading ]] || fail "the landing's reading outlived its card"
has "$out" "sluice deleted bolt/tenant-environments from GitHub at $tip"
git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still on GitHub"
eq "$(git -C "$k" config branch.bolt/tenant-environments.crew || true)" ""
grep -qF "agent prompt swb-1-conductor '[crew] plan(tenant-environments): land the bolt ($me@mac-studio)'" \
  "$CREW_TEST_LOG" || fail "the conductor was not told of the landing:"$'\n'"$(calls)"
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -c)" "0"
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still there"
eq "$(field $box bolt.land On bolt/tenant-environments) $(field $box bolt.land Commit bolt/tenant-environments)" "bolt/tenant-environments unit/a WilldanGroup/crew-state@$(act_tip)"
eq "$(field $box bolt.land Repo bolt/tenant-environments) $(field $box bolt.land Head bolt/tenant-environments)" "switchboard-kit $(git -C "$k" rev-parse main)"
eq "$(field $box bolt.land By bolt/tenant-environments)" "wldn-ops"  # closed by the landing's read in main-level ops's name
# The stub's record of a submission keeps no time it was submitted or told, so the bolt's age and split can't be told
# and the entry carries neither, the landing going on (run-record "sluice's record can't be read at the landing").
eq "$(field $box bolt.land Age bolt/tenant-environments)$(field $box bolt.land Split bolt/tenant-environments)" ""
ok "a drop frees the last slot and closes the units workspace; the bolt, submitted again on the user's word once its checks can run, lands at GitHub's head, its worktree removed and the detached main checkout left as it was, and is closed as it lands, recording the commit main holds, sluice deleting its branch from GitHub and the host, closing the kit's landings card with where GitHub's main holds it and the timer, ending its row's reading and releasing its preview, and its conductor is told, its pane carrying the branch of the bolt its team builds"

# swb-1's other bolt dropped: the team holds none, its pane carries no branch, and each of its conductor and ops, whose
# session carried the bolt's branch, which only a start changes, is restarted at its next stop.
restarted() { cat "$(home_of $box)/.local/state/crew/renew/$1.log" 2>/dev/null | grep -c "$1 is restarted on crew" || true; }
restarted_since() { test "$(restarted "$1")" -gt "$2"; }
before_conductor=$(restarted swb-1-conductor) before_ops=$(restarted swb-1-ops)
: > "$CREW_TEST_LOG"
expect_ok crew bolt drop ssh-fix "folded into the next"
eq "$(branch)" "none"
until_ok restarted_since swb-1-conductor "$before_conductor" || fail "swb-1-conductor was not restarted for its dropped bolt"
until_ok restarted_since swb-1-ops "$before_ops" || fail "swb-1-ops was not restarted for its dropped bolt"
eq "$(jq -r 'select(.agent == "swb-1-conductor") | .branch' "$CREW_TEST_CLAUDE_LOG" | tail -1)" "null"
grep -q "^$box wldn-1 agent prompt swb-1-ops '\[crew\] crew restarted you on crew .*its team no longer holds bolt/ssh-fix" "$CREW_TEST_LOG" ||
  fail "ops was not told why it was restarted:"$'\n'"$(calls)"
ok "a team whose last bolt goes holds none: its pane carries no branch for sluice, and its conductor and ops are restarted at their next stop without it"

# A bolt landed with a chore of its own still at ready (plan.21, plan.8's reading of 2026-10-27): its close is refused,
# said by the landing, and recorded once in main-level ops's name, though the waiter's read and the submission's own
# each tried it; its head line on the board says it landed on main and was not closed, in those words, and a team read
# with the chore still at ready reads nothing more of it.
crew bolt new zone-lists "The zone list grows." --repo switchboard-kit >/dev/null
crew bolt give swb-1 zone-lists >/dev/null
crew chore add tidy-zones "Tidy the zone list." --bolt zone-lists >/dev/null
# on_bolt <bolt> <line> <subject>: a commit on the bolt's branch, pushed as sluice pushes a landing on a bolt on GitHub
on_bolt() { git -C "$k" worktree add -q "$T/$1" "bolt/$1" && echo "$2" >> "$T/$1/zones.txt" &&
  commit_all "$T/$1" "$3" && git -C "$k" worktree remove "$T/$1" && git -C "$k" push -q origin "bolt/$1"; }
on_bolt zone-lists north "feat: the zone list" || fail "the bolt took no commit"
ready="chore tidy-zones has not landed on main: it is ready"
out=$(export CREW_AGENT=wldn-ops; crew bolt submit zone-lists 2>&1) || fail "the landing did not land:"$'\n'"$out"
has "$out" "bolt/zone-lists landed on switchboard-kit's main at"
has "$out" "bolt/zone-lists landed and was not closed: $ready; crew's next read of the bolt closes it once that is mended"
eq "$(git -C "$k" config branch.bolt/zone-lists.crew)" "landed"
eq "$(plan -t Bolt -e "Bolt = 'zone-lists'" -c)" "1"
eq "$(record_of $box | grep -c "^Refused: $ready$")" "1"
eq "$(field $box bolt.land By bolt/zone-lists) | $(field $box bolt.land Refused bolt/zone-lists)" "wldn-ops | $ready"
expect_ok crew board --label wldn
has "$out" "zone-lists  swb-1 on $box  landed on main, not closed: $ready"
has "$out" "bolt zone-lists: it landed on main and was not closed: $ready"
out=$(export CREW_AGENT=swb-1-conductor; crew status swb-1 2>&1) || fail "the team could not be read:"$'\n'"$out"
lacks "$out" "zone-lists landed and was not closed"
eq "$(record_of $box | grep -c "^Refused: $ready$")" "1"
ok "a bolt landed with a chore still at ready has its close refused, said and recorded once in main-level ops's name over the two reads that tried it, and its head line on the board says it landed on main and was not closed, in those words"

# The branch takes a commit after its landing, and the planner drops the chore: the team's read that follows closes the
# bolt, sluice refusing its branch's delete, so it is kept on GitHub and, at its commit, on the host, named, its mark
# unset and the keeping recorded, and the team's next read leaves it.
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
expect_ok crew status swb-1
lacks "$out" "bolt/zone-lists"
eq "$(short bolt/zone-lists)" "$at"
git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q bolt/zone-lists >/dev/null || fail "the refused delete removed bolt/zone-lists from GitHub"
ok "once the planner drops the chore the team's read closes the bolt, its branch, holding a commit main lacks, kept on GitHub, sluice refusing its delete, and at its commit on the host, named, its mark unset and the keeping recorded, and the team's next read leaves it"

# A landing outlives its submitter (plan.21): crew bolt submit is killed once sluice has queued the landing, sluice still
# undecided; the waiter it left on the team's host calls sluice wait again, a call at a time, while it exits 5, and, no
# stage starting on the bolt meanwhile, then reads the landing from sluice's record, records it landed and closes the
# bolt, no one running crew bolt land.
# queued <bolt>: the bolt's landing is recorded queued where it was submitted, and its entry is on the branch, where
# every host reads it (read.5)
queued() { [[ $(field mac-studio bolt.submit Outcome "bolt/$1") == queued ]] &&
  grep -q "^runs(mac-studio): bolt.submit bolt/$1 " <<<"$(git --git-dir "$ws" log --format=%s wldn/main)"; }
# closed <bolt>: the plan holds the bolt no more
closed() { [[ $(plan -t Bolt -e "Bolt = '$1'" -c) == 0 ]]; }
# killed <bolt> <pid>: crew bolt submit of the bolt, run in the background as <pid>, killed with the python it runs
killed() {
  pkill -f "lib/plan.py bolt submit $1\$" || true; wait "$2" 2>/dev/null || true
  until_ok bash -c '! pgrep -f "lib/plan.py bolt submit $1\$" >/dev/null' _ "$1" || fail "crew bolt submit $1 was not stopped"
}
# A test that stops before it lets sluice decide leaves no waiter of its own calling sluice wait.
trap 'rm -f "$T/sluice-wait-holds"; pkill -f "lib/plan.py bolt submit (far|near)-reach\$" || true' EXIT
crew bolt new far-reach "The zones reach far." --repo switchboard-kit >/dev/null
crew bolt give swb-1 far-reach >/dev/null 2>&1
crew unit add far-one "Unit far-one." --bolt far-reach >/dev/null
on_bolt far-reach far "feat: far zones" || fail "the bolt took no commit"
touch "$T/sluice-wait-holds"  # sluice has not decided
(export CREW_AGENT=wldn-ops; crew bolt submit far-reach > "$T/far-reach.out" 2>&1) &
submitter=$!
until_ok queued far-reach || fail "the landing was not recorded queued:"$'\n'"$(cat "$T/far-reach.out")"
killed far-reach "$submitter"
n=$(field mac-studio bolt.submit Submission bolt/far-reach)
far=$kd/places/land-far-reach
waiter=$(cat "$(git -C "$far" rev-parse --absolute-git-dir)/crew-landing")
kill -0 "$waiter" 2>/dev/null || fail "no waiter runs on the landing's submission #$n"
export CREW_AGENT=swb-1-conductor
expect_fail "bolt far-reach's landing is queued in sluice, submitted from $far: unit far-one's construct starts once it has landed or been refused" \
  crew unit run far-one construct
unset CREW_AGENT
crew unit drop far-one "not in this bolt" >/dev/null
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
ok "a landing outlives the submitter that queued it: its waiter on the team's host calls sluice wait again while sluice is undecided, no stage starting on the bolt meanwhile, then reads the landing from sluice's record, records it landed and closes the bolt"

# The waiter stopped as well before sluice decided: nothing records the landing until the conductor's next command,
# whose team read finds the landing's worktree standing with no waiter alive and reads it, recording it landed and
# closing the bolt.
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
kill -KILL "$waiter"
until_ok bash -c '! kill -0 "$1" 2>/dev/null' _ "$waiter" || fail "the waiter was not stopped"
rm "$T/sluice-wait-holds"
eq "$(plan -t Bolt -e "Bolt = 'near-reach'" -c) $(field $box bolt.submit Outcome bolt/near-reach)" "1 "
out=$(export CREW_AGENT=swb-1-conductor; crew status swb-1 2>&1) || fail "the team could not be read:"$'\n'"$out"
has "$out" "bolt/near-reach landed on switchboard-kit's main at"
eq "$(plan -t Bolt -e "Bolt = 'near-reach'" -c)" "0"
eq "$(field $box bolt.submit Outcome bolt/near-reach) $(field $box bolt.land By bolt/near-reach)" "landed wldn-ops"
has "$(field $box bolt.land Why bolt/near-reach)" "read from sluice's record by swb-1-conductor"
ok "a landing whose submitter and waiter were both stopped before sluice decided is read by the conductor's next command, which records it landed and closes the bolt"

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
# named in sluice's words.
crew bolt new queued-one "Landed with a submission queued." --repo switchboard-kit >/dev/null
crew unit add q1 "Unit q1." --bolt queued-one >/dev/null
crew bolt give swb-1 queued-one >/dev/null 2>&1
mkdir -p "$k/openspec/changes/archive/2026-10-22-q1"; echo "# q1" > "$k/openspec/changes/archive/2026-10-22-q1/proposal.md"
commit_all "$k" "chore(openspec): archive q1"; push "$k"
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
by_hand 'p.insert(plan.Rec("Bolt", [("Bolt", "made-before"), ("Repo", "switchboard-kit"), ("Goal", "Made before."), ("Team", "swb-1")]))
unit("mb", "made-before")'
git -C "$k" branch -q --no-track bolt/made-before main; git -C "$k" config branch.bolt/made-before.crew given
on_branch "$k" bolt/made-before "chore: bolts kept on the host" .config/sluice.toml $'[branches."bolt/*"]\nrequired = ["#check-full"]\n'
mkdir -p "$k/openspec/changes/archive/2026-10-22-mb"; echo "# mb" > "$k/openspec/changes/archive/2026-10-22-mb/proposal.md"
commit_all "$k" "chore(openspec): archive mb"; push "$k"
git -C "$k" update-ref refs/heads/bolt/made-before "$(git -C "$k" commit-tree "main^{tree}" -p bolt/made-before -p main -m "chore(land): #20 chore/bolts-on-github")"
git -C "$k" push -q origin bolt/made-before  # as sluice pushes the branch its landing's pull request opens from
expect_ok crew bolt submit made-before
has "$out" "sluice deleted bolt/made-before from GitHub at"
git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q bolt/made-before >/dev/null && fail "bolt/made-before is still on GitHub"
git -C "$k" rev-parse --verify -q bolt/made-before >/dev/null && fail "bolt/made-before is still on the host"
calls | grep -q " sluice branch create bolt/made-before " && fail "crew ran a create for a bolt made before"
ok "a bolt made before lands through its pull request, and sluice deletes its branch from GitHub with no create run for it"

github() { git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse --verify -q "$1" >/dev/null; }
console=$(short bolt/console-pages)
expect_ok crew bolt drop console-pages "the portal lists them"
has "$out" "sluice deleted bolt/console-pages from GitHub at $console"
has "$out" "$kd/places/c and unit/c are removed; the branch was at"
github bolt/console-pages && fail "bolt/console-pages is still on GitHub"
git -C "$k" rev-parse --verify -q bolt/console-pages >/dev/null && fail "bolt/console-pages is still on the host"
eq "$(git --git-dir "$ws" log -1 --format=%b "$(act_tip)" | head -1)" "the portal lists them"
ok "dropping a held bolt removes its units' places and has sluice delete its branch from GitHub and the host, with the reason in the commit"

# A dropped bolt holding a merge main lacks: sluice refuses its delete, and the branch is kept on GitHub and the host,
# marked dropped, named as the drop's unmerged work in sluice's words and recorded once; the team's next read leaves it,
# saying nothing, until a landing brings its tip into main, when the next read has sluice delete it.
crew bolt new kept-work "Work dropped before it landed." --repo switchboard-kit >/dev/null
crew bolt give swb-2 kept-work >/dev/null
git -C "$k" worktree add -q "$T/kept-work" bolt/kept-work && echo kept > "$T/kept-work/kept.txt" &&
  commit_all "$T/kept-work" "feat: work merged into the bolt" && git -C "$k" worktree remove "$T/kept-work" &&
  git -C "$k" push -q origin bolt/kept-work || fail "the bolt took no merge"  # as sluice pushes a landing on a bolt on GitHub
tip=$(git -C "$k" rev-parse bolt/kept-work)
expect_ok crew bolt drop kept-work "not this quarter"
has "$out" "bolt/kept-work is kept on GitHub at ${tip:0:7}: bolt kept-work was dropped, and sluice did not delete it: bolt/kept-work at $tip has not landed into main; submit it there first; it is the drop's unmerged work, the user's to keep or delete, and crew asks sluice again once main holds its tip"
github bolt/kept-work || fail "the refused delete removed bolt/kept-work from GitHub"
eq "$(git -C "$k" rev-parse bolt/kept-work) $(git -C "$k" config branch.bolt/kept-work.crew)" "$tip dropped"
eq "$(field $box branch.kept Head bolt/kept-work team/swb-2) | $(field $box branch.kept Why bolt/kept-work)" \
  "${tip:0:7} | bolt kept-work was dropped, and main does not hold its tip (sluice)"
expect_ok crew status swb-2
lacks "$out" "bolt/kept-work"
eq "$(record_of $box | grep -c "^On: bolt/kept-work")" "1"
ok "a dropped bolt holding a merge main lacks is kept on GitHub and the host, marked, named in sluice's words and recorded once, and the next read leaves it"
git -C "$k" merge -q --no-edit bolt/kept-work && push "$k"  # a landing that carried its work
expect_ok crew status swb-2
has "$out" "bolt/kept-work is removed: main now holds bolt kept-work's tip, and sluice deleted it from GitHub at ${tip:0:7}"
github bolt/kept-work && fail "bolt/kept-work is still on GitHub"
git -C "$k" rev-parse --verify -q bolt/kept-work >/dev/null && fail "bolt/kept-work is still on the host"
ok "once main holds a dropped bolt's tip, the team's next read has sluice delete its kept branch from GitHub and the host"

# Two bolts of one kit proven at once: one landings card in main-level ops's name, on the partition's main machine, a
# box a bolt in the plan's order, the lower row forecast to conflict with the one above it; a merge that moves the
# second's head changes the card in place, naming it.
# proven <bolt> <unit> <file> <line>: the unit's change, adding the line to the file, archived and merged into the bolt
# by its submission, its place and branch gone, so the bolt reads proven at sluice's green head
proven() {
  local p; p=$(place "$k" "$1" "$2") || return 1
  change "$p" "$2" 1 1; echo "$4" >> "$p/$3"; commit_all "$p" "feat($2): its change" || return 1
  mkdir -p "$p/openspec/changes/archive"; git -C "$p" mv "openspec/changes/$2" "openspec/changes/archive/2026-10-23-$2" &&
    git -C "$p" commit -qm "docs(openspec): archive $2" && merge_as swb-1-unit-1 "$p" "bolt/$1" &&
    git -C "$k" worktree remove "$p" && git -C "$k" branch -qD "unit/$2"
}
for b in north south east; do crew bolt new "$b" "The $b regions." --repo switchboard-kit >/dev/null; done
crew bolt give swb-1 north >/dev/null 2>&1; crew bolt give swb-2 south >/dev/null 2>&1
crew unit add north-regions "North's regions." --bolt north >/dev/null; crew unit add south-regions "South's regions." --bolt south >/dev/null
proven north north-regions regions.txt north || fail "north's unit did not merge"
proven south south-regions regions.txt south || fail "south's unit did not merge"
: > "$CREW_TEST_LOG"
expect_ok on_box _land-card wldn switchboard-kit
kit=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $kit ]] || fail "no landings card was raised for north and south:"$'\n'"$out"
posted=$(calls | grep "^$box pendingyou post_request " | tail -1)
eq "$(jq -c '[.idempotencyKey, .session.label, .kind, .highStakes, [.options[].label], .recommendedIds]' <<<"${posted#* post_request }")" \
  '["land/switchboard-kit@wldn:3","wldn-ops","multi",true,["1. north","2. south"],["land:north","land:south"]]'  # two closed before it
has "$posted" "It is forecast to conflict with north on regions.txt."
eq "$(field $box card.post Heads kit/switchboard-kit)" "north@$(short bolt/north) south@$(short bolt/south)"
crew unit add south-more "More of south." --bolt south >/dev/null
proven south south-more south.txt more || fail "south's second unit did not merge"
: > "$CREW_TEST_LOG"
expect_ok on_box _land-card wldn switchboard-kit
has "$out" "card land/switchboard-kit: $kit changed"
changed=$(calls | grep "^$box pendingyou update_request ")
has "$changed" "\"changeNote\": \"south's head is now $(short bolt/south)\""
calls | grep -q "^$box pendingyou post_request " && fail "the card was posted again rather than changed in place"
ok "two proven bolts of one kit are one landings card in main-level ops's name, a box each in the plan's order, the lower forecast to conflict with the one above, and a merge moving the second's head changes it in place"

# A third bolt proven joins the card in place; the user sends it with all three ticked, and one crew bolt submit lands
# them in the card's order, each queued behind the one before on the one host, each closed as it lands: south, which
# conflicts with north on main once north has landed, is refused, recorded at its head in sluice's words and held on
# its row saying them, and east lands all the same; the command exits non-zero naming south, and the card closes with
# what landed and what was held.
crew bolt give swb-1 east >/dev/null 2>&1
crew unit add east-files "East's files." --bolt east >/dev/null
proven east east-files east.txt east || fail "east's unit did not merge"
: > "$CREW_TEST_LOG"
expect_ok on_box _land-card wldn switchboard-kit
has "$out" "card land/switchboard-kit: $kit changed"
has "$(calls | grep "^$box pendingyou update_request ")" "\"changeNote\": \"east reads proven and joins the card\""
echo '{"answer": {"choiceIds": ["land:north", "land:south", "land:east"]}}' > "$(home_of $box)/.stub-pendingyou/answered/$kit.json"
out=$(export CREW_AGENT=wldn-ops; HOST=$box crew card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
has "$out" "lands them: crew bolt submit north south east --label wldn"
south=$(git -C "$k" rev-parse bolt/south)
: > "$CREW_TEST_LOG"
expect_fail "south did not land, as said above; north and east landed" crew bolt submit north south east
eq "$(calls | grep "^$box wt submit " | sed 's/.* from //; s/ as .*//; s/.*land-//')" $'north\nsouth\neast'
has "$out" "bolt/north landed on switchboard-kit's main at"
has "$out" "bolt/south did not land: sluice refused it or found a conflict; switchboard-kit's main moved to"
has "$out" "bolt/east landed on switchboard-kit's main at"
eq "$(plan -t Bolt -e "Bolt = 'north' || Bolt = 'east'" -c) $(plan -t Bolt -e "Bolt = 'south'" -c)" "0 1"
eq "$(field $box bolt.submit Head bolt/south)" "$south"
has "$(field $box bolt.submit Refused bolt/south)" " conflict: regions.txt"
has "$(calls | grep "^$box pendingyou ack_answer ")" "\"outcome\": \"Landed on GitHub's main: north at"
closed=$(field $box card.close Outcome kit/switchboard-kit)  # whole in the run record, cut on the card
has "$closed" "and east at"
has "$closed" "Held: south, held: sluice refused its landing at ${south:0:7}, and it waits for its team's fix: #"
has "$closed" " conflict: regions.txt"
case $closed in *"words above"*) fail "the card's close points at words above, which are in ops's terminal, not on the card" ;; esac
calls | grep -q "^$box pendingyou post_request " && fail "a card was posted though no row can land"
ok "one crew bolt submit lands the ticked bolts in the card's order, each queued behind the one before and closed as it lands, the second refused for its conflict, recorded at its head and held on its row, the third landing all the same; it exits non-zero naming the one held, and the card closes with what landed and what was held"

# The send stands for south's work (record 0031 as amended 2026-10-24): the close kept it, south's team takes main in by
# a fix that only merges main, and once that merges no landings card asks for south; ops reads it with no card open,
# under the earlier send, with the crew bolt submit that lands it, and that command lands it, nothing asked again.
eq "$(field $box card.close Heads kit/switchboard-kit)" "south@${south:0:7}"
has "$closed" "your send stands for it: it lands once its team's fix has only taken main in and sluice has proven it"
sp=$kd/places/fix-south--take-main
export CREW_AGENT=swb-2-conductor
expect_ok crew fix swb-2 take-main "Take main into the bolt: the landing conflicts on regions.txt." --bolt south
git -C "$sp" fetch -q origin
git -C "$sp" merge -q origin/main >/dev/null 2>&1 && fail "taking main into south did not stop on regions.txt"
printf 'north\nsouth\n' > "$sp/regions.txt"; git -C "$sp" add regions.txt
GIT_EDITOR=true git -C "$sp" commit -q --no-edit || fail "the merge of main into south did not commit"
expect_ok crew fix swb-2 take-main --wait --bolt south
expect_ok crew fix swb-2 take-main --merge --bolt south
merge_as swb-2-unit-1 "$sp" bolt/south || fail "south's take-main submission failed"
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-2 take-main --wait --bolt south
unset CREW_AGENT
moved=$(grep -o "delivered merge of fix/south/take-main: bolt/south holds it at [0-9a-f]*" <<<"$out")
[[ -n $moved && ${moved##* } != "${south:0:7}" ]] || fail "south's head did not move with its fix's merge:"$'\n'"$out"
has "$out" "card land/switchboard-kit: south lands on the user's send of an earlier card, so it is no row of this one"
calls | grep -q "^$box pendingyou post_request " && fail "a landings card asked for south again though its own work is unchanged"
out=$(export CREW_AGENT=wldn-ops; HOST=$box crew card read land/switchboard-kit 2>&1) || fail "ops could not read the earlier send:"$'\n'"$out"
eq "$out" "card land/switchboard-kit: no landings card of switchboard-kit is open
  to land on the user's send of an earlier card: south
  lands them: crew bolt submit south --label wldn"
# Ops's session ended while its crew bolt submit south waited on the landing, #90, still queued on main at south's head
# (bolt-teams "Ops restarted while its landing stood"): run again, it reads sluice's queue, submits nothing and waits on
# #90 again, and once sluice lands it south is landed and closed as any landing is.
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
calls | grep -q "^$box pendingyou post_request " && fail "a landings card was posted for south's landing"
ok "a ticked bolt sluice refused keeps the user's send through a fix that only takes main in: no card asks for it, ops reads it with no card open under the earlier send, and the command it prints, run again after its landing stood in sluice, waits on that landing again, submitting nothing, and lands it"

# Main moving under a proven row: GitHub's main lands a change to the file far's unit added, and the builder's host
# has it as origin/main, as the fleet's timer fetches it; crew rail on the main level's host, the partition's main
# machine, raises the kit's landings card again, which forecasts far against main after a fetch, holds far taking main
# first, so a list of two becomes an approval of west alone, followed, and tells swb-1-conductor the take-main fix,
# naming far while swb-1 holds two bolts, recorded on far; a second crew rail, main not having moved, tells nothing,
# raises nothing and records nothing.
crew bolt new west "The west regions." --repo switchboard-kit >/dev/null; crew bolt give swb-1 west >/dev/null 2>&1
crew unit add west-files "West's files." --bolt west >/dev/null
proven west west-files west.txt west || fail "west's unit did not merge"
crew bolt new far "The far regions." --repo switchboard-kit >/dev/null; crew bolt give swb-1 far >/dev/null 2>&1
crew unit add far-files "Far's files." --bolt far >/dev/null
proven far far-files far.txt far || fail "far's unit did not merge"
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
has "$(calls | grep "^$box pendingyou cancel_request ")" "far takes main first: forecast to conflict with main on far.txt at $(short origin/main); swb-1-conductor takes main in by a fix"
posted=$(calls | grep "^$box pendingyou post_request " | tail -1)
eq "$(jq -c '[.kind, .follows, .title]' <<<"${posted#* post_request }")" "[\"approve\",\"$kit\",\"Land the bolt west on switchboard-kit's main\"]"
has "$posted" "**far**: takes main first: forecast to conflict with main on far.txt at $(short origin/main)"
has "$(told swb-1-conductor)" "bolt/far is forecast to conflict with main on far.txt"
has "$(told swb-1-conductor)" "take-main-$(short origin/main)"
has "$(told swb-1-conductor)" "--bolt far"
eq "$(field $box forecast Heads bolt/far) | $(field $box forecast Paths bolt/far) | $(field $box forecast Reached bolt/far)" \
  "bolt/far@$(short bolt/far) main@$(short origin/main) | far.txt | told"
: > "$CREW_TEST_LOG"
expect_ok on_box rail --label wldn
lacks "$out" "landings cards forecast again"
eq "$(told swb-1-conductor)" ""
calls | grep -q "^$box pendingyou \(post\|update\|cancel\)_request " && fail "a second rail read changed the landings card:"$'\n'"$(calls)"
eq "$(record_of $box | grep -c "^Heads: bolt/far@")" "1"
ok "main moving under a proven row makes crew rail on the main level's host raise the kit's landings card again, holding the row taking main first and telling its conductor the take-main fix, recorded once; a second crew rail tells and raises nothing"

# A bolt the user left: near joins west on a card of two boxes, and the user sends it ticking none, which ops's crew
# card read acts on at once, closing it and following it with both rows unticked as left, the set recorded. Main then
# lands a change to the file west's unit added: crew rail's raise keeps west's box, changes the waiting card in place
# saying it would take main first, records the forecast as found while left, and tells swb-1-conductor nothing of
# west. The user ticks west on the card that follows: crew card read raises it first, so swb-1-conductor is told the
# take-main fix for west, recorded as told, and the read leaves west out of the command that lands, its send standing.
crew bolt new near "The near regions." --repo switchboard-kit >/dev/null; crew bolt give swb-2 near >/dev/null 2>&1
crew unit add near-files "Near's files." --bolt near >/dev/null
proven near near-files near.txt near || fail "near's unit did not merge"
expect_ok on_box _land-card wldn switchboard-kit
two=$(grep -o "^card land/switchboard-kit: req_stub-[0-9]*" <<<"$out" | tail -1 | cut -d' ' -f3)
eq "$(field $box card.post Heads kit/switchboard-kit)" "west@$(short bolt/west) near@$(short bolt/near)"
echo '{"answer": {"choiceIds": []}}' > "$(home_of $box)/.stub-pendingyou/answered/$two.json"
out=$(export CREW_AGENT=wldn-ops; HOST=$box crew card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
has "$out" "no bolt ticked: nothing lands"
eq "$(field $box landing.left Heads kit/switchboard-kit)" "west@$(short bolt/west) near@$(short bolt/near)"
eq "$(field $box card.post Heads kit/switchboard-kit)" "west@$(short bolt/west):left near@$(short bolt/near):left"
left=$(field $box card.post Card kit/switchboard-kit)
[[ $left != "$two" ]] || fail "no card followed the send that left west and near"
echo "main's west" > "$k/west.txt"; commit_all "$k" "feat: main's own west"; push "$k"
: > "$CREW_TEST_LOG"
expect_ok on_box rail --label wldn
changed=$(calls | grep "^$box pendingyou update_request ")
has "$changed" "\"changeNote\": \"west, which you left, would take main first: forecast to conflict with main on west.txt at $(short origin/main)\""
has "$changed" "It would take main first if you tick it: forecast to conflict with main on west.txt"
eq "$(jq -c '.recommendedIds' <<<"${changed#* update_request }")" "[]"
lacks "$(told swb-1-conductor)" "bolt/west"
eq "$(field $box forecast Heads bolt/west) | $(field $box forecast Reached bolt/west)" "bolt/west@$(short bolt/west) main@$(short origin/main) | left"
echo '{"answer": {"choiceIds": ["land:west"]}}' > "$(home_of $box)/.stub-pendingyou/answered/$left.json"
: > "$CREW_TEST_LOG"
out=$(export CREW_AGENT=wldn-ops; HOST=$box crew card read land/switchboard-kit 2>&1) || fail "ops could not read its card:"$'\n'"$out"
has "$out" "west takes main first: its team takes main in by a fix, and the user's send stands for it"
lacks "$out" "crew bolt submit"
has "$(told swb-1-conductor)" "bolt/west is forecast to conflict with main on west.txt"
has "$(told swb-1-conductor)" "take-main-$(short origin/main)"
eq "$(field $box forecast Reached bolt/west)" "told"
eq "$(field $box landing.left Heads kit/switchboard-kit)" "near@$(short bolt/near)"
ok "a bolt the user left keeps its box when main moves under it, the card saying it would take main first and its conductor told nothing; a send ticking it, read by ops, tells the take-main fix and submits nothing of it"
