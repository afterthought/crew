# A unit's stages from the bolt's give, through the crew command on the stubs (tests.11, record 0022): give has sluice
# make the bolt's branch on GitHub and no worktree (record 0026, plan.19); a unit's place is cut from the bolt on
# GitHub after a fetch and made ready through the kit's declaration as every worktree crew makes is (plan.17), a setup
# that fails refusing the stage until a second run sets the place up; each stage of a unit takes a slot, starts a fresh
# agent in the unit's place and sends its prompt; the waits end each stage at its deliverable and record it; the
# team's read records an end nobody waited on, fetching and gathering once; verify's report ends it; code's prompt
# names an unmerged unit's overlapping Touches; a wait says a conflict sluice's overview shows for the stage's
# submission, before its answer (record 0032); a merge in a kit whose main takes no pull requests asks nothing of
# GitHub, and, once main takes them, a merge drafts the bolt's ready landing pull request before its prompt is sent,
# and one whose gh fails does not start, naming the repository in gh's words (bolt-teams). The units journey's other parts:
# t-journey-slots, t-journey-merge, t-journey-prompts, t-journey-fix, t-journey-land.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
expect_ok crew up swb-1
eq "$(field $box team.up On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
eq "$(field $box team.up By)" "$me@mac-studio"
expect_ok crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit --source books/x.md
has "$out" "plan(tenant-environments): add the bolt ($me@mac-studio)"
by_hand 'old = {plan.declares(q): q for q in plan.Plan(plan.HEADER.replace(" Amended", "")).paras if plan.declares(q)}
p.paras = [old.get(plan.declares(x), x) for x in p.paras]'
expect_ok crew unit add a "Unit a." --bolt tenant-environments --source books/x.md --source switchboard-kit:docs/y.md
has "$out" "plan(tenant-environments): add a ($me@mac-studio)"
eq "$(plan -t Unit -e "Unit = 'a'" -P Source)" $'books/x.md\nswitchboard-kit:docs/y.md'
has "$(grep '^%allowed: Unit' "$T/plan.rec")" "Amended"
by_hand 'unit("b", "tenant-environments", "a"); [unit(u, "tenant-environments") for u in "cde"]
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
expect_ok crew bolt give swb-1
has "$out" "swb-1 holds tenant-environments: sluice made bolt/tenant-environments on GitHub (origin) from switchboard-kit's main at $(git -C "$k" rev-parse --short main), built on $box and merged into only through sluice"
eq "$(plan -t Bolt -e "Bolt = 'tenant-environments'" -P Team)" "swb-1"
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$(git -C "$k" rev-parse main)"
eq "$(git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse bolt/tenant-environments)" "$(git -C "$k" rev-parse main)"
[[ ! -e $kd/bolts ]] || fail "give made a worktree for the bolt"
eq "$(field mac-studio bolt.give On) $(field mac-studio bolt.give Commit)" "bolt/tenant-environments team/swb-1 WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
clean_forecast
ok "crew up records the team's agents; bolt new and unit add each commit to the plan in the asker's name, a write bringing an older plan's descriptors in step; give has sluice make the bolt's branch on GitHub from main, and no worktree"

# The conductor runs the stages on the team's host.
export CREW_AGENT=swb-1-conductor
expect_ok crew unit run a construct
has "$out" "swb-1-unit-1 has a: construct, in $kd/places/a"
eq "$(cat "$slots")" "unit-1 unit a $kd/places/a"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/a)" "origin/bolt/tenant-environments"
eq "$(ready "$kd/places/a")" 1
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:propose a Unit a. Sources: books/x.md; switchboard-kit:docs/y.md.'"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1,swb-1 units"
eq "$(field $box stage.start On stage/a/construct)" "stage/a/construct unit/a agent/swb-1-unit-1"
eq "$(field $box stage.start By stage/a/construct)" "swb-1-conductor"
has "$(cat "$stages")" "unit-1 a construct "
ok "construct takes a free slot, makes the unit's place from the bolt on GitHub ready through the kit's declaration, starts a fresh agent sent its prompt in the units workspace, and records the start it owes an end"

