# A unit's Touches is a list crew reads: code is refused, saying the change must declare what it touches, when its
# proposal has no `## Touches` heading, no fenced block under it or an empty one; a unit whose Touches overlap those
# of an unmerged unit ahead of it in the bolt starts code with the overlap and the other unit's change in its prompt,
# overlap holding nothing; and verify's prompt names each path the unit changed against its bolt and did not declare,
# its own change's folder aside and counting only the unit's own commits, never a sibling unit's work its place took by
# a merge. Each scenario of the bolt-teams spec on Touches.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b c; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v "/exit" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
# touches <unit> <entries...>: the unit's proposal ends with a Touches block holding the entries, committed
touches() {
  local u=$1 f=$kd/places/$1/openspec/changes/$1/proposal.md; shift
  printf '# Proposal\n\n## Why\n\nx\n\n## What Changes\n\n- y\n\n## Touches\n\n```\n' > "$f"
  printf '%s\n' "$@" >> "$f"; echo '```' >> "$f"
  commit_all "$kd/places/$u" "docs($u): touches"
}
for u in a b c; do crew unit run $u construct >/dev/null; change "$kd/places/$u" $u 0 2; commit_all "$kd/places/$u" "docs($u): the change"; done

f=$kd/places/c/openspec/changes/c/proposal.md
printf '# Proposal\n\n## Why\n\nx\n' > "$f"; commit_all "$kd/places/c" "docs(c): no touches"
expect_fail "unit c's code is refused: its change must declare what it touches, and its proposal.md has no \`## Touches\` heading" crew unit run c code
printf '# Proposal\n\n## Touches\n\nplugin/lib/plan.py\n\n## Other\n\n```\nx\n```\n' > "$f"; commit_all "$kd/places/c" "docs(c): touches as prose"
expect_fail "its \`## Touches\` heading holds no fenced block" crew unit run c code
printf '# Proposal\n\n## Touches\n\n```\n\n```\n' > "$f"; commit_all "$kd/places/c" "docs(c): an empty block"
expect_fail "the block under its \`## Touches\` heading is empty" crew unit run c code
ok "code is refused, saying the change must declare what it touches, with no heading, no fenced block or an empty one"

touches a plugin/lib/plan.py docs/a.md
touches b plugin/lib/plan.py 'tests/**'
touches c 'docs/**'
: > "$CREW_TEST_LOG"
expect_ok crew unit run a code
eq "$(prompt_to swb-1-unit-1)" "'/opsx:apply a'"
expect_ok crew unit run b code
eq "$(prompt_to swb-1-unit-2)" "'/opsx:apply b Its Touches overlap those of a, ahead of it in the bolt and not merged, on plugin/lib/plan.py; a'\"'\"'s change is $kd/places/a/openspec/changes/a/.'"
expect_ok crew unit run c code "Mind the docs."
eq "$(prompt_to swb-1-unit-3)" "'/opsx:apply c Mind the docs. Its Touches overlap those of a, ahead of it in the bolt and not merged, on docs/** against docs/a.md; a'\"'\"'s change is $kd/places/a/openspec/changes/a/.'"
ok "code starts for every unit; a later unit's prompt names the entries it overlaps of each unmerged unit ahead of it, and that unit's change"

mkdir -p "$kd/places/b/plugin/lib" "$kd/places/b/tests"
echo x > "$kd/places/b/plugin/lib/plan.py"; echo t > "$kd/places/b/tests/t-x.sh"; echo r > "$kd/places/b/README.md"
mkdir -p "$kd/places/b/docs"; echo d > "$kd/places/b/docs/b.md"
rewrite "$kd/places/b/openspec/changes/b/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/b" "feat(b): built"
expect_ok crew unit run b verify
eq "$(prompt_to swb-1-unit-2)" "'/opsx:verify b Changed and not declared in its Touches: README.md, docs/b.md.'"
ok "verify's prompt names each path the unit changed against its bolt and did not declare, and none of its own change"

mkdir -p "$kd/places/a/plugin/lib"; echo a > "$kd/places/a/plugin/lib/plan.py"; commit_all "$kd/places/a" "feat(a): built"
git -C "$kd/places/c" merge -q --no-ff unit/a -m "chore: take a's work"
echo c > "$kd/places/c/README.md"
rewrite "$kd/places/c/openspec/changes/c/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/c" "feat(c): built"
expect_ok crew unit run c verify
eq "$(prompt_to swb-1-unit-3)" "'/opsx:verify c Changed and not declared in its Touches: README.md.'"
ok "a sibling unit's work a place took by a merge is not the unit's: verify names only the unit's own undeclared paths"
