# crew's test runners enter crew's devenv shell themselves (tests.1, record 0024). Started outside it, from anywhere,
# tests/run and tests/suite each run themselves again inside it with devenv shell -- from the checkout they are in, and
# go on there; a devenv shell that sets no DEVENV_ROOT stops them rather than looping; and with no devenv on the path
# they say so and run nothing.
# Reads: tests/suite
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
mkdir -p "$T/bin" "$T/elsewhere"

# A stand-in devenv first on PATH: `devenv shell -- <command>` logs where it ran and what, then runs the command with
# DEVENV_ROOT the folder it ran in, as devenv does; with $T/no-root it sets none.
cat > "$T/bin/devenv" <<STANDIN
#!/bin/sh
echo "\$(pwd -P) \$*" >> "$T/devenv.log"
[ "\$1" = shell ] && [ "\$2" = -- ] || { echo "stand-in devenv: only shell -- <command>" >&2; exit 2; }
shift 2
[ -e "$T/no-root" ] || export DEVENV_ROOT="\$(pwd -P)"
exec "\$@"
STANDIN
chmod +x "$T/bin/devenv"
# outside <command...>: run from $T/elsewhere with no devenv shell in the environment; output in $out, exit in $rc
outside() { rc=0; out=$(cd "$T/elsewhere" && env -u DEVENV_ROOT PATH="$T/bin:$PATH" "$@" 2>&1) || rc=$?; }

outside "$CREW/tests/run" no-such
eq "$(cat "$T/devenv.log")" "$CREW shell -- $CREW/tests/run no-such"
has "$out" "no test t-no-such"; eq "$rc" 1
: > "$T/devenv.log"
outside "$CREW/tests/suite" --no-such
eq "$(cat "$T/devenv.log")" "$CREW shell -- $CREW/tests/suite --no-such"
has "$out" "usage: tests/suite"; eq "$rc" 2
ok "tests/run and tests/suite started outside the shell run themselves again inside it, from their checkout, and go on there"

touch "$T/no-root"; : > "$T/devenv.log"
outside "$CREW/tests/run" no-such
eq "$rc" 2; has "$out" "devenv shell set no DEVENV_ROOT"
eq "$(wc -l < "$T/devenv.log" | tr -d ' ')" "1"
rm "$T/no-root"
rc=0; out=$(cd "$T/elsewhere" && env -u DEVENV_ROOT PATH="$(path_without devenv)" "$CREW/tests/suite" 2>&1) || rc=$?
eq "$rc" 2; has "$out" "devenv is not on this host's path"
ok "a shell that sets no DEVENV_ROOT stops a runner rather than looping, and with no devenv on the path it runs nothing"
