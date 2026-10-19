# A team's agents through the crew command on the stubs (tests.11, record 0022): crew up starts a team's conductor and
# ops on its host in one workspace, each greeted once and recorded, and status, down, resume, restart, clear, rebuild and
# close act on them; a bolt given to a team that is up is cut from GitHub's main as it stands, with no worktree, and
# restarts them in the kit's main checkout, greeting each; a role resumes where its conversation began, and one with
# none is started fresh and greeted; a conductor brought back is told a unit waits amended; and a landing records
# GitHub's main, however far the host's own lags. The main level's agents are t-journey-main's. Which agents a command
# greets, what each is greeted with, where it runs and resumes, and what a conductor brought back is told are logic
# cases (tests/py/test_teams.py); how git makes a bolt's branch, contract cases
# (tests/contract/test_git.py).
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
pane_cwd() { herdr_state $box wldn-1 ".panes[\"$(awk -v r="$1" '$1==r{print $2}' "$(home_of $box)/.local/state/swb-1-team/panes")\"].cwd"; }
eq "$(pane_cwd conductor)" "$k"
ok "crew up starts a team's conductor and ops on its host, in one workspace with a conductor tab and in the kit's main checkout, greets each once and records it; status lists them and four free slots"

crew bolt new smoke "Prove the loop." --repo switchboard-kit >/dev/null
pushed from-a-mac
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt give swb-1 smoke
eq "$(git -C "$k" rev-parse bolt/smoke)" "$(git -C "$other" rev-parse main)"
[[ $(git -C "$k" rev-parse bolt/smoke) != "$(git -C "$k" rev-parse main)" ]] || fail "the bolt was cut from the host's own main"
eq "$(launched swb-1-conductor)" "$k fresh"; eq "$(launched swb-1-ops)" "$k fresh"
eq "$(pane_cwd conductor)" "$k"
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"
has "$(grep "agent prompt swb-1-conductor '" "$CREW_TEST_LOG")" "Your team now holds the bolt smoke. Read where your bolt stands"
eq "$(greetings $box wldn-1 swb-1-ops)" "1"
has "$(grep "agent prompt swb-1-ops '" "$CREW_TEST_LOG")" "You are swb-1'\"'\"'s ops; your team holds the bolt smoke."
eq "$(field $box agent.restart By agent/swb-1-ops)" "$me@mac-studio"
ok "a bolt given to a team that is up is cut from GitHub's main as it stands, with no worktree, and restarts its conductor and ops in the kit's main checkout, then greets each once, told the bolt"

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

# A landing records GitHub's main, and refuses nothing for the host's own main lagging it: the unit lands on GitHub's
# main from this host, as sluice's landing leaves the host's main, and another lands there after.
git -C "$k" pull -q --ff-only origin main
change "$k" amended-one 3 3; commit_all "$k" "feat: amended-one"; git -C "$k" branch -q -f bolt/later main
git -C "$k" push -q origin main; pushed later-from-a-mac
expect_ok crew bolt land later
eq "$(field mac-studio bolt.land Head bolt/later)" "$(git -C "$other" rev-parse main)"
ok "a landing records the commit GitHub's main holds after a fetch, and refuses nothing for the host's own main lagging it"
