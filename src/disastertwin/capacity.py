"""Capacity and supply pressure audits for synthetic disaster response."""

from __future__ import annotations

import numpy as np
import pandas as pd


def audit_facility_capacity(facilities: pd.DataFrame, supplies: pd.DataFrame, demand: pd.DataFrame) -> pd.DataFrame:
    """Audit shelter, hospital, and supply pressure at facility level."""
    total_shelter = int(demand["shelter_bed_demand"].sum()) if not demand.empty else 0
    total_medical = int(demand["medical_case_demand"].sum()) if not demand.empty else 0
    resource_need = {
        "food_packs": int(demand["food_pack_demand"].sum()) if not demand.empty else 0,
        "water_liters": int(demand["water_liter_demand"].sum()) if not demand.empty else 0,
        "medical_kits": max(1, total_medical // 3),
        "rescue_teams": int(demand["rescue_team_demand"].sum()) if not demand.empty else 0,
        "buses": max(1, total_shelter // 80),
        "shelter_beds": total_shelter,
    }
    supply_totals = supplies.groupby("resource_type", as_index=False)["available_units"].sum()
    supply_lookup = dict(zip(supply_totals["resource_type"], supply_totals["available_units"]))
    shortage_scores = {key: _shortage_score(supply_lookup.get(key, 0), need) for key, need in resource_need.items()}

    rows = []
    for facility in facilities.itertuples(index=False):
        relevant_supplies = supplies[supplies["facility_id"].eq(facility.facility_id)]
        facility_supply_units = int(relevant_supplies["available_units"].sum())
        readiness = float(facility.staffing_readiness)
        backup_penalty = 0.0 if bool(facility.backup_power) else 0.14
        access_penalty = 0.0 if bool(facility.accessible_design) else 0.10
        status_penalty = {"open": 0.0, "limited": 0.16, "standby": 0.25}.get(str(facility.operational_status), 0.1)
        if facility.facility_type == "shelter":
            pressure = total_shelter / max(1, int(facility.capacity) * max(0.2, readiness))
        elif facility.facility_type == "hospital":
            pressure = total_medical / max(1, int(facility.capacity) * max(0.2, readiness))
        elif facility.facility_type == "distribution_hub":
            pressure = np.mean(list(shortage_scores.values())) * 1.4
        else:
            pressure = 0.55 + status_penalty + backup_penalty
        pressure_score = float(np.clip(0.52 * min(1.6, pressure) / 1.6 + backup_penalty + access_penalty + status_penalty, 0, 1))
        rows.append({
            "facility_id": facility.facility_id,
            "facility_type": facility.facility_type,
            "zone_id": facility.zone_id,
            "capacity": int(facility.capacity),
            "staffing_readiness": readiness,
            "facility_supply_units": facility_supply_units,
            "capacity_pressure_score": round(pressure_score, 4),
            "capacity_pressure_class": _pressure_class(pressure_score),
            "backup_power_gap": not bool(facility.backup_power),
            "accessibility_gap": not bool(facility.accessible_design),
            "status_gap": str(facility.operational_status) != "open",
        })
    return pd.DataFrame(rows).sort_values("capacity_pressure_score", ascending=False).reset_index(drop=True)


def supply_shortage_summary(supplies: pd.DataFrame, demand: pd.DataFrame) -> pd.DataFrame:
    """Create resource-level shortage summary."""
    totals = supplies.groupby("resource_type", as_index=False)["available_units"].sum()
    needs = {
        "food_packs": int(demand["food_pack_demand"].sum()),
        "water_liters": int(demand["water_liter_demand"].sum()),
        "medical_kits": max(1, int(demand["medical_case_demand"].sum()) // 3),
        "rescue_teams": int(demand["rescue_team_demand"].sum()),
        "buses": max(1, int(demand["shelter_bed_demand"].sum()) // 80),
        "shelter_beds": int(demand["shelter_bed_demand"].sum()),
    }
    rows = []
    supply_lookup = dict(zip(totals["resource_type"], totals["available_units"]))
    for resource, needed in needs.items():
        available = int(supply_lookup.get(resource, 0))
        gap = max(0, needed - available)
        ratio = available / max(1, needed)
        rows.append({
            "resource_type": resource,
            "required_units": int(needed),
            "available_units": available,
            "shortage_units": int(gap),
            "coverage_ratio": round(float(ratio), 4),
            "shortage_score": round(_shortage_score(available, needed), 4),
            "shortage_class": _pressure_class(_shortage_score(available, needed)),
        })
    return pd.DataFrame(rows).sort_values("shortage_score", ascending=False).reset_index(drop=True)


def capacity_summary(capacity: pd.DataFrame, shortages: pd.DataFrame) -> dict[str, int | float]:
    """Summarize capacity and shortage pressure."""
    if capacity.empty:
        return {"critical_capacity_facility_count": 0, "mean_capacity_pressure_score": 0.0}
    return {
        "critical_capacity_facility_count": int(capacity["capacity_pressure_class"].isin(["high", "critical"]).sum()),
        "mean_capacity_pressure_score": float(capacity["capacity_pressure_score"].mean()),
        "resource_shortage_type_count": int((shortages["shortage_units"] > 0).sum()) if not shortages.empty else 0,
        "highest_resource_shortage_score": float(shortages["shortage_score"].max()) if not shortages.empty else 0.0,
    }


def _shortage_score(available: int | float, needed: int | float) -> float:
    needed = max(1.0, float(needed))
    return float(np.clip((needed - float(available)) / needed, 0, 1))


def _pressure_class(score: float) -> str:
    if score >= 0.78:
        return "critical"
    if score >= 0.60:
        return "high"
    if score >= 0.36:
        return "medium"
    return "low"
