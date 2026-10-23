# A team's agents through the crew command on the stubs (tests.11, record 0022): crew up starts a team's conductor and
# ops on its host in one workspace, each greeted once and recorded, and status, down, resume, restart, clear, rebuild and
# close act on them; a give is refused, nothing changed, while the kit's policy names no remote for its bolts or the
# host's sluice has no branch create; a bolt given to a team that is up is made on GitHub by sluice from main as it
# stands, with no worktree, and restarts them in the kit's main checkout, greeting each; a role resumes where its
# conversation began, and one with none is started fresh and greeted; crew up opens again in the team's workspace a
# pane herdr brought back dead; a conductor brought back is told a unit waits amended; a landing records GitHub's
# main, however far the host's own lags; and a team holding a bolt made before gives went through sluice is told once
# a read that it is local until it lands, its places cut from the host's own branch. The main level's agents are t-journey-main's. Which agents a command greets,
# what each is greeted with, where it runs and resumes, whether a pane is dead and where it opens again, and what a
# conductor brought back is told are logic cases (tests/py/test_teams.py); what a give checks and says around sluice's
# create, logic cases too (tests/py/test_bolt_commands.py).
# Reads: plugin/hooks/ tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

expect_ok crew up swb-1
has "$out" "swb-1-conductor started"; has "$out" "swb-1-ops started"; has "$out" "swb-1-conductor greeted"; has "$out" "swb-1-ops greeted"
grep -q "^mac-studio ssh $box " "$CREW_TEST_LOG" || fail "crew up did not run on the team's host"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
eq "$(herdr_state $box wldn-1 '[.tabs[].label] | join(",")')" "conductor"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
eq "$(launched swb-1-conductor)" "$k fresh"
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"; eq "$(greetings $box wldn-1 swb-1-ops)" "1"
has "$(grep "agent prompt swb-1-ops '" "$CREW_TEST_LOG")" "'[crew] You are swb-1'\"'\"'s ops; your team holds no bolt. Nothing is asked of you now"
eq "$(field $box team.up On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
eq "$(field $box team.up By)" "$me@mac-studio"
eq "$(field $box greet On agent/swb-1-conductor)" "agent/swb-1-conductor team/swb-1"
eq "$(field $box greet On agent/swb-1-ops)" "agent/swb-1-ops team/swb-1"
[[ -d $(home_of $box)/.local/state/swb-1-team && ! -d $(home_of mac-studio)/.local/state/swb-1-team ]] || fail "the team's state is not on its host"
expect_fail "swb-1-conductor is already up" crew up swb-1
expect_ok crew status swb-1
has "$out" "swb-1-conductor"; has "$out" "swb-1-ops"; eq "$(grep -c ' free ' <<<"$out")" "4"
pane_of() { awk -v r="$1" '$1==r{print $2}' "$(home_of $box)/.local/state/swb-1-team/panes"; }
pane_cwd() { herdr_state $box wldn-1 ".panes[\"$(pane_of "$1")\"].cwd"; }
# The branch a role's pane tells sluice's plugins it works for (teams.20), "none" when its pane carries none.
pane_branch() { herdr_state $box wldn-1 ".panes[\"$(pane_of "$1")\"].tokens.sluice_branch // \"none\""; }
eq "$(pane_cwd conductor)" "$k"
eq "$(pane_branch conductor) $(pane_branch ops)" "none none"
ok "crew up starts a team's conductor and ops on its host, in one workspace with a conductor tab and in the kit's main checkout, greets each once and records it; status lists them and four free slots"

crew bolt new smoke "Prove the loop." --repo switchboard-kit >/dev/null
# A give is refused, the plan unchanged and no branch made anywhere, while the kit's policy on GitHub's main names no
# remote for its bolts, and while the host's sluice has no `branch create`.
plan_at=$(git --git-dir "$ws" rev-parse wldn/main)
policy=$(cat "$other/.config/sluice.toml")
printf '[branches."bolt/*"]\nrequired = ["#check-full"]\n\n[branches.main]\nrequired = ["#check-full"]\nremote = "origin"\n' > "$other/.config/sluice.toml"
commit_all "$other" "chore: bolts kept on the host"; git -C "$other" push -q origin main
expect_fail "switchboard-kit gives bolts only on GitHub, and its $k/.config/sluice.toml on origin/main names no remote for its bolt branches: its [branches.\"bolt/*\"] needs \`remote = \"origin\"\`" \
  crew bolt give swb-1 smoke
