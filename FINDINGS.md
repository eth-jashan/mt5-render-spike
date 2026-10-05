# MT5 farm spike — findings (5 October 2026)

Render Standard (2 GB), Debian Wine 8.0, Python 3.11.9 embeddable, MetaTrader5 package, terminal build 5.00 / 6241.
Accounts: `mq1` (MetaQuotes-Demo, USD), `mq2` (MetaQuotes-Demo, EUR, never the boot account), `b2a` (ICMarketsSC-Demo, Standard, USD), `b2b` (Pepperstone-Demo, USD). b2a/b2b log in with master passwords (no investor set); probes only read. Raw results: `results.jsonl` on the service.

| Spec 10 row | Result | Bar | Verdict |
|---|---|---|---|
| Startup | A terminal with **no** account blocks on the "Select a company" wizard; Python gets IPC timeout -10005. Login without password: same. Python launching the terminal itself: same. A config with Login + Password + Server: Python attaches in 0.01 s. | — | Boot each slot with a **farm-owned** demo account from a config held in RAM (`/dev/shm`, deleted after 60 s). Works. |
| 1. Switching | mq1 ↔ mq2: 134/134 OK, median 1.4 s, max 3.9 s. Across all four accounts on three brokers in one terminal: 80/80 OK, 0 wrong-account, median 1.6 s, max 1.9 s (MetaQuotes ≈ 1.3 s, IC/Pepperstone ≈ 1.7 s). | ≥ 99.5 %, median < 15 s | **Pass** |
| 2. Password on disk | After logins via `mt5.login`, no file under the terminal folder holds any password (UTF-8 or UTF-16LE), including mq2's, which never booted the terminal. The boot account's password (RAM config) isn't stored either. | none on disk | **Pass** |
| 3. Second broker | A stock terminal knows only MetaQuotes: ICMarketsSC-Demo logins time out, even when booting from a config. **Fix found:** drive the terminal's own "Find your company" wizard (xdotool on Xvfb) with the broker name or exact server name. Searching "Pepperstone" made Pepperstone-Demo log in (15 s first login); "IC Markets" didn't cover the Seychelles entity, but searching the server name "ICMarketsSC-Demo" did (Raw Trading Ltd, 6 s). | logs in | **Pass, with an onboarding step per broker server:** search once, then keep the resulting `Config/servers.dat` in the golden prefix. |
| 4. Real trades | 21 trade deals on mq1/mq2 (opened from the phone app: reason 2 = mobile). type 0 buy / 1 sell / 2 balance; entry 0 = in, 1 = out; a 0.2-lot position closed in two 0.1 parts keeps one `position_id` across its three deals; an open position's `ticket` = `identifier` = its deals' `position_id`. Commission 0 on MetaQuotes demo; profit in account currency (mq2: EUR). **History arrives after login:** mq2's first read returned 0 deals, then 14 a second later; ready within 2–3 s. | fields map | **Pass**, with the rule: after login, poll until every open position's opening deal is present and the count is stable. |
| 5. Investor mode | mq2 investor login: `trade_allowed=false`; master login: `true`. Other fields identical. | detectable | **Pass**: `trade_allowed` tells investor from master. |
| 6. Server time | MetaQuotes-Demo, ICMarketsSC-Demo and Pepperstone-Demo: the first H1 bar of all 57 weeks (2025-W37 → 2026-W41) opens at 00:00 server time, across the US DST changes of 2 Nov 2025 and 8 Mar 2026; live offset +3 h = the rule. New brokers' price history took 12–15 s to download on first request. | within 1 s across 1 Nov 2026 | **Pass**: EET + US DST holds for all three brokers. Keep the per-broker check (weekly-open inference) for every newly onboarded server. |
| 7. Four slots | On Standard (2 GB): container RSS 1.6 → 2.5 GB within 7 min of booting 4 terminals, then Render restarted it (no OOM event recorded). One slot: 0.84 GB container peak. | 4 slots in 4 GB | **Not proven.** ≈ 0.5 GB per terminal; needs a 4 GB run. |
| 8. Error codes | Wrong password: (-6, "Terminal: Authorization failed") in 5.9 s. Unknown login: the same -6 in 1.2 s. Unknown server: (-10005, "IPC timeout") after 30.9 s, the call's own timeout. | — | AUTH ← -6. **Unknown server is indistinguishable from a hang**; the farm must check the server name against `servers.dat`/broker search before login to report SERVER_NOT_FOUND. |

Memory, one slot: whole container peak RSS 836 MB (Xvfb + wineserver + terminal + Python).
Timing: container start → probes running ≈ 5 min (Wine/Python 55 s, terminal install 25 s, LiveUpdate wait 150 s).
LiveUpdate shows a "Restart to install updates" dialog; it doesn't block IPC, but the farm image should pin a build.

Other notes:
- The terminal logs "unstable and unsupported Wine 8.0 … please upgrade to Wine 10 or later". The farm image should use Wine 10 (the first spike found the installer failing under Wine 11 in this container; 10 is untested).
- Throughput, one slot: a switch plus a full history read takes ≈ 1.5 s, so login time, not CPU, bounds a slot (≈ 2,000 syncs an hour in theory; the broker's own rate limits are untested).
- A failed login to an unknown server blocks the slot for the whole timeout (30–60 s); 66 such logins made one run take 46 minutes. The farm must validate the server name first.
