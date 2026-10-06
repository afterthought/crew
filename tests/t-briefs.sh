# Every brief prints for its team or partition with no token left unfilled.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  [[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/$role.md left ${BASH_REMATCH[0]} unfilled"
  has "$out" "# You are swb-1-"
  lacks "$out" "fable"; lacks "$out" "explorer"
  echo "$role: $(wc -c <<<"$out" | tr -d ' ') characters"
done
expect_fail "no definition 'fable' for a team" crewpy brief swb-1 fable
[[ ! -e $CREW/plugin/roles/fable.md && ! -e $CREW/plugin/roles/explorer.md && ! -e $CREW/plugin/roles/verifier.md ]] || fail "a retired role is still there"
ok "every team brief prints with no unfilled token"

expect_ok crewpy brief swb-1 conductor
for want in "unit approve" "review" "tell wldn-design" "signal" "never by hand" "Don't create tracking files" "`wldn/main` of WilldanGroup/crew-state"; do
  has "$out" "$want"
done
has "$out" "plannotator-tui herdr open"; has "$out" "openspec/changes/<unit>/proposal.md"
ok "the conductor takes units through review, asks the design agent, records signals, and writes the plan only through crew"

for role in design planner dispatcher main-ops; do
  expect_ok crewpy brief wldn $role
  [[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/$role.md left ${BASH_REMATCH[0]} unfilled"
  has "$out" "of wldn"; lacks "$out" "fable"
  echo "$role: $(wc -c <<<"$out" | tr -d ' ') characters"
done
expect_ok crewpy brief wldn design
for want in attach challenge new-territory answered drop "unit add" "tell wldn-planner" "tell <conductor>"; do has "$out" "$want"; done
expect_ok crewpy brief wldn planner
for want in "only agent that proposes bolts" "--signal" "plan propose <file>" "plan proposed <n>" "--replaces <n>" "--unblocks <bolt>" \
  "plan agree <n>" "only when the user says so" "wldn/main"; do has "$out" "$want"; done
for gone in "bin/crew bolt new" "bin/crew unit add" "bin/crew unit move" "bin/crew unit drop" "Agree any change to it"; do lacks "$out" "$gone"; done
for want in 'unit amend <unit> "<new intent>"' "never a drop and a new unit" "why the unit changes rather than being replaced" \
  "A unit that has merged is not amended"; do has "$out" "$want"; done
has "$out" '`swb-1` builds Switchboard in switchboard-kit'; has "$out" "on mac-studio in session wldn-5"
expect_ok crewpy brief swb-1 conductor
for want in "plan proposed <n>" "plan agree <n>" "crew refuses it from you"; do has "$out" "$want"; done
for want in "at any stage before it merges" "crew marks the unit amended" "code waits for that approval" \
  "When crew tells you a unit's intent was amended, run construct again" "tell \`wldn-planner\`, who proposes the amendment"; do has "$out" "$want"; done
expect_ok crewpy brief swb-1 construct
for want in "## Writing a change again" "the unit's intent was amended" "stay ticked only where the work they describe" \
  "Commit the revision, however small"; do has "$out" "$want"; done
expect_ok crewpy brief wldn operator
for want in "plan proposed --label wldn" "plan approve <n> --label wldn" "only on the user's word"; do has "$out" "$want"; done
expect_ok crewpy brief wldn design; has "$out" 'crew refuses `--bolt` from you'
expect_ok crewpy brief wldn dispatcher
for want in "bolt give <team>" "up <team>" "account ia" "one bolt deploy at a time"; do has "$out" "$want"; done
has "$out" $'The teams here:\n\n- `atl-1` builds Atlas'; has "$out" $'its conductor is `atl-1-conductor`\n\nYou give these teams'
expect_ok crewpy brief wldn main-ops
for want in "wt merge main --no-squash --no-remove" "bolt land <bolt>" "Deploy main"; do has "$out" "$want"; done
expect_fail "no definition 'conductor' for a main level" crewpy brief wldn conductor
ok "every main-level brief prints for wldn with no unfilled token"

expect_ok crewpy brief wldn operator
[[ $out =~ \{\{[A-Z_]+\}\} ]] && fail "roles/operator.md left ${BASH_REMATCH[0]} unfilled"
for want in "bolts --label wldn" "status <team>" "sites wldn" "tell <agent>" '`wldn-planner`' '`wldn-design`' "<team>-conductor" "terminal-browser open <url> --split right"; do has "$out" "$want"; done
HOST=chuck-herdr-alpha expect_ok crewpy brief wldn operator
has "$out" "chuck-herdr-alpha is a box, which can't open the dev.swancloud.net names"; lacks "$out" "terminal-browser open"
ok "the operator brief prints for wldn, opening sites on a Mac and giving the Mac URL on a box"

# Every brief says who is speaking in the agent's pane; the six that record findings say how, with the excerpt, and
# where crew writes the signal.
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role
  has "$out" 'A message in your pane that begins `[crew tell from <name>]` was sent with crew tell by that agent'
  has "$out" 'one that begins `[crew]` is crew'"'"'s own; anything else typed there is the user.'
done
for role in design planner main-ops dispatcher operator; do
  expect_ok crewpy brief wldn $role
  has "$out" 'A message in your pane that begins `[crew tell from <name>]` was sent with crew tell by that agent'
done
for brief in "swb-1 conductor" "swb-1 ops" "wldn main-ops" "wldn design" "wldn planner" "wldn operator"; do
  expect_ok crewpy brief $brief
  has "$out" 'signal <slug> "<what it asserts, in a sentence>" --excerpt "<the exact words the user said or the tool printed>"'
  has "$out" "Copy the excerpt, never reword it"; has "$out" "a refusal means the words were reworded"
  has "$out" '`signals/` on `wldn/main` of WilldanGroup/crew-state'
  lacks "$out" "signal in WilldanGroup/willdan-blueprints"
done
expect_ok crewpy brief wldn design; lacks "$out" "crew writes signals straight to"; has "$out" "signal show <signal id>"
expect_ok crewpy brief wldn planner; has "$out" "signal show <signal id>"
ok "every brief says who speaks in its pane, and the six that record findings quote the words and say what a refusal means"

# The plan and the moves live on the flywheel's branch of its state repository: no brief names a plan/<label>
# branch or a moves.rec in the blueprints, and the design agent and the planner name the state repository.
for role in conductor ops construct coder verify; do
  expect_ok crewpy brief swb-1 $role; lacks "$out" "plan/wldn"; lacks "$out" "signals/moves.rec"
done
for role in design planner main-ops dispatcher operator; do
  expect_ok crewpy brief wldn $role; lacks "$out" "plan/wldn"; lacks "$out" "signals/moves.rec"
done
expect_ok crewpy brief wldn design; has "$out" "\`moves.rec\` on \`wldn/main\` of WilldanGroup/crew-state"
lacks "$out" "route moves straight to"
expect_ok crewpy brief wldn planner; has "$out" "\`wldn/main\` of WilldanGroup/crew-state"
ok "every brief names the flywheel's branch for the plan and the moves, and none names plan/<label>"
