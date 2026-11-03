"""What the run record holds of a bolt's conflict with main (rail-cards "A row forecast to conflict with main takes main
first until a fix takes main in"): plan.main_conflict for the conflict with main the record holds at the bolt's head,
and plan.said_heads for what the landings card's raise has said, a forecast found while the bolt was left counting only
while it still is."""
import plan


class TestSaidHeads:
    """What the landings card's raise reads as said once (plan.said_heads)."""

    def test_what_was_said_counts_a_forecast_found_while_left_only_while_the_bolt_is_still_left(self):
        entries = [dict(Act="forecast", On=["bolt/t"], Heads="bolt/t@1111111 main@2222222", Reached="left"),
                   dict(Act="forecast", On=["bolt/s"], Heads="bolt/s@1111111 main@2222222", Reached="wait"),
                   dict(Act="amendment", On=["unit/a", "unit/b"], Heads="a b@3333333", Reached="prompt"),
                   dict(Act="forecast", On=["bolt/r"], Heads="bolt/r@1111111", Reached="wait", Refused="no")]
        assert plan.said_heads(entries, {"t"}) == {"bolt/t@1111111 main@2222222", "bolt/s@1111111 main@2222222", "a b@3333333"}
        assert plan.said_heads(entries, ()) == {"bolt/s@1111111 main@2222222", "a b@3333333"}


class TestMainConflict:
    """What the run record holds of a bolt's conflict with main at its present head (rail-cards "A row forecast to
    conflict with main takes main first"), as a conductor's wait or a landings card's raise recorded it."""
    H, OLD = "1" * 40, "9" * 40

    def entry(self, heads, paths="docs/builds.md", on=("bolt/t",), **more):
        return dict(Act="forecast", On=list(on), Heads=heads, **({"Paths": paths} if paths else {}), **more)

    def test_a_waits_forecast_at_the_present_head_is_read(self):
        got = plan.main_conflict([self.entry(f"bolt/t@{self.H[:7]} main@2222222", Reached="wait")], "t", self.H)
        assert got == ("2222222", ["docs/builds.md"])

    def test_a_raises_forecast_is_read_the_same_way_the_latest_first(self):
        entries = [self.entry(f"bolt/t@{self.H[:7]} main@2222222", Reached="wait"),
                   self.entry(f"bolt/t@{self.H[:7]} main@3333333", "README.md docs/builds.md", Reached="told")]
        assert plan.main_conflict(entries, "t", self.H) == ("3333333", ["README.md", "docs/builds.md"])

    def test_one_at_a_head_the_bolt_has_moved_from_holds_nothing(self):
        assert plan.main_conflict([self.entry(f"bolt/t@{self.OLD[:7]} main@2222222")], "t", self.H) is None

    def test_one_met_only_queued_on_main_holds_nothing(self):
        assert plan.main_conflict([self.entry(f"bolt/t@{self.H[:7]} main@2222222 #7")], "t", self.H) is None

    def test_the_form_a_wait_records_when_sluice_could_not_forecast_holds_nothing(self):
        assert plan.main_conflict([self.entry(f"bolt/t@{self.H[:7]}", paths=None)], "t", self.H) is None

    def test_a_units_forecast_against_the_bolt_another_bolts_and_a_refused_one_hold_nothing(self):
        heads = f"bolt/t@{self.H[:7]} main@2222222"
        assert plan.main_conflict([self.entry(f"u@aaaaaaa bolt/t@{self.H[:7]}", on=("unit/u", "bolt/t")),
                                   self.entry(heads.replace("bolt/t@", "bolt/s@"), on=("bolt/s",)),
                                   self.entry(heads, Refused="no")], "t", self.H) is None
        assert plan.main_conflict([self.entry(heads)], "t", None) is None
