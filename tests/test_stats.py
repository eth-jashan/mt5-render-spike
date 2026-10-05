import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "probes"))
from stats import percentile, summarize_switches

class StatsTest(unittest.TestCase):
    def test_percentile(self):
        self.assertEqual(percentile([3, 1, 2, 5, 4], 50), 3)
        self.assertEqual(percentile([1, 2, 3, 4], 100), 4)

    def test_summarize_switches(self):
        rows = [{"ok": True, "seconds": s, "wrong_account": False} for s in (2, 4, 6, 8)]
        rows.append({"ok": False, "seconds": 30, "wrong_account": False})
        s = summarize_switches(rows)
        self.assertEqual((s["count"], s["ok"], s["failed"]), (5, 4, 1))
        self.assertAlmostEqual(s["ok_rate"], 0.8)
        self.assertEqual(s["max"], 8)

    def test_summarize_counts_wrong_account(self):
        rows = [{"ok": True, "seconds": 3, "wrong_account": True}, {"ok": True, "seconds": 3, "wrong_account": False}]
        s = summarize_switches(rows)
        self.assertEqual(s["wrong_account"], 1)
        self.assertEqual(s["ok"], 1)  # a wrong-account login is not a successful switch

if __name__ == "__main__":
    unittest.main()
