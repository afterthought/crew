# A host clones a kit once and never pulls it. bolt give fetches the kit first: it cuts the bolt from GitHub's main,
# fast-forwarding a clean main to it, or from the host's main when that already holds all of GitHub's, and refuses a
# main that has gone its own way. bolt land refuses while the kit's main is behind GitHub's.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
r=$(remote WilldanGroup/switchboard-kit); git clone -q --bare "$k" "$r"
git -C "$k" remote add origin https://github.com/WilldanGroup/switchboard-kit; git -C "$k" fetch -q origin
other=$T/elsewhere; git clone -q "$r" "$other"
pushed() { git -C "$other" pull -q --rebase origin main; echo "$1" > "$other/$1"; commit_all "$other" "feat: $1"; git -C "$other" push -q origin main; }
crew state init wldn >/dev/null
team() { git --git-dir "$ws" show wldn/main:plan.rec | recsel -t Bolt -e "Bolt = '$1'" -P Team; }
landed() { crew unit add "$2" "x" --bolt "$1" >/dev/null; change "$k" "$2" 3 3; commit_all "$k" "feat: $2"; git -C "$kd/bolts/$1" merge -q --ff-only main; }

pushed from-a-mac
crew bolt new one "First." --repo switchboard-kit >/dev/null
expect_ok crew bolt give swb-1 one
has "$out" "main fast-forwarded 1 commit to GitHub's"
eq "$(git -C "$k" rev-parse bolt/one)" "$(git -C "$other" rev-parse main)"
eq "$(git -C "$k" rev-parse main)" "$(git -C "$other" rev-parse main)"
ok "a bolt is cut from GitHub's main, fetched first, and a clean main behind it is fast-forwarded"

landed one first-unit
pushed later-from-a-mac
expect_fail "switchboard-kit's main on chuck-herdr-alpha is 1 commit behind GitHub's (with 1 of its own): rebase it onto origin/main" crew bolt land one
eq "$(team one)" "swb-1"
git -C "$k" rebase -q origin/main
expect_ok crew bolt land one
ok "land is refused while the kit's main is behind GitHub's, and lands once main is rebased onto it"

crew bolt new two "Second." --repo switchboard-kit >/dev/null
expect_ok crew bolt give swb-1 two
has "$out" "main holds 1 commit GitHub's main does not yet have; the bolt is cut from them"
eq "$(git -C "$k" rev-parse bolt/two)" "$(git -C "$k" rev-parse main)"
landed two second-unit
git -C "$k" push -q origin main
expect_ok crew bolt land two
ok "a bolt is cut from the host's main when it holds all of GitHub's and more"

echo local > "$k/local"; commit_all "$k" "feat: local only"
pushed another-from-a-mac
crew bolt new three "Third." --repo switchboard-kit >/dev/null
expect_fail "main on this host has 1 commit of its own and lacks 1 commit of GitHub's: rebase it onto origin/main first, and never push it with force" crew bolt give swb-1 three
eq "$(team three)" ""
git -C "$k" rebase -q origin/main; git -C "$k" push -q origin main
echo wip > "$k/README.md"
pushed yet-another
expect_ok crew bolt give swb-1 three
has "$out" "main is 1 commit behind GitHub's and was left as it is"
eq "$(git -C "$k" rev-parse bolt/three)" "$(git -C "$other" rev-parse main)"
ok "a main gone its own way is refused before the plan is written, and a dirty main is left as it is"
