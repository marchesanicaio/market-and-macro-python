# Code from "Average true range: the volatility measure I actually keep on the screen" by Caio Marchesani
# https://caiomarchesani.com/articles/understanding-average-true-range-atr-first-derivative-of-the-volatility-equation/

import numpy as np
import pandas as pd
import yfinance as yf


def ohlc(ticker, start, end="2026-11-07"):
    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(ticker, axis=1, level=1)
    return df[["High", "Low", "Close"]].dropna()


def wilder_atr(df, n=14):
    h, l, c = (df[k].to_numpy() for k in ("High", "Low", "Close"))
    tr = np.full(len(df), np.nan)
    tr[1:] = np.maximum.reduce([h[1:] - l[1:], abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])])
    atr = np.full(len(df), np.nan)
    atr[n] = tr[1:n + 1].mean()
    for i in range(n + 1, len(df)):
        atr[i] = ((n - 1) * atr[i - 1] + tr[i]) / n
    return pd.Series(tr, df.index), pd.Series(atr, df.index)


spx = ohlc("^GSPC", "1989-12-01")
tr, atr = wilder_atr(spx)
h, l, c, a = spx.High.to_numpy(), spx.Low.to_numpy(), spx.Close.to_numpy(), atr.to_numpy()
N, s0 = len(spx), spx.index.searchsorted(pd.Timestamp("1991-01-01"))

print("S&P 500, 14-day ATR on selected days")
for d in ["2025-02-19", "2025-04-02", "2025-04-08", "2025-04-09", "2025-04-10", "2026-11-06"]:
    print(f"  {d}: true range {tr[d]:6.1f}  ATR {atr[d]:6.1f}  ({atr[d] / spx.Close[d]:.2%} of the close)")
pct = 100 * a[s0:] / c[s0:]
print(f"  ATR as % of the close since 1991: median {np.median(pct):.2f}, "
      f"6 Nov 2026 above {np.mean(pct < pct[-1]):.0%} of days")

move = np.abs(c[s0:] - c[s0 - 1:-1]) / a[s0 - 1:-1]
print(f"\nClose-to-close moves, {N - s0} days from 1991, in units of the previous day's ATR")
print(f"  median {np.median(move):.2f}; beyond 1, 1.5, 2, 3 ATR: "
      + ", ".join(f"{np.mean(move > k):.1%}" for k in (1, 1.5, 2, 3)))

print("\nStop k ATRs from the close: share of days it is touched (long / short)")
print("    k    next day      5 days       20 days")
for k in (1, 1.5, 2, 3):
    row = []
    for n in (1, 5, 20):
        lo = pd.Series(l).rolling(n).min().shift(-n).to_numpy()[s0:N - n]
        hi = pd.Series(h).rolling(n).max().shift(-n).to_numpy()[s0:N - n]
        row.append(f"{np.mean(lo <= c[s0:N - n] - k * a[s0:N - n]):5.1%} /{np.mean(hi >= c[s0:N - n] + k * a[s0:N - n]):5.1%}")
    print(f"  {k:3}  " + "  ".join(row))

P = a / c
i = np.arange(s0, N - 20)
below = (np.lib.stride_tricks.sliding_window_view(P, 252)[s0 - 252:N - 272] < P[i, None]).sum(1)
q = np.minimum(4, (below / 252 * 5).astype(int))
hi20 = pd.Series(h).rolling(20).max().shift(-20).to_numpy()[i]
lo20 = pd.Series(l).rolling(20).min().shift(-20).to_numpy()[i]
print("\nNext 20 days by how quiet the ATR is against its own past year")
print("  fifth            days  range in ATRs  range in %  ATR higher 20 days on")
for k, name in enumerate(["quietest", "second", "middle", "fourth", "busiest"]):
    m = q == k
    print(f"  {name:<14}{m.sum():6}{np.median((hi20 - lo20)[m] / a[i][m]):11.2f}"
          f"{np.median((hi20 - lo20)[m] / c[i][m]):12.2%}{np.mean(a[i + 20][m] > a[i][m]):14.1%}")

cs = pd.Series(c)
prior = cs.rolling(50).max().shift(1)
new_high = cs > prior
first = (new_high & ~new_high.shift(1, fill_value=False)).to_numpy()
fell_back = (cs.rolling(10).min().shift(-10) < prior).to_numpy()
idx = np.arange(N)
ok = first & (idx >= max(s0, 51)) & (idx + 20 < N)
print("\nFirst close at a new 50-day high, by whether the ATR rose over the previous 10 days")
for name, m in (("ATR rising", ok & (np.roll(a, 10) < a)), ("ATR flat or falling", ok & ~(np.roll(a, 10) < a))):
    j = idx[m]
    print(f"  {name:<20}{len(j):4} cases; back below the old high within 10 days {np.mean(fell_back[j]):.1%}; "
          f"median 20-day return {np.median(c[j + 20] / c[j] - 1):+.2%}")

print("\nStake for a £1,000 loss at a stop 2 ATRs away")
for d in ["2025-02-19", "2025-04-10", "2026-11-06"]:
    print(f"  {d}: stop {2 * atr[d]:5.0f} points, £{1000 / (2 * atr[d]):.2f} a point")

print("\nATR on the last day, in price and as % of the close")
for t in ("^GSPC", "GC=F", "CL=F"):
    df = ohlc(t, "2024-01-01")
    last = wilder_atr(df)[1].iloc[-1]
    print(f"  {t:<6}{df.Close.iloc[-1]:10.2f}{last:9.2f}{last / df.Close.iloc[-1]:8.2%}")
