"""Route-delay and access-risk simulation for synthetic disaster response."""

from __future__ import annotations

import numpy as np
import pandas as pd


def audit_route_delays(roads: pd.DataFrame, zones: pd.DataFrame, scenario: pd.DataFrame) -> pd.DataFrame:
    """Estimate road and zone access delays under disaster stress."""
    severity = float(scenario.iloc[0]["severity_index"]) if not scenario.empty else 0.7
    zone_exposure = zones.set_index("zone_id")["exposure_index"].to_dict()
    rows = []
    for road in roads.itertuples(index=False):
        endpoint_exposure = np.mean([zone_exposure.get(road.from_zone, 0.5), zone_exposure.get(road.to_zone, 0.5)])
        delay_multiplier = 1 + 1.25 * float(road.damage_probability) + 0.85 * float(road.debris_index) + 0.65 * float(road.flood_or_fire_exposure) + 0.35 * severity
        capacity_penalty = 1 + max(0, 0.75 - float(road.road_capacity_index))
        travel_minutes = float(road.baseline_travel_minutes) * delay_multiplier * capacity_penalty
        access_risk = float(np.clip(0.30 * road.damage_probability + 0.22 * road.debris_index + 0.20 * road.flood_or_fire_exposure + 0.18 * endpoint_exposure + 0.10 * severity, 0, 1))
        rows.append({
            "road_id": road.road_id,
            "from_zone": road.from_zone,
            "to_zone": road.to_zone,
            "baseline_travel_minutes": float(road.baseline_travel_minutes),
            "estimated_travel_minutes": round(travel_minutes, 3),
            "delay_minutes": round(max(0.0, travel_minutes - float(road.baseline_travel_minutes)), 3),
            "access_risk_score": round(access_risk, 4),
            "access_risk_class": _risk_class(access_risk),
            "critical_route": bool(road.critical_route),
        })
    return pd.DataFrame(rows).sort_values("access_risk_score", ascending=False).reset_index(drop=True)


def zone_access_summary(route_audit: pd.DataFrame, zones: pd.DataFrame) -> pd.DataFrame:
    """Aggregate road delay and access risk by zone."""
    rows = []
    for zone in zones.itertuples(index=False):
        group = route_audit[route_audit["from_zone"].eq(zone.zone_id) | route_audit["to_zone"].eq(zone.zone_id)]
        if group.empty:
            mean_delay = 0.0
            access_risk = 0.0
        else:
            mean_delay = float(group["delay_minutes"].mean())
            access_risk = float(group["access_risk_score"].mean())
        rows.append({
            "zone_id": zone.zone_id,
            "mean_route_delay_minutes": round(mean_delay, 3),
            "zone_access_risk_score": round(access_risk, 4),
            "route_count": int(len(group)),
            "is_access_fragile": bool(access_risk >= 0.55 or mean_delay >= 45),
        })
    return pd.DataFrame(rows)


def routing_summary(route_audit: pd.DataFrame) -> dict[str, int | float]:
    """Summarize route-delay audit."""
    if route_audit.empty:
        return {"high_access_risk_route_count": 0, "mean_delay_minutes": 0.0}
    return {
        "high_access_risk_route_count": int(route_audit["access_risk_class"].isin(["high", "critical"]).sum()),
        "mean_delay_minutes": float(route_audit["delay_minutes"].mean()),
        "max_delay_minutes": float(route_audit["delay_minutes"].max()),
    }


def _risk_class(score: float) -> str:
    if score >= 0.78:
        return "critical"
    if score >= 0.60:
        return "high"
    if score >= 0.36:
        return "medium"
    return "low"
