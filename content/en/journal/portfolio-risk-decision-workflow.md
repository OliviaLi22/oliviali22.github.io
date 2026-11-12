---
title: From a risk number to a portfolio decision
date: 2026-11-12
category: Project note
tags: Portfolio Risk, Research Methods
summary: A methodology note on bringing tracking error, historical stress, concentration, and trading costs into one inspectable workflow.
---
## The question behind the measure

Tracking error describes how a portfolio's returns differ from a benchmark. It does not, on its own, explain concentration, the effect of a past stress period, or the cost of changing positions. A useful research workflow keeps those questions distinct so that a rebalancing choice can be examined rather than hidden behind a single score.

## An illustrative workflow

The [Portfolio Risk Decision Engine](/work/portfolio-risk-decision-engine/) is a Python research prototype built around an illustrative five-ETF portfolio and an SPY benchmark. It calculates volatility, tracking error, drawdown, concentration, and asset risk contributions. It also examines observed returns during the 2020 COVID-19 selloff and a 2022 equity and bond drawdown window.

The decision stage uses constrained optimization to compare tracking error, historical stress exposure, and estimated trading costs. A walk-forward comparison from 2023 through 2025 applies the same held-out dates to no rebalancing, a rules-based approach, and optimized decisions. The code produces local tables, figures, and an offline dashboard.

## Reading the output carefully

Predicted tracking error, realized tracking error, and exposure to an observed stress window answer different questions. A lower value for one does not establish a better outcome for the others. That distinction matters when reading a portfolio decision as research evidence.

The public repository includes the [code and methodology](https://github.com/OliviaLi22/portfolio-risk-decision-engine), while market data snapshots and generated reports remain outside Git. This note makes no numerical performance claim. The selected assets, historical windows, estimation choices, and trading-cost assumptions all shape the comparisons; historical results cannot establish future performance.
