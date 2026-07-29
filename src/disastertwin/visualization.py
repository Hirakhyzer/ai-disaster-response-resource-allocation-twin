"""Plotting helpers for synthetic disaster-response outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_demand_by_zone(demand: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    demand.head(12).sort_values("demand_index").plot(x="zone_id", y="demand_index", kind="barh", ax=ax, legend=False)
    ax.set_title("Highest synthetic demand zones")
    ax.set_xlabel("Demand index")
    _save(fig, path)


def plot_capacity_pressure(capacity: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    capacity["capacity_pressure_class"].value_counts().reindex(["low", "medium", "high", "critical"]).fillna(0).plot(kind="bar", ax=ax)
    ax.set_title("Facility capacity pressure classes")
    ax.set_xlabel("Pressure class")
    ax.set_ylabel("Facility count")
    _save(fig, path)


def plot_resource_shortages(shortages: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    shortages.sort_values("shortage_score").plot(x="resource_type", y="shortage_score", kind="barh", ax=ax, legend=False)
    ax.set_title("Resource shortage scores")
    ax.set_xlabel("Shortage score")
    _save(fig, path)


def plot_equity_gap(equity: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    equity.head(12).sort_values("equity_gap_score").plot(x="zone_id", y="equity_gap_score", kind="barh", ax=ax, legend=False)
    ax.set_title("Highest synthetic equity-gap zones")
    ax.set_xlabel("Equity gap score")
    _save(fig, path)


def plot_scenario_comparison(comparison: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    comparison.sort_values("overall_planning_score").plot(x="strategy", y="overall_planning_score", kind="barh", ax=ax, legend=False)
    ax.set_title("Response strategy comparison")
    ax.set_xlabel("Overall planning score")
    _save(fig, path)


def plot_route_delay(routes: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    routes["delay_minutes"].plot(kind="hist", bins=12, ax=ax)
    ax.set_title("Synthetic route delay distribution")
    ax.set_xlabel("Delay minutes")
    _save(fig, path)
