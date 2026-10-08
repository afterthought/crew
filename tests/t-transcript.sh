# What crew reads of a Claude transcript to check a signal's excerpt: every string of every complete JSON line,
# whitespace aside, but crew signal commands, what the agent wrote, and the writing of an excerpt's file. The grade,
# the source record (the latest that holds the words) and who asserted it. Claude Code writes the running command's
# record only once it returns, so the transcript is taken for the live session's when its last record was written in
# the last 15 minutes; a paraphrase is refused only then.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
h=mac-studio
# verdict <session> <excerpt> [skip...]: the grade, who asserted it, the source line's number and uuid, and the
# reason when there is one; STAGE_BY names the conductor whose stage the session runs
verdict() {
  as $h python3 -c 'import os, sys; sys.path.insert(0, sys.argv[1]); import transcript
v = transcript.check(sys.argv[2], sys.argv[3], sys.argv[4:], os.environ.get("STAGE_BY"))
print(" ".join(str(x) for x in (v.grade, v.asserted_by, v.n, v.uuid)) + (f": {v.reason}" if v.reason else ""))' "$CREW/plugin/lib" "$@"
}
# An earlier crew signal, as the agent's Bash call records it; its --excerpt holds the words too, and is never a source.
cmd='{"type":"assistant","uuid":"a-9","message":{"role":"assistant","content":[{"type":"tool_use","name":"Bash","input":{"command":"/w/crew/main/plugin/bin/crew signal open-groups \"Templates need a check.\" --excerpt \"open security groups\""}}]}}'

transcript $h s-typed .claude-sub-ia >/dev/null <<EOF
{"type":"user","uuid":"u-1","timestamp":"$(ago 1)","message":{"role":"user","content":"Also check the templates for open security groups, please."}}
{"type":"assistant","uuid":"a-1","message":{"role":"assistant","content":[{"type":"text","text":"I'll record that."}]}}
EOF
eq "$(verdict s-typed "open security groups")" "verified user 1 u-1"
ok "typed text is verified, asserted by the user, in an account's own folder"

transcript $h s-tool >/dev/null <<'EOF'
{"type":"user","uuid":"u-2","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"sg-0a1 ingress 0.0.0.0/0: open security groups in 3 templates"}]}}
{"type":"user","uuid":"u-3","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":[{"type":"text","text":"WARN open security groups in stack edge"}]}]}}
EOF
eq "$(verdict s-tool "open security groups in 3 templates")" "verified tool 1 u-2"
eq "$(verdict s-tool "open security groups in stack edge")" "verified tool 2 u-3"
ok "a tool's output, with string content or a list of blocks, is verified, asserted by a tool"

transcript $h s-tell >/dev/null <<EOF
{"type":"user","uuid":"u-4","message":{"role":"user","content":"[crew tell from swb-2-conductor] The deploy left open security groups behind."}}
{"type":"user","uuid":"u-5","message":{"role":"user","content":"[crew tell from $me@mac-studio] Leave the open security groups for now."}}
{"type":"user","uuid":"u-6","message":{"role":"user","content":"[crew] plan(edge): open security groups move to the queue ($me@mac-studio)"}}
EOF
eq "$(verdict s-tell "The deploy left open security groups behind.")" "verified agent:swb-2-conductor 1 u-4"
eq "$(verdict s-tell "Leave the open security groups for now.")" "verified user 2 u-5"
eq "$(verdict s-tell "open security groups move to the queue")" "verified crew 3 u-6"
ok "what crew tell carried is asserted by its sender, the user's own tell by the user, and crew's notice by crew"

# A stage's own prompts, as Claude Code records them: code's slash command and its skill's text after it, a fix, a merge.
transcript $h s-stage >/dev/null <<'EOF'
{"type":"user","uuid":"u-20","message":{"role":"user","content":"<command-message>opsx:apply</command-message>\n<command-name>/opsx:apply</command-name>\n<command-args>edge-groups Close the open security groups verify found.</command-args>"}}
{"type":"user","uuid":"u-21","isMeta":true,"message":{"role":"user","content":[{"type":"text","text":"Implement tasks from an OpenSpec change.\n\n\nARGUMENTS: edge-groups Close the open security groups verify found."}]}}
{"type":"user","uuid":"u-22","message":{"role":"user","content":"Fix: The deploy leaves open security groups on stack edge."}}
{"type":"user","uuid":"u-23","message":{"role":"user","content":"Merge fix/smoke-2/edge into bolt/smoke-2: wt merge bolt/smoke-2 --no-squash --no-remove"}}
{"type":"user","uuid":"u-24","message":{"role":"user","content":"Leave Fix: as it is, the open security groups are mine.\n\nARGUMENTS: edge-groups Close the open security groups verify found."}}
EOF
export STAGE_BY=swb-2-conductor
eq "$(verdict s-stage "/opsx:apply")" "verified agent:swb-2-conductor 1 u-20"
eq "$(verdict s-stage "Implement tasks from an OpenSpec change.")" "verified agent:swb-2-conductor 2 u-21"
eq "$(verdict s-stage "open security groups on stack edge")" "verified agent:swb-2-conductor 3 u-22"
eq "$(verdict s-stage "wt merge bolt/smoke-2")" "verified agent:swb-2-conductor 4 u-23"
eq "$(verdict s-stage "the open security groups are mine")" "verified user 5 u-24"
eq "$(verdict s-stage "Close the open security groups verify found.")" "verified user 5 u-24"
unset STAGE_BY
eq "$(verdict s-stage "open security groups on stack edge")" "verified user 3 u-22"
eq "$(verdict s-stage "Implement tasks from an OpenSpec change.")" "verified user 2 u-21"
ok "a stage's own prompt, with its command's skill text after it, is its conductor's; elsewhere, or not next, the user's"

