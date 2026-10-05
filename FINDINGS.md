# MT5 farm spike — findings (5 October 2026)

Render Standard (2 GB), Debian Wine 8.0, Python 3.11.9 embeddable, MetaTrader5 package, terminal build 5.00 / 6241.
One account so far: `mq1` (MetaQuotes-Demo, investor password). Raw results: `results.jsonl` on the service.

| Spec 10 row | Result | Bar | Verdict |
|---|---|---|---|
| Startup | A terminal with **no** account blocks on the "Select a company" wizard; Python gets IPC timeout -10005. Login without password: same. Python launching the terminal itself: same. A config with Login + Password + Server: Python attaches in 0.01 s. | — | Boot each slot with a **farm-owned** demo account from a config held in RAM (`/dev/shm`, deleted after 60 s). Works. |
| 1. Switching | 200/200 logins OK, 0 wrong-account, p99 0.07 s, deal read ≤ 0.06 s | ≥ 99.5 %, median < 15 s | **Pass for one account only.** Re-logging the same account is effectively a no-op, so the real switch time needs 2+ accounts. |
| 2. Password on disk | After logins via `mt5.login`: no file under the terminal folder contains the password (UTF-8 or UTF-16LE). Nothing to wipe; login still works. The boot account's password (from the RAM config) is not stored either. | none on disk | **Pass** (recheck with a second account that is never the boot account). |
| 3. Second broker | not run (no second-broker account yet) | — | pending |
| 4. Real trades | Only the demo's initial balance deal (type 2 = balance, entry 0, position_id 0, symbol ""). No positions. | — | pending demo trades |
| 5. Investor mode | `trade_allowed=false`, `trade_expert=true`, `trade_mode=0` with the investor password. Master comparison not run. | — | `trade_allowed=false` is the likely signal; confirm against master |
| 6. Server time | MetaQuotes-Demo: the first H1 bar of all 57 weeks (2025-W37 → 2026-W41) opens at 00:00 server time, across the US DST changes of 2 Nov 2025 and 8 Mar 2026. Live tick offset now +3 h = rule's expectation. | within 1 s across 1 Nov 2026 | **Pass for MetaQuotes**: EET + US DST confirmed from history. Other brokers pending. |
| 7. Four slots | see below | 4 slots in 4 GB | running |
| 8. Error codes | Wrong password: (-6, "Terminal: Authorization failed") in 5.9 s. Unknown login: the same -6 in 1.2 s. Unknown server: (-10005, "IPC timeout") after 30.9 s, the call's own timeout. | — | AUTH ← -6. **Unknown server is indistinguishable from a hang**; the farm must check the server name against `servers.dat`/broker search before login to report SERVER_NOT_FOUND. |

Memory, one slot: whole container peak RSS 836 MB (Xvfb + wineserver + terminal + Python).
Timing: container start → probes running ≈ 5 min (Wine/Python 55 s, terminal install 25 s, LiveUpdate wait 150 s).
LiveUpdate shows a "Restart to install updates" dialog; it doesn't block IPC, but the farm image should pin a build.
