import json, os, sys, tempfile, time, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "probes"))
from common import CallTimeout, emit, load_accounts, redact, timed_call

RAW = json.dumps([
    {"label": "mq1", "login": 10012991192, "server": "MetaQuotes-Demo", "investor": "Inv@1"},
    {"label": "b2a", "login": 5001, "server": "Broker-Demo", "investor": "x", "master": "M#2"},
])

class CommonTest(unittest.TestCase):
    def test_load_accounts(self):
        accounts = load_accounts(RAW)
        self.assertEqual([a.label for a in accounts], ["mq1", "b2a"])
        self.assertIsNone(accounts[0].master)
        self.assertEqual(accounts[1].master, "M#2")

    def test_load_accounts_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            load_accounts(json.dumps([{"label": "x"}]))

    def test_redact(self):
        self.assertEqual(redact("bad pw Inv@1 and M#2", ["Inv@1", "M#2"]), "bad pw *** and ***")

    def test_timed_call_returns_result_and_duration(self):
        result, seconds = timed_call(lambda: 42, timeout_s=1)
        self.assertEqual(result, 42)
        self.assertLess(seconds, 1)

    def test_timed_call_times_out(self):
        with self.assertRaises(CallTimeout):
            timed_call(lambda: time.sleep(2), timeout_s=0.2)

    def test_emit_appends_json_lines(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ["SPIKE_RESULTS"] = os.path.join(d, "r.jsonl")
            emit("demo", account="mq1", seconds=1.5)
            with open(os.environ["SPIKE_RESULTS"]) as f:
                self.assertEqual(json.loads(f.readline()), {"probe": "demo", "account": "mq1", "seconds": 1.5})

if __name__ == "__main__":
    unittest.main()
