"""Pure statistics for probe results."""


def percentile(values: list, pct: float) -> float:
    if not values:
        raise ValueError("no values")
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(pct / 100 * (len(ordered) - 1))))
    return ordered[index]


def summarize_switches(rows: list) -> dict:
    good = [r["seconds"] for r in rows if r["ok"] and not r["wrong_account"]]
    wrong = sum(1 for r in rows if r["wrong_account"])
    summary = {"count": len(rows), "ok": len(good), "failed": len(rows) - len(good) - wrong,
               "wrong_account": wrong, "ok_rate": len(good) / len(rows) if rows else 0.0}
    if good:
        summary.update(p50=percentile(good, 50), p90=percentile(good, 90), p99=percentile(good, 99), max=max(good))
    return summary
