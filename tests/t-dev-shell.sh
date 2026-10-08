# A Claude session in a crew checkout works inside crew's devenv shell. With a stand-in devenv, the checkout's
# SessionStart hook enters the shell and appends what it set or changed to the session's env file, keeping a line
# crew's own hook wrote there, printing nothing and leaving the shell's bookkeeping out; it leaves alone a session
# with no env file and one already in this checkout's shell; and when devenv fails or is missing it changes
# nothing, still exits 0, and gives the session one line that names no workaround. The hook is the one
# .claude/settings.json runs. tests/run refuses to start outside a devenv shell. No CLAUDE.md, README, brief or
# skill tells an agent to wrap a command in `devenv shell --`, and a checkout carries the .envrc and ignores
# devenv's and direnv's working files.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
hook=$CREW/.claude/hooks/devenv-shell
mkdir -p "$T/bin" "$T/repo" "$T/profile/bin" "$T/empty"
repo=$(cd "$T/repo" && pwd -P)

# A stand-in devenv first on PATH, as devenv behaves for what the hook reads: `devenv shell -- <command>` prints to
# its stdout, then runs the command in the checkout with the shell's variables set and its profile first on PATH.
cat > "$T/bin/devenv" <<EOF
#!/bin/sh
echo "\$*" >> "$T/devenv.log"
[ "\$1" = shell ] && [ "\$2" = -- ] && [ \$# -gt 2 ] || { echo "stand-in devenv: only shell -- <command>" >&2; exit 2; }
[ -e "$T/devenv-fails" ] && { echo "stand-in devenv: failed" >&2; exit 1; }
shift 2
echo "stand-in devenv: entering the shell"
export DEVENV_ROOT="\$(pwd -P)" DEVENV_PROFILE="$T/profile" PATH="$T/profile/bin:\$PATH" CREW_SHELL_PROBE='a b' TMPDIR="$T/devenv-tmp"
exec "\$@"
EOF
chmod +x "$T/bin/devenv"; export PATH="$T/bin:$PATH"

# start [env...]: the hook as Claude Code runs it at a session's start in $T/repo, outside any shell; its stdout is
# in $out and its exit in $rc.
start() { rc=0; out=$(env -u DEVENV_ROOT "$@" CLAUDE_PROJECT_DIR="$T/repo" python3 "$hook" </dev/null 2>"$T/hook.err") || rc=$?; }
logged() { [[ -s $T/devenv.log ]]; }

echo 'export CREW_AGENT=crw-1-unit-1' > "$T/env"
start CLAUDE_ENV_FILE="$T/env"
eq "$rc" 0; eq "$out" ""
logged || fail "the hook never ran devenv"
eq "$(head -1 "$T/env")" 'export CREW_AGENT=crw-1-unit-1'
for v in TMPDIR PWD HOME SHLVL; do grep -q "^export $v=" "$T/env" && fail "the hook exported $v:"$'\n'"$(cat "$T/env")"; done
read -r root agent probe path < <(env -u DEVENV_ROOT -u CREW_AGENT -u CREW_SHELL_PROBE bash --noprofile --norc -c \
  '. "$1"; printf "%s\t%s\t%s\t%s\n" "$DEVENV_ROOT" "$CREW_AGENT" "${CREW_SHELL_PROBE// /_}" "$PATH"' _ "$T/env")
eq "$root" "$repo"; eq "$agent" crw-1-unit-1; eq "$probe" a_b
[[ $path == "$T/profile/bin:"* ]] || fail "the session's PATH does not start with the shell's profile: $path"
ok "the hook enters the shell silently, keeps crew's own line, and leaves the shell's bookkeeping out"

rm -f "$T/devenv.log"
start -u CLAUDE_ENV_FILE
eq "$rc" 0; eq "$out" ""
logged && fail "the hook ran devenv with no env file"
ok "a session with no env file is left alone"

cp "$T/env" "$T/env.before"
rc=0; out=$(DEVENV_ROOT=$T/repo CLAUDE_PROJECT_DIR=$T/repo CLAUDE_ENV_FILE=$T/env python3 "$hook" </dev/null 2>&1) || rc=$?
eq "$rc" 0; eq "$out" ""
cmp -s "$T/env" "$T/env.before" || fail "the hook changed the env file of a session already in the shell"
logged && fail "the hook ran devenv for a session already in the shell"
ok "a session already in this checkout's shell is left alone"

# could_not <why>: the hook changed nothing, exited 0, and gave the session one line naming no workaround.
could_not() {
  eq "$rc" 0
  cmp -s "$T/env" "$T/env.before" || fail "the hook changed the env file when $1:"$'\n'"$(cat "$T/env")"
  eq "$(wc -l <<<"$out" | tr -d ' ')" 1
  has "$out" "not in crew's devenv shell"; lacks "$out" "devenv shell --"
}
touch "$T/devenv-fails"
start CLAUDE_ENV_FILE="$T/env"
logged || fail "the hook never ran devenv"
could_not "devenv failed"
rm -f "$T/devenv-fails"
py=$(command -v python3)
rc=0; out=$(env -u DEVENV_ROOT PATH="$T/empty" CLAUDE_PROJECT_DIR="$T/repo" CLAUDE_ENV_FILE="$T/env" "$py" "$hook" </dev/null 2>/dev/null) || rc=$?
could_not "devenv was missing"
ok "a session that can't enter the shell starts as it was and is told so in one line"

hooks=$(python3 -c 'import json, sys; [print(h["command"], h["timeout"]) for e in json.load(open(sys.argv[1]))["hooks"]["SessionStart"] for h in e["hooks"]]' "$CREW/.claude/settings.json")
eq "$(wc -l <<<"$hooks" | tr -d ' ')" 1
has "$hooks" '.claude/hooks/devenv-shell"'; [[ $hooks == *" 600" ]] || fail "the hook's timeout is not 600: $hooks"
ok ".claude/settings.json runs the hook at every start"

mkdir -p "$T/tmp"
rc=0; out=$(env -u DEVENV_ROOT TMPDIR="$T/tmp" "$CREW/tests/run" t-docs 2>&1) || rc=$?
eq "$rc" 2; has "$out" "devenv shell"
[[ -z $(ls -A "$T/tmp") ]] || fail "tests/run made a scratch directory outside the shell: $(ls -A "$T/tmp")"
ok "tests/run refuses to start outside a devenv shell"

wrapped=$(grep -rlF -- 'devenv shell --' "$CREW/CLAUDE.md" "$CREW/README.md" "$CREW/plugin/roles" "$CREW/plugin/skills" || true)
[[ -z $wrapped ]] || fail "these tell an agent to wrap a command in devenv shell --:"$'\n'"$wrapped"
ok "no doc an agent reads wraps a command in devenv shell --"

grep -qxF 'use devenv' "$CREW/.envrc" || fail ".envrc does not enter devenv"
for line in .devenv/ .direnv/ '!.envrc'; do grep -qxF -- "$line" "$CREW/.gitignore" || fail ".gitignore lacks $line"; done
ok "a checkout carries the .envrc and ignores devenv's and direnv's working files"
