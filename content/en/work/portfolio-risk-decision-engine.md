---
title: Portfolio Risk Decision Engine
summary: A Python workflow comparing portfolio risk, historical stress exposure, and constrained rebalancing decisions.
question: How do tracking error, historical stress losses, concentration, and trading costs affect a rebalancing decision?
approach: Implemented risk diagnostics, historical stress tests, CVXPY optimization, and a walk-forward strategy comparison.
field: Portfolio risk / decision support
status: Research prototype
stage: prototype
order: 1
repository: https://github.com/OliviaLi22/portfolio-risk-decision-engine
pipeline: Validated ETF prices | Risk diagnostics | Stress and optimization | Walk-forward comparison | Reports and dashboard
---
## Research question

How do tracking error, concentration, exposure to past stress periods, and trading costs point toward different choices when rebalancing a portfolio?

## Why I built it

A risk estimate is more useful when the decision it informs, and the assumptions behind that decision, are visible. This project builds a reproducible workflow for comparing several objectives rather than treating any one metric as a complete answer. It is an illustrative research system, not a client portfolio or investment recommendation.

## What is implemented

- A Python command-line workflow validates adjusted ETF prices, stores local Parquet data, and computes volatility, tracking error, drawdown, concentration, and asset risk contributions.
- Historical scenarios use the observed COVID-19 selloff and 2022 equity/bond drawdown windows.
- A CVXPY optimizer evaluates rebalancing under tracking-error, asset-weight, and turnover limits while accounting for estimated trading costs.
- A 2023–2025 walk-forward comparison evaluates no rebalancing, a rules-based approach, and optimized decisions using the same held-out dates.
- Reporting code generates CSV tables, figures, a written decision summary, robustness analyses, and an offline dashboard from local data. Synthetic-fixture tests cover the analytical modules.

## Data and assumptions

The configured illustration holds SPY, QQQ, IWM, IEF, and GLD against an SPY benchmark, using daily market data from 2018 through 2025. Prices come from Yahoo Finance. The portfolio, stress windows, risk budgets, trading costs, and rebalance cadence are explicit configuration choices; they were not calibrated to a client mandate. The full-history diagnostic and walk-forward comparison use different rebalancing conventions, as documented in the repository.

## Results and visualizations

The code generates charts and an offline dashboard after market data are downloaded locally. Data snapshots and generated reports are excluded from the public repository, so no numerical outcome or performance claim is published here. The [methodology notes](https://github.com/OliviaLi22/portfolio-risk-decision-engine/blob/master/docs/implementation_notes.md) and [robustness notes](https://github.com/OliviaLi22/portfolio-risk-decision-engine/blob/master/docs/robustness.md) explain how to interpret the outputs.

## Limitations

Yahoo Finance data can contain errors or revisions. The selected ETF universe and historical stress windows are illustrative; the covariance window, constraints, and cost assumptions affect the decisions. The model omits taxes, market impact, liquidity, and intraday execution. Historical walk-forward comparisons cannot establish future performance or crisis protection.

## What the work makes clear

The documented robustness analysis treats predicted tracking error, realized tracking error, stress exposure, and diversification as separate claims. Improving one does not establish improvement in the others. That distinction is central to reading the engine's decisions responsibly.
