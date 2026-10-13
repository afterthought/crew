{ pkgs, config, ... }:
let
  # proto from moonrepo's own release build, at the version sluice pins: the one tool devenv holds that installs the
  # others. Linux takes the static musl build, so no loader needs patching.
  proto =
    let
      version = "0.63.1";
      target = {
        aarch64-darwin = "aarch64-apple-darwin";
        x86_64-darwin = "x86_64-apple-darwin";
        aarch64-linux = "aarch64-unknown-linux-musl";
        x86_64-linux = "x86_64-unknown-linux-musl";
      }.${pkgs.stdenv.hostPlatform.system} or (throw "proto ${version}: no release build for ${pkgs.stdenv.hostPlatform.system}");
      hashes = {
        aarch64-apple-darwin = "8bfde4c862381eeb6e82d0858bb6215732cbd1e384e4eae45da8fa08095e0ffd";
        x86_64-apple-darwin = "aaaff78c7125de1b765f00177f35da75ee16fb1363e07632ace27213ff5d893b";
        aarch64-unknown-linux-musl = "111f5b6a38d3979ebafbc095c8d91ef69c99d1f018addb3582179d4ab91b3441";
        x86_64-unknown-linux-musl = "8596b98ccd833d1203e71931ba25e866d3239f9d3859c922a035a7b830f29d17";
      };
    in
    pkgs.stdenvNoCC.mkDerivation {
      pname = "proto";
      inherit version;
      src = pkgs.fetchurl {
        url = "https://github.com/moonrepo/proto/releases/download/v${version}/proto_cli-${target}.tar.xz";
        sha256 = hashes.${target};
      };
      sourceRoot = "proto_cli-${target}";
      installPhase = ''
        runHook preInstall
        install -Dm755 -t $out/bin proto proto-shim
        runHook postInstall
      '';
    };
in
{
  # The system tools crew's own scripts call. herdr, wt and openspec come from the machine and from each team's
  # repository. recutils (recsel, recfix) reads and checks the bolt plan. proto installs and activates the
  # application tools .prototools pins: moon, which runs crew's suite as tasks in parallel and replays a task whose
  # inputs already passed (tests/suite, .moon/workspace.yml; record 0008), and Python, at the minor every host runs
  # crew on, with uv. pytest runs the logic and contract tiers (record 0022), synced by moon from tests/pyproject.toml
  # into tests/.venv; crew's own Python imports nothing but the standard library (code.1).
  packages = [ pkgs.jq proto pkgs.recutils ];

  # moon's task archives (.moon/cache/outputs) are a link into the git common dir, so every worktree of crew on a
  # host and its main checkout share them: a test the coder passed replays at the merge's gate, and one the gate
  # passed replays in the bolt's verification. The rest of .moon/cache stays the checkout's own, since it records
  # the checkout's absolute paths. moon reads no setting for where its cache lives, hence the link.
  #
  # proto's and moon's homes are crew's own, in the git common dir, so every worktree shares one install: moon puts
  # both homes' bin first on every task's PATH, and a user's own installs there (an older moon among them) must never
  # run in a task. Entering the shell installs what .prototools pins when a pin is missing from the proto home and can
  # be installed, then activates it. A checkout that is no git repository gets neither link nor homes of its own.
  #
  # proto's install runs only for a missing pin, read from .prototools against proto's layout (tools/<tool>/<version>
  # under its home, proto 0.63.1): one that finds every pin installed still took 2.8 of a warm entry's 3.2 seconds
  # (median of ten, mac-studio at a load of 15, 2026-10-13), and an agent enters the shell for every command it runs
  # through it (record 0024); without it a warm entry took 0.37 seconds.
  enterShell = ''
    if _crew_common="$(git -C "${config.devenv.root}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
      _moon_cache="${config.devenv.root}/.moon/cache"
      [ -L "$_moon_cache" ] && rm -f "$_moon_cache"
      mkdir -p "$_crew_common/moon-outputs" "$_moon_cache"
      if [ ! -L "$_moon_cache/outputs" ]; then
        rm -rf "$_moon_cache/outputs"
        ln -s "$_crew_common/moon-outputs" "$_moon_cache/outputs"
      fi
      export PROTO_HOME="$_crew_common/proto" MOON_HOME="$_crew_common/moon-home"
    fi
    unset _crew_common _moon_cache
    if [ -f "${config.devenv.root}/.prototools" ]; then
      while read -r _tool _eq _version _; do
        case $_tool in "" | \#*) continue ;; \[*) break ;; esac
        if [ ! -d "''${PROTO_HOME:-$HOME/.proto}/tools/$_tool/''${_version//\"/}" ]; then
          ${proto}/bin/proto install --config-mode upwards >/dev/null 2>&1 || true
          break
        fi
      done < "${config.devenv.root}/.prototools"
    fi
    unset _tool _eq _version
    eval "$(${proto}/bin/proto activate bash --export --no-bin --config-mode upwards 2>/dev/null)"
  '';
}
