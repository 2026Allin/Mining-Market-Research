#!/usr/bin/env python3
"""Offline daily-bar arithmetic; no network, persistence, calendar or attribution."""
import json
import math
import sys
from datetime import date, datetime
from statistics import mean


def number(value, *, volume=False):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("numeric values must be finite numbers or null")
    if not math.isfinite(value) or value < 0 or (not volume and value == 0):
        raise ValueError("prices must be positive; volumes nonnegative and finite")
    return value


def percent_change(first, last):
    return None if first is None or last is None else (last / first - 1) * 100


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("timezone offset required")
    return parsed


def align_publication(published_at, sessions):
    """Classify against host-verified session bounds, never infer missing sessions."""
    if not published_at or not sessions:
        return {"status": "unknown", "reason": "publication_or_verified_sessions_missing"}
    try:
        publication = timestamp(published_at)
    except (ValueError, TypeError, AttributeError):
        return {"status": "unknown", "reason": "publication_timezone_or_time_unknown"}
    checked = []
    previous_close = None
    for session in sessions:
        day = date.fromisoformat(session["date"])
        opened, closed = timestamp(session["open_at"]), timestamp(session["close_at"])
        if opened >= closed or (previous_close and opened <= previous_close):
            raise ValueError("verified sessions must be ordered and nonoverlapping")
        if opened.date() != day:
            raise ValueError("session date must match local open date")
        checked.append((session["date"], opened, closed))
        previous_close = closed
    for day, opened, closed in checked:
        if publication == opened or publication == closed:
            return {"status": "boundary_uncertain", "first_possible_session": day}
        if opened < publication < closed:
            return {"status": "intraday_mixed", "first_possible_session": day}
        if publication < opened:
            return {"status": "before_next_verified_session", "first_possible_session": day}
    return {"status": "after_last_verified_session", "first_possible_session": None}


def analyze(payload):
    if payload.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    windows = [payload.get("baseline_window", 20), payload.get("percentile_window", 60),
               payload.get("min_samples", 10)]
    if any(type(n) is not int or not 1 <= n <= 1000 for n in windows):
        raise ValueError("windows and min_samples must be integers in 1..1000")
    baseline, percentile_window, minimum = windows
    if minimum > min(baseline, percentile_window):
        raise ValueError("min_samples cannot exceed either window")
    price_basis = payload.get("price_basis", "unknown")
    volume_basis = payload.get("volume_basis", "unknown")
    if price_basis not in ("raw", "adjusted", "unknown") or volume_basis not in ("raw", "adjusted", "unknown"):
        raise ValueError("unsupported price/volume basis")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be a nonempty list of actual observations")
    groups, seen = {}, set()
    for source in rows:
        if not isinstance(source, dict):
            raise ValueError("each row must be an object")
        row = dict(source)
        key = (row.get("exchange"), row.get("ticker"))
        if any(not isinstance(v, str) or not v.strip() for v in key):
            raise ValueError("exact exchange and ticker required")
        date.fromisoformat(row["date"])
        unique = (*key, row["date"])
        if unique in seen:
            raise ValueError("duplicate listing/date observations")
        seen.add(unique)
        for field in ("open", "high", "low", "close", "volume"):
            row[field] = number(row.get(field), volume=field == "volume")
        if row["high"] is not None and row["low"] is not None and row["high"] < row["low"]:
            raise ValueError("high cannot be below low")
        groups.setdefault(key, []).append(row)
    output = []
    for (exchange, ticker), series in sorted(groups.items()):
        series.sort(key=lambda row: row["date"])
        observations = []
        for i, row in enumerate(series):
            prior = [r["volume"] for r in series[max(0, i-baseline):i] if r["volume"] is not None]
            history = [r["volume"] for r in series[max(0, i-percentile_window):i] if r["volume"] is not None]
            reasons, ratio, rank = [], None, None
            volume = row["volume"]
            if volume_basis == "unknown":
                reasons.append("volume_basis_unknown")
            elif volume is None:
                reasons.append("volume_missing")
            else:
                if len(prior) < minimum:
                    reasons.append("baseline_insufficient")
                elif mean(prior) == 0:
                    reasons.append("baseline_zero")
                else:
                    ratio = volume / mean(prior)
                if len(history) >= minimum:
                    rank = 100 * (sum(v < volume for v in history) + .5 * sum(v == volume for v in history)) / len(history)
                else:
                    reasons.append("percentile_sample_insufficient")
            prior_close = series[i-1]["close"] if i else None
            known_price = price_basis != "unknown"
            if not known_price:
                reasons.append("price_basis_unknown")
            observations.append({"date": row["date"], "volume": volume,
                "relative_volume": ratio, "baseline_n": len(prior),
                "baseline_mean": mean(prior) if prior else None,
                "volume_midrank_percentile": rank, "percentile_n": len(history),
                "previous_observation_return_pct": percent_change(prior_close, row["close"]) if known_price else None,
                "opening_gap_pct": percent_change(prior_close, row["open"]) if known_price else None,
                "open_to_close_pct": percent_change(row["open"], row["close"]) if known_price else None,
                "warnings": reasons})
        volumes = [r["volume"] for r in series if r["volume"] is not None]
        output.append({"exchange": exchange, "ticker": ticker, "row_count": len(series),
            "start_date": series[0]["date"], "end_date": series[-1]["date"],
            "missing_close": sum(r["close"] is None for r in series),
            "missing_volume": len(series)-len(volumes), "volume_n": len(volumes),
            "endpoint_return_pct": percent_change(series[0]["close"], series[-1]["close"]) if price_basis != "unknown" else None,
            "average_volume": mean(volumes) if volumes and volume_basis != "unknown" else None,
            "observations": observations})
    return {"schema_version": 1, "status": "calculated", "price_basis": price_basis,
        "volume_basis": volume_basis, "baseline_window": baseline,
        "percentile_window": percentile_window, "min_samples": minimum,
        "scope": "provided_observations_only_not_database_completeness",
        "formulas": {"return_pct": "100*(last/first-1)",
            "relative_volume": "volume/mean(non-null prior-window volumes); current excluded",
            "percentile": "100*(less+0.5*equal)/prior_n; current excluded"},
        "publication_alignment": align_publication(payload.get("published_at"), payload.get("sessions")),
        "instruments": output}


def main():
    try:
        result = analyze(json.load(sys.stdin))
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        print(json.dumps({"status": "invalid_input", "reason": str(exc)}))
        return 2
    print(json.dumps(result, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
