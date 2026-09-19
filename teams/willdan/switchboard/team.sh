# The Switchboard team. Every NAME here is a {{NAME}} in the role briefs.
TEAM=switchboard
SYSTEM=Switchboard
KIT_NAME=switchboard-kit
ORG=willdan
MACHINE=mac-studio
SESSION=willdan
KIT_REPO=switchboard-kit/main
DESIGN_REPO=willdan-blueprints/main
# How many coders the team has. Each builds one change at a time, in that change's own worktree.
CODERS=2
REPORTS=~/.local/state/switchboard-team/reports
FABLE_RECORDS='in switchboard-kit `docs/spec/` and the blueprints book'
DESIGN_DOCS='`docs/spec/` or the book'
CITE='the `docs/spec/` pages'
DONT_EDIT="Don't edit \`docs/spec/\`, \`books/switchboard-kit/\` or switchboard-kit's \`openspec/\` yourself."
PLAN_EXAMPLE=', such as `plan-mvp-stage1.md`'
TIER='the tier it is proven at (T0 to T3, `docs/spec/self-hosting.md`)'
# Run once inside a new worktree before a coder starts in it. Empty when the repository's own hooks do it.
WORKTREE_PREPARE='PATH=$KIT/.devenv/profile/bin:$PATH bun install --frozen-lockfile'