printf '%s\n' "$policy" > "$other/.config/sluice.toml"; commit_all "$other" "chore: bolts on GitHub"; git -C "$other" push -q origin main
echo "sluice 0.18.0" > "$T/sluice-version"
expect_fail "a bolt is given through sluice 0.20.0 or later, which has \`branch create\`, and sluice --version on $box said: sluice 0.18.0" \
  crew bolt give swb-1 smoke
rm "$T/sluice-version"
eq "$(git --git-dir "$ws" rev-parse wldn/main)" "$plan_at"
git -C "$k" rev-parse --verify -q bolt/smoke >/dev/null && fail "a refused give made bolt/smoke on the host"
git --git-dir "$r" rev-parse --verify -q bolt/smoke >/dev/null && fail "a refused give made bolt/smoke on GitHub"
calls | grep -q " sluice branch create " && fail "a refused give ran sluice's create"
ok "a give is refused, the plan unchanged and no branch made, while the kit's policy on GitHub's main names no remote for its bolts or the host's sluice has no branch create"

pushed from-a-mac
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt give swb-1 smoke
github=$(git -C "$other" rev-parse main)
has "$out" "swb-1 holds smoke: sluice made bolt/smoke on GitHub (origin) from switchboard-kit's main at ${github:0:7}, built on $box"
eq "$(git --git-dir "$r" rev-parse bolt/smoke) $(git -C "$k" rev-parse bolt/smoke)" "$github $github"
[[ $(git -C "$k" rev-parse bolt/smoke) != "$(git -C "$k" rev-parse main)" ]] || fail "the bolt was cut from the host's own main"
eq "$(git -C "$k" config branch.bolt/smoke.crew)" "given"
eq "$(calls | grep " sluice branch ")" "$box sluice branch create bolt/smoke --from main --json in $(cd "$k" && pwd -P)"
eq "$(launched swb-1-conductor)" "$k fresh"; eq "$(launched swb-1-ops)" "$k fresh"
eq "$(pane_cwd conductor)" "$k"
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"
has "$(grep "agent prompt swb-1-conductor '" "$CREW_TEST_LOG")" "Your team now holds the bolt smoke. Read where your bolt stands"
eq "$(greetings $box wldn-1 swb-1-ops)" "1"
has "$(grep "agent prompt swb-1-ops '" "$CREW_TEST_LOG")" "You are swb-1'\"'\"'s ops; your team holds the bolt smoke."
eq "$(field $box agent.restart By agent/swb-1-ops)" "$me@mac-studio"
eq "$(pane_branch conductor) $(pane_branch ops)" "bolt/smoke bolt/smoke"
eq "$(jq -r 'select(.agent == "swb-1-conductor") | .branch' "$CREW_TEST_CLAUDE_LOG" | tail -1)" "bolt/smoke"
ok "a bolt given to a team that is up is made on GitHub by sluice from main as it stands, marked as crew's on the host, with no worktree, and restarts its conductor and ops in the kit's main checkout, carrying the bolt's branch for sluice, then greets each once, told the bolt"

# herdr's server restarts, keeping no token, and resumes the conductor bare, without crew's environment.
cp=$(pane_of conductor); sid=$(jq -r 'select(.agent == "swb-1-conductor") | .session' "$CREW_TEST_CLAUDE_LOG" | tail -1)
as $box herdr --session wldn-1 pane report-metadata "$cp" --source crew --clear-token sluice_branch >/dev/null
as $box env HERDR_ENV=1 HERDR_SESSION=wldn-1 HERDR_PANE_ID="$cp" HERDR_BIN_PATH="$TESTS/stubs/herdr" \
  python3 "$CREW/plugin/hooks/session-start" <<<"{\"session_id\":\"$sid\",\"source\":\"resume\"}"
branch_is() { [[ $(pane_branch "$1") == "$2" ]]; }
until_ok branch_is conductor bolt/smoke || fail "the resumed conductor's pane did not get its bolt's branch back: $(pane_branch conductor)"
ok "a conductor herdr resumes bare gets its bolt's branch back on its pane"

