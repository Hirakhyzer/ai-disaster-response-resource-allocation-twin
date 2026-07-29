"""Synthetic disaster-response data generator.

All records are fictional and intended for planning-support research only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

DISASTER_TYPES = ["flood", "heatwave", "earthquake", "wildfire_smoke", "storm_surge"]
RESOURCE_TYPES = ["food_packs", "water_liters", "medical_kits", "rescue_teams", "buses", "shelter_beds"]


@dataclass(frozen=True)
class SyntheticDisasterConfig:
    """Configuration for the synthetic disaster generator."""
    zones: int = 20
    facilities: int = 10
    seed: int = 42
    disaster_type: str = "flood"


def generate_synthetic_disaster_data(config: SyntheticDisasterConfig) -> dict[str, pd.DataFrame]:
    """Generate fictional zones, facilities, supplies, roads, and scenario settings."""
    if config.zones < 6:
        raise ValueError("zones must be at least 6")
    if config.facilities < 4:
        raise ValueError("facilities must be at least 4")
    disaster_type = config.disaster_type if config.disaster_type in DISASTER_TYPES else "flood"
    rng = np.random.default_rng(config.seed)

    zones = _zones(config.zones, disaster_type, rng)
    facilities = _facilities(config.facilities, zones, rng)
    supplies = _supplies(facilities, rng)
    roads = _roads(zones, rng)
    scenario = pd.DataFrame([{
        "scenario_id": "SCN-001",
        "disaster_type": disaster_type,
        "severity_index": float(np.round(rng.uniform(0.55, 0.92), 3)),
        "forecast_horizon_hours": int(rng.choice([24, 36, 48, 72])),
        "planning_boundary": "synthetic planning exercise only",
    }])
    return {
        "scenario": scenario,
        "zones": zones,
        "facilities": facilities,
        "supplies": supplies,
        "roads": roads,
    }


def _zones(count: int, disaster_type: str, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for idx in range(count):
        exposure = float(np.round(rng.beta(2.2, 2.0), 3))
        social_vulnerability = float(np.round(rng.beta(2.0, 2.4), 3))
        population = int(rng.integers(1800, 24000))
        rows.append({
            "zone_id": f"Z{idx + 1:03d}",
            "zone_name": f"Synthetic Zone {idx + 1}",
            "disaster_type": disaster_type,
            "population": population,
            "households": int(population / rng.uniform(2.4, 3.7)),
            "exposure_index": exposure,
            "social_vulnerability_index": social_vulnerability,
            "elderly_share": float(np.round(rng.uniform(0.06, 0.32), 3)),
            "disability_access_need": float(np.round(rng.uniform(0.04, 0.26), 3)),
            "vehicle_access_gap": float(np.round(rng.uniform(0.05, 0.45), 3)),
            "population_density_index": float(np.round(rng.uniform(0.25, 1.0), 3)),
            "critical_infrastructure_count": int(rng.integers(0, 7)),
            "baseline_power_outage_probability": float(np.round(rng.uniform(0.08, 0.55), 3)),
            "synthetic_data_notice": "fictional planning zone",
        })
    return pd.DataFrame(rows)


def _facilities(count: int, zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    types = ["shelter", "hospital", "distribution_hub", "emergency_ops", "staging_area"]
    rows = []
    for idx in range(count):
        facility_type = str(rng.choice(types, p=[0.34, 0.20, 0.24, 0.08, 0.14]))
        capacity_base = {
            "shelter": (250, 2500),
            "hospital": (80, 850),
            "distribution_hub": (900, 6500),
            "emergency_ops": (40, 220),
            "staging_area": (120, 900),
        }[facility_type]
        rows.append({
            "facility_id": f"F{idx + 1:03d}",
            "facility_name": f"Synthetic {facility_type.replace('_', ' ').title()} {idx + 1}",
            "facility_type": facility_type,
            "zone_id": str(rng.choice(zones["zone_id"])),
            "capacity": int(rng.integers(*capacity_base)),
            "backup_power": bool(rng.random() > 0.24),
            "accessible_design": bool(rng.random() > 0.30),
            "staffing_readiness": float(np.round(rng.uniform(0.42, 0.96), 3)),
            "operational_status": str(rng.choice(["open", "limited", "standby"], p=[0.70, 0.22, 0.08])),
            "synthetic_data_notice": "fictional facility",
        })
    return pd.DataFrame(rows)


def _supplies(facilities: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for facility in facilities.itertuples(index=False):
        for resource in RESOURCE_TYPES:
            base = {
                "food_packs": (300, 10000),
                "water_liters": (1000, 60000),
                "medical_kits": (20, 1400),
                "rescue_teams": (1, 32),
                "buses": (0, 45),
                "shelter_beds": (30, 2600),
            }[resource]
            rows.append({
                "facility_id": facility.facility_id,
                "resource_type": resource,
                "available_units": int(rng.integers(*base)),
                "resupply_hours": int(rng.integers(6, 96)),
                "evidence_status": str(rng.choice(["verified", "estimated", "stale"], p=[0.58, 0.30, 0.12])),
            })
    return pd.DataFrame(rows)


def _roads(zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    zone_ids = list(zones["zone_id"])
    rows = []
    edge_count = max(len(zone_ids) * 2, 12)
    for idx in range(edge_count):
        start, end = rng.choice(zone_ids, size=2, replace=False)
        rows.append({
            "road_id": f"R{idx + 1:03d}",
            "from_zone": str(start),
            "to_zone": str(end),
            "baseline_travel_minutes": float(np.round(rng.uniform(8, 70), 2)),
            "damage_probability": float(np.round(rng.beta(1.8, 3.4), 3)),
            "debris_index": float(np.round(rng.uniform(0.0, 0.75), 3)),
            "flood_or_fire_exposure": float(np.round(rng.uniform(0.0, 0.92), 3)),
            "road_capacity_index": float(np.round(rng.uniform(0.35, 1.0), 3)),
            "critical_route": bool(rng.random() > 0.68),
        })
    return pd.DataFrame(rows)
