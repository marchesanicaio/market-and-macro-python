# Code from "Correlation in trading: what the number means and what it is for" by Caio Marchesani
# https://caiomarchesani.com/articles/understanding-correlation-in-trading-a-quantitative-approach/

import numpy as np
import pandas as pd
import yfinance as yf

PAIRS = [("EURUSD=X", "GBPUSD=X"), ("XLK", "XLY"), ("GC=F", "EURUSD=X"),
         ("GC=F", "JPY=X"), ("CAD=X", "CL=F"), ("^GSPC", "ZN=F"),
         ("XLU", "XLK")]
SECTORS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
tickers = sorted({t for p in PAIRS for t in p} | set(SECTORS))
px = yf.download(tickers, start="1998-12-01", end="2026-11-07",
                 auto_adjust=True, progress=False)["Close"]


def weekly_returns(t):
    s = px[t].dropna()
    s = s.resample("W-FRI").last().dropna()
    return np.log(s).diff().dropna()


def pair(a, b, start, end="2026-11-07"):
    x = pd.concat([weekly_returns(a), weekly_returns(b)], axis=1,
                  sort=True).dropna()
    return x.loc[start:end]


print("Weekly returns, 2016 to October 2026")
for a, b in PAIRS:
    x = pair(a, b, "2016-01-01")
    roll = x.iloc[:, 0].rolling(52).corr(x.iloc[:, 1]).dropna()
    print(f"  {a:>9} {b:>9}  {x.corr().iloc[0, 1]:+.2f}"
          f"  52-week range {roll.min():+.2f} to {roll.max():+.2f}")

x = pair("^GSPC", "ZN=F", "2000-10-01")
roll = x.iloc[:, 0].rolling(52).corr(x.iloc[:, 1]).dropna()
for name, part in [("2001-2021", roll[:"2021-12-31"]),
                   ("2022 on", roll["2022-01-01":])]:
    print(f"Stocks and bonds {name}: average {part.mean():+.2f},",
          f"positive in {(part > 0).mean():.0%} of 52-week windows")

daily = np.log(px[SECTORS].dropna()).diff().dropna().loc["1999-01-01":]
c = daily.rolling(63).corr()
upper = np.triu_indices(len(SECTORS), 1)
avg = c.groupby(level=0).apply(lambda m: m.values[upper].mean()).dropna()
print("Average correlation between sectors, 63 days:",
      f"median {avg.median():.2f},",
      f"highest {avg.max():.2f} on {avg.idxmax():%d %b %Y}")