first=$(jq -r 'select(.agent == "swb-1-ops") | .session' "$CREW_TEST_CLAUDE_LOG" | tail -1)
expect_ok crew down swb-1
eq "$(herdr_state $box wldn-1 '.agents | length')" "0"
has "$(field $box team.down On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew resume swb-1
has "$out" "swb-1-conductor resumed"; has "$out" "swb-1-ops resumed"
eq "$(launched swb-1-ops)" "$k resumed"
eq "$(jq -r 'select(.agent == "swb-1-ops") | .argv | .[index("--resume") + 1]' "$CREW_TEST_CLAUDE_LOG")" "$first"
eq "$(count $box agent.resume)" "2"
grep -q "agent prompt swb-1-\(conductor\|ops\) '" "$CREW_TEST_LOG" && fail "crew resume greeted an agent it brought back with its conversation"
CREW_TEST_TRUST=1 expect_ok crew restart swb-1 ops
has "$out" "swb-1-ops started"; has "$out" "swb-1-ops greeted"; lacks "$out" "conductor"
eq "$(grep -c "^$box wldn-1 agent send-keys w[0-9]*:p[0-9]* down enter" "$CREW_TEST_LOG")" "1"
expect_fail "no role 'fable' here; roles: conductor ops" crew restart swb-1 fable
: > "$CREW_TEST_LOG"
CREW_TEST_BYPASS=1 expect_ok crew restart swb-1 ops
eq "$(grep -c "agent send-keys" "$CREW_TEST_LOG")" "0"
expect_ok crew clear swb-1 ops
eq "$(field $box agent.clear On)" "team/swb-1 agent/swb-1-ops"
expect_ok crew rebuild swb-1
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
expect_ok crew close swb-1
eq "$(herdr_state $box wldn-1 '.workspaces | length')" "0"
ok "down, resume (in the folder the conversation began in, greeting nobody), restart with the folder-trust question answered and never the Bypass warning, clear, rebuild and close act on the conductor and ops, each recorded, the pane's shell in the role's folder"

# An ops started with no first message, as crw-2's give left crw-2-ops on 2026-10-19, has no conversation to resume:
# crew resume starts it fresh and greets it, so it has one for the next resume (teams.7).
expect_ok crew up swb-1
CREW_TEST_NO_MESSAGE=1 expect_ok crew restart swb-1 ops --no-greet
lacks "$out" "greeted"
crew down swb-1 >/dev/null; : > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew resume swb-1 ops
has "$out" "swb-1-ops has no conversation to resume; starting it fresh"
eq "$(launched swb-1-ops)" "$k fresh"
eq "$(greetings $box wldn-1 swb-1-ops)" "1"
has "$(grep "agent prompt swb-1-ops '" "$CREW_TEST_LOG")" "You are swb-1'\"'\"'s ops; your team holds the bolt smoke."
crew close swb-1 >/dev/null
ok "an ops crew resume finds no conversation for is started fresh and greeted, told the bolt its team holds"

for gone in "assign swb-1 coder-1 x" "opsx swb-1 explorer /opsx:propose x"; do
  if out=$(crew $gone 2>&1); then fail "crew $gone still works"; fi
  has "$out" "A team builds one bolt at a time"
done
expect_ok crew up atl-1
eq "$(herdr_state mac-studio wldn-5 '[.tabs[].label] | join(",")')" "conductor,git"
ok "assign and opsx are gone, and a team on a Mac has a git tab"

