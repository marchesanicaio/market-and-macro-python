# Code from "Relative value trading vs directional trading, and what each one teaches you about risk" by Caio Marchesani
# https://caiomarchesani.com/articles/relative-value-trading-vs-directional-trading-key-differences-and-risk-mitigation/

import numpy as np
import pandas as pd
import yfinance as yf

px = yf.download(["BZ=F", "CL=F"], start="2010-01-01", end="2026-10-31", interval="1wk")["Close"].dropna()
brent, wti = px["BZ=F"], px["CL=F"]
spread = brent - wti

print("Volatility of weekly changes, $ a barrel a year:")
print("  Brent ", round(brent.diff().std() * np.sqrt(52), 2))
print("  spread", round(spread.diff().std() * np.sqrt(52), 2))
print("Average spread by year:")
print(spread.groupby(spread.index.year).mean().round(2))

# Relative value: when the spread is more than 2 standard deviations from its
# 52-week average, bet on a return to the average. Out at the average, at
# 4 standard deviations against (the spread stop), or after 26 weeks.
z = (spread - spread.rolling(52).mean().shift(1)) / spread.rolling(52).std().shift(1)
rv, pos = [], 0
for t in range(52, len(spread)):
    if pos == 0:
        if abs(z.iloc[t]) > 2:
            pos, entry, start = -np.sign(z.iloc[t]), spread.iloc[t], t
    elif pos * z.iloc[t] >= 0 or pos * z.iloc[t] <= -4 or t - start >= 26:
        rv.append(pos * (spread.iloc[t] - entry))
        pos = 0

# Directional: long Brent above its 26-week average, short below
ma26 = brent.rolling(26).mean()
trend, pos = [], 0
for t in range(25, len(brent)):
    want = 1 if brent.iloc[t] > ma26.iloc[t] else -1
    if pos == 0:
        pos, entry = want, brent.iloc[t]
    elif want != pos:
        trend.append(pos * (brent.iloc[t] - entry))
        pos, entry = want, brent.iloc[t]

for name, p in (("Relative value", pd.Series(rv)), ("Directional", pd.Series(trend))):
    print(f"{name}: {len(p)} trades, {(p > 0).mean():.0%} winners, "
          f"average win {p[p > 0].mean():.2f}, average loss {p[p <= 0].mean():.2f}, "
          f"total {p.sum():.2f}")
