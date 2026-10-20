# A bolt landed through sluice, through the crew command on the stubs (tests.11, record 0022), a part of the units
# journey (t-journey-units): no unit starts on a bolt while its landing is in flight; a unit merges into the bolt by a
# submission, and crew bolts reads the bolt's verification from sluice's verdict on it; crew bolt submit lands the
# bolt by a submission to main from a short-lived worktree, naming a conflict for the team and moving nothing; a fix
# takes main into the bolt by a submission to the bolt, and its merge's end raises the bolt's landing card, keyed by
# the bolt, in its conductor's name, with its reading of what the bolt brings to main started first on the team's
# host and linked from it, which crew card session gives again, and the address of a preview of its head, which the
# kit's policy there declares, asked of sluice first; the preview's stack failing is said on the card, changed in
# place by the process that waited on it; a fix started on the bolt withdraws the card, held for it, ending its
# reading and releasing its preview, and once the fix merges and the bolt reads proven again a new card follows it
# with a new reading and a preview of the new head; the landing then lands, leaving the kit's detached main checkout
# as it was and marking the bolt's branch landed; the bolt lands in the plan once every unit has, recording the commit
# main holds and removing its branch, since main holds every commit of it, and the place a stopped landing left on it,
# its landing card closed on the team's host with where GitHub's main holds it, ending its reading and releasing its
# preview, and its conductor told; a landed bolt's branch holding a commit main lacks is kept and named instead, its
# mark unset and the keeping recorded, and the team's next read leaves it; a bolt no team holds lands once its unit's
# change is on main; and dropping a held
# bolt removes its branch and places.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
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
(cd "$pa" && SLUICE_AGENT=swb-1-unit-1 wt submit bolt/tenant-environments --no-remove >/dev/null 2>&1) || fail "a's submission failed"
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
echo "# switchboard-kit, main's" > "$k/README.md"; commit_all "$k" "docs: main's title"
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
: > "$CREW_TEST_LOG"
expect_fail "bolt/tenant-environments did not land: sluice refused it or found a conflict, and main is where it was" crew bolt submit tenant-environments
has "$out" "sluice: bolt/tenant-environments conflicts with main"
eq "$(calls | grep "^$box wt submit ")" "$box wt submit main --no-remove from $land as $me@mac-studio"
eq "$(git -C "$k" rev-parse main)" "$main_before"
[[ ! -e $land ]] || fail "the landing's worktree is still there"
ok "crew bolt submit lands a bolt by a submission to main from a short-lived worktree, and a conflict lands nothing and is named for the team"

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
tm=fix/tenant-environments/take-main tmp=$kd/places/fix-tenant-environments--take-main
export CREW_AGENT=swb-1-conductor
expect_ok crew fix swb-1 take-main "Take main into the bolt: the landing conflicts on README.md."
git -C "$tmp" merge -q main >/dev/null 2>&1 && fail "taking main did not stop on the title"
echo "# switchboard-kit, main's and the bolt's" > "$tmp/README.md"; git -C "$tmp" add README.md
GIT_EDITOR=true git -C "$tmp" commit -q --no-edit || fail "the merge of main did not commit"
expect_ok crew fix swb-1 take-main --wait
expect_ok crew fix swb-1 take-main --merge
(cd "$tmp" && SLUICE_AGENT=swb-1-unit-1 wt submit bolt/tenant-environments --no-remove >/dev/null 2>&1) || fail "the fix's submission failed"
: > "$CREW_TEST_LOG"
touch "$CREW_TEST_ROOT/sluice-preview-holds"  # the preview's stack takes its time to come up
expect_ok crew fix swb-1 take-main --wait
has "$out" "delivered merge of $tm: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
# The merge's end finds the bolt proven, and raises its landing card in its conductor's name, keyed by the bolt, with a
# preview of its head asked of sluice first, once, in the kit's main checkout, and its address listed.
card=$(grep -o "^card land/tenant-environments: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $card ]] || fail "the merge's end raised no landing card:"$'\n'"$out"
has "$out" "call get_request (requestId $card, name swb-1-conductor)"
posted=$(calls | grep "^$box pendingyou post_request ")
has "$posted" '"idempotencyKey": "land/tenant-environments"'
h1=$(git -C "$k" rev-parse bolt/tenant-environments)
eq "$(calls | grep "^$box sluice preview ")" "$box sluice preview bolt/tenant-environments $h1 --wait --json in $(cd "$k" && pwd -P)"
has "$posted" "Try it running: a preview of ${h1:0:7} sluice brings up, at these addresses once it is up."
has "$posted" "web: http://web-${h1:0:7}--bolt-tenant-environments--kit"
ok "a fix takes main into the bolt by a submission to the bolt, and the merge's end raises the bolt's landing card once it reads proven, keyed by the bolt, printing the line that adopts it, with the address of a preview of its head asked of sluice first"

# The landing card's reading, started with it on the team's host: one session on the head's folder, the bolt's page
# first and its diff against main last, its link on the card, and crew card session giving it again.
url=$(jq -r .url "$reading/session.json"); pid=$(jq -r .pid "$reading/session.json")
[[ $url =~ ^http://chuck-herdr-alpha\.ts\.swancloud\.net:194[3-5][0-9]$ ]] || fail "the landing's reading is not on the box's tailnet name: $url"
eq "$(listed)" "$pid"
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
ok "the landing card's reading is started with it on the team's host, the bolt's page, each unit's change and the bolt's diff against main as one review, its link on the card, and crew card session gives it again, starting nothing"

# The preview's stack fails: the process crew handed the ask to changes the card in place while it waits on the user.
previews=$(home_of $box)/.local/state/crew/previews/wldn
touch "$CREW_TEST_ROOT/sluice-preview-fails"; rm "$CREW_TEST_ROOT/sluice-preview-holds"
until_ok grep -q "^card land/tenant-environments: $card changed" "$previews/tenant-environments.log" ||
  fail "the card was not changed for its preview's end:"$'\n'"$(cat "$previews/tenant-environments.log")"
changed=$(calls | grep "^$box pendingyou update_request " | tail -1)
has "$changed" "\"changeNote\": \"Its preview of ${h1:0:7} did not come up\""
has "$changed" "A preview of ${h1:0:7} was asked for and is not there: starting web / stub: the preview command failed: web did not come up."
lacks "$changed" "web: http://"
rm "$CREW_TEST_ROOT/sluice-preview-fails"
ok "a preview whose stack fails is said on the card, changed in place while it waits on the user"

# A defect noted on the card: a fix started on the bolt withdraws it, held for the fix, ending its reading and releasing
# its preview; once the fix merges and the bolt reads proven again, the merge's end raises the card again, following
# the one the fix held, with a new reading and a preview of the new head.
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 gap "The zone list misses one zone."
has "$out" "card land/tenant-environments: $card withdrawn"
has "$out" "ended land/tenant-environments's session, plannotator pid $pid"
has "$out" "released land/tenant-environments's preview of ${h1:0:7}"
gone "$pid"; eq "$(listed)" ""
has "$(calls | grep "^$box pendingyou cancel_request ")" '"reason": "held for a fix: The zone list misses one zone."'
eq "$(calls | grep -c "^$box sluice release ")" "1"
gp=$kd/places/fix-tenant-environments--gap
echo four >> "$gp/shared.txt"; commit_all "$gp" "fix(a): the zone list holds every zone"
expect_ok crew fix swb-1 gap --wait
expect_ok crew fix swb-1 gap --merge
(cd "$gp" && SLUICE_AGENT=swb-1-unit-1 wt submit bolt/tenant-environments --no-remove >/dev/null 2>&1) || fail "the gap fix's submission failed"
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 gap --wait
again=$(grep -o "^card land/tenant-environments: req_stub-[0-9]*" <<<"$out" | cut -d' ' -f3)
[[ -n $again && $again != "$card" ]] || fail "the landing card was not raised again:"$'\n'"$out"
h2=$(git -C "$k" rev-parse bolt/tenant-environments)
posted=$(calls | grep "^$box pendingyou post_request " | tail -1)
has "$posted" "\"follows\": \"$card\""
pid2=$(jq -r .pid "$reading/session.json"); url2=$(jq -r .url "$reading/session.json")
[[ $pid2 != "$pid" ]] || fail "the landing card raised again has its old reading"
eq "$(listed)" "$pid2"
has "$posted" "\"url\": \"$url2\""
has "$posted" "web: http://web-${h2:0:7}--bolt-tenant-environments--kit"
eq "$(calls | grep "^$box sluice preview ")" "$box sluice preview bolt/tenant-environments $h2 --wait --json in $(cd "$k" && pwd -P)"
ok "a fix started on the bolt withdraws its landing card, held for the fix, ending its reading and releasing its preview, and once the fix merges a new card follows it with a new reading and a preview of the new head"
unset CREW_AGENT
git -C "$k" switch -q --detach  # the kit's main checkout as the anchor the fleet's timer moves (plan.18)
expect_ok crew bolt submit tenant-environments
has "$out" "bolt/tenant-environments landed on switchboard-kit's main at $(short main): now crew bolt land tenant-environments."
grep -q level <<<"$out" && fail "the landing spoke of levelling a detached checkout:"$'\n'"$out"
eq "$(git -C "$k" log -1 --format='%an %P' main)" "sluice $main_before $(git -C "$k" rev-parse bolt/tenant-environments)"
eq "$(git -C "$k" rev-parse HEAD) $(cat "$k/README.md")" "$main_before # switchboard-kit, main's"
eq "$(git -C "$k" status --porcelain)" ""
[[ ! -e $land ]] || fail "the landing's worktree is still there"
eq "$(field mac-studio bolt.submit On)" "bolt/tenant-environments"
eq "$(git -C "$k" config branch.bolt/tenant-environments.crew)" "landed"
ok "the landing then lands, its worktree removed, the detached main checkout left as it was and the bolt's branch marked landed"
git -C "$k" switch -q main  # the timer's move, for the steps below that commit on the kit's main

# The user approves the landing card raised again. A landing stopped before it removed its worktree left one on the
# bolt's branch, its process gone, which the landing sweeps with the bolt's branch.
mkdir -p "$(home_of $box)/.stub-pendingyou/answered"
echo '{"answer": {"approved": true}}' > "$(home_of $box)/.stub-pendingyou/answered/$again.json"
git -C "$k" worktree add -q "$land" bolt/tenant-environments
sh -c 'echo $$' > "$(git -C "$land" rev-parse --absolute-git-dir)/crew-landing"
: > "$CREW_TEST_LOG"
expect_ok crew bolt land tenant-environments
has "$out" "tenant-environments has landed at switchboard-kit's $(git -C "$k" rev-parse --short=7 main) and swb-1 holds no bolt"
n=$(git -C "$k" log -1 --format='%(trailers:key=Sluice-Submission,valueonly)' main)
has "$(calls | grep "^$box pendingyou ack_answer ")" "\"outcome\": \"landed on GitHub's main at $(short main) (#$n); every host's folder follows by swancloud's timer within minutes\""
has "$out" "card land/tenant-environments: $again closed"
has "$out" "released land/tenant-environments's preview of ${h2:0:7}"
eq "$(ls "$CREW_TEST_ROOT/sluice-previews")" ""
has "$out" "ended land/tenant-environments's session, plannotator pid $pid2"
gone "$pid2"; eq "$(listed)" ""
[[ ! -e $reading ]] || fail "the landing's reading outlived its card"
has "$out" "$land is removed: bolt tenant-environments is in no plan"
[[ ! -e $land ]] || fail "the landing's worktree outlived the landing"
has "$out" "bolt/tenant-environments is removed: bolt tenant-environments has landed, and main holds every commit of it (git cherry); it was at"
grep -qF "agent prompt swb-1-conductor '[crew] plan(tenant-environments): land the bolt ($me@mac-studio)'" \
  "$CREW_TEST_LOG" || fail "the conductor was not told of the landing:"$'\n'"$(calls)"
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -c)" "0"
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still there"
eq "$(field mac-studio bolt.land On) $(field mac-studio bolt.land Commit)" "bolt/tenant-environments unit/a WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
eq "$(field mac-studio bolt.land Repo) $(field mac-studio bolt.land Head)" "switchboard-kit $(git -C "$k" rev-parse main)"
ok "a drop frees the last slot and closes the units workspace; the bolt lands once every unit has, recording the commit main holds, removing its branch, the place a stopped landing left and what is over, closing its landing card on the team's host with where GitHub's main holds it and the timer, ending its reading and releasing its preview, and its conductor is told"

# A bolt whose branch takes a commit after its landing: crew bolt land keeps the branch at its commit, the user's, its
# mark unset and the keeping recorded on the team's host, and the team's next read leaves it.
crew bolt new zone-lists "The zone list grows." --repo switchboard-kit >/dev/null
crew bolt give swb-1 zone-lists >/dev/null
on_bolt() { git -C "$k" worktree add -q "$T/zone-lists" bolt/zone-lists && echo "$1" >> "$T/zone-lists/zones.txt" &&
  commit_all "$T/zone-lists" "$2" && git -C "$k" worktree remove "$T/zone-lists"; }
on_bolt north "feat: the zone list" || fail "the bolt took no commit"
expect_ok crew bolt submit zone-lists
eq "$(git -C "$k" config branch.bolt/zone-lists.crew)" "landed"
on_bolt south "feat: one zone more, after the landing" || fail "the bolt took no commit after its landing"
at=$(short bolt/zone-lists)
expect_ok crew bolt land zone-lists
has "$out" "bolt/zone-lists is kept at $at: bolt zone-lists has landed, and it holds 1 commit whose patch main lacks (git cherry), the user's to keep or delete"
eq "$(git -C "$k" config branch.bolt/zone-lists.crew)" ""
eq "$(field $box branch.kept Head bolt/zone-lists) $(field $box branch.kept Count bolt/zone-lists)" "$at 1"
eq "$(field $box branch.kept From bolt/zone-lists) | $(field $box branch.kept Why bolt/zone-lists)" \
  "bolt/zone-lists | bolt zone-lists has landed, and main lacks its patches"
expect_ok crew status swb-1
lacks "$out" "bolt/zone-lists"
eq "$(short bolt/zone-lists)" "$at"
ok "a landed bolt's branch holding a commit main lacks is kept at its commit and named, its mark unset and the keeping recorded, and the team's next read leaves it"

# A bolt built outside a team: no team holds it, and it lands once its unit's change is on the kit's main.
crew bolt new done-outside "Built outside a team." --repo switchboard-kit >/dev/null
crew unit add done-x "Unit done-x." --bolt done-outside >/dev/null
expect_fail "unit done-x has not landed on main: it is ready" crew bolt land done-outside
mkdir -p "$k/openspec/changes/archive/2026-10-12-done-x"; echo "# done-x" > "$k/openspec/changes/archive/2026-10-12-done-x/proposal.md"
commit_all "$k" "chore(openspec): archive done-x"
expect_ok crew bolt land done-outside
eq "$(tail -1 <<<"$out")" "done-outside has landed at switchboard-kit's $(git -C "$k" rev-parse main | cut -c1-7); no team held it"
eq "$(field mac-studio bolt.land Head bolt/done-outside) $(plan -t Bolt -e "Bolt = 'done-outside'" -c)" "$(git -C "$k" rev-parse main) 0"
ok "a bolt no team holds lands once its unit's change is on its kit's main, recording the commit main holds"

expect_ok crew bolt drop console-pages "the portal lists them"
has "$out" "bolt/console-pages is removed: bolt console-pages is in no plan; it was at"
has "$out" "$kd/places/c and unit/c are removed; the branch was at"
eq "$(git --git-dir "$ws" log -1 --format=%b wldn/main | head -1)" "the portal lists them"
ok "dropping a held bolt removes its branch and its units' places, with the reason in the commit"
