# Code from "Can you teach me how to trade?" by Caio Marchesani
# https://caiomarchesani.com/articles/can-you-teach-me-how-to-trade/

import numpy as np

rng = np.random.default_rng(1275)
YEARS, TRADES, WIN_RATE = 10_000, 250, 0.55
wins = rng.random((YEARS, TRADES)) < WIN_RATE  # same luck for every size

print(f"{'Risk per trade':>14} {'Median year':>12} {'Fall 20%':>9}"
      f" {'Fall 50%':>9} {'Ending down':>12}")
for risk in (0.01, 0.02, 0.05, 0.10, 0.20):
    equity = np.cumprod(np.where(wins, 1 + risk, 1 - risk), axis=1)
    peak = np.maximum.accumulate(np.maximum(equity, 1), axis=1)
    worst = (equity / peak).min(axis=1) - 1
    print(f"{risk:>14.0%} {np.median(equity[:, -1]) - 1:>+12.0%}"
          f" {(worst <= -0.2).mean():>9.0%} {(worst <= -0.5).mean():>9.0%}"
          f" {(equity[:, -1] < 1).mean():>12.0%}")

runs = ["".join("W" if w else "L" for w in year).split("W") for year in wins]
longest = np.array([max(len(r) for r in year) for year in runs])
print(f"Longest losing run in a year: median {np.median(longest):.0f},",
      f"6 or more in {(longest >= 6).mean():.0%} of years,",
      f"8 or more in {(longest >= 8).mean():.0%}")