expect_fail "unit b is waiting: it comes after a, whose change is not committed yet" crew unit run b construct
eq "$(wc -l < "$slots" | tr -d ' ')" "1"
[[ ! -d $kd/places/b ]] || fail "b's place was made"
has "$(field $box stage.start Refused stage/b/construct)" "unit b is waiting"
eq "$(ls -A "$(home_of $box)/.cache/crew/reads" "$(home_of mac-studio)/.cache/crew/reads" 2>/dev/null | grep -v '^/\|^$' || true)" ""
ok "a stage refused takes no slot, makes no place, leaves no reading, and is recorded refused"

change "$kd/places/a" a 0 3; commit_all "$kd/places/a" "docs(a): the change"
status swb-1-unit-1 working
expect_ok crew unit wait a --stuck 0 --timeout 0
eq "$out" "construct on a is still running after the wait's 0 ms: swb-1-unit-1 is working; nothing is recorded yet"
status swb-1-unit-1 idle
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered construct on a: its change is committed at $(short unit/a)"
eq "$(field $box stage.end Ended stage/a/construct)" "delivered"
eq "$(field $box stage.end Delivered stage/a/construct)" "unit/a@$(short unit/a)"
eq "$(field $box stage.end Result stage/a/construct)" "planned"
eq "$(cat "$stages")" ""
ok "a wait reads the stage still running while its agent works, then records its end with what it delivered"

echo a > "$kd/places/a/a-work"; commit_all "$kd/places/a" "feat(a): its own work"; tick a 1.1
touch "$T/moon-fails"
expect_fail "$kd/places/b is made but not ready: moon setup exited 1" crew unit run b construct
has "$out" "stand-in moon: setup failed"; has "$out" "Running the command again sets it up."
eq "$(wc -l < "$slots" | tr -d ' ')" "1"
rm "$T/moon-fails"
ok "a setup that fails refuses the stage in the tool's words, with the place made and no slot taken"

expect_ok crew unit run b construct
eq "$(ready "$kd/places/b")" 2
has "$out" "swb-1-unit-2 has b: construct, in $kd/places/b"
git -C "$k" merge-base --is-ancestor unit/a unit/b || fail "b's place does not hold a's work"
eq "$(field $box stage.start Took stage/b/construct)" "a@$(git -C "$k" rev-parse --short=7 unit/a)"
expect_ok crew unit run a code
grep -q "^$box wldn-1 agent prompt $(pane swb-1-unit-1) /exit\|^$box wldn-1 agent prompt swb-1-unit-1 /exit" "$CREW_TEST_LOG" || fail "a's construct agent was not ended"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:apply a'"
ok "a dependent's construct takes its After unit's head; code ends the slot's agent and starts a fresh one at its own effort"

# The team's read on its host: an end nobody waited on recorded late, the state branch fetched and the kit gathered once.
tick a 1.2; tick a 1.3
stale=$(home_of $box)/.cache/crew/reads/OLDOLDOL; mkdir -p "$stale"; echo $box > "$stale/host"; touch -t 202601010000 "$stale"
: > "$T/reads.log"
PATH="$T/shim:$PATH" CREW_TEST_READS=$T/reads.log expect_ok crew status swb-1
for want in "swb-1-conductor" "swb-1-ops" "a  verify 3/3" "b  construct"; do has "$out" "$want"; done
eq "$(reads fetch) $(reads gather) $(reads openspec)" "1 1 0"
eq "$(ls -A "$(home_of $box)/.cache/crew/reads" 2>/dev/null)" ""
eq "$(field $box stage.end Ended stage/a/code)" "delivered"
eq "$(field $box stage.end Observed stage/a/code)" "late"
eq "$(field $box stage.end Tasks stage/a/code)" "3/3"
ok "crew status lists the roles and each slot's stage, fetches and gathers once, leaves no reading and removes one a day old, and records a delivered end nobody waited on, late"

