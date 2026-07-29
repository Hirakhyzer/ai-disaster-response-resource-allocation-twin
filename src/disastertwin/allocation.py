"""Transparent resource allocation heuristics for synthetic disaster response."""

from __future__ import annotations

import numpy as np
import pandas as pd

RESOURCE_DEMAND_COLUMNS = {
    "food_packs": "food_pack_demand",
    "water_liters": "water_liter_demand",
    "medical_kits": "medical_case_demand",
    "rescue_teams": "rescue_team_demand",
    "buses": "shelter_bed_demand",
    "shelter_beds": "shelter_bed_demand",
}


def allocate_resources(demand: pd.DataFrame, supplies: pd.DataFrame, zone_access: pd.DataFrame, strategy: str = "balanced") -> pd.DataFrame:
    """Allocate resources to zones using transparent planning heuristics."""
    supply_totals = supplies.groupby("resource_type", as_index=False)["available_units"].sum()
    available = dict(zip(supply_totals["resource_type"], supply_totals["available_units"]))
    merged = demand.merge(zone_access, on="zone_id", how="left").fillna({"zone_access_risk_score": 0.0, "mean_route_delay_minutes": 0.0})
    priority = _priority_weights(merged, strategy)
    rows = []
    for resource, demand_col in RESOURCE_DEMAND_COLUMNS.items():
        total_available = int(available.get(resource, 0))
        resource_need = merged[demand_col].astype(float)
        if resource == "medical_kits":
            resource_need = np.ceil(resource_need / 3)
        if resource == "buses":
            resource_need = np.ceil(resource_need / 80)
        weighted_need = resource_need * priority
        denom = float(weighted_need.sum()) or 1.0
        for idx, zone in merged.reset_index(drop=True).iterrows():
            raw_share = total_available * float(weighted_need.iloc[idx]) / denom
            allocated = int(min(float(resource_need.iloc[idx]), max(0, round(raw_share))))
            service_ratio = allocated / max(1.0, float(resource_need.iloc[idx]))
            unmet = max(0.0, float(resource_need.iloc[idx]) - allocated)
            rows.append({
                "zone_id": zone["zone_id"],
                "resource_type": resource,
                "strategy": strategy,
                "required_units": int(np.ceil(resource_need.iloc[idx])),
                "allocated_units": allocated,
                "unmet_units": int(np.ceil(unmet)),
                "service_ratio": round(float(service_ratio), 4),
                "zone_priority_weight": round(float(priority.iloc[idx]), 4),
                "allocation_review_flag": bool(service_ratio < 0.65),
            })
    return pd.DataFrame(rows).sort_values(["resource_type", "service_ratio"]).reset_index(drop=True)


def allocation_summary(allocation: pd.DataFrame) -> dict[str, int | float]:
    """Summarize allocation results."""
    if allocation.empty:
        return {"mean_service_ratio": 0.0, "under_served_allocation_count": 0}
    return {
        "mean_service_ratio": float(allocation["service_ratio"].mean()),
        "under_served_allocation_count": int((allocation["service_ratio"] < 0.65).sum()),
        "total_unmet_units": int(allocation["unmet_units"].sum()),
    }


def _priority_weights(demand: pd.DataFrame, strategy: str) -> pd.Series:
    vulnerability = demand["vulnerability_index"].astype(float)
    demand_index = demand["demand_index"].astype(float)
    access_risk = demand.get("zone_access_risk_score", pd.Series(0, index=demand.index)).astype(float)
    if strategy == "equity_priority":
        weights = 0.45 + 0.35 * vulnerability + 0.15 * demand_index + 0.05 * access_risk
    elif strategy == "medical_surge":
        medical_norm = demand["medical_case_demand"].astype(float) / max(1.0, float(demand["medical_case_demand"].max()))
        weights = 0.40 + 0.30 * medical_norm + 0.20 * demand_index + 0.10 * vulnerability
    elif strategy == "logistics_priority":
        weights = 0.40 + 0.30 * access_risk + 0.20 * demand_index + 0.10 * vulnerability
    elif strategy == "evacuation_priority":
        shelter_norm = demand["shelter_bed_demand"].astype(float) / max(1.0, float(demand["shelter_bed_demand"].max()))
        weights = 0.40 + 0.30 * shelter_norm + 0.20 * access_risk + 0.10 * vulnerability
    else:
        weights = 0.45 + 0.25 * demand_index + 0.18 * vulnerability + 0.12 * access_risk
    return weights.clip(lower=0.05)
