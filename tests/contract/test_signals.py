"""What crew assumes of git when the board reads the signals no move has taken, at a tip of a branch it fetched:
board.signals_at lists signals/<capture>/<nn>-<name>.md by git ls-tree and reads each capture and signal with
git cat-file at that tip, never a checkout (state.4; the crew-board spec's Inception lane)."""
import board
import plan


def test_a_moved_signal_is_left_out_and_each_is_read_with_its_captures_time_and_who_captured_it(repo, monkeypatch):
    monkeypatch.setattr(plan, "cache", lambda name: repo.path)  # crew's cache of the blueprints, as fetch leaves it
    cap = "---\ncapture: 2026-10-01-planning\nsource: meeting\ncaptured_by: wldn-planner\nat: 2026-10-01T12:00:00+02:00\nsignals: 2\n---\n"
    tip = repo.commit("signals: the planning meeting", {
        "signals/2026-10-01-planning/capture.md": cap,
        "signals/2026-10-01-planning/01-zones.md": "---\nsignal: 2026-10-01-planning/01-zones\nkind: ask\n---\n\nEvery apex is a zone.\n",
        "signals/2026-10-01-planning/02-tenants.md": "---\nsignal: 2026-10-01-planning/02-tenants\nkind: constraint\n---\n\n\nTenants never share.\n"})
    repo.commit("docs: later", {"signals/2026-10-01-planning/03-later.md": "---\nkind: ask\n---\n\nAfter the tip.\n"})
    got = board.signals_at("WilldanGroup/willdan-blueprints", tip, "blueprints", {"2026-10-01-planning/01-zones"})
    assert got == [{"signal": "2026-10-01-planning/02-tenants", "home": "blueprints", "captured_by": "wldn-planner",
                    "at": "2026-10-01T10:00:00Z", "kind": "constraint", "first": "Tenants never share."}]
