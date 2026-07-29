"""Response strategy scenario comparison for synthetic disaster planning."""

from __future__ import annotations

import pandas as pd

from disastertwin.allocation import allocate_resources
from disastertwin.equity import audit_equity


STRATEGIES = ["balanced", "equity_priority", "medical_surge", "logistics_priority", "evacuation_priority"]


def compare_response_strategies(demand: pd.DataFrame, supplies: pd.DataFrame, zone_access: pd.DataFrame) -> pd.DataFrame:
    """Compare response-allocation strategies using transparent KPIs."""
    rows = []
    for strategy in STRATEGIES:
        allocation = allocate_resources(demand, supplies, zone_access, strategy=strategy)
        equity = audit_equity(demand, allocation, zone_access)
        rows.append({
            "strategy": strategy,
            "mean_service_ratio": float(allocation["service_ratio"].mean()),
            "minimum_service_ratio": float(allocation["service_ratio"].min()),
            "total_unmet_units": int(allocation["unmet_units"].sum()),
            "equity_review_zone_count": int(equity["requires_human_equity_review"].sum()),
            "mean_equity_gap_score": float(equity["equity_gap_score"].mean()),
            "high_gap_zone_count": int(equity["equity_priority_class"].isin(["high", "critical"]).sum()),
            "planning_boundary": "synthetic scenario comparison only; human incident-command review required",
        })
    comparison = pd.DataFrame(rows)
    comparison["overall_planning_score"] = (
        0.45 * comparison["mean_service_ratio"]
        + 0.20 * comparison["minimum_service_ratio"]
        + 0.20 * (1 - comparison["mean_equity_gap_score"])
        + 0.15 * (1 - comparison["equity_review_zone_count"] / max(1, len(demand)))
    ).round(4)
    return comparison.sort_values("overall_planning_score", ascending=False).reset_index(drop=True)


def scenario_summary(comparison: pd.DataFrame) -> dict[str, int | float | str]:
    """Summarize scenario comparison."""
    if comparison.empty:
        return {"best_strategy": "none", "best_strategy_score": 0.0}
    best = comparison.iloc[0]
    return {
        "best_strategy": str(best["strategy"]),
        "best_strategy_score": float(best["overall_planning_score"]),
        "scenario_count": int(len(comparison)),
    }
