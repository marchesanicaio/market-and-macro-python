# Code from "The pandemic ended a decade of deflation, and it was the channel, not the amount" by Caio Marchesani
# https://caiomarchesani.com/articles/how-covid-19-ended-the-era-of-deflation/

import pandas as pd

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="


def fred(series, freq=None):
    s = pd.read_csv(FRED + series, index_col=0, parse_dates=True,
                    na_values=".").squeeze()
    return s.asfreq(freq) if freq else s   # a missing month stays a gap


cpi = fred("CPIAUCNS", "MS")           # US CPI, all items, not seasonally adjusted
hicp = fred("CP0000EZ19M086NEST", "MS")  # euro area HICP, all items
annual = {"United States": cpi.resample("YE").mean().pct_change() * 100,
          "Euro area": hicp.resample("YE").mean().pct_change() * 100,
          "United Kingdom": fred("FPCPITOTLZGGBR"),
          "Japan": fred("FPCPITOTLZGJPN")}
print("                2010-19  below 2%  peak          2024   2025")
for name, s in annual.items():
    s = s.groupby(s.index.year).first().loc[2010:2025].dropna()
    dec = s.loc[2010:2019]
    peak = s.loc[2021:2023].idxmax()
    print(f"{name:15} {dec.mean():6.2f}  {(dec < 2).sum():5} of 10"
          f"  {peak} {s[peak]:4.1f}  {s.get(2024, float('nan')):5.1f}"
          f"  {s.get(2025, float('nan')):5.1f}")

yoy = (cpi.pct_change(12) * 100).dropna()
dec = yoy.loc["2010":"2019"]
print(f"US CPI, 12-month rate: 2010-19 average {dec.mean():.2f}%,",
      f"below 2% in {(dec < 2).sum()} of {len(dec)} months;",
      f"peak {yoy.loc['2021':].max():.1f}% in {yoy.loc['2021':].idxmax():%b %Y};",
      f"latest {yoy.iloc[-1]:.1f}% ({yoy.index[-1]:%b %Y})")

fed = fred("WALCL") / 1e6
print(f"Fed assets, $tn: Sep 2008 {fed['2008-09-03']:.2f}, Dec 2014 {fed['2014-12-31']:.2f},",
      f"peak {fed.max():.2f} ({fed.idxmax():%b %Y}), latest {fed.iloc[-1]:.2f}")
m2 = (fred("M2SL", "MS").pct_change(12) * 100).dropna()
print(f"M2 growth: 2010-19 average {m2.loc['2010':'2019'].mean():.1f}%,",
      f"peak {m2.loc['2020':].max():.1f}% in {m2.loc['2020':].idxmax():%b %Y}")
transfers = fred("PCTR", "MS") / 1000
saving = fred("PSAVERT", "MS")
print(f"Transfers to households, $tn a year: Feb 2020 {transfers['2020-02-01']:.2f},",
      f"Apr 2020 {transfers['2020-04-01']:.2f}, Mar 2021 {transfers['2021-03-01']:.2f}")
print(f"Saving rate: 2010-19 average {saving.loc['2010':'2019'].mean():.1f}%,",
      f"Apr 2020 {saving['2020-04-01']:.1f}%, Mar 2021 {saving['2021-03-01']:.1f}%,",
      f"latest {saving.iloc[-1]:.1f}%")
deficit = fred("FYFSGDA188S")
print(f"Federal balance, % of GDP: 2010-19 average {deficit.loc['2010':'2019'].mean():.1f},",
      " ".join(f"{y} {deficit[str(y)].iloc[0]:.1f}" for y in (2020, 2021, 2024, 2025)))
