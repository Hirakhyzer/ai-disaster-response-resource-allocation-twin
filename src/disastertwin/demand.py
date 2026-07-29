"""Emergency demand forecasting for synthetic disaster zones."""

from __future__ import annotations

import numpy as np
import pandas as pd


def forecast_emergency_demand(zones: pd.DataFrame, scenario: pd.DataFrame) -> pd.DataFrame:
    """Forecast zone-level shelter, medical, rescue, and supply demand."""
    severity = float(scenario.iloc[0]["severity_index"]) if not scenario.empty else 0.7
    rows = []
    for zone in zones.itertuples(index=False):
        vulnerability = float(zone.social_vulnerability_index)
        exposure = float(zone.exposure_index)
        mobility_gap = float(zone.vehicle_access_gap)
        outage = float(zone.baseline_power_outage_probability)
        impact = np.clip(0.18 + 0.34 * exposure + 0.25 * vulnerability + 0.18 * outage + 0.05 * severity, 0, 1)
        shelter_demand = int(zone.population * (0.04 + 0.16 * impact + 0.08 * mobility_gap))
        medical_demand = int(zone.population * (0.006 + 0.035 * impact + 0.022 * zone.elderly_share + 0.018 * zone.disability_access_need))
        rescue_demand = int(zone.population * (0.002 + 0.018 * exposure + 0.013 * mobility_gap))
        food_packs = int(zone.population * (0.32 + 0.52 * impact))
        water_liters = int(zone.population * (2.5 + 5.8 * impact))
        demand_index = float(np.clip(0.30 * exposure + 0.25 * vulnerability + 0.18 * outage + 0.15 * mobility_gap + 0.12 * severity, 0, 1))
        rows.append({
            "zone_id": zone.zone_id,
            "population": int(zone.population),
            "vulnerability_index": round(vulnerability, 4),
            "exposure_index": round(exposure, 4),
            "demand_index": round(demand_index, 4),
            "shelter_bed_demand": max(1, shelter_demand),
            "medical_case_demand": max(1, medical_demand),
            "rescue_team_demand": max(1, rescue_demand),
            "food_pack_demand": max(1, food_packs),
            "water_liter_demand": max(1, water_liters),
            "priority_class": _priority(demand_index),
        })
    return pd.DataFrame(rows).sort_values("demand_index", ascending=False).reset_index(drop=True)


def demand_summary(demand: pd.DataFrame) -> dict[str, int | float]:
    """Summarize forecast demand."""
    if demand.empty:
        return {"highest_demand_index": 0.0, "total_shelter_bed_demand": 0}
    return {
        "highest_demand_index": float(demand["demand_index"].max()),
        "high_priority_zone_count": int(demand["priority_class"].isin(["high", "critical"]).sum()),
        "total_shelter_bed_demand": int(demand["shelter_bed_demand"].sum()),
        "total_medical_case_demand": int(demand["medical_case_demand"].sum()),
        "total_food_pack_demand": int(demand["food_pack_demand"].sum()),
        "total_water_liter_demand": int(demand["water_liter_demand"].sum()),
    }


def _priority(score: float) -> str:
    if score >= 0.78:
        return "critical"
    if score >= 0.60:
        return "high"
    if score >= 0.40:
        return "medium"
    return "low"