transcript $h s-stage-args >/dev/null <<'EOF'
{"type":"user","uuid":"u-25","message":{"role":"user","content":"<command-message>opsx:verify</command-message>\n<command-name>/opsx:verify</command-name>\n<command-args>edge-groups The groups still open?</command-args>"}}
{"type":"user","uuid":"u-26","isMeta":true,"message":{"role":"user","content":[{"type":"text","text":"Verify that an implementation matches the change.\n\n\nARGUMENTS: edge-groups The groups still open?"}]}}
EOF
eq "$(STAGE_BY=swb-2-conductor verdict s-stage-args "The groups still open?")" "verified agent:swb-2-conductor 2 u-26"
ok "the words a stage's command carries are the conductor's in the skill text that ends with them"

transcript $h s-own >/dev/null <<EOF
{"type":"user","uuid":"u-7","message":{"role":"user","content":"Have a look at the templates."}}
{"type":"assistant","uuid":"a-7","message":{"role":"assistant","content":[{"type":"text","text":"The templates leave open security groups."}]}}
$cmd
EOF
eq "$(verdict s-own "The templates leave open security groups.")" "refused unknown None None"
eq "$(verdict s-own "the user wants every template locked down")" "refused unknown None None"
eq "$(verdict s-own "open security groups")" "refused unknown None None"
ok "words only in the agent's own record, nowhere, or only in a crew signal command are refused"

transcript $h s-untyped >/dev/null <<'EOF'
{"uuid":"x-1","payload":{"text":"open security groups everywhere"}}
{"payload":{"command":"crew signal open-groups --excerpt-file /tmp/e.txt"}}
EOF
eq "$(verdict s-untyped "open security groups everywhere")" "found unknown 1 x-1"
ok "a transcript with no type fields grades found, the line it is in its source"

printf '%s\nthis is not JSON\n' '{"type":"user","message":{"content":"open security groups"}}' | transcript $h s-garbled >/dev/null
eq "$(verdict s-garbled "open security groups")" "unverified unknown None None: the transcript is not JSON lines"
eq "$(verdict "" "open security groups")" "unverified unknown None None: herdr names no session"
eq "$(verdict s-none "open security groups")" "unverified unknown None None: no transcript for session s-none"
ok "a file that is not JSON lines, no session and no file each grade unverified"

transcript $h s-stale >/dev/null <<EOF
{"type":"user","uuid":"u-8","timestamp":"$(ago 20)","message":{"role":"user","content":"open security groups"}}
{"type":"assistant","uuid":"a-8","message":{"role":"assistant","content":[{"type":"text","text":"Noted."}]}}
EOF
eq "$(verdict s-stale "open security groups")" "unverified unknown None None: session s-stale's transcript has not been written for 20 minutes: crew may be reading another session's"
f=$(transcript $h s-quiet <<'EOF'
{"type":"user","uuid":"u-9","message":{"role":"user","content":"open security groups"}}
EOF
)
touch -t 202001010000 "$f"
out=$(verdict s-quiet "open security groups")
has "$out" "unverified unknown None None: session s-quiet's transcript has not been written for "
has "$out" " minutes: crew may be reading another session's"
f=$(transcript $h s-recent <<EOF
{"type":"user","uuid":"u-10","timestamp":"$(ago 30)","message":{"role":"user","content":"open security groups"}}
{"type":"user","uuid":"u-11","timestamp":"$(ago 14)","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t9","content":"done"}]}}
EOF
)
touch -t 202001010000 "$f"
eq "$(verdict s-recent "open security groups")" "verified user 1 u-10"
ok "a transcript whose last record, by its timestamp or else the file's time, is over 15 minutes old grades unverified"

{ printf '%s\n' '{"type":"user","uuid":"u-12","message":{"role":"user","content":"check   for open\n   security\tgroups"}}'
  printf '%s' '{"type":"user","uuid":"u-13","message":{"content":"open sec'; } | transcript $h s-space >/dev/null
eq "$(verdict s-space $'open security\n groups')" "verified user 1 u-12"
ok "whitespace differs freely, and a trailing line still being written is left out"

transcript $h s-twice >/dev/null <<'EOF'
{"type":"user","uuid":"u-14","message":{"role":"user","content":"open security groups, again"}}
{"type":"user","uuid":"u-15","message":{"role":"user","content":"I said: open security groups"}}
EOF
eq "$(verdict s-twice "open security groups")" "verified user 2 u-15"
ok "of two records holding the words, the latest is the source"

transcript $h s-file >/dev/null <<'EOF'
{"type":"user","uuid":"u-16","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t3","content":"File created successfully at: /tmp/e.txt"}]},"toolUseResult":{"type":"create","filePath":"/tmp/e.txt","content":"the words I wrote myself"}}
EOF
eq "$(verdict s-file "the words I wrote myself" /tmp/e.txt)" "refused unknown None None"
eq "$(verdict s-file "the words I wrote myself")" "verified tool 1 u-16"
ok "with --excerpt-file, the records that wrote the file are not searched"
