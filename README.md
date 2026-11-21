# Market and macro data in Python

Python scripts from my articles on [caiomarchesani.com](https://caiomarchesani.com/). Each one rebuilds an article's figures from public data, so you can rerun it, change a date range or a ticker, and see whether the result still holds.

The code in each file is exactly as published in the article. The only addition is two comment lines at the top naming the article and its address. The articles carry the explanation and the charts; the files here are for rerunning the numbers.

## Running them

Python 3 with numpy and pandas covers most of them. Scripts that read market prices also need yfinance (`pip install yfinance`). FRED series are read as CSV from the St. Louis Fed's public service, so no API key is needed.

Data gets revised. Yahoo Finance fills gaps and adjusts old closes, and FRED revises its series too, so a run today can come out slightly different from the figure printed in the article.

## The scripts

| File | Article | Data |
|---|---|---|
| `60-40-portfolio-value-at-risk.py` | [The 60/40 portfolio’s value at risk, tested on 23 years of data](https://caiomarchesani.com/articles/60-40-portfolio-value-at-risk/) | Yahoo Finance (SPY, IEF) |
| `value-at-risk-backtest.py` | [Value at risk in practice: how often it fails, with real data](https://caiomarchesani.com/articles/value-at-risk-in-practice/) | Yahoo Finance (^GSPC, BTC-USD) |
| `yield-curve-recession-signal.py` | [The yield curve as a recession signal: what fifty years show](https://caiomarchesani.com/articles/yield-curve-recession-signal/) | FRED (T10Y2Y, T10Y3M, GS10, TB3MS, DGS10, DGS2, THREEFYTP10, FEDFUNDS, TDSP, UNRATE, USREC) |
| `gold-and-real-yields.py` | [Gold and real yields: the model that stopped working in 2022](https://caiomarchesani.com/articles/gold-and-real-yields/) | FRED (DFII10, DTWEXBGS) and Yahoo Finance (GC=F) |
| `pairs-trading-shell-bp.py` | [Pairs trading in practice: Shell against BP, 2010 to 2026](https://caiomarchesani.com/articles/pairs-trading-shell-bp/) | Yahoo Finance (SHEL.L, BP.L) |

New scripts are added here as new articles go up. Earlier scripts are collected on [OSF](https://osf.io/abrdp/), and several run in the browser as [Kaggle notebooks](https://www.kaggle.com/caiomarchesani).

If a script stops working because a data source has changed, or a figure no longer matches, the [contact page](https://caiomarchesani.com/contact/) is the place to tell me.

## About

Caio Marchesani is a hedge fund manager, trader, engineer and all-round investor. He holds an MEng in Mechanical Engineering from University College London and has spent more than fifteen years in energy and macro markets. After working for Deutsche Bank and hedge funds, he became a partner at Oil Analytics and then set up his own quantitative macro energy fund in London. Outside finance he invests in and builds businesses. He founded Acai Berry Foods, the açaí café brand that has grown from London to the UAE and New York.

## Licence

MIT. See `LICENSE`.
