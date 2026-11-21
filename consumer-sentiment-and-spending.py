# Code from "Consumer confidence as a leading indicator: what 48 years of data show" by Caio Marchesani
# https://caiomarchesani.com/articles/learning-about-trading-indicators-part-3-understanding-the-consumer-confidence-index-a-leading-indicator-for-traders/

import pandas as pd

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UMCSENT,USREC,PCEC96"
df = pd.read_csv(url, index_col=0, parse_dates=True).loc["1978":]

drop = df["UMCSENT"] - df["UMCSENT"].shift(12)
warnings = df[(drop <= -15) & (drop.shift(1) > -15)]
print(warnings[["UMCSENT", "USREC"]])

fwd = df["PCEC96"].shift(-12) / df["PCEC96"] - 1
print(drop.loc["2008":].corr(fwd.loc["2008":]))
