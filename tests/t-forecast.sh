# Conflicts are forecast on the conductor's waits: git merge-tree dry-runs each unmerged unit's merge with the bolt
# and with each unmerged unit ahead of it, moving no ref. A forecast reaches the later unit once, never the earlier:
# told to its stage's agent once that is not working, carried in its next stage's prompt when no stage of it runs, or
# as a settle stage when it has delivered its verify; a forecast between two unmerged units gives the later After on
# the earlier. Each scenario of the bolt-teams spec on forecasts.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
printf 'one\ntwo\nthree\n' > "$k/shared.txt"; printf 'one\ntwo\n' > "$k/other.txt"; printf 'one\ntwo\n' > "$k/third.txt"
commit_all "$k" "chore: files the units share"
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b d c; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
bolt=$kd/bolts/tenant-environments
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
pane() { herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key"; }
told() { grep "^$box wldn-1 agent prompt $1 '\[crew\]" "$CREW_TEST_LOG" || true; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v "/exit" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
entries() {
  as $box python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))):
    for e in record.parse(open(f).read()):
        if e["Act"] == sys.argv[2]:
            print(json.dumps(e))' "$CREW/plugin/lib" "$1"
}
refs() { git -C "$k" for-each-ref --format='%(refname) %(objectname)'; }
# edit <unit> <file> <line two>: the unit's own line two of a shared file, committed in its place
edit() {
  printf 'one\n%s\n' "$3" > "$kd/places/$1/$2"; [[ $2 == shared.txt ]] && echo three >> "$kd/places/$1/$2"
  commit_all "$kd/places/$1" "feat($1): its own line"
}
for u in a b d c; do crew unit run $u construct >/dev/null; change "$kd/places/$u" $u 0 2; commit_all "$kd/places/$u" "docs($u): the change"; done
for u in a b d c; do crew unit wait $u >/dev/null; done  # each construct delivered, nothing yet in conflict
eq "$(entries forecast | wc -l | tr -d ' ')" "0"
crew unit run b code >/dev/null
edit a shared.txt "two, as a has it"; edit b shared.txt "two, as b has it"; edit d other.txt "two, as d has it"; edit c third.txt "two, as c has it"
as $box herdr --session wldn-1 stub status "$(pane swb-1-unit-2)" working
before=$(refs)
: > "$CREW_TEST_LOG"
expect_ok crew unit wait b --timeout 0
eq "$(told swb-1-unit-2)" ""
eq "$(entries forecast | wc -l | tr -d ' ')" "0"
eq "$(plan -t Unit -e "Unit = 'b'" -P After)" "a"
ok "a forecast between two unmerged units gives the later After on the earlier, and waits while the later unit's agent works"

as $box herdr --session wldn-1 stub status "$(pane swb-1-unit-2)" idle
: > "$CREW_TEST_LOG"
expect_ok crew unit wait b --timeout 0
eq "$(refs)" "$before"
has "$(told swb-1-unit-2)" "Your merge after a, ahead of you in the bolt and not merged, is forecast to conflict on shared.txt. You merge after it: take its work into your place (git merge unit/a)"
has "$(told swb-1-unit-2)" "change is $kd/places/a/openspec/changes/a/. Its Why: x What it changes: y'"
eq "$(told swb-1-unit-1)" ""
eq "$(entries forecast | jq -r '[(.On | join(" ")), .Heads, .Paths, .Reached] | join(" | ")')" \
  "unit/b unit/a | b@$(git -C "$k" rev-parse --short=7 unit/b) a@$(git -C "$k" rev-parse --short=7 unit/a) | shared.txt | told"
ok "once the later unit's agent is not working it is told, with the paths and the other unit's change; the earlier unit is told nothing, and no ref moved"

: > "$CREW_TEST_LOG"
expect_ok crew unit wait b --timeout 0
eq "$(told swb-1-unit-2)" ""
eq "$(entries forecast | wc -l | tr -d ' ')" "1"
ok "a wait that finds neither head moved tells nothing again"

# d planned with no stage running, and c verified and waiting to merge, each meet the bolt's own line.
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
rewrite "$kd/places/c/openspec/changes/c/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/c" "feat(c): done"
crew unit run c verify >/dev/null
echo "# Verify c" > "$reports/verify-c-$(date +%Y%m%d-%H%M).md"
expect_ok crew unit wait c
has "$out" "delivered verify on c"
printf 'one\ntwo, as the bolt has it\n' > "$bolt/other.txt"; printf 'one\ntwo, as the bolt has it\n' > "$bolt/third.txt"
commit_all "$bolt" "feat: the bolt's own line"
: > "$CREW_TEST_LOG"
expect_ok crew unit wait b --timeout 0
eq "$(entries forecast | jq -r 'select(.On[0] == "unit/d") | [(.On | join(" ")), .Paths, .Reached] | join(" | ")')" "unit/d bolt/tenant-environments | other.txt | prompt"
eq "$(told swb-1-unit-3)" ""
eq "$(entries forecast | jq -r 'select(.On[0] == "unit/c") | [(.On | join(" ")), .Paths, .Reached] | join(" | ")')" "unit/c bolt/tenant-environments | third.txt | settle"
has "$(prompt_to "$(pane swb-1-unit-4)")" "'Settle c: Your branch is forecast to conflict with bolt/tenant-environments on third.txt. Rebase your place onto the bolt (git rebase bolt/tenant-environments)"
eq "$(entries stage.start | jq -r 'select(.On[0] == "stage/c/settle") | .By')" "swb-1-conductor"
ok "a unit with no stage running keeps its forecast for its next stage, and a verified unit waiting to merge gets a settle stage"

: > "$CREW_TEST_LOG"
expect_ok crew unit run d code
has "$(prompt_to "$(pane swb-1-unit-3)")" "'/opsx:apply d Your branch is forecast to conflict with bolt/tenant-environments on other.txt."
id=$(entries forecast | jq -r 'select(.On[0] == "unit/d") | .Id')
eq "$(entries stage.start | jq -r 'select(.On[0] == "stage/d/code") | .Forecast')" "$id"
expect_ok crew unit run d code
eq "$(prompt_to "$(pane swb-1-unit-3)")" "'/opsx:apply d'"
ok "the next stage's prompt carries the forecast once, and its start names the forecast it carried"