expect_ok crew unit run a verify
eq "$(prompt_to swb-1-unit-1)" "'/opsx:verify a Changed and not declared in its Touches: a-work.'"
mkdir -p "$reports"; report=$reports/verify-a-20261008-1412.md; echo "the report" > "$report"
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered verify on a: the report is $report"
expect_ok crew trace report/verify-a-20261008-1412.md
has "$out" "stage/a/verify unit/a agent/swb-1-unit-1 → verify 3/3, delivered report/verify-a-20261008-1412.md"
ok "verify's prompt names what the unit changed and did not declare; the report it saves ends it, and crew trace finds it"

change "$kd/places/b" b 0 2; commit_all "$kd/places/b" "docs(b): the change"
touches b 'src/b/**' src/a/x
expect_ok crew unit run b code
eq "$(prompt_to swb-1-unit-2)" "'/opsx:apply b Its Touches overlap those of a, ahead of it in the bolt and not merged, on src/a/x against src/a/**; a'\"'\"'s change is $kd/places/a/openspec/changes/a/.'"
looks() { grep -c " agent get swb-1-unit-2$" "$CREW_TEST_LOG" || true; }
n=$(looks)
crew unit wait b --stuck 3600000 --timeout 1800000 > "$T/wait.out" 2>&1 &
waiting=$!
until_ok eval '(( $(looks) > n ))' || fail "the wait never looked at b"
kill -0 $waiting 2>/dev/null || fail "the wait returned before b's tasks were ticked: $(cat "$T/wait.out")"
tick b 1.1; tick b 1.2
wait $waiting || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(tail -1 "$T/wait.out")" "swb-1-unit-2 delivered code on b: every task is ticked (2/2) at $(short unit/b)"
ok "code's prompt names the Touches it overlaps of an unmerged unit ahead of it, and a wait that saw a task open sees it ticked at its next look"


# Each look of a wait reads sluice's overview beside the refs: a conflict sluice recorded for the merge's submission
# from a's place, out of the queue before any look saw it there, is placed by asking sluice status of it once, and said
# to the conductor in sluice's words before the wait's answer.
expect_ok crew unit run a merge
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq -n --arg at "$now" --arg repository "$(git -C "$k" rev-parse --path-format=absolute --git-common-dir)" '{at: $at,
  branches: [{at: null, branch: "bolt/tenant-environments", candidates: [], depth: 0, parallel: 1, submissions: [], version: 3,
    window: 1, recent: [{at: $at, event: "conflict", id: 7, paths: ["shared.txt"], schema: "sluice/log@1", with: []}]}],
  host: "chuck-herdr-alpha", previews: [], repository: $repository, schema: "sluice/overview@1", sessions: []}' > "$T/sluice-overview.json"
jq -n --arg at "$now" --arg path "$(cd "$kd/places/a" && pwd -P)" '{schema: "sluice/submission@1", id: 7,
  branch: "bolt/tenant-environments", head: "0000000000000000000000000000000000000000",
  from: {agent: "swb-1-unit-1", worktree: "unit/a", path: $path}, submitted: $at, after: [], priority: 0, attempt: 1,
  state: "conflict", conflict: {paths: ["shared.txt"], with: []}, told: $at}' > "$T/sluice-status-7.json"
expect_ok crew unit wait a --timeout 0
eq "$(head -1 <<<"$out")" "merge on a: sluice says of swb-1-unit-1's submission to bolt/tenant-environments: conflict #7 on shared.txt; the wait goes on until the stage ends"
has "$(tail -1 <<<"$out")" "merge on a is still running after the wait's 0 ms"
eq "$(grep -c "^$box sluice status 7 --json in " "$CREW_TEST_LOG")" 1
eq "$(grep -c "^$box gh " "$CREW_TEST_LOG")" 0
ok "a wait says the conflict sluice recorded for the stage's submission, placed by sluice status, before its answer; a merge in a kit whose main takes no pull requests asks nothing of GitHub"

