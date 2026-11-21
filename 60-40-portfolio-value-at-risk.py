# Code from "The 60/40 portfolio’s value at risk, tested on 23 years of data" by Caio Marchesani
# https://caiomarchesani.com/articles/60-40-portfolio-value-at-risk/

import numpy as np
import pandas as pd
import yfinance as yf

px = yf.download(["SPY", "IEF"], start="2002-07-01", end="2026-11-07",
                 auto_adjust=True, progress=False)["Close"].dropna()
r = px.pct_change().dropna()
port = 0.6 * r["SPY"] + 0.4 * r["IEF"]          # rebalanced to 60/40 every day
W, Z, LAM = 250, 2.3263478740408408, 0.94      # window, 99% normal quantile, RiskMetrics decay


def ewma_var(x):
    out = pd.Series(np.nan, index=x.index)
    v = (x.iloc[:W] ** 2).mean()
    for i in range(W, len(x)):
        if i > W:
            v = LAM * v + (1 - LAM) * x.iloc[i - 1] ** 2
        out.iloc[i] = -Z * np.sqrt(v)
    return out


var = pd.DataFrame({
    "normal": -Z * port.rolling(W).std().shift(1),
    "historical": port.rolling(W).quantile(0.01).shift(1),
    "EWMA": ewma_var(port),
}).dropna()
ret = port.loc[var.index]


def kupiec(hit, p=0.01):
    T, x = len(hit), hit.sum()
    q = x / T
    return -2 * ((T - x) * np.log(1 - p) + x * np.log(p) - (T - x) * np.log(1 - q) - x * np.log(q))


def christoffersen(hit):
    a, b = hit[:-1], hit[1:]
    n = {(i, j): int(((a == i) & (b == j)).sum()) for i in (0, 1) for j in (0, 1)}
    p01 = n[0, 1] / (n[0, 0] + n[0, 1])
    p11 = n[1, 1] / (n[1, 0] + n[1, 1])
    p = (n[0, 1] + n[1, 1]) / sum(n.values())
    ll = lambda k, q: k * np.log(q) if k else 0.0
    return -2 * (ll(n[0, 0] + n[1, 0], 1 - p) + ll(n[0, 1] + n[1, 1], p)
                 - ll(n[0, 0], 1 - p01) - ll(n[0, 1], p01) - ll(n[1, 0], 1 - p11) - ll(n[1, 1], p11)), n[1, 1]


print(f"60/40 SPY/IEF, {len(ret)} days of one-day 99% VaR, {ret.index[0]:%d %b %Y} to {ret.index[-1]:%d %b %Y}")
print("method      exceptions  share  Kupiec  Christoffersen  back-to-back  2008  2018  2020  2022")
for m in var:
    hit = (ret < var[m]).astype(int).to_numpy()
    lr_ind, n11 = christoffersen(hit)
    by_year = pd.Series(hit, index=ret.index).groupby(ret.index.year).sum()
    print(f"{m:<11}{hit.sum():>10}{hit.mean():>7.2%}{kupiec(hit):>8.1f}{lr_ind:>16.1f}{n11:>14}"
          + "".join(f"{by_year.get(y, 0):>6}" for y in (2008, 2018, 2020, 2022)))

end21, y22 = r.loc[:"2021-12-31"].iloc[-W:], r.loc["2022"]
sd = lambda w, rho: Z * np.sqrt(0.36 * w[0] ** 2 + 0.16 * w[1] ** 2 + 0.48 * rho * w[0] * w[1])
s21, s22 = end21.std().to_numpy(), y22.std().to_numpy()
c21, c22 = end21.corr().iloc[0, 1], y22.corr().iloc[0, 1]
print(f"\n2022: SPY {(1 + y22['SPY']).prod() - 1:.1%}, IEF {(1 + y22['IEF']).prod() - 1:.1%}, "
      f"60/40 {(1 + port.loc['2022']).prod() - 1:.1%}; worst day {port.loc['2022'].min():.2%} "
      f"on {port.loc['2022'].idxmin():%d %b}")
print(f"  daily sd SPY {s21[0]:.2%} -> {s22[0]:.2%}, IEF {s21[1]:.2%} -> {s22[1]:.2%}; "
      f"correlation {c21:.2f} -> {c22:.2f}")
print(f"  normal VaR on 3 Jan 2022 {sd(s21, c21):.2%}; with 2022 volatility {sd(s22, c21):.2%}; "
      f"with 2022 volatility and correlation {sd(s22, c22):.2%}")
hit22 = ret.loc["2022"] < var["normal"].loc["2022"]
both = (r["SPY"] < 0) & (r["IEF"] < 0)
print(f"  normal-VaR exceptions in 2022 on days both fell: {(hit22 & both.loc[hit22.index]).sum()} of {hit22.sum()}; "
      f"days both fell: {both.loc['2022'].mean():.1%} of 2022, {both.loc[var.index[0]:'2021'].mean():.1%} before")

rho = r["SPY"].rolling(W).corr(r["IEF"]).shift(1).loc[var.index]
print(f"\n250-day SPY/IEF correlation: negative on {(rho.loc[:'2021'] < 0).mean():.1%} of days to 2021 "
      f"(average {rho.loc[:'2021'].mean():.2f}), {(rho.loc['2022':] < 0).mean():.1%} since "
      f"(average {rho.loc['2022':].mean():.2f}); latest {rho.iloc[-1]:.2f}")
