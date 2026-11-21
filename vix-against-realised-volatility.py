# Code from "Implied vs historical volatility: what ten years of the VIX show" by Caio Marchesani
# https://caiomarchesani.com/articles/understanding-volatility-in-trading-part-2-implied-vs-historical-volatility/

import numpy as np
import pandas as pd

base = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
vix = pd.read_csv(base + "VIXCLS", index_col=0, parse_dates=True, na_values=".").iloc[:, 0]
spx = pd.read_csv(base + "SP500", index_col=0, parse_dates=True, na_values=".").iloc[:, 0].dropna()

r = np.log(spx).diff()
fwd = r.rolling(21).std().shift(-21) * np.sqrt(252) * 100   # the next 21 trading days
df = pd.concat({"vix": vix, "fwd": fwd}, axis=1).dropna()

gap = df["vix"] - df["fwd"]
print((gap >= 0).mean(), gap.median(), gap.mean())
print(df.corr())
