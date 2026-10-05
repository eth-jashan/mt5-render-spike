import calendar, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "probes"))
from offset import expected_offset_hours, infer_rule, week_open_hours

def ts(y, mo, d, h):
    return calendar.timegm((y, mo, d, h, 0, 0))

class OffsetTest(unittest.TestCase):
    def test_week_open_hours_takes_first_bar_after_the_gap(self):
        bars = [ts(2026, 3, 6, 22), ts(2026, 3, 6, 23), ts(2026, 3, 9, 0), ts(2026, 3, 9, 1)]
        self.assertEqual(week_open_hours(bars), {"2026-W11": 0})

    def test_infer_constant_midnight(self):
        self.assertEqual(infer_rule({"2026-W10": 0, "2026-W11": 0, "2026-W12": 0})["rule"], "constant-midnight")

    def test_infer_flags_inconsistent_weeks(self):
        result = infer_rule({"2026-W10": 0, "2026-W11": 23, "2026-W12": 0})
        self.assertEqual(result["rule"], "inconsistent")
        self.assertEqual(result["outliers"], ["2026-W11"])

    def test_expected_offset_follows_us_dst(self):
        self.assertEqual(expected_offset_hours(ts(2026, 1, 15, 12), "EET+US-DST"), 2)
        self.assertEqual(expected_offset_hours(ts(2026, 7, 15, 12), "EET+US-DST"), 3)
        # US DST 2026: 8 March 07:00 UTC to 1 November 06:00 UTC
        self.assertEqual(expected_offset_hours(ts(2026, 3, 8, 6), "EET+US-DST"), 2)
        self.assertEqual(expected_offset_hours(ts(2026, 3, 8, 8), "EET+US-DST"), 3)
        self.assertEqual(expected_offset_hours(ts(2026, 11, 1, 5), "EET+US-DST"), 3)
        self.assertEqual(expected_offset_hours(ts(2026, 11, 1, 7), "EET+US-DST"), 2)

if __name__ == "__main__":
    unittest.main()
