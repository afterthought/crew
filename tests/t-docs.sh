# README, the crew skill and crew's usage name the same commands: every command in the README is in the usage,
# and none of the removed ones is in any of them. CLAUDE.md names how an agent runs crew's tools through the shell
# per command, and no role brief or crew skill does (tests.7); a landing pushes nothing and levels no host in each of
# them (docs.2, plan.18); a checkout carries the .envrc a person's direnv enters the shell with, and ignores devenv's
# and direnv's working files and the tests' .venv.
# Reads: README.md CLAUDE.md plugin/roles/ plugin/skills/ .envrc .gitignore
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
(( n > 40 )) || fail "too few commands read from the README"
ok "every command in the README is in crew's usage"

for gone in assign release opsx fable explorer verifier coder-; do
  for doc in usage readme skill; do lacks "${!doc}" "$gone"; done
done
for gone in assign release opsx; do expect_fail "A team builds one bolt at a time" crew $gone swb-1; done
for doc in usage readme skill; do lacks "${!doc}" "unit approve"; lacks "${!doc}" "review/<unit>"; done
for doc in usage readme skill; do has "${!doc}" "crew review"; has "${!doc}" "settle"; done
ok "none of the removed commands or roles is in the README, the skill or the usage, and each names crew review and the settle stage"

for doc in usage readme skill; do has "${!doc}" "crew ops offer <env>"; has "${!doc}" "[--notes <file>] [--steps <file>]"; done
for doc in usage readme skill; do
  for gone in "crew plan card" "crew card post" "crew card change" "crew card close" "post|change" "propose|proposed|agree|card"; do
    lacks "${!doc}" "$gone"
  done
  has "${!doc}" "crew record"
done
for doc in usage readme; do has "${!doc}" "session|wait|end <key>"; has "${!doc}" "read <key>"; done
for want in "crew card session <key>" "crew card wait <key>" "crew card end <key>" "crew card read <key>"; do has "$skill" "$want"; done
expect_fail "invalid choice: 'post'" crew card post land/x
expect_fail "invalid choice: 'card'" crew plan card 1
ok "the README, the skill and the usage give crew ops offer's notes and steps, crew record and crew card read, wait, session and end, and no crew plan card or crew card post, change or close, which crew no longer has"

for doc in usage readme skill; do
  has "${!doc}" "pushes nothing and levels no host"; has "${!doc}" "origin/main"; lacks "${!doc}" "behind GitHub's"
done
ok "the README, the skill and the usage say a landing pushes nothing and levels no host, and a bolt is cut from origin/main"

for doc in usage readme skill; do has "${!doc}" "--bolt <bolt>"; has "${!doc}" "one more"; has "${!doc}" "waits to land"; done
ok "the README, the skill and the usage say a team may hold one more bolt that waits to land, and crew fix names its bolt with --bolt"

has "$(cat "$CREW/CLAUDE.md")" "devenv shell -- "
wrapped=$(grep -rlF -- 'devenv shell --' "$CREW/plugin/roles" "$CREW/plugin/skills" || true)
[[ -z $wrapped ]] || fail "these briefs or skills name the shell's wrap, which is CLAUDE.md's to say:"$'\n'"$wrapped"
ok "CLAUDE.md names the per-command form of crew's shell, and no brief or skill does"

grep -qxF 'use devenv' "$CREW/.envrc" || fail ".envrc does not enter devenv"
for line in .devenv/ .direnv/ '!.envrc' tests/.venv/; do grep -qxF -- "$line" "$CREW/.gitignore" || fail ".gitignore lacks $line"; done
ok "a checkout carries the .envrc and ignores devenv's and direnv's working files and the tests' .venv"
