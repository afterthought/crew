# A write to the flywheel's branch names its run-record entry in a Crew-Entry trailer, and carries the host's
# uncarried entries to runs/<host>/ on the branch in the same commit; crew events --push carries on its own, and
# makes no commit when there is nothing to carry. crew events and crew trace read the branch, then each host they
# reach, so a host that is down is shown as far as it had carried, and a host that lost its record keeps it there.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
box=chuck-herdr-alpha
wb=$(blueprints WilldanGroup/willdan-blueprints); ws=$(remote WilldanGroup/crew-state)
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
export CREW_LABEL=wldn
day=$(date -u +%F)
emit() { local h=$1; shift; as "$h" python3 "$CREW/plugin/lib/record.py" emit --label wldn "$@"; }
# onbranch <host>: the ids that host's file of the day holds on the branch
onbranch() { git --git-dir "$ws" show "wldn/main:runs/$1/$day.rec" 2>/dev/null | sed -n 's/^Id: //p'; }
commits() { git --git-dir "$ws" rev-list --count wldn/main; }

CREW_AGENT=wldn-planner crew bolt new tenants "Tenants." --repo switchboard-kit >/dev/null
sha=$(git --git-dir "$ws" rev-parse wldn/main)
eid=$(git --git-dir "$ws" log -1 --format='%(trailers:key=Crew-Entry,valueonly)' wldn/main | head -1)
[[ -n $eid ]] || fail "the write's commit has no Crew-Entry trailer"
rec=$(home_of mac-studio)/.local/state/crew/wldn/runs/mac-studio/$day.rec
eq "$(recsel -t Entry -e "Id = '$eid'" -P Act,Commit "$rec")" $'bolt.new\n'"WilldanGroup/crew-state@$sha"
ok "a write's Crew-Entry trailer is the id of the one entry that names its commit"

tell=$(emit mac-studio --act tell --on agent/wldn-planner --field Chars=5)
lacks "$(onbranch mac-studio)" "$tell"
CREW_AGENT=wldn-planner crew bolt new consoles "Consoles." --repo switchboard-kit >/dev/null
has "$(onbranch mac-studio)" "$tell"; has "$(onbranch mac-studio)" "$eid"
git --git-dir "$ws" show "wldn/main:runs/mac-studio/$day.rec" > "$T/runs.rec"; recfix --check "$T/runs.rec" || fail "the carried file fails recfix --check"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" $'plan.rec\n'"runs/mac-studio/$day.rec"
ok "a tell's entry, and the last write's own, reach the branch with the next plan write"

n=$(commits)
expect_ok crew events --push --label wldn
has "$out" "carried mac-studio's run record"
eq "$(commits)" "$((n + 1))"
eq "$(git --git-dir "$ws" diff-tree --no-commit-id --name-only -r wldn/main)" "runs/mac-studio/$day.rec"
eq "$(git --git-dir "$ws" log -1 --format='%(trailers:key=Crew-Entry,valueonly)' wldn/main | tr -d '\n')" ""
eq "$(onbranch mac-studio | sort)" "$(recsel -C -t Entry -P Id "$rec" | sort)"
expect_ok crew events --push --label wldn
has "$out" "nothing of mac-studio's run record left to carry"
eq "$(commits)" "$((n + 1))"
ok "crew events --push carries what is left in a commit of its own, and nothing when nothing is left"

emit $box --act unit.add --on unit/x --on queue/switchboard-kit --why "plan(queue): add x" >/dev/null
HOST=$box expect_ok crew events --push --label wldn
has "$out" "carried $box's run record"
/bin/sleep 1
emit $box --act unit.drop --on unit/x --on queue/switchboard-kit --why "plan(queue): drop x" >/dev/null
echo "$box" > "$T/down"
expect_ok crew events --label wldn --about unit/x
has "$out" "unit.add"; lacks "$out" "unit.drop"; has "$out" "$box did not answer"
expect_ok crew trace unit/x --label wldn
has "$out" "unit.add"; lacks "$out" "unit.drop"; has "$out" "$box did not answer"
rm "$T/down"
expect_ok crew events --label wldn --about unit/x
has "$out" "unit.add"; has "$out" "unit.drop"; lacks "$out" "did not answer"
eq "$(grep -c 'unit.add' <<<"$out")" "1"
ok "events and trace read the branch first: a host that is down is shown as far as it had carried, and named"

carried=$(onbranch $box)
rm -rf "$(home_of $box)/.local/state/crew/wldn"
emit $box --act unit.add --on unit/y --on queue/switchboard-kit --why "plan(queue): add y" >/dev/null
HOST=$box expect_ok crew events --push --label wldn
for id in $carried; do has "$(onbranch $box)" "$id"; done
eq "$(onbranch $box | wc -l | tr -d ' ')" "$(( $(wc -w <<<"$carried") + 1 ))"
ok "a host that lost its run record after carrying keeps its entries on the branch, and adds new ones beside them"
