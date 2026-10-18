#!/usr/bin/env python3
"""
forecast_trimmed_mean.py

Baseline 7-day sales forecast using a same-weekday trimmed mean.

For each store and each future date:
  1. Take the last `lookback` (default 6) actual sales on the same weekday.
  2. Drop the single highest and single lowest value.
  3. Average what is left.
  4. Multiply by an optional event/promo multiplier (default 1.00).

If a store has fewer than 3 same-weekday values, there is nothing sensible to
trim, so the plain average of what exists is used (method is labeled
"same_weekday_mean_fallback"). If there are none, that date is skipped.

Forecasts are based only on actual history (not on earlier forecasts), so a
horizon longer than 7 days repeats each weekday's baseline.

Usage:
  python scripts/forecast_trimmed_mean.py --input data/synthetic_sales.csv \
      --output output/forecast_example.csv --horizon 7 --multiplier 1.00
"""

from __future__ import annotations

import argparse
from typing import Optional, Sequence

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {"date", "store_id", "net_sales"}
METHOD = "same_weekday_trimmed_mean"
FALLBACK_METHOD = "same_weekday_mean_fallback"


def trimmed_mean(values: Sequence[float]) -> Optional[float]:
    """Average after dropping one highest and one lowest value.

    Needs at least 3 values; returns None otherwise.
    """
    v = np.sort(np.asarray(values, dtype=float))
    if len(v) < 3:
        return None
    return float(v[1:-1].mean())


def load_sales(path: str) -> pd.DataFrame:
    """Read and clean a sales CSV with columns date, store_id, net_sales."""
    df = pd.read_csv(path)
    return clean_sales(df)


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df = df[list(REQUIRED_COLUMNS)].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["net_sales"] = pd.to_numeric(df["net_sales"], errors="coerce")
    df["store_id"] = df["store_id"].astype(str).str.strip()
    df = df.dropna(subset=["date", "store_id", "net_sales"])
    # One row per store per day: if a day appears twice, keep the last one.
    df = df.drop_duplicates(subset=["store_id", "date"], keep="last")
    return df.sort_values(["store_id", "date"]).reset_index(drop=True)


def forecast(
    df: pd.DataFrame,
    horizon: int = 7,
    multiplier: float = 1.0,
    lookback: int = 6,
) -> pd.DataFrame:
    """Forecast `horizon` days after the latest date in `df` for every store."""
    if horizon < 1:
        raise ValueError("horizon must be at least 1")
    if lookback < 3:
        raise ValueError("lookback must be at least 3 to allow trimming")
    df = clean_sales(df)
    if df.empty:
        raise ValueError("No valid sales rows after cleaning")

    start = df["date"].max().normalize() + pd.Timedelta(days=1)
    rows = []
    for store_id, hist in df.groupby("store_id", sort=True):
        for h in range(horizon):
            target = start + pd.Timedelta(days=h)
            same_day = hist[hist["date"].dt.weekday == target.weekday()]
            recent = same_day.sort_values("date")["net_sales"].tail(lookback).to_numpy()
            if len(recent) == 0:
                continue
            base = trimmed_mean(recent)
            method = METHOD
            if base is None:
                base = float(recent.mean())
                method = FALLBACK_METHOD
            rows.append(
                {
                    "date": target.date().isoformat(),
                    "store_id": store_id,
                    "forecast_net_sales": round(base * multiplier, 2),
                    "base_forecast": round(base, 2),
                    "multiplier": multiplier,
                    "method": method,
                }
            )
    return pd.DataFrame(
        rows,
        columns=["date", "store_id", "forecast_net_sales", "base_forecast", "multiplier", "method"],
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Same-weekday trimmed-mean sales forecast.")
    p.add_argument("--input", required=True, help="CSV with date, store_id, net_sales")
    p.add_argument("--output", required=True, help="Where to write the forecast CSV")
    p.add_argument("--horizon", type=int, default=7, help="Days to forecast (default 7)")
    p.add_argument("--multiplier", type=float, default=1.0, help="Event/promo adjustment (default 1.00)")
    p.add_argument("--lookback", type=int, default=6, help="Same-weekday values to use (default 6)")
    a = p.parse_args()

    out = forecast(load_sales(a.input), horizon=a.horizon, multiplier=a.multiplier, lookback=a.lookback)
    out.to_csv(a.output, index=False)
    print(f"Wrote {len(out)} forecast rows to {a.output}")


if __name__ == "__main__":
    main()
