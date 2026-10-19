# Data

## `synthetic_sales.csv`: SYNTHETIC, not real sales

This file is **generated** by `scripts/generate_synthetic_data.py` (20 weeks, 3 stores, seed 42).
The numbers are made up to have a realistic shape (weekday pattern, slight upward trend, noise, a few
one-off spikes and dips). They do **not** come from any real restaurant or POS system.

Regenerate it with:

```bash
python scripts/generate_synthetic_data.py --output data/synthetic_sales.csv --weeks 20 --seed 42
```

## Input format (for your own data)

| column | description | example |
|---|---|---|
| `date` | business date (YYYY-MM-DD) | `2026-03-01` |
| `store_id` | store identifier | `101` |
| `net_sales` | daily net sales | `2520.75` |

One row per store per day. Don't commit real business data to a public repository.
