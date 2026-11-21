# Code from "Historical volatility: how to calculate it, with a worked example" by Caio Marchesani
# https://caiomarchesani.com/articles/calculating-volatility-part-1-historical-volatility/

import numpy as np
import pandas as pd
import yfinance as yf

END = "2026-11-07"   # the last close used is 6 November 2026
ANN = np.sqrt(252)


def closes(ticker, start):
    px = yf.download(ticker, start=start, end=END, auto_adjust=True, progress=False)["Close"]
    return px.squeeze().dropna()


px = closes("^GSPC", "1989-12-01")
r = np.log(px / px.shift(1)).dropna()
r = r[r.index >= "1990-01-01"]
hv = {w: r.rolling(w).std() * ANN * 100 for w in (10, 30, 90, 252)}

print(f"S&P 500, {len(r)} daily log returns, {r.index[0].date()} to {r.index[-1].date()}")
print(f"  whole period: {r.std() * ANN * 100:.1f}% a year")

last = r.iloc[-30:]
print("\nThe four steps on the last 30 returns")
print(f"  mean {last.mean() * 100:+.2f}% a day, standard deviation {last.std() * 100:.2f}% a day,"
      f" annualised {last.std() * ANN * 100:.1f}%")

print("\nReturn, 30-day and 252-day figure on selected days")
for d in ("2025-04-08", "2025-04-09", "2025-05-15", "2025-05-21", "2025-05-22",
          "2026-04-10", "2026-04-13", "2026-11-06"):
    print(f"  {d}  {r[d] * 100:+6.2f}%  {hv[30][d]:5.1f}  {hv[252][d]:5.1f}")

print("\nLargest one-day falls in the 30-day figure, and the return that left the window")
fall = hv[30].diff().nsmallest(3)
for d in fall.index:
    i = r.index.get_loc(d)
    print(f"  {d.date()}: {hv[30].iloc[i - 1]:.1f} to {hv[30].iloc[i]:.1f}"
          f" ({r.iloc[i - 30] * 100:+.2f}% on {r.index[i - 30].date()})")

gap = (hv[30] - hv[252]).abs().dropna()
print(f"\n30-day against 252-day: median gap {gap.median():.1f} points,"
      f" more than 5 points apart on {(gap > 5).mean() * 100:.1f}% of days,"
      f" widest {gap.max():.1f} on {gap.idxmax().date()}")

print("\nLeaving the mean out (root mean square of the returns)")
for w in (30, 252):
    zero = np.sqrt((r ** 2).rolling(w).mean()) * ANN * 100
    g = (zero - hv[w]).abs().dropna()
    d = g.idxmax()
    print(f"  {w:3d} days: median gap {g.median():.2f} points, 95% of days within {g.quantile(0.95):.2f},"
          f" widest {g.max():.2f} on {d.date()} ({hv[w][d]:.1f} with, {zero[d]:.1f} without)")

p = px[px.index >= "1989-12-29"]
weekly = np.log(p.groupby(p.index.to_period("W-FRI")).last()).diff().dropna()
monthly = np.log(p.groupby(p.index.to_period("M")).last()).diff().dropna()
print("\nSame prices, three frequencies, annualised")
print(f"  daily {r.std() * ANN * 100:.1f}%   weekly {weekly.std() * np.sqrt(52) * 100:.1f}%"
      f"   monthly {monthly.std() * np.sqrt(12) * 100:.1f}%")
days = r[r.index.year < 2026].groupby(r[r.index.year < 2026].index.year).size()
print(f"  trading days a year, 1990 to 2025: {days.min()} to {days.max()}, average {days.mean():.1f}")

nxt = hv[30].shift(-30)
ok = hv[252].notna() & nxt.notna()
print(f"\nTrailing window as a forecast of the next 30 days, {ok.sum()} days")
print("  window  correlation  median miss  within 25%  next / trailing")
for w in (10, 30, 90, 252):
    t, n = hv[w][ok], nxt[ok]
    print(f"  {w:6d}{t.corr(n):13.2f}{(n - t).abs().median():13.1f}"
          f"{((n / t - 1).abs() <= 0.25).mean() * 100:11.1f}%{(n / t).median():16.2f}")
t, n = hv[30][ok], nxt[ok]
print(f"  next 30 days more than 1.5 times the trailing 30: {(n / t > 1.5).mean() * 100:.1f}% of days")

print("\nHistorical volatility on the last day: 30 days and 252 days")
for name, ticker in (("7-10 year Treasuries (IEF)", "IEF"), ("S&P 500", "^GSPC"),
                     ("Gold futures (GC=F)", "GC=F"), ("WTI crude futures (CL=F)", "CL=F")):
    c = closes(ticker, "2025-06-01")
    x = np.log(c / c.shift(1)).dropna()
    print(f"  {name:27s}{x.iloc[-30:].std() * ANN * 100:6.1f}%{x.iloc[-252:].std() * ANN * 100:7.1f}%")
