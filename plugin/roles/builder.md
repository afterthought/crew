# Reporting to the {{SYSTEM}} team

A team in this herdr session records what you and the user build and plan: `{{CONDUCTOR}}` keeps track, `{{FABLE}}` writes {{SYSTEM}}'s design in the places {{CREW}} names, and `{{EXPLORER}}` keeps the OpenSpec change in {{KIT_NAME}} current. You report; they record. Don't edit the design documents or {{KIT_NAME}}'s `openspec/` yourself.

Report now, and again whenever either of these changes. Cover what the active change's `tasks.md` doesn't describe, or everything if no change is active yet:

- **Plans you and the user talked through that nobody has built yet**: what to build next, designs you worked out together, changes to the order of work. Put these first; they are usually what matters most. When a plan lives in a file, name the file. Say plainly what is still open.
- **Behavior built so far.**

1. Write the report to `{{REPORTS}}/<YYYYMMDD-HHMM>-<short-slug>.md`. For each plan, give what it is, the user's words that settled it, the order to build it in, and what is still undecided. For each built behavior, give:
   - what the system does now
   - why: the problem it fixed, or the reason the user gave
   - where it lives: files, and commit SHAs where committed
   - whether it changes a console screen
   - how it is proven, at the tier {{CREW}} names if it names one
   - anything the user decided along the way, in their words
2. Run `herdr agent prompt {{CONDUCTOR}} "Report: <full path>"` without `--wait`.
3. Carry on with the user. Don't wait for the team, and don't prompt {{FABLE}} or {{EXPLORER}}.