# A merge sluice landed on the bolt from another host is on GitHub's bolt/tenant-environments, which this host's own
# lags: a unit's place is cut from GitHub's after a fetch, tracking it, and holds that merge.
w=$T/another-host; git clone -q -b bolt/tenant-environments "$(remote WilldanGroup/switchboard-kit)" "$w"
echo elsewhere > "$w/landed-elsewhere"; commit_all "$w" "chore(land): #9 unit/elsewhere"; git -C "$w" push -q origin bolt/tenant-environments
landed=$(git -C "$w" rev-parse HEAD)
git -C "$k" cat-file -e "$landed^{commit}" 2>/dev/null && fail "the host already held the merge"
expect_ok crew unit run c construct
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/c)" "origin/bolt/tenant-environments"
git -C "$k" merge-base --is-ancestor "$landed" unit/c || fail "c's place does not hold the merge landed on GitHub"
ok "a unit's place is cut from the bolt on GitHub after a fetch, holding a merge landed there from another host"

# Once main takes pull requests, a merge into the bolt holds its landing pull request first (bolt-teams): one whose gh
# fails does not start, naming the repository in gh's words, and the next drafts the ready one before its prompt is sent.
rewrite "$k/.config/sluice.toml" '/^\[branches.main\]$/,/^remote/ s/^remote = "origin"$/&\n\n[branches.main.pull_requests]\nreviews = 0/'
commit_all "$k" "chore: main takes pull requests"; push "$k"
gh_repo=WilldanGroup/switchboard-kit
pr=$(pull $gh_repo bolt/tenant-environments false)
merges=$(sent swb-1-unit-1 "'Merge a")
echo "HTTP 401: Bad credentials (https://api.github.com/graphql)" > "$T/gh-fails"
expect_fail "unit a's merge into bolt/tenant-environments does not start: crew can't read $gh_repo's open pull request from bolt/tenant-environments into main: gh exited 1: HTTP 401: Bad credentials (https://api.github.com/graphql)" \
  crew unit run a merge
eq "$(sent swb-1-unit-1 "'Merge a")" "$merges"
has "$(field $box stage.start Refused stage/a/merge)" "does not start"
rm "$T/gh-fails"
: > "$CREW_TEST_LOG"
expect_ok crew unit run a merge
has "$out" "Its pull request https://github.com/$gh_repo/pull/$pr is a draft, so no merge into bolt/tenant-environments lands it"
eq "$(drafted "$pr")" true
eq "$(grep -E "^$box (gh pr ready $pr -R $gh_repo --undo|wldn-1 agent prompt swb-1-unit-1 'Merge a)" "$CREW_TEST_LOG" | cut -d' ' -f2-3)" $'gh pr\nwldn-1 agent'
ok "once main takes pull requests, a merge whose gh fails does not start, naming the repository in gh's words, and a merge drafts the bolt's ready landing pull request before its prompt is sent"

# A merge sluice lands on GitHub's bolt pushing as its app moves neither the host's own bolt/tenant-environments nor its
# tracking ref (sluice 0.36.4 on deneb, 2026-10-23): the merge's wait fetches at its look and sees it delivered at
# GitHub's head, and crew bolts shows the unit merged (plan.19).
rm -f "$T/sluice-overview.json" "$T/sluice-status-7.json"
d=$(date -u +%Y-%m-%d); mkdir -p "$kd/places/a/openspec/changes/archive"
git -C "$kd/places/a" mv openspec/changes/a "openspec/changes/archive/$d-a"; commit_all "$kd/places/a" "docs(openspec): archive a"
copy=$(git -C "$k" rev-parse bolt/tenant-environments)
touch "$T/sluice-leaves-copy"
merge_as swb-1-unit-1 "$kd/places/a" bolt/tenant-environments || fail "a's merge did not land"
rm "$T/sluice-leaves-copy"
github=$(git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse bolt/tenant-environments)
tracked=$(git -C "$k" rev-parse refs/remotes/origin/bolt/tenant-environments)
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$copy"
[[ $tracked != "$github" ]] || fail "the landing moved the host's tracking ref"
git -C "$k" merge-base --is-ancestor unit/a "$tracked" && fail "the host's tracking ref already holds a's merge"
expect_ok crew unit wait a
eq "$(head -1 <<<"$out")" "swb-1-unit-1 delivered merge on a: bolt/tenant-environments holds it at ${github:0:7}"
eq "$(stage a)" "merged"
ok "a merge landed on GitHub leaving the host's copy and tracking ref behind is delivered at GitHub's head, and crew bolts shows it merged"
