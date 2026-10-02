# Verifying Algorithmic Trading Pedagogy on Live Data: A Reproducible Benchmark of Trend vs. Mean-Reversion Rules (2015–2026)

**Working paper draft — Oxford Algorithmic Trading Benchmark 2026.**
All empirical claims refer to `results/benchmark.json` generated 2026-10-02 from live Yahoo Finance data (SPY 2955 bars, QQQ 2955, BTC-USD 4293).

## 1. Question

Can the evaluation discipline taught in the Oxford Saïd Algorithmic Trading Programme (Vulkan, 6 modules, 4 principles) distinguish investable systematic rules from overfit artefacts when confronted with 2015–2026 live public data?

## 2. Design

Seven systems (SMA 10/30, 20/50, 50/200; RSI 14/30/70, 7/20/80; Donchian 20/10; Buy-and-Hold control), no look-ahead (`shift(1)`), 10 bps/trade + 2× stress, 70/30 IS/OOS, 8-window walk-forward (IS-frac 0.7), 2000-path Monte-Carlo drawdown bands, Deflated Sharpe (K=7), PBO-proxy (IS-winner below-median OOS rate), SMA parameter sweep, logistic RSI+spread overlay.

## 3. Results (verified)

- **H1 (BH dominates return, loses risk): confirmed.** BH total return exceeds every systematic on all symbols (SPY 2.742 vs. best systematic 1.291; QQQ 6.282 vs. 4.350; BTC 271.2 vs. 222.5) with worst MaxDD (−34.1%, −35.6%, −83.4%).
- **H2 (trend > reversion on crypto): confirmed.** BTC trend Sharpe 0.88–1.11 vs. RSI 0.42–0.52; return gap >30×. Equities gap <0.2 Sharpe — regime effect, not parameter luck.
- **H3 (OOS decay): mixed — informative.** BTC decays (RSI 0.62→0.17); SPY/QQQ OOS exceeds IS (bull-regime composition). Fixed splits without regime stratification mislead.
- **H4 (walk-forward fragility ≈25%): confirmed.** 2 of 8 windows invert sign per symbol (e.g., SPY 1.75→−2.52). PBO-proxy 0.125–0.50.
- **H5 (cost veto binds): confirmed.** SPY Donchian −42% under 2× costs vs. SMA_50_200 −2%.
- **H6 (ML overlay ≈ chance): confirmed.** OOS accuracy 55.8/56.9/50.6% — no post-cost edge.

## 4. Contribution

A one-command Docker artefact mapping each Oxford module to an executable check, with three documented hidden patterns (return-vs-pain frontier, crypto trend-reversion asymmetry, inverted equity decay) and an honest DSR-saturation limitation (K=7 → K≥100 grid-as-trials as immediate follow-up).

## 5. Reproduction

`docker compose up research` or `python -m src.experiments.run_benchmark --symbols SPY,QQQ,BTC-USD`. Tests: `pytest tests/ -v`. Data: Yahoo primary, Stooq fallback, synthetic labelled fallback. No keys.

## 6. Ethics / risk

Research only, not investment advice. No live execution. Future live work requires paper-trading gate (≥1 month), pre-registered stops (MC-p5 DD, −15 pp win-rate, 1.5× streak), and microstructure-aware engine (Backtrader/Nautilus) before capital.
