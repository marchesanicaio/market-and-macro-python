# Code from "Pairs trading in practice: Shell against BP, 2010 to 2026" by Caio Marchesani
# https://caiomarchesani.com/articles/pairs-trading-shell-bp/

import numpy as np
import yfinance as yf

px = yf.download(["SHEL.L", "BP.L"], start="2010-01-01", end="2026-10-31", auto_adjust=True)["Close"].dropna()
s, b = np.log(px["SHEL.L"].to_numpy()), np.log(px["BP.L"].to_numpy())
dates = px.index


def eg_test(s, b):
    """Engle-Granger: hedge ratio, ADF t-statistic on the residual, half-life in days."""
    beta, alpha = np.polyfit(b, s, 1)
    e = s - alpha - beta * b
    de = np.diff(e)
    y = de[1:]
    X = np.column_stack([np.ones(len(y)), e[1:-1], de[:-1]])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    s2 = resid @ resid / (len(y) - 3)
    t = coef[1] / np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
    return beta, t, -np.log(2) / np.log(1 + coef[1])


for lo, hi in [("2010", "2014"), ("2015", "2019"), ("2020", "2021"), ("2022", "2026"), ("2010", "2026")]:
    m = (dates >= f"{lo}-01-01") & (dates <= f"{hi}-12-31")
    beta, t, half_life = eg_test(s[m], b[m])
    print(f"{lo}-{hi}: hedge ratio {beta:.2f}, test statistic {t:.2f}, half-life {half_life:.0f} days")


def pair_rule(s, b, window=252, entry=2.0, stop=4.0, max_days=60, cost=0.0025):
    """Trade the residual of a rolling regression, using only past data."""
    trades, pos = [], 0
    for t in range(window, len(s)):
        if pos:
            pnl += pos * ((s[t] - s[t - 1]) - beta * (b[t] - b[t - 1]))
        bt, at = np.polyfit(b[t - window:t], s[t - window:t], 1)
        sd_t = np.std(s[t - window:t] - at - bt * b[t - window:t], ddof=1)
        if not pos:
            z = (s[t] - at - bt * b[t]) / sd_t
            if abs(z) > entry and bt > 0:
                pos, start, beta, alpha, sd, pnl = -np.sign(z), t, bt, at, sd_t, 0.0
        else:
            z = (s[t] - alpha - beta * b[t]) / sd
            if pos * z >= 0 or pos * z <= -stop or t - start >= max_days:
                trades.append(pnl / (1 + beta) - cost)
                pos = 0
    return np.array(trades)


trades = pair_rule(s, b)
print(f"{len(trades)} trades, {(trades > 0).mean():.0%} winners, "
      f"average {trades.mean():.2%}, total {trades.sum():.1%}")
