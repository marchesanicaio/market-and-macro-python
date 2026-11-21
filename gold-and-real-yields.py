# Code from "Gold and real yields: the model that stopped working in 2022" by Caio Marchesani
# https://caiomarchesani.com/articles/gold-and-real-yields/

import numpy as np
import pandas as pd
import yfinance as yf

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="


def fred(series):
    return pd.read_csv(FRED + series, index_col=0, parse_dates=True,
                       na_values=".").squeeze()


def ols(y, *x):
    """Coefficients (constant first), t-statistics and R-squared."""
    X = np.column_stack([np.ones(len(y))] + [np.asarray(v, float) for v in x])
    y = np.asarray(y, float)
    b = np.linalg.solve(X.T @ X, X.T @ y)
    e = y - X @ b
    t = b / np.sqrt(e @ e / (len(y) - X.shape[1]) * np.diag(np.linalg.inv(X.T @ X)))
    return b, t, 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))


def adf(e):
    """Engle-Granger step two: ADF with a constant and one lag. t and half-life."""
    e = np.asarray(e, float)
    d = np.diff(e)
    b, t, _ = ols(d[1:], e[1:-1], d[:-1])
    return t[1], np.log(0.5) / np.log(1 + b[1])


gold = yf.download("GC=F", start="2006-01-01", end="2026-11-07",
                   progress=False)["Close"].squeeze()
real = fred("DFII10")                          # 10-year TIPS yield, per cent
usd = fred("DTWEXBGS")                         # broad trade-weighted dollar

w = pd.DataFrame({"gold": gold, "real": real}).dropna()
w = w.resample("W-FRI").last().dropna()        # Friday closes
old = w.loc[:"2021"]

b, _, r2 = ols(np.log(old.gold), old.real)
fit = np.exp(b[0] + b[1] * w.real)
gap = np.log(w.gold / fit)                     # log distance from the line
miss = gap.loc[:"2021"].std(ddof=2)
print(f"2006-2021 fit ({len(old)} weeks): gold = ${np.exp(b[0]):,.0f} x",
      f"exp({b[1]:.3f} x real yield), R2 {r2:.2f}")
print(f"  one point on the real yield: {np.exp(b[1]) - 1:+.0%} on gold;",
      f"typical miss {miss:.0%}")

stat, half = adf(gap.loc[:"2021"])
print(f"  cointegration test, 2006-2021: t = {stat:.2f}, half-life {half:.0f} weeks")
bw, _, _ = ols(np.log(w.gold), w.real)
stat, half = adf(np.log(w.gold) - bw[0] - bw[1] * w.real)
print(f"  same test, 2006-2026 refitted: t = {stat:.2f}, half-life {half:,.0f} weeks"
      " (5% critical value -3.34)")
inside = gap.index[gap <= 2 * miss][-1]
print(f"  last week within two typical misses of the line: {inside:%d %b %Y}")

print("Week ending  real yield     gold     fit  gold/fit")
for year in range(2021, 2027):
    row = w.loc[str(year)].iloc[-1]
    f = fit.loc[row.name]
    print(f"{row.name:%d %b %Y}  {row.real:10.2f}  {row.gold:7,.0f}  {f:6,.0f}"
          f"  {row.gold / f:8.2f}")

lo, hi = w.real.loc["2021"].idxmin(), w.real.loc["2023"].idxmax()
print(f"{lo:%d %b %Y} to {hi:%d %b %Y}: real yield {w.real[lo]:.2f} to"
      f" {w.real[hi]:.2f}, gold ${w.gold[lo]:,.0f} to ${w.gold[hi]:,.0f}"
      f" ({w.gold[hi] / w.gold[lo] - 1:+.0%}); the fit implied"
      f" {np.exp(b[1] * (w.real[hi] - w.real[lo])) - 1:+.0%}")

d = pd.DataFrame({"gold": np.log(w.gold).diff() * 100,
                  "real": w.real.diff()}).dropna()
for label, part in (("2006-2021", d.loc[:"2021"]), ("2022-2026", d.loc["2022":])):
    beta = ols(part.gold, part.real)[0][1]
    print(f"Weekly changes, {label}: correlation {part.gold.corr(part.real):+.2f},",
          f"{beta:+.1f}% on gold per point")
late = d.loc["2022":]
print("By year:", ", ".join(f"{year} {g.gold.corr(g.real):+.2f}"
                            for year, g in late.groupby(late.index.year)))
roll = d.gold.rolling(52).corr(d.real).dropna()
for label, part in (("to 2021", roll.loc[:"2021"]), ("since 2022", roll.loc["2022":])):
    print(f"52-week correlation {label}: below zero in {(part < 0).sum()} of"
          f" {len(part)} weeks, range {part.min():+.2f} to {part.max():+.2f}")

x = pd.DataFrame({"gold": gold, "real": real, "usd": usd}).dropna()
x = x.resample("W-FRI").last().dropna()
dx = pd.DataFrame({"gold": np.log(x.gold).diff() * 100, "real": x.real.diff(),
                   "usd": np.log(x.usd).diff() * 100}).dropna()
print("Weekly gold (%) on real yield (points) and the dollar (%), together:")
for label, p in (("2006-2021", dx.loc[:"2021"]), ("2022-2026", dx.loc["2022":])):
    bb, tt, rr = ols(p.gold, p.real, p.usd)
    print(f"  {label}: real yield {bb[1]:+.1f} (t {tt[1]:.1f}), dollar {bb[2]:+.2f}"
          f" (t {tt[2]:.1f}), R2 {rr:.2f}, {len(p)} weeks")
