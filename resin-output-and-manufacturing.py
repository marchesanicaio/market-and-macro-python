# Code from "Ethylene cracker utilisation: the leading indicator nobody outside oil has heard of" by Caio Marchesani
# https://caiomarchesani.com/articles/learning-about-trading-indicators-1/

import pandas as pd

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="


def yearly_change(code):
    s = pd.read_csv(FRED + code, index_col=0, parse_dates=True)[code]
    return (s / s.shift(12) - 1).mul(100).rolling(3).mean().dropna()


resin = yearly_change("IPN325211N")  # plastics materials and resins
manuf = yearly_change("IPMAN")       # all manufacturing


def lead(x, y, k, start):
    d = pd.concat([x, y.shift(-k)], axis=1).dropna().loc[start:"2026-09-01"]
    d = d[(d.index < "2019-06-01") | (d.index > "2022-06-01")]
    return d.iloc[:, 0].corr(d.iloc[:, 1])


tests = [("resin leads manufacturing", resin, manuf, "1973-01-01"),
         ("manufacturing leads resin", manuf, resin, "1973-01-01"),
         ("resin leads, since 2000", resin, manuf, "2000-01-01")]
LAGS = (0, 1, 2, 3, 4, 6, 9, 12)
print(f"{'months ahead':26}", " ".join(f"{k:>5}" for k in LAGS))
for name, x, y, start in tests:
    print(f"{name:26}", " ".join(f"{lead(x, y, k, start):+.2f}" for k in LAGS))


def downturns(s):
    neg = s < 0
    runs = (neg != neg.shift()).cumsum()
    return [f"{g.index[0]:%b %Y}" for _, g in s[neg].groupby(runs[neg])
            if len(g) >= 3 and g.index[0] >= pd.Timestamp("1985-01-01")]


print("Resin output falling from:", ", ".join(downturns(resin)))
print("Manufacturing falling from:", ", ".join(downturns(manuf)))
