# mt5-render-spike (THROWAWAY)

Measures the self-hosted MT5 farm design before it is built: the trading-journal spec
`docs/superpowers/specs/2026-10-05-self-hosted-mt5-sync-design.md`, section 10.

- `probes/` runs under Windows Python in Wine. `tests/` runs on any machine: `python3 -m unittest discover -s tests`.
- Accounts come only from the `SPIKE_ACCOUNTS` environment variable (JSON), or the older `MT5_*` variables. Nothing is printed but labels.
- `SPIKE_MODE=single` (default) runs every probe on one slot. `SPIKE_MODE=four` runs the switching probe on four slots.
- Results: `GET /results.jsonl` on the service URL.

Delete this repo once plan 3b starts.
