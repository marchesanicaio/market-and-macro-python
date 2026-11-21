# Code from "Value at risk in practice: how often it fails, with real data" by Caio Marchesani
# https://caiomarchesani.com/articles/value-at-risk-in-practice/

import numpy as np
import pandas as pd
import yfinance as yf

px = yf.download(["^GSPC", "BTC-USD"], start="1989-12-29", end="2026-11-08",
                 progress=False)["Close"]
WINDOW, Z = 250, {95: 1.645, 99: 2.326}


def backtest(close, level):
    """Yesterday's one-day VaR, two ways, and today's return, all in per cent."""
    r = np.log(close.dropna()).diff().dropna() * 100
    normal = -Z[level] * r.rolling(WINDOW).std().shift(1)
    hist = r.rolling(WINDOW).quantile(1 - level / 100).shift(1)
    keep = normal.notna()
    return r[keep], {"normal": normal[keep], "historical": hist[keep]}


for name, col in (("S&P 500", "^GSPC"), ("Bitcoin", "BTC-USD")):
    for level in (95, 99):
        r, var = backtest(px[col], level)
        if level == 95:
            print(f"{name}: {len(r):,} days from {r.index[0]:%d %b %Y}")
        for method, v in var.items():
            hit = r < v
            worst = (r - v)[hit].idxmin()
            print(f"  {level}% {method:10}: {hit.sum():4} exceptions, {hit.mean():.1%}"
                  f" of days against {100 - level}%; average loss {(r / v)[hit].mean():.2f}"
                  f" x VaR; worst {worst:%d %b %Y}, {r[worst]:.1f}% against {v[worst]:.1f}%")

r, var = backtest(px["^GSPC"], 99)
hit = r < var["normal"]
count = hit.rolling(WINDOW).sum().dropna()
print(f"S&P 500, 99% normal, exceptions in the last {WINDOW} days:",
      f"0 to 4 on {(count <= 4).mean():.0%} of days, 5 to 9 on",
      f"{((count >= 5) & (count <= 9)).mean():.0%}, 10 or more on {(count >= 10).mean():.0%};",
      f"most {count.max():.0f} ({count.idxmax():%d %b %Y})")
days = np.flatnonzero(hit.to_numpy())
print(f"  within five days of the one before: {(np.diff(days) <= 5).mean():.0%}",
      f"of exceptions; {1 - 0.99 ** 5:.0%} if they were independent")
full = hit.loc["1991":"2025"]                    # whole calendar years only
by_year = full.groupby(full.index.year).sum()
print(f"  full years 1991-2025: none in {', '.join(map(str, by_year.index[by_year == 0]))};",
      "most:", ", ".join(f"{y} {n}" for y, n in by_year.nlargest(5).items()))

# Going further: formal tests, a faster model, ten days and expected shortfall
LAMBDA = 0.94                                    # RiskMetrics decay


def returns(close):
    return np.log(close.dropna()).diff().dropna() * 100


def ewma(close, level):
    """One-day VaR from an exponentially weighted variance, started on the first year."""
    r = returns(close)
    s2, out = r.iloc[:WINDOW].var(), []
    for x in r.iloc[WINDOW:]:
        out.append(-Z[level] * np.sqrt(s2))
        s2 = LAMBDA * s2 + (1 - LAMBDA) * x * x
    return r.iloc[WINDOW:], pd.Series(out, index=r.index[WINDOW:])


def kupiec(hit, p):
    """Likelihood ratio for the share of exceptions; above 3.84 rejects at 5%."""
    T, x = len(hit), int(hit.sum())
    q = x / T
    return -2 * ((T - x) * np.log((1 - p) / (1 - q)) + x * np.log(p / q))


def christoffersen(hit):
    """Likelihood ratio for independence, and P(exception | exception yesterday)."""
    h = np.asarray(hit, int)
    a, b = h[:-1], h[1:]
    n = {(i, j): int(((a == i) & (b == j)).sum()) for i in (0, 1) for j in (0, 1)}
    p01 = n[0, 1] / (n[0, 0] + n[0, 1])
    p11 = n[1, 1] / (n[1, 0] + n[1, 1])
    p = (n[0, 1] + n[1, 1]) / len(a)
    ll = lambda k, pr: k * np.log(pr) if k else 0.0
    lr = -2 * (ll(n[0, 0] + n[1, 0], 1 - p) + ll(n[0, 1] + n[1, 1], p)
               - ll(n[0, 0], 1 - p01) - ll(n[0, 1], p01)
               - ll(n[1, 0], 1 - p11) - ll(n[1, 1], p11))
    return lr, p11


print("99% one-day VaR    share   Kupiec  Christoffersen  P(again next day)  loss/VaR")
for name, col in (("S&P 500", "^GSPC"), ("Bitcoin", "BTC-USD")):
    r, var = backtest(px[col], 99)
    var["EWMA"] = ewma(px[col], 99)[1]
    for method, v in var.items():
        hit = r < v
        lr_ind, again = christoffersen(hit)
        print(f"{name:8} {method:10} {hit.mean():5.1%}  {kupiec(hit, 0.01):7.1f}"
              f"  {lr_ind:14.1f}  {again:17.0%}  {(r / v)[hit].mean():8.2f}")

r, var = backtest(px["^GSPC"], 99)
e = ewma(px["^GSPC"], 99)[1]
crash = slice("2020-02-24", "2020-03-20")
print(f"S&P 500, 24 Feb to 20 Mar 2020: normal {(r < var['normal'])[crash].sum()},"
      f" EWMA {(r < e)[crash].sum()} exceptions in {len(r[crash])} days;"
      f" VaR on 21 Feb {var['normal']['2020-02-21']:.2f} and {e['2020-02-21']:.2f},"
      f" on 18 Mar {var['normal']['2020-03-18']:.2f} and {e['2020-03-18']:.2f}")

ten = r.groupby(np.arange(len(r)) // 10)
blocks = pd.DataFrame({"loss": ten.sum(), "start": ten.apply(lambda s: s.index[0])})
blocks = blocks[ten.size() == 10]
for method, v in (("normal", var["normal"]), ("EWMA", e)):
    hit = blocks.loss.to_numpy() < np.sqrt(10) * v[blocks.start].to_numpy()
    print(f"Ten-day 99% VaR by the square root of 10, {method}: {hit.sum()} of {len(hit)}"
          f" ten-day periods, {hit.mean():.1%}")

r = returns(px["^GSPC"])
q975 = r.rolling(WINDOW).quantile(0.025).shift(1)
es = r.rolling(WINDOW).apply(lambda w: np.sort(w)[:6].mean(), raw=True).shift(1)
ok = q975.notna()
r, q975, es = r[ok], q975[ok], es[ok]
hit = r < q975
print(f"97.5% historical VaR: {hit.mean():.1%} of days; average loss on those days {r[hit].mean():.2f}%"
      f" against a forecast expected shortfall of {es[hit].mean():.2f}%")
print(f"6 Nov 2026: one-day 99% VaR normal {var['normal'].iloc[-1]:.2f}%, historical"
      f" {var['historical'].iloc[-1]:.2f}%, EWMA {e.iloc[-1]:.2f}%; 97.5% expected shortfall"
      f" {r.iloc[-WINDOW:].sort_values().iloc[:6].mean():.2f}%")
