"""Equity and service-gap audit for synthetic disaster resource allocation."""

from __future__ import annotations

import pandas as pd


def audit_equity(demand: pd.DataFrame, allocation: pd.DataFrame, zone_access: pd.DataFrame) -> pd.DataFrame:
    """Audit vulnerable-zone service gaps across allocated resources."""
    ratios = allocation.groupby("zone_id", as_index=False).agg(
        mean_service_ratio=("service_ratio", "mean"),
        min_service_ratio=("service_ratio", "min"),
        unmet_units=("unmet_units", "sum"),
        review_flag_count=("allocation_review_flag", "sum"),
    )
    merged = demand.merge(ratios, on="zone_id", how="left").merge(zone_access, on="zone_id", how="left").fillna(0)
    rows = []
    mean_service = float(merged["mean_service_ratio"].mean()) if not merged.empty else 0.0
    for zone in merged.itertuples(index=False):
        vulnerability = float(zone.vulnerability_index)
        service_gap = max(0.0, 1 - float(zone.mean_service_ratio))
        equity_gap = 0.40 * service_gap + 0.24 * vulnerability + 0.18 * float(zone.zone_access_risk_score) + 0.18 * max(0.0, mean_service - float(zone.mean_service_ratio))
        rows.append({
            "zone_id": zone.zone_id,
            "vulnerability_index": round(vulnerability, 4),
            "demand_index": round(float(zone.demand_index), 4),
            "mean_service_ratio": round(float(zone.mean_service_ratio), 4),
            "min_service_ratio": round(float(zone.min_service_ratio), 4),
            "unmet_units": int(zone.unmet_units),
            "zone_access_risk_score": round(float(zone.zone_access_risk_score), 4),
            "equity_gap_score": round(min(1.0, equity_gap), 4),
            "equity_priority_class": _gap_class(equity_gap),
            "requires_human_equity_review": bool(equity_gap >= 0.45 or (vulnerability >= 0.65 and zone.mean_service_ratio < 0.75)),
        })
    return pd.DataFrame(rows).sort_values("equity_gap_score", ascending=False).reset_index(drop=True)


def equity_summary(equity: pd.DataFrame) -> dict[str, int | float]:
    """Summarize equity audit results."""
    if equity.empty:
        return {"equity_review_zone_count": 0, "mean_equity_gap_score": 0.0}
    return {
        "equity_review_zone_count": int(equity["requires_human_equity_review"].sum()),
        "mean_equity_gap_score": float(equity["equity_gap_score"].mean()),
        "highest_equity_gap_score": float(equity["equity_gap_score"].max()),
    }


def _gap_class(score: float) -> str:
    if score >= 0.74:
        return "critical"
    if score >= 0.55:
        return "high"
    if score >= 0.34:
        return "medium"
    return "low"
