# README, the crew skill and crew's usage name the same commands: every command in the README is in the usage,
# and none of the removed ones is in any of them. CLAUDE.md names how an agent runs crew's tools through the shell
# per command, and no role brief or crew skill does (tests.7); a landing pushes nothing and levels no host in each of
# them (docs.2, plan.18), and a start, a land and a drop go through sluice's branch create and delete, a dropped bolt's
# branch kept while main lacks its tip (plan.19); CLAUDE.md
# says a host loads crew live from crew/live/plugin or released at a tag swancloud pins, never from a checkout on main,
# which nobody pulls or levels (plan.18, plan.19); a checkout carries the .envrc a person's direnv enters the shell
# with, and ignores devenv's and direnv's working files and the tests' .venv. crew's openspec/config.yaml hands crew's
# construct and coder crew's conventions for its changes (docs.6): each task names its check, no proof list, tick a
# task once its check passes.
# Reads: README.md CLAUDE.md plugin/roles/ plugin/skills/ .envrc .gitignore openspec/config.yaml
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
usage=$(crew 2>&1 || true)
readme=$(cat "$CREW/README.md"); skill=$(cat "$CREW/plugin/skills/crew/SKILL.md")
n=0
while read -r line; do
  words=${line#crew }; words=${words%%[<\[\"-]*}; set -- $words
  cmds=$1; subs=${2:-}
  for c in ${cmds//|/ }; do
    lines=$(grep -E "^ *crew +$c( |$)" <<<"$usage") || fail "README's crew $c is not in crew's usage"
    for sub in ${subs//|/ }; do
      grep -qE "(^| |\|)$sub( |\||$)" <<<"$lines" || fail "README's crew $c $sub is not in crew's usage"
      n=$((n + 1))
    done
    n=$((n + 1))
  done
done < <(grep -E '^crew ' "$CREW/README.md")
echo "$n commands checked"
(( n >= 100 )) || fail "too few commands read from the README"
ok "every command in the README is in crew's usage"

for gone in assign release opsx fable explorer verifier coder-; do
  for doc in usage readme skill; do lacks "${!doc}" "$gone"; done
done
for gone in assign release opsx list status up rebuild close restart resume clear down _tidy _status _team; do
  expect_fail "every bolt, unit and chore of the plans" crew $gone swb-1
done
for doc in usage readme skill; do
  team=$(grep -oE '(^|[^a-z_])crew +(list|status|up|rebuild|close|restart|resume|clear|down)([^a-z]|$)' <<<"${!doc}" || true)
  [[ -z $team ]] || fail "the $doc names a team command:"$'\n'"$team"
  for gone in "<team or partition>" "(sent to <team" "SLUICE_BRANCH" "sluice_branch" "conductor fresh" "unit slot"; do
    lacks "${!doc}" "$gone"
  done
  has "${!doc}" 'crew send'; has "${!doc}" '<partition> "<text>"'
done
for doc in usage readme skill; do lacks "${!doc}" "unit approve"; lacks "${!doc}" "review/<unit>"; done
for doc in usage readme skill; do has "${!doc}" "crew review"; done
for gone in "unit run" "unit wait" "unit free" "chore run" "chore wait" "chore free" "crew needs" "fix <team>"; do
  for doc in usage readme skill; do lacks "${!doc}" "$gone"; done
done
for gone in "unit run a code" "unit wait a" "chore free c"; do expect_fail "invalid choice" crew $gone; done
expect_fail "crew: run bolt teams of agents in herdr" crew needs "what it needs"
ok "none of the removed commands or roles is in the README, the skill or the usage, a team command among them, crew drives no stage and waits on none, crew send names a partition alone, and each names crew review"

for doc in usage readme skill; do has "${!doc}" "crew ops offer <env>"; has "${!doc}" "[--notes <file>] [--steps <file>]"; done
for doc in usage readme skill; do
  for gone in "crew plan card" "crew card post" "crew card change" "crew card close" "post|change" "propose|proposed|agree|card"; do
    lacks "${!doc}" "$gone"
  done
  has "${!doc}" "crew record"
done
for doc in usage readme; do has "${!doc}" "session|end <key>"; has "${!doc}" "read <key>"; lacks "${!doc}" "session|wait|end"; done
for want in "crew card session <key>" "crew card end <key>" "crew card read <key>"; do has "$skill" "$want"; done
lacks "$skill" "crew card wait <key>"
for doc in usage readme skill; do
  has "${!doc}" "crew card wait"; has "${!doc}" "refused at once, naming"
  has "${!doc}" "standing in sluice"
done
for doc in usage readme skill; do has "${!doc}" "what an earlier send still lands, with or without a card open"; done
for doc in usage readme skill; do has "${!doc}" "preview <key> <thing> [--done]"; done
has "$skill" "crew card preview <key> <thing> [--done]"
expect_fail "invalid choice: 'post'" crew card post land/x
expect_fail "invalid choice: 'card'" crew plan card 1
ok "the README, the skill and the usage give crew ops offer's notes and steps, crew record and crew card read, session, end and preview, crew card wait refused naming the read, crew card read land/<kit> with no card open, each submission standing in sluice on its row, and no crew plan card or crew card post, change or close, which crew no longer has"

for doc in usage readme skill; do
  has "${!doc}" "pushes nothing and levels no host"; has "${!doc}" "origin/main"; lacks "${!doc}" "behind GitHub's"
done
ok "the README, the skill and the usage say a landing pushes nothing and levels no host, and a bolt is cut from origin/main"

for doc in usage readme skill; do
  has "${!doc}" "sluice branch create"; has "${!doc}" "sluice branch delete"; has "${!doc}" "0.20.0"
  has "${!doc}" "stays local until it lands"
done
for doc in readme skill; do has "${!doc}" "origin/bolt/<bolt>"; done
for doc in usage readme skill; do has "${!doc}" "while main lacks its tip"; lacks "${!doc}" "a dropped bolt's whatever it holds"; done
has "$usage" "land and drop have sluice delete it"; has "$skill" "\`crew bolt land\` and \`crew bolt drop\` have sluice delete"
has "$readme" "for a started bolt, it then has sluice delete the bolt's branch"
ok "the README, the skill and the usage say a start has sluice make the bolt's branch on GitHub and a land and a drop have sluice delete it, a dropped bolt's kept while main lacks its tip, a start refused below sluice 0.20.0, every place cut from the bolt on GitHub, and a bolt made before local until it lands"

for doc in usage readme skill; do
  has "${!doc}" '<bolt> <name> "<what is wrong>"'; has "${!doc}" "start"; has "${!doc}" "started already"; has "${!doc}" "waits to land"
  for gone in "bolt give" "crew bolt give" "one more" "a give" "never refused for the bolts" "plan agree" "dispatch" "agreement"; do
    lacks "${!doc}" "$gone"
  done
  has "${!doc}" "bolt start"
done
expect_fail "unrecognized arguments: --merge" crew fix tenant-environments edge --merge
ok "the README, the skill and the usage say a bolt's work is started by crew bolt start, refused for one started already, and name no give, agreement or dispatcher, a proven bolt waits to land, and crew fix names its bolt, with no --merge or --wait"

for doc in usage readme skill; do
  for want in "version 5, which lists no team" "version 2, 3 or 4 among them" "in Flume stream" "Path: flume" "no team's conductor, ops or slot" \
    "requests.rec" "<label>/runner/<host>" "crew answer" "fix <kit> <name> --send"; do has "${!doc}" "$want"; done
  for gone in "due to cross" "due back" "however they went down" "closes what the hold left" "crossed team" "version 3 of the teams file" \
    "Version 3 of the teams file" "version-2 file" "version 4 names" "version 4 of the teams file" "at version 2 or 3" "versions 2 and 3" \
    "<team|label>"; do lacks "${!doc}" "$gone"; done
done
ok "the README, the skill and the usage say the teams file is version 5 and lists no team, an older one refused, that crew runs no team's agents, its launches in requests.rec and its runner's branch, crew answer and crew main fix, and no team due to cross or crossing"

for doc in usage readme skill; do
  for want in "runs as its kind" "every role stands" "asks.rec" "roles.rec" "crew-<role>--<label>" "end --report <path>" \
    "open <role>" "land <repo> <name> --brief-file <file>" "delivered [--label L]" "pendingyou watch -- crew _answered" \
    "ended at its next stop" "never restarted"; do has "${!doc}" "$want"; done
done
for doc in usage readme; do has "${!doc}" "turns/<role>.md"; done
ok "the README, the skill and the usage say a partition's flume, a role that runs as its kind, its asks in asks.rec and its record in roles.rec, crew role start, end, open and land, crew review delivered, the follower's notice of a card's change, and a standing agent of such a role ended at its stop"

has "$(cat "$CREW/CLAUDE.md")" "devenv shell -- "
wrapped=$(grep -rlF -- 'devenv shell --' "$CREW/plugin/roles" "$CREW/plugin/skills" || true)
[[ -z $wrapped ]] || fail "these briefs or skills name the shell's wrap, which is CLAUDE.md's to say:"$'\n'"$wrapped"
ok "CLAUDE.md names the per-command form of crew's shell, and no brief or skill does"

claude=$(cat "$CREW/CLAUDE.md")
for want in "## How crew reaches a host" "crew/live/plugin" "release tags" "cut from \`origin/main\`"; do has "$claude" "$want"; done
for gone in "This checkout is live" "read-tree" "merge --ff-only" "git pull" "brings every host's checkout up"; do
  lacks "$claude" "$gone"
done
ok "CLAUDE.md says crew/main is an anchor, a host loads crew live from crew/live/plugin or released at a pinned tag, and work is cut from origin/main, with no pull or levelling of crew's checkout"

grep -qxF 'use devenv' "$CREW/.envrc" || fail ".envrc does not enter devenv"
for line in .devenv/ .direnv/ '!.envrc' tests/.venv/; do grep -qxF -- "$line" "$CREW/.gitignore" || fail ".gitignore lacks $line"; done
ok "a checkout carries the .envrc and ignores devenv's and direnv's working files and the tests' .venv"

config=$(cat "$CREW/openspec/config.yaml")
for want in "the check in crew's tiers that proves it" "tests/suite --affected" "*Task notes*" "no proof list of any name" \
  "*After deploy* lists only the steps no check can be code" "is a check this change adds" \
  "Tick a task only once the check it names passes"; do
  has "$config" "$want"
done
ok "crew's openspec/config.yaml says crew's conventions for its changes: each task names its check, no proof list, and a task is ticked once its check passes"
