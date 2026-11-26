# Code from "The Brent-WTI spread: why the physical gap hit $37 in 2026" by Caio Marchesani
# https://caiomarchesani.com/articles/brent-wti-spread/

import numpy as np
import pandas as pd
import yfinance as yf

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
LAST = "2026-11-03"   # the last day with both spot prices when I ran this
PERIODS = (("1987", "2010"), ("2011", "2015"), ("2016", "2025"), ("2026", "2026"))


def fred(series):
    s = pd.read_csv(FRED + series, index_col=0, parse_dates=True, na_values=".").squeeze()
    return s.dropna().loc[:LAST]


def front_month(ticker):
    px = yf.download(ticker, start="2016-01-01", end="2026-11-07", auto_adjust=True, progress=False)["Close"]
    return px.squeeze().dropna()


spot = pd.DataFrame({"brent": fred("DCOILBRENTEU"), "wti": fred("DCOILWTICO")}).dropna()
s = spot["brent"] - spot["wti"]
print(f"Spot Brent minus spot WTI, {len(s)} days, {s.index[0]:%d %b %Y} to {s.index[-1]:%d %b %Y}")

print("\nPeriod       days    mean  median  5th pct  95th pct  WTI dearer")
for a, b in PERIODS:
    x = s.loc[a:b]
    print(f"{a}-{b}{len(x):7d}{x.mean():8.2f}{x.median():8.2f}{x.quantile(0.05):9.2f}"
          f"{x.quantile(0.95):10.2f}{(x < 0).mean() * 100:11.1f}%")

print("\nExtremes")
for label, d in (("WTI furthest above Brent", s.idxmin()), ("Brent furthest above WTI", s.idxmax()),
                 ("widest, 2011-2015", s.loc["2011":"2015"].idxmax()),
                 ("widest, 2026", s.loc["2026"].idxmax())):
    print(f"  {label:26s}{d:%d %b %Y}  Brent {spot.at[d, 'brent']:7.2f}"
          f"  WTI {spot.at[d, 'wti']:7.2f}  spread {s[d]:+7.2f}")
print(f"  latest, {s.index[-1]:%d %b %Y}: {s.iloc[-1]:+.2f}")

print("\nAverage spot spread by year, 2010-2025")
yearly = s.loc["2010":"2025"].groupby(s.loc["2010":"2025"].index.year).mean()
print("  " + "  ".join(f"{y}:{v:.2f}" for y, v in yearly.items()))

pct = (s / spot["wti"] * 100)[spot["wti"] > 0]
print("\nThe spread as a percentage of the WTI price")
for a, b in PERIODS:
    x = pct.loc[a:b]
    print(f"  {a}-{b}: median {x.median():5.1f}%, 95th pct {x.quantile(0.95):5.1f}%")
for d in (s.loc["2011":"2015"].idxmax(), s.loc["2026"].idxmax()):
    print(f"  {d:%d %b %Y}: {pct[d]:.1f}%")


def half_life(x, k):
    """Fit the change over k days against the starting level: x[t+k] - x[t] = a + b x[t]."""
    b, a = np.polyfit(x.iloc[:-k], (x.shift(-k) - x).iloc[:-k], 1)
    return k * np.log(0.5) / np.log(1 + b), -a / b


print("\nHalf-life of the spot spread in trading days, measured over 1, 5 and 21 days")
for a, b in (("2011", "2015"), ("2016", "2019"), ("2021", "2025"), ("2026", "2026")):
    x = s.loc[a:b]
    h = [half_life(x, k) for k in (1, 5, 21)]
    print(f"  {a}-{b}: {h[0][0]:5.1f} {h[1][0]:5.1f} {h[2][0]:5.1f}"
          f"   level {h[0][1]:5.2f} (1 day), {h[2][1]:5.2f} (21 days)")

fut = pd.DataFrame({"brent": front_month("BZ=F"), "wti": front_month("CL=F")}).dropna()
f = fut["brent"] - fut["wti"]
print(f"\nFront-month futures spread in 2026: mean {f['2026'].mean():.2f},"
      f" widest {f['2026'].max():.2f} on {f['2026'].idxmax():%d %b %Y},"
      f" last {f.iloc[-1]:.2f} on {f.index[-1]:%d %b %Y}")
d = s.loc["2026"].idxmax()
print(f"On {d:%d %b %Y}: spot spread {s[d]:.2f}, futures spread {f[d]:.2f}")

print("\nDaily change in the spread: median size, and correlation with the next day's change")
for name, x in (("spot", s), ("futures", f)):
    for a, b in (("2021", "2025"), ("2026", "2026")):
        dx = x.loc[a:b].diff().dropna()
        print(f"  {name:8s}{a}-{b}: {dx.abs().median():.2f}  {dx.autocorr():+.2f}")

gap = (spot["brent"] - fut["brent"]).dropna()
print("\nSpot Brent minus front-month Brent futures")
for a, b in (("2016", "2025"), ("2026", "2026")):
    x = gap.loc[a:b]
    print(f"  {a}-{b}: median {x.median():+.2f}, widest {x.max():+.2f} on {x.idxmax():%d %b %Y},"
          f" above $5 on {(x > 5).sum()} of {len(x)} days, above $10 on {(x > 10).sum()}")
