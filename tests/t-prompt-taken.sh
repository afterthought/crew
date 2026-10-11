# A stage's prompt is taken or sent again (teams.15): crew sends it once the agent is ready for input, reads the
# agent's transcript on its host for it, and when it is not there with the agent idle clears the input with one ctrl+c
# and sends it once more. crew.py stage-prompt answers 0 when it is taken; 3 when it never was, sent twice and the input
# cleared again, or when the agent was never ready and nothing was typed; and 1 when crew could not tell, as for an
# agent that went to work with no record of the prompt, which is neither pressed nor sent again.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
box=chuck-herdr-alpha
export CREW_TAKEN_WITHIN=1
herdr_box() { as $box herdr --session wldn-1 "$@"; }
p=$(herdr_box workspace create --cwd "$(space $box willdan)" --label "swb-1 units" | jq -r .result.root_pane.pane_id)
for n in 1 2 3 4 5; do
  q=$(herdr_box pane split "$p" --direction right --cwd "$(space $box willdan)" | jq -r .result.pane.pane_id)
  herdr_box stub agent "$q" swb-1-unit-$n
done
prompts() { grep -c "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" || true; }
clears() { grep -c "^$box wldn-1 agent send-keys $1 ctrl+c$" "$CREW_TEST_LOG" || true; }
# what the log holds for an agent's prompts and ctrl+c, in order: P for a prompt, C for a ctrl+c
order() { sed -n "s/^$box wldn-1 agent prompt $1 .*/P/p; s/^$box wldn-1 agent send-keys $1 ctrl+c$/C/p" "$CREW_TEST_LOG" | tr -d '\n'; }
typed() { herdr_state $box wldn-1 ".agents[] | select(.name == \"$1\") | .typed // \"\""; }
# received <agent>: the prompts its session's transcript holds, one a line
received() {
  local sid; sid=sid-$(herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key" | tr : -)
  as $box bash -c 'cat "$HOME"/.claude/projects/*/"$1".jsonl 2>/dev/null' _ "$sid" | jq -r '.message.content'
}

expect_ok crewpy stage-prompt swb-1-unit-1 "/opsx:apply a Close the footer."
eq "$(order swb-1-unit-1)" "P"
eq "$(received swb-1-unit-1)" $'<command-name>/opsx:apply</command-name>\n<command-args>a Close the footer.</command-args>'
ok "a prompt taken at once is sent once, read back from the transcript on the agent's host, and nothing is pressed"

herdr_box stub leave swb-1-unit-2 1
expect_ok crewpy stage-prompt swb-1-unit-2 "Fix: The banner flickers."
eq "$(order swb-1-unit-2)" "PCP"
eq "$(received swb-1-unit-2)" "Fix: The banner flickers."
eq "$(typed swb-1-unit-2)" ""
ok "a prompt left typed is cleared with one ctrl+c and sent once more, and received once, alone"

herdr_box stub leave swb-1-unit-3 2
expect_fail "sent twice" crewpy stage-prompt swb-1-unit-3 "/opsx:verify a"
eq "$(order swb-1-unit-3)" "PCPC"
eq "$(received swb-1-unit-3)" ""
eq "$(typed swb-1-unit-3)" ""
ok "a prompt not taken twice is cleared twice, and nothing is left typed"

# An agent never ready, and one that went to work with no record of its prompt, each take crew's full wait: side by side.
herdr_box stub status swb-1-unit-4 blocked
herdr_box stub leave swb-1-unit-5 1 working
crewpy stage-prompt swb-1-unit-4 "/opsx:apply b" > "$T/blocked.out" 2>&1 & blocked=$!
crewpy stage-prompt swb-1-unit-5 "/opsx:apply c" > "$T/working.out" 2>&1 & working=$!
rc=0; wait $blocked || rc=$?
eq "$rc" "3"
eq "$(cat "$T/blocked.out")" "as it was waiting on a question in its pane"
eq "$(prompts swb-1-unit-4)" "0"
eq "$(typed swb-1-unit-4)" ""
ok "an agent waiting on a question in its pane throughout is never sent the prompt, and the reason names the question"

rc=0; wait $working || rc=$?
eq "$rc" "1"
eq "$(cat "$T/working.out")" "it went to work, and its transcript showed no prompt received 60 seconds on, so it may have taken it"
eq "$(order swb-1-unit-5)" "P"
ok "an agent that went to work with no record of its prompt is neither pressed nor sent it again, and crew says it can't tell"

CREW_TAKEN_WITHIN=0 expect_fail "CREW_TAKEN_WITHIN is a whole number of seconds above 0, not \"0\"" crewpy stage-prompt swb-1-unit-1 "/opsx:apply a"
eq "$(order swb-1-unit-1)" "P"
ok "a limit crew can't read is refused before anything is typed"
