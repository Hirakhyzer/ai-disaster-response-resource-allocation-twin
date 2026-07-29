"""Run the independent synthetic disaster-response resource allocation digital twin.

The command uses only fictional zones, facilities, supplies, roads, and disaster
scenario parameters. It demonstrates emergency demand forecasting, shelter and
hospital capacity auditing, route-delay modeling, transparent resource allocation,
equity-gap review, scenario comparison, reporting, figures, and a hash-chained
audit log.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from disastertwin.allocation import allocate_resources, allocation_summary
from disastertwin.audit import append_record, verify_log
from disastertwin.capacity import audit_facility_capacity, capacity_summary, supply_shortage_summary
from disastertwin.config import ensure_output_dirs, set_seed
from disastertwin.demand import demand_summary, forecast_emergency_demand
from disastertwin.equity import audit_equity, equity_summary
from disastertwin.reporting import write_report
from disastertwin.routing import audit_route_delays, routing_summary, zone_access_summary
from disastertwin.scenarios import compare_response_strategies, scenario_summary
from disastertwin.synthetic import SyntheticDisasterConfig, generate_synthetic_disaster_data
from disastertwin.visualization import (
    plot_capacity_pressure,
    plot_demand_by_zone,
    plot_equity_gap,
    plot_resource_shortages,
    plot_route_delay,
    plot_scenario_comparison,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic disaster-response resource allocation digital twin.")
    parser.add_argument("--zones", type=int, default=20)
    parser.add_argument("--facilities", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--disaster-type", default="flood")
    parser.add_argument("--strategy", default="balanced")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    data = generate_synthetic_disaster_data(SyntheticDisasterConfig(
        zones=args.zones,
        facilities=args.facilities,
        seed=args.seed,
        disaster_type=args.disaster_type,
    ))
    scenario = data["scenario"]
    zones = data["zones"]
    facilities = data["facilities"]
    supplies = data["supplies"]
    roads = data["roads"]

    demand = forecast_emergency_demand(zones, scenario)
    capacity = audit_facility_capacity(facilities, supplies, demand)
    shortages = supply_shortage_summary(supplies, demand)
    routes = audit_route_delays(roads, zones, scenario)
    zone_access = zone_access_summary(routes, zones)
    allocation = allocate_resources(demand, supplies, zone_access, strategy=args.strategy)
    equity = audit_equity(demand, allocation, zone_access)
    comparison = compare_response_strategies(demand, supplies, zone_access)

    summary = {
        "seed": args.seed,
        "disaster_type": args.disaster_type,
        "strategy": args.strategy,
        "synthetic_zone_count": int(len(zones)),
        "synthetic_facility_count": int(len(facilities)),
        "synthetic_supply_record_count": int(len(supplies)),
        "synthetic_road_link_count": int(len(roads)),
        "data_origin": "synthetic fictional disaster-response planning data",
        "decision_boundary": "planning support only; not dispatch, evacuation command, public warning, or medical triage",
    }
    summary.update(demand_summary(demand))
    summary.update(capacity_summary(capacity, shortages))
    summary.update(routing_summary(routes))
    summary.update(allocation_summary(allocation))
    summary.update(equity_summary(equity))
    summary.update(scenario_summary(comparison))

    scenario.to_csv(outputs["results"] / "synthetic_disaster_scenario.csv", index=False)
    zones.to_csv(outputs["results"] / "synthetic_zones.csv", index=False)
    facilities.to_csv(outputs["results"] / "synthetic_facilities.csv", index=False)
    supplies.to_csv(outputs["results"] / "synthetic_supply_inventory.csv", index=False)
    roads.to_csv(outputs["results"] / "synthetic_road_links.csv", index=False)
    demand.to_csv(outputs["results"] / "synthetic_emergency_demand.csv", index=False)
    capacity.to_csv(outputs["results"] / "synthetic_capacity_audit.csv", index=False)
    shortages.to_csv(outputs["results"] / "synthetic_resource_shortages.csv", index=False)
    routes.to_csv(outputs["results"] / "synthetic_route_delay_audit.csv", index=False)
    zone_access.to_csv(outputs["results"] / "synthetic_zone_access_summary.csv", index=False)
    allocation.to_csv(outputs["results"] / "synthetic_resource_allocation.csv", index=False)
    equity.to_csv(outputs["results"] / "synthetic_equity_audit.csv", index=False)
    comparison.to_csv(outputs["results"] / "synthetic_scenario_comparison.csv", index=False)

    audit_path = outputs["audit"] / "disaster_response_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "independent synthetic disaster-response planning support only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_disaster_response_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_disaster_response_report.md", summary, demand, capacity, shortages, routes, allocation, equity, comparison)
    plot_demand_by_zone(demand, outputs["figures"] / "synthetic_demand_by_zone.png")
    plot_capacity_pressure(capacity, outputs["figures"] / "synthetic_capacity_pressure.png")
    plot_resource_shortages(shortages, outputs["figures"] / "synthetic_resource_shortages.png")
    plot_equity_gap(equity, outputs["figures"] / "synthetic_equity_gap.png")
    plot_scenario_comparison(comparison, outputs["figures"] / "synthetic_scenario_comparison.png")
    plot_route_delay(routes, outputs["figures"] / "synthetic_route_delay.png")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
