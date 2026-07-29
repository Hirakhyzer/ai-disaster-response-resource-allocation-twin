from disastertwin.allocation import allocate_resources
from disastertwin.capacity import audit_facility_capacity, supply_shortage_summary
from disastertwin.demand import forecast_emergency_demand
from disastertwin.equity import audit_equity
from disastertwin.routing import audit_route_delays, zone_access_summary
from disastertwin.scenarios import compare_response_strategies
from disastertwin.synthetic import SyntheticDisasterConfig, generate_synthetic_disaster_data


def _data():
    return generate_synthetic_disaster_data(SyntheticDisasterConfig(zones=9, facilities=5, seed=11))


def test_disaster_modules_return_expected_rows():
    data = _data()
    demand = forecast_emergency_demand(data["zones"], data["scenario"])
    capacity = audit_facility_capacity(data["facilities"], data["supplies"], demand)
    shortages = supply_shortage_summary(data["supplies"], demand)
    routes = audit_route_delays(data["roads"], data["zones"], data["scenario"])
    access = zone_access_summary(routes, data["zones"])
    allocation = allocate_resources(demand, data["supplies"], access)
    equity = audit_equity(demand, allocation, access)
    comparison = compare_response_strategies(demand, data["supplies"], access)

    assert len(demand) == len(data["zones"])
    assert len(capacity) == len(data["facilities"])
    assert len(shortages) == 6
    assert len(routes) == len(data["roads"])
    assert len(access) == len(data["zones"])
    assert len(equity) == len(data["zones"])
    assert comparison["overall_planning_score"].between(0, 1).all()
    assert allocation["service_ratio"].ge(0).all()


def test_priority_and_equity_classes_are_valid():
    data = _data()
    demand = forecast_emergency_demand(data["zones"], data["scenario"])
    routes = audit_route_delays(data["roads"], data["zones"], data["scenario"])
    access = zone_access_summary(routes, data["zones"])
    allocation = allocate_resources(demand, data["supplies"], access, strategy="equity_priority")
    equity = audit_equity(demand, allocation, access)
    assert demand["priority_class"].isin(["low", "medium", "high", "critical"]).all()
    assert equity["equity_priority_class"].isin(["low", "medium", "high", "critical"]).all()
