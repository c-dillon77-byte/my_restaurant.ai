import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from forecast_trimmed_mean import forecast, trimmed_mean
from generate_synthetic_data import generate


def test_trimmed_mean_matches_documented_example():
    # Example from docs/implementation_plan.txt (Phase 5)
    assert trimmed_mean([2100, 2250, 2400, 2600, 1900, 2350]) == pytest.approx(2275.0)


def test_trimmed_mean_needs_three_values():
    assert trimmed_mean([100, 200]) is None
    assert trimmed_mean([100, 200, 900]) == pytest.approx(200.0)


def _weekly_history(store="101", weeks=6, start="2026-03-02"):
    """Mondays only, values 1000, 1100, ... so the answer is easy to check."""
    dates = pd.date_range(start, periods=weeks, freq="7D")  # 2026-03-02 is a Monday
    return pd.DataFrame({"date": dates, "store_id": store, "net_sales": [1000 + 100 * i for i in range(weeks)]})


def test_forecast_uses_same_weekday_and_multiplier():
    df = _weekly_history()
    # Last date is a Monday, so a 7-day horizon reaches the next Monday on day 7.
    out = forecast(df, horizon=7, multiplier=1.10)
    monday = out[pd.to_datetime(out["date"]).dt.weekday == 0].iloc[0]
    # values 1000..1500 -> drop 1000 and 1500 -> mean(1100..1400) = 1250
    assert monday["base_forecast"] == pytest.approx(1250.0)
    assert monday["forecast_net_sales"] == pytest.approx(1375.0)
    assert monday["method"] == "same_weekday_trimmed_mean"
    # Other weekdays have no history in this data, so they are skipped.
    assert len(out) == 1


def test_forecast_fallback_with_short_history():
    df = _weekly_history(weeks=2)
    out = forecast(df, horizon=7)
    assert out.iloc[0]["method"] == "same_weekday_mean_fallback"
    assert out.iloc[0]["base_forecast"] == pytest.approx(1050.0)


def test_forecast_on_synthetic_data_covers_every_store_and_day():
    df = generate(weeks=8, seed=1)
    out = forecast(df, horizon=7)
    assert len(out) == 3 * 7
    assert set(out["store_id"]) == {"101", "102", "103"}
    assert (out["forecast_net_sales"] > 0).all()
    first_forecast = pd.to_datetime(out["date"]).min()
    assert first_forecast == pd.to_datetime(df["date"]).max() + pd.Timedelta(days=1)


def test_missing_columns_raise():
    with pytest.raises(ValueError, match="Missing required columns"):
        forecast(pd.DataFrame({"date": ["2026-01-01"], "net_sales": [1.0]}))


def test_duplicate_rows_are_collapsed():
    df = _weekly_history()
    dup = pd.concat([df, df.tail(1)])
    assert forecast(dup).equals(forecast(df))


def test_generator_is_deterministic():
    assert generate(weeks=3, seed=7).equals(generate(weeks=3, seed=7))
