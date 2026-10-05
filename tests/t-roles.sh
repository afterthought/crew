# Each role starts from its agent definition: the model and effort in its frontmatter, unless the teams file
# overrides them for the team or partition, and its brief appended to Claude Code's system prompt.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
box=$(space chuck-herdr-alpha willdan); mac=$(space mac-studio madswan)
mkdir -p "$box"/{switchboard-kit,willdan-blueprints,breadboard-kit,atlas-kit}/main "$mac/blueprints/main" "$box/switchboard-kit/places/the-unit"
mkdir -p "$(home_of chuck-herdr-alpha)/.local/state/swb-1-team"
echo "unit-2 unit the-unit $box/switchboard-kit/places/the-unit" > "$(home_of chuck-herdr-alpha)/.local/state/swb-1-team/slots"

role() {  # role <host> <scope> <role> [stage]: start it with the stub claude, print and keep its launch
  : > "$CREW_TEST_CLAUDE_LOG"
  as "$1" "$CREW/plugin/bin/crew-role" "${@:2}" || fail "crew-role ${*:2} failed"
  launch=$(python3 -c 'import json, sys
l = json.loads(open(sys.argv[1]).read())
a = l["argv"]; i = a.index("--append-system-prompt")
print(" ".join(a[:i]), "| cwd", l["cwd"], "| agent", l["agent"], "| label", l["label"], "| brief", len(a[i + 1]), "chars")' "$CREW_TEST_CLAUDE_LOG")
  echo "${*:2}: $launch"
}

opus='--model claude-opus-5-5[1m]'; fable='--model claude-fable-5-1'
role chuck-herdr-alpha swb-1 conductor;     has "$launch" "$opus --effort high"; has "$launch" "--name swb-1-conductor"
first=$(jq -r .session "$CREW_TEST_CLAUDE_LOG")
has "$launch" "cwd $box/switchboard-kit/main"; has "$launch" "--add-dir $box/switchboard-kit --add-dir $box/willdan-blueprints/main"
has "$launch" "agent swb-1-conductor | label wldn"
role chuck-herdr-alpha swb-1 ops;           has "$launch" "$opus --effort high"; has "$launch" "--name swb-1-ops"
role chuck-herdr-alpha swb-1 unit-2 construct; has "$launch" "$opus --effort high"; has "$launch" "cwd $box/switchboard-kit/places/the-unit"
role chuck-herdr-alpha swb-1 unit-2 code;   has "$launch" "$opus --effort xhigh"; has "$launch" "--name swb-1-unit-2"
role chuck-herdr-alpha swb-1 unit-2 verify; has "$launch" "$opus --effort high"
role chuck-herdr-alpha swb-1 unit-2 merge;  has "$launch" "$opus --effort xhigh"
role chuck-herdr-alpha swb-1 unit-2 fix;    has "$launch" "$opus --effort xhigh"
role chuck-herdr-alpha wldn design;         has "$launch" "$fable --effort xhigh"; has "$launch" "--name wldn-design"
has "$launch" "cwd $box/willdan-blueprints/main"; has "$launch" "--add-dir $box/atlas-kit/main --add-dir $box/breadboard-kit/main --add-dir $box/switchboard-kit/main"
role chuck-herdr-alpha wldn planner;        has "$launch" "$fable --effort xhigh"; has "$launch" "--name wldn-planner"
role chuck-herdr-alpha wldn ops;            has "$launch" "$opus --effort high"; has "$launch" "--name wldn-ops"
role chuck-herdr-alpha wldn dispatcher;     has "$launch" "$opus --effort medium"; has "$launch" "--name wldn-dispatch-chuck-herdr-alpha"
role chuck-herdr-alpha wldn operator;       has "$launch" "$opus --effort medium"; has "$launch" "--name wldn-operator-chuck-herdr-alpha"
has "$launch" "cwd $box |"
role mac-studio madswan planner;            has "$launch" "$fable --effort xhigh"; has "$launch" "cwd $mac/blueprints/main"
ok "every role starts on its definition's model and effort"

edit teams "$(part wldn)['roles'] = {'planner': {'effort': 'max'}, 'operator': {'model': 'claude-opus-5-5'}}; $(team swb-1)['roles'] = {'coder': {'effort': 'max', 'model': 'claude-sonnet-5-5'}}"
role chuck-herdr-alpha wldn planner;        has "$launch" "$fable --effort max"
role mac-studio madswan planner;            has "$launch" "$fable --effort xhigh"
role chuck-herdr-alpha wldn operator;       has "$launch" "--model claude-opus-5-5 --effort medium"
role chuck-herdr-alpha swb-1 unit-2 merge;  has "$launch" "--model claude-sonnet-5-5 --effort max"
role chuck-herdr-alpha swb-1 unit-2 construct; has "$launch" "$opus --effort high"
role chuck-herdr-alpha swb-2 conductor;     has "$launch" "$opus --effort high"
ok "an override changes its role for that team or partition only"

role chuck-herdr-alpha swb-1 conductor resume; has "$launch" "--name swb-1-conductor --resume $first"
role mac-studio madswan design resume;   has "$launch" "--name madswan-design"; lacks "$launch" "--resume"
expect_fail "no role 'fable' on team swb-1" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" swb-1 fable
expect_fail "swb-1 has 4 unit slots, so no unit-5" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" swb-1 unit-5 code
expect_fail "swb-1-unit-1 holds no unit or fix" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" swb-1 unit-1 code
expect_fail "which stage?" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" swb-1 unit-2 apply
expect_fail "no role 'conductor' at wldn's main level" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" wldn conductor
ok "an unknown role, slot or stage is refused"
