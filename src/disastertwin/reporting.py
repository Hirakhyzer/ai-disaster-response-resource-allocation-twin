"""Markdown report generation for synthetic disaster-response planning."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_report(
    path: str | Path,
    summary: dict,
    demand: pd.DataFrame,
    capacity: pd.DataFrame,
    shortages: pd.DataFrame,
    routes: pd.DataFrame,
    allocation: pd.DataFrame,
    equity: pd.DataFrame,
    comparison: pd.DataFrame,
) -> None:
    """Write a compact disaster-response planning report."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    top_demand = demand.head(8)[["zone_id", "demand_index", "priority_class", "shelter_bed_demand", "medical_case_demand"]]
    top_capacity = capacity.head(8)[["facility_id", "facility_type", "capacity_pressure_score", "capacity_pressure_class"]]
    top_routes = routes.head(8)[["road_id", "from_zone", "to_zone", "delay_minutes", "access_risk_class"]]
    top_equity = equity.head(8)[["zone_id", "equity_gap_score", "equity_priority_class", "mean_service_ratio"]]
    allocation_review = allocation[allocation["allocation_review_flag"]].head(10)[["zone_id", "resource_type", "required_units", "allocated_units", "service_ratio"]]
    content = [
        "# Synthetic Disaster Response Resource Allocation Report",
        "",
        "> This report is generated from fictional synthetic disaster-response data. It supports planning review only and must not be used for real-time dispatch, evacuation orders, medical triage, public warnings, or life-safety decisions.",
        "",
        "## Summary",
        "",
        _dict_table(summary),
        "",
        "## Highest demand zones",
        "",
        top_demand.to_markdown(index=False),
        "",
        "## Facility capacity pressure",
        "",
        top_capacity.to_markdown(index=False),
        "",
        "## Resource shortage summary",
        "",
        shortages.to_markdown(index=False),
        "",
        "## Route delay and access risk",
        "",
        top_routes.to_markdown(index=False),
        "",
        "## Allocation review sample",
        "",
        allocation_review.to_markdown(index=False) if not allocation_review.empty else "No allocation rows below the review threshold.",
        "",
        "## Equity review zones",
        "",
        top_equity.to_markdown(index=False),
        "",
        "## Scenario comparison",
        "",
        comparison.to_markdown(index=False),
        "",
        "## Planning boundary",
        "",
        "Every output is a synthetic planning signal. Final interpretation requires emergency-management authorities, trained responders, verified field data, incident command, legal authority, and human review.",
    ]
    path.write_text("\n".join(content), encoding="utf-8")


def _dict_table(summary: dict) -> str:
    return pd.DataFrame([{"metric": key, "value": value} for key, value in summary.items()]).to_markdown(index=False)
