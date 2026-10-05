# A role resumes its last conversation in the folder that conversation began in, which, since a conductor moves into
# its bolt's worktree, need not be where it starts today; a last session never spoken to starts fresh. The pane's own
# shell moves to the role's folder, which is the folder herdr saves and resumes the agent in after a restart.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
# last <agent>: the folder and the session of its last launch, or "fresh" for a new conversation
last() { jq -r --arg a "$1" 'select(.agent == $a) | "\(.cwd) \(.argv | index("--resume") as $i | if $i then .[$i + 1] else "fresh" end)"' "$CREW_TEST_CLAUDE_LOG" | tail -1; }
session() { jq -r --arg a "$1" 'select(.agent == $a) | .session' "$CREW_TEST_CLAUDE_LOG" | tail -1; }
pane_cwd() { herdr_state $box wldn-1 ".panes[\"$(awk -v r="$1" '$1==r{print $2}' "$(home_of $box)/.local/state/swb-1-team/panes")\"].cwd"; }

expect_ok crew up swb-1
first=$(session swb-1-conductor)
eq "$(pane_cwd conductor)" "$k"
crew down swb-1 >/dev/null
crew bolt new smoke "Prove the loop." --repo switchboard-kit >/dev/null
crew bolt give swb-1 smoke >/dev/null
expect_ok crew resume swb-1 conductor
eq "$(last swb-1-conductor)" "$k $first"
eq "$(pane_cwd conductor)" "$k"
ok "a conversation begun in the kit's main checkout is resumed there, though the role now starts in its bolt's worktree"

expect_ok crew restart swb-1 conductor --no-greet
second=$(session swb-1-conductor)
eq "$(last swb-1-conductor)" "$kd/bolts/smoke fresh"
eq "$(pane_cwd conductor)" "$kd/bolts/smoke"
crew down swb-1 >/dev/null
expect_ok crew resume swb-1 conductor
eq "$(last swb-1-conductor)" "$kd/bolts/smoke $second"
ok "a role starts in its folder with the pane's own shell moved there, and resumes there"

crew down swb-1 >/dev/null
CREW_TEST_NO_MESSAGE=1 expect_ok crew restart swb-1 conductor --no-greet
crew down swb-1 >/dev/null
expect_ok crew resume swb-1 conductor
has "$out" "swb-1-conductor has no conversation to resume; starting it fresh"
eq "$(last swb-1-conductor)" "$kd/bolts/smoke fresh"
ok "a last session never spoken to is not resumed, nor the conversation before it: the role starts fresh"

crew down swb-1 >/dev/null
old=0ld5e55-10n; proj=$(home_of $box)/.claude/projects/$(sed 's/[^A-Za-z0-9]/-/g' <<<"$k"); mkdir -p "$proj"
echo "{\"type\":\"user\",\"cwd\":\"$k\"}" > "$proj/$old.jsonl"
printf 'CREW_AGENT=swb-1-ops\nCREW_LABEL=wldn\n' > "$(home_of $box)/.local/state/crew/sessions/$old"
touch -t 203001010000 "$(home_of $box)/.local/state/crew/sessions/$old"
expect_ok crew resume swb-1 ops
eq "$(last swb-1-ops)" "$k $old"
ok "a record kept before the folder was is resumed in the folder its transcript names"
