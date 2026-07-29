% Plot synthetic disaster-response outputs exported by the Python lab.
% Run after: python scripts/run_synthetic_disaster_lab.py

resultsDir = fullfile("outputs", "results");
figuresDir = fullfile("outputs", "figures");
if ~exist(figuresDir, "dir")
    mkdir(figuresDir);
end

demand = readtable(fullfile(resultsDir, "synthetic_emergency_demand.csv"));
equity = readtable(fullfile(resultsDir, "synthetic_equity_audit.csv"));
comparison = readtable(fullfile(resultsDir, "synthetic_scenario_comparison.csv"));

figure;
bar(categorical(demand.zone_id(1:min(12,height(demand)))), demand.demand_index(1:min(12,height(demand))));
title("Synthetic Demand Index by Zone");
ylabel("Demand index");
saveas(gcf, fullfile(figuresDir, "matlab_demand_index.png"));

figure;
bar(categorical(equity.zone_id(1:min(12,height(equity)))), equity.equity_gap_score(1:min(12,height(equity))));
title("Synthetic Equity Gap by Zone");
ylabel("Equity gap score");
saveas(gcf, fullfile(figuresDir, "matlab_equity_gap.png"));

figure;
bar(categorical(comparison.strategy), comparison.overall_planning_score);
title("Synthetic Response Strategy Comparison");
ylabel("Overall planning score");
saveas(gcf, fullfile(figuresDir, "matlab_strategy_comparison.png"));
