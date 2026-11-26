# Market and macro data in Python

Python scripts from my articles on [caiomarchesani.com](https://caiomarchesani.com/). Each one rebuilds an article's figures from public data, so you can rerun it, change a date range or a ticker, and see whether the result still holds.

The code in each file is exactly as published in the article. The only addition is two comment lines at the top naming the article and its address. The articles carry the explanation and the charts; the files here are for rerunning the numbers.

## Running them

Python 3 with numpy and pandas covers most of them. Scripts that read market prices also need yfinance (`pip install yfinance`). FRED series are read as CSV from the St. Louis Fed's public service, so no API key is needed.

Data gets revised. Yahoo Finance fills gaps and adjusts old closes, and FRED revises its series too, so a run today can come out slightly different from the figure printed in the article. The payrolls script is built around that problem: it reads each month's early estimates from archived ALFRED vintages.

## The scripts

### Volatility and risk

| File | Article | Data |
|---|---|---|
| `sp500-historical-volatility.py` | [Volatility in trading: what it is and what I do about it](https://caiomarchesani.com/articles/understanding-volatility-in-trading-part-1/) | Yahoo Finance (^GSPC) |
| `historical-volatility.py` | [Historical volatility: how to calculate it, with a worked example](https://caiomarchesani.com/articles/calculating-volatility-part-1-historical-volatility/) | Yahoo Finance (^GSPC, IEF, GC=F, CL=F) |
| `vix-against-realised-volatility.py` | [Implied vs historical volatility: what ten years of the VIX show](https://caiomarchesani.com/articles/understanding-volatility-in-trading-part-2-implied-vs-historical-volatility/) | FRED (VIXCLS, SP500) |
| `implied-volatility-black-scholes.py` | [Implied volatility, and how to back it out of the Black-Scholes formula](https://caiomarchesani.com/articles/understanding-implied-volatility-and-calculating-it-using-the-black-scholes-equation/) | none (standard library only) |
| `average-true-range.py` | [Average true range: the volatility measure I actually keep on the screen](https://caiomarchesani.com/articles/understanding-average-true-range-atr-first-derivative-of-the-volatility-equation/) | Yahoo Finance (^GSPC, GC=F, CL=F) |
| `value-at-risk-backtest.py` | [Value at risk in practice: how often it fails, with real data](https://caiomarchesani.com/articles/value-at-risk-in-practice/) | Yahoo Finance (^GSPC, BTC-USD) |
| `60-40-portfolio-value-at-risk.py` | [The 60/40 portfolio’s value at risk, tested on 23 years of data](https://caiomarchesani.com/articles/60-40-portfolio-value-at-risk/) | Yahoo Finance (SPY, IEF) |
| `position-size-drawdowns.py` | [Can you teach me how to trade?](https://caiomarchesani.com/articles/can-you-teach-me-how-to-trade/) | none (simulated with NumPy) |
| `vix-term-structure.py` | [The VIX term structure: fifty inversions and what came after](https://caiomarchesani.com/articles/vix-term-structure-inversions/) | Yahoo Finance (^VIX, ^VIX3M, ^GSPC) |

### Correlation and spreads

| File | Article | Data |
|---|---|---|
| `correlation-25-years.py` | [Correlation in trading: what the number means and what it is for](https://caiomarchesani.com/articles/understanding-correlation-in-trading-a-quantitative-approach/) | Yahoo Finance (^GSPC, ZN=F, GC=F, CL=F, currencies, sector ETFs) |
| `brent-wti-relative-value.py` | [Relative value trading vs directional trading, and what each one teaches you about risk](https://caiomarchesani.com/articles/relative-value-trading-vs-directional-trading-key-differences-and-risk-mitigation/) | Yahoo Finance (BZ=F, CL=F) |
| `pairs-trading-shell-bp.py` | [Pairs trading in practice: Shell against BP, 2010 to 2026](https://caiomarchesani.com/articles/pairs-trading-shell-bp/) | Yahoo Finance (SHEL.L, BP.L) |

### Energy

| File | Article | Data |
|---|---|---|
| `crack-spread-3-2-1.py` | [How refinery margins work: the 3-2-1 crack spread explained](https://caiomarchesani.com/articles/crack-spread-explained/) | Yahoo Finance (CL=F, RB=F, HO=F) |
| `resin-output-and-manufacturing.py` | [Ethylene cracker utilisation: the leading indicator nobody outside oil has heard of](https://caiomarchesani.com/articles/learning-about-trading-indicators-1/) | FRED (IPN325211N, IPMAN) |
| `refinery-yields.py` | [Refinery yields since 1993: the barrel has moved from 2:1 to 3:2](https://caiomarchesani.com/articles/refinery-yield-barrel-of-crude/) | EIA (monthly US refinery yields) |
| `brent-wti-spread.py` | [The Brent-WTI spread: why the physical gap hit $37 in 2026](https://caiomarchesani.com/articles/brent-wti-spread/) | FRED (DCOILBRENTEU, DCOILWTICO), Yahoo Finance (BZ=F, CL=F) |

### Macro

| File | Article | Data |
|---|---|---|
| `nonfarm-payrolls-revisions.py` | [Non-farm payrolls: the most watched number in markets, and what it actually leads](https://caiomarchesani.com/articles/learning-about-trading-indicators-part-5-non-farm-payrolls-a-leading-indicator-for-traders/) | FRED and ALFRED (PAYEMS, USREC) |
| `durable-goods-core-capex.py` | [Durable goods orders as a leading indicator: read the core capex line, not the headline](https://caiomarchesani.com/articles/learning-about-trading-indicators-part-4/) | FRED (NEWORDER) |
| `consumer-sentiment-and-spending.py` | [Consumer confidence as a leading indicator: what 48 years of data show](https://caiomarchesani.com/articles/learning-about-trading-indicators-part-3-understanding-the-consumer-confidence-index-a-leading-indicator-for-traders/) | FRED (UMCSENT, PCEC96, USREC) |
| `cpi-and-the-fed-balance-sheet.py` | [The pandemic ended a decade of deflation, and it was the channel, not the amount](https://caiomarchesani.com/articles/how-covid-19-ended-the-era-of-deflation/) | FRED (CPIAUCNS, WALCL, M2SL and others) |
| `yield-curve-recession-signal.py` | [The yield curve as a recession signal: what fifty years show](https://caiomarchesani.com/articles/yield-curve-recession-signal/) | FRED (T10Y2Y, T10Y3M, GS10, TB3MS, DGS10, DGS2, THREEFYTP10, FEDFUNDS, TDSP, UNRATE, USREC) |
| `gold-and-real-yields.py` | [Gold and real yields: the model that stopped working in 2022](https://caiomarchesani.com/articles/gold-and-real-yields/) | FRED (DFII10, DTWEXBGS) and Yahoo Finance (GC=F) |

New scripts are added here as new articles go up. The same scripts are also collected on [OSF](https://osf.io/abrdp/), and several run in the browser as [Kaggle notebooks](https://www.kaggle.com/caiomarchesani).

If a script stops working because a data source has changed, or a figure no longer matches, the [contact page](https://caiomarchesani.com/contact/) is the place to tell me.

## About

Caio Marchesani is a hedge fund manager, trader, engineer and all-round investor. He holds an MEng in Mechanical Engineering from University College London and has spent more than fifteen years in energy and macro markets. After working for Deutsche Bank and hedge funds, he became a partner at Oil Analytics and then set up his own quantitative macro energy fund in London. Outside finance he invests in and builds businesses. He founded Acai Berry Foods, the açaí café brand that has grown from London to the UAE and New York.

## Licence

MIT. See `LICENSE`.
