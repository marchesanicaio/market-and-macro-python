# Code from "Volatility in trading: what it is and what I do about it" by Caio Marchesani
# https://caiomarchesani.com/articles/understanding-volatility-in-trading-part-1/

import numpy as np
import pandas as pd
import yfinance as yf

px = yf.download("^GSPC", start="1989-12-01", end="2026-11-07",
                 auto_adjust=False, progress=False)["Close"].squeeze()
r = np.log(px).diff().dropna().loc["1990-01-02":]

yearly = r.groupby(r.index.year).std() * np.sqrt(252) * 100
print(f"Volatility {r.std() * np.sqrt(252):.1%} a year;",
      f"calmest year {yearly.idxmin()} ({yearly.min():.1f}%),",
      f"wildest {yearly.idxmax()} ({yearly.max():.1f}%)")

big = r.abs() > 0.02
print(f"Days with a move above 2%: {big.mean():.1%};",
      f"the day after one: {big[big.shift(1, fill_value=False)].mean():.1%}")


def acf(x, k):
    x = x - x.mean()
    return (x.values[k:] * x.values[:-k]).sum() / (x.values ** 2).sum()


print("Autocorrelation, size of move:",
      " ".join(f"{k}d {acf(r.abs(), k):.2f}" for k in (1, 5, 21, 63, 252)))
print("Autocorrelation, direction:   ",
      " ".join(f"{k}d {acf(r, k):+.2f}" for k in (1, 5, 21)))


def stats(daily):
    equity = (1 + daily).cumprod()
    log = np.log(1 + daily)
    years = len(daily) / 252
    roll = log.rolling(252).std().dropna() * np.sqrt(252)
    cagr = equity.iloc[-1] ** (1 / years) - 1
    vol = log.std() * np.sqrt(252)
    drawdown = (equity / equity.cummax() - 1).min()
    return (f"{cagr:6.1%} {vol:6.1%} {drawdown:7.1%} {daily.min():6.1%}"
            f"   {roll.min():.1%} to {roll.max():.1%}")


sigma = r.rolling(21).std().shift(1) * np.sqrt(252)
simple = np.exp(r) - 1
keep = sigma.notna()
print("                       return    vol drawdown  worst   1-year vol")
print("Buy and hold          ", stats(simple[keep]))
for target in (0.10, 0.15):
    weight = (target / sigma).clip(upper=2)
    print(f"Sized to {target:.0%} vol      ", stats((weight * simple)[keep]))
