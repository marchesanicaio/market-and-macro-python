# Code from "The yield curve as a recession signal: what fifty years show" by Caio Marchesani
# https://caiomarchesani.com/articles/yield-curve-recession-signal/

from math import erf

import numpy as np
import pandas as pd

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="


def fred(series):
    return pd.read_csv(FRED + series, index_col=0, parse_dates=True,
                       na_values=".").squeeze().dropna()


def runs(negative, least=3):
    """First month, last month and length of each run of inverted months."""
    block = (negative != negative.shift()).cumsum()
    found = [(g.index[0], g.index[-1], len(g))
             for _, g in negative[negative].groupby(block)]
    return [run for run in found if run[2] >= least]


def months(a, b):
    return (b.year - a.year) * 12 + b.month - a.month


daily = fred("T10Y2Y").loc[:"2026-11-06"]     # 10-year minus 2-year yield
spread = daily.resample("MS").mean()
rec = fred("USREC").loc[spread.index[0]:]     # 1 in an NBER recession month
starts = rec.index[(rec == 1) & (rec.shift() == 0)]

print("Signal    months  deepest  recession  lead  last inverted")
matched = set()
for first, last, n in runs(spread < 0):
    if rec.get(first, 0) == 1:
        continue                              # began inside a recession
    low = spread[first:last].min()
    later = starts[starts > first]
    if len(later):
        s = later[0]
        matched.add(s)
        before = spread[first:s - pd.DateOffset(months=1)]
        final = before[before < 0].index[-1]
        print(f"{first:%b %Y}  {n:6}  {low:7.2f}  {s:%b %Y}   {months(first, s):4}"
              f"  {final:%b %Y}")
    else:
        print(f"{first:%b %Y}  {n:6}  {low:7.2f}  none by {rec.index[-1]:%b %Y},"
              f" {months(first, rec.index[-1])} months on")
print("Recessions with no signal first:",
      ", ".join(f"{s:%b %Y}" for s in starts if s not in matched) or "none")

y19 = daily.loc["2019"]
print(f"2019: {int((y19 < 0).sum())} trading days below zero,",
      f"lowest {y19.min():.2f} on {y19.idxmin():%d %b %Y}")
neg = daily.loc["2022":][daily.loc["2022":] < 0]
print(f"2022-24: {len(neg)} trading days below zero, {neg.index[0]:%d %b %Y}",
      f"to {neg.index[-1]:%d %b %Y}, lowest {neg.min():.2f} on {neg.idxmin():%d %b %Y}")
print(f"Latest: {daily.iloc[-1]:+.2f} on {daily.index[-1]:%d %b %Y}")

bills = fred("T10Y3M").loc[:"2026-11-06"].resample("MS").mean()
print("10-year minus 3-month, runs of three months or more:",
      ", ".join(f"{a:%b %Y} ({n})" for a, b, n in runs(bills < 0)))

u = fred("UNRATE").loc["2022":]
print(f"Unemployment: {u['2022-07-01']:.1f}% in Jul 2022, low {u.min():.1f}%",
      f"({u.idxmin():%b %Y}), high {u.max():.1f}% ({u.idxmax():%b %Y}),",
      f"latest {u.iloc[-1]:.1f}% ({u.index[-1]:%b %Y})")

# Why 2022 was different: a probit model, the term premium and debt service
Phi = np.vectorize(lambda z: 0.5 * (1 + erf(z / 2 ** 0.5)))


def probit(x, y):
    """Maximum-likelihood probit of y (0 or 1) on x, by Fisher scoring."""
    X = np.column_stack([np.ones(len(x)), x])
    y = np.asarray(y, float)
    b = np.zeros(2)
    for _ in range(100):
        z = X @ b
        p = np.clip(Phi(z), 1e-12, 1 - 1e-12)
        f = np.exp(-z * z / 2) / np.sqrt(2 * np.pi)
        g = X.T @ (f * (y - p) / (p * (1 - p)))
        H = (X * (f * f / (p * (1 - p)))[:, None]).T @ X
        step = np.linalg.solve(H, g)
        b += step
        if np.abs(step).sum() < 1e-10:
            break
    return b


usrec = fred("USREC")
m3 = (fred("GS10") - fred("TB3MS")).dropna()   # monthly 10-year minus 3-month
fit = pd.DataFrame({"s": m3, "y": usrec.shift(-12)}).loc["1960":"2018"].dropna()
a, b = probit(fit.s, fit.y)
prob = pd.Series(Phi(a + b * m3), index=m3.index)
print(f"Probit, 1960-2018 ({len(fit)} months): P(recession in 12 months) ="
      f" Phi({a:.2f} {b:+.2f} x spread); spread 0: {Phi(a):.0%}, spread -1: {Phi(a - b):.0%}")
begins = usrec.index[(usrec == 1) & (usrec.shift() == 0)]
print("Highest probability in the 24 months before each recession:",
      ", ".join(f"{s:%b %Y} {prob[s - pd.DateOffset(months=24):s - pd.DateOffset(months=1)].max():.0%}"
                for s in begins[begins >= "1962"]))
late = prob.loc["2022":]
over = late.index[late > 0.5]
span = f", {over[0]:%b %Y} to {over[-1]:%b %Y}" if len(over) else ""
print(f"Since 2022: peak {late.max():.0%} ({late.idxmax():%b %Y}); above 50% in {len(over)}"
      f" months{span}; latest {late.iloc[-1]:.0%} ({late.index[-1]:%b %Y})")

month = lambda s: fred(s).loc[:"2026-11-06"].resample("MS").mean()
y10, y2, tp = month("DGS10"), month("DGS2"), month("THREEFYTP10")   # Kim-Wright
print("Deepest month  10y-2y  term premium  expected path (10y - premium - 2y)")
for first, last, n in runs(spread.loc["1990":] < 0):
    worst = spread[first:last].idxmin()
    print(f"{worst:%b %Y}      {spread[worst]:+.2f}         {tp[worst]:+.2f}"
          f"          {y10[worst] - tp[worst] - y2[worst]:+.2f}")

ff, dsr = fred("FEDFUNDS"), fred("TDSP")       # debt service, % of disposable income
q = lambda d: f"Q{(d.month - 1) // 3 + 1} {d.year}"
top = dsr.loc["2022":]
print(f"Fed funds {ff['2022-02-01']:.2f}% (Feb 2022) to {ff.loc['2022':].max():.2f}%"
      f" ({ff.loc['2022':].idxmax():%b %Y})")
print(f"Household debt service: {dsr['2007-10-01']:.1f}% (Q4 2007), {dsr['2019-10-01']:.1f}% (Q4 2019),"
      f" low {dsr.loc['2020':'2021'].min():.1f}% ({q(dsr.loc['2020':'2021'].idxmin())}),"
      f" highest since 2022 {top.max():.1f}% ({q(top.idxmax())}), latest {dsr.iloc[-1]:.1f}% ({q(dsr.index[-1])})")