# herdr brings atl-1's conductor and ops back dead, their folder gone at its restart, as it brought crw-2's back before
# test D (2026-10-18): crew up closes each and opens it again in the team's workspace, the git tab left as it stands.
crew down atl-1 >/dev/null
apane() { awk -v r="$1" '$1 == r {print $2}' "$(home_of mac-studio)/.local/state/atl-1-team/panes"; }
c=$(apane conductor); o=$(apane ops); g=$(apane git-kit)
for p in "$c" "$o"; do as mac-studio herdr --session wldn-5 stub dead "$p" "$T/trash/gone"; done
expect_ok crew up atl-1
has "$out" "atl-1's conductor pane $c is dead: herdr could not bring it back in $T/trash/gone (Saved directory is unavailable. Restore the directory and restart this session.); crew closes it and opens it again"
has "$out" "atl-1's ops pane $o is dead"; has "$out" "atl-1-conductor started"; has "$out" "atl-1-ops started"
eq "$(herdr_state mac-studio wldn-5 "[.panes | keys[] | select(. == \"$c\" or . == \"$o\")] | length")" "0"
eq "$(herdr_state mac-studio wldn-5 '[.workspaces[].label] | join(",")'),$(apane git-kit)" "atl-1,$g"
eq "$(herdr_state mac-studio wldn-5 '[.tabs[].label] | join(",")')" "git,conductor"
eq "$(herdr_state mac-studio wldn-5 '[.agents[].name] | sort | join(",")')" "atl-1-conductor,atl-1-ops"
ok "crew up closes the conductor's and ops' panes herdr brought back dead, saying so, and opens them again in the team's workspace beside its git tab"

# A unit of swb-2's bolt waits amended: the conductor brought back is told so, by its greeting or, on resume, as crew's notice.
crew bolt new later "What comes next." --repo switchboard-kit >/dev/null
crew unit add amended-one "Unit amended-one." --bolt later >/dev/null
crew bolt give swb-2 later >/dev/null 2>&1
p=$(place "$k" later amended-one); change "$p" amended-one 1 3; commit_all "$p" "docs(amended-one): the change"
w=$T/hand; git clone -q -b wldn/main "$ws" "$w"
python3 - "$CREW/plugin/lib" "$w/plan.rec" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
p.unit("amended-one").set("Amended", "intent")
open(f, "w").write(p.text())
PY
commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
: > "$CREW_TEST_LOG"
expect_ok crew up swb-2
has "$(grep "agent prompt swb-2-conductor '" "$CREW_TEST_LOG")" "'[crew] Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct). Read where your bolt stands with"
crew down swb-2 >/dev/null; : > "$CREW_TEST_LOG"
expect_ok crew resume swb-2 conductor
eq "$(grep "agent prompt swb-2-conductor '" "$CREW_TEST_LOG")" "$box wldn-1 agent prompt swb-2-conductor '[crew] Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct).'"
ok "a conductor brought back is told the unit that waits amended: in its greeting by crew up, as crew's notice by crew resume"

# A landing reads what landed and records GitHub's main, refusing nothing for the host's own main lagging it: the unit
# lands on GitHub's main from this host, as sluice's landing leaves the host's main and its origin/main where the host
# last fetched them, and another lands there after.
git -C "$k" pull -q --ff-only origin main
change "$k" amended-one 3 3; commit_all "$k" "feat: amended-one"; git -C "$k" branch -q -f bolt/later main
git -C "$k" push -q "$r" main; pushed later-from-a-mac
eq "$(git -C "$k" rev-parse origin/main)" "$(git -C "$k" rev-parse main~)"
expect_ok crew bolt land later
eq "$(field mac-studio bolt.land Head bolt/later)" "$(git -C "$other" rev-parse main)"
ok "a landing fetches GitHub's main before it reads which units landed, records the commit it holds, and refuses nothing for the host's own main lagging it"

# A bolt made before gives went through sluice: its branch made with git on the kit's host, at a commit whose policy
# names no remote for bolts, while the kit's main now names origin. Each read of its team says once that it is local
# until it lands, no create is run for it, and a unit's place is cut from the host's own branch.
w=$T/hand-before; git clone -q -b wldn/main "$ws" "$w"
python3 - "$CREW/plugin/lib" "$w/plan.rec" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
p.insert(plan.Rec("Bolt", [("Bolt", "made-before"), ("Repo", "switchboard-kit"), ("Goal", "Made before."), ("Team", "swb-2")]))
p.insert(plan.Rec("Unit", [("Unit", "mb"), ("Repo", "switchboard-kit"), ("Bolt", "made-before"), ("Intent", "Unit mb.")]))
open(f, "w").write(p.text())
PY
commit_all "$w" "plan: a bolt made before"; git -C "$w" push -q origin wldn/main
git -C "$k" branch -q --no-track bolt/made-before main; git -C "$k" config branch.bolt/made-before.crew given
on_branch "$k" bolt/made-before "chore: bolts kept on the host" .config/sluice.toml $'[branches."bolt/*"]\nrequired = ["#check-full"]\n'
: > "$CREW_TEST_LOG"
expect_ok crew status swb-2
eq "$(grep -c "is local until it lands" <<<"$out")" "1"
has "$out" "bolt/made-before is local until it lands: it was made before bolts were on GitHub, so its places are cut from the local branch, and its landing puts it on GitHub"
export CREW_AGENT=swb-2-conductor
expect_ok crew unit run mb construct
unset CREW_AGENT
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/mb)" "bolt/made-before"
calls | grep -q " sluice branch create " && fail "crew ran a create for a bolt made before"
git --git-dir "$r" rev-parse --verify -q bolt/made-before >/dev/null && fail "a bolt made before was put on GitHub"
ok "a team's read says once that a bolt made before is local until it lands, runs no create for it, and cuts its places from the host's own branch"
