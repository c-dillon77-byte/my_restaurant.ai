#!/usr/bin/env python3
"""
generate_synthetic_data.py

Creates a SYNTHETIC daily sales history so the forecasting scripts can be
run and tested end to end. None of these numbers come from a real business.

Each store gets:
- a base daily sales level
- a day-of-week pattern (busier Fri/Sat, slower Sun)
- a small upward trend
- random noise, plus a few one-off spikes/dips (to show why the trimmed
  mean drops the highest and lowest values)

Usage:
  python scripts/generate_synthetic_data.py --output data/synthetic_sales.csv --weeks 20 --seed 42
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

# Synthetic store profiles: store_id -> base daily net sales
STORE_BASES = {"101": 2400.0, "102": 1900.0, "103": 3200.0}

# Monday=0 ... Sunday=6 multipliers
WEEKDAY_FACTORS = [0.95, 0.97, 1.00, 1.03, 1.15, 1.25, 0.80]


def generate(weeks: int = 20, start: str = "2026-01-05", seed: int = 42) -> pd.DataFrame:
    """Return a DataFrame with columns date, store_id, net_sales (all synthetic)."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start=start, periods=weeks * 7, freq="D")
    rows = []
    for store_id, base in STORE_BASES.items():
        for i, d in enumerate(dates):
            trend = 1.0 + 0.0005 * i  # ~ +0.05% per day
            value = base * WEEKDAY_FACTORS[d.weekday()] * trend
            value *= rng.normal(1.0, 0.04)  # everyday noise
            if rng.random() < 0.03:  # occasional event spike or bad day
                value *= rng.choice([0.6, 1.5])
            rows.append({"date": d.date().isoformat(), "store_id": store_id, "net_sales": round(value, 2)})
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Generate synthetic restaurant sales data.")
    p.add_argument("--output", default="data/synthetic_sales.csv")
    p.add_argument("--weeks", type=int, default=20)
    p.add_argument("--start", default="2026-01-05", help="First date (YYYY-MM-DD)")
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    df = generate(weeks=a.weeks, start=a.start, seed=a.seed)
    df.to_csv(a.output, index=False)
    print(f"Wrote {len(df)} synthetic rows for {df['store_id'].nunique()} stores to {a.output}")


if __name__ == "__main__":
    main()
