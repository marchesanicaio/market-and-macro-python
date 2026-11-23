# Code from "The VIX term structure: fifty inversions and what came after" by Caio Marchesani
# https://caiomarchesani.com/articles/vix-term-structure-inversions/

import numpy as np
import pandas as pd
import yfinance as yf

END = "2026-11-07"   # the last close used is 6 November 2026


def closes(ticker):
    px = yf.download(ticker, start="2006-07-17", end=END, auto_adjust=True, progress=False)["Close"]
    return px.squeeze().dropna()


df = pd.DataFrame({"vix": closes("^VIX"), "vix3m": closes("^VIX3M"), "spx": closes("^GSPC")}).dropna()
df["ratio"] = df["vix"] / df["vix3m"]
inv = df["ratio"] > 1

print(f"{len(df)} trading days, {df.index[0].date()} to {df.index[-1].date()}")
print(f"  VIX above VIX3M on {inv.sum()} days ({inv.mean() * 100:.1f}%); median ratio {df['ratio'].median():.2f}")

print("\nVIX, VIX3M and their ratio on selected days")
for d in ("2008-10-24", "2020-03-16", "2025-04-08", "2026-11-04", "2026-11-05", "2026-11-06"):
    print(f"  {d}  {df['vix'][d]:6.2f}  {df['vix3m'][d]:6.2f}  {df['ratio'][d]:5.2f}")

run = (inv != inv.shift()).cumsum()[inv]
spells = pd.DataFrame({"start": run.index.to_series().groupby(run).first(),
                       "end": run.index.to_series().groupby(run).last(),
                       "days": run.groupby(run).size()})
print(f"\n{len(spells)} inversions: median length {spells['days'].median():.0f} days,"
      f" {(spells['days'] == 1).sum()} lasted one day, {(spells['days'] <= 3).sum()} three days or fewer,"
      f" {(spells['days'] >= 10).sum()} ten days or more")
print("  longest five: start, end, days, highest ratio, S&P 500 from first close to last")
for _, s in spells.sort_values("days", ascending=False).head(5).iterrows():
    part = df.loc[s["start"]:s["end"]]
    print(f"  {s['start'].date()}  {s['end'].date()}  {s['days']:3d}  {part['ratio'].max():.2f}"
          f"  {(part['spx'].iloc[-1] / part['spx'].iloc[0] - 1) * 100:+6.1f}%")
by_year = inv.groupby(inv.index.year).sum()
print("  inverted days by year: " + " ".join(f"{y}:{n}" for y, n in by_year.items()))


def row(label, r):
    r = r.dropna()
    print(f"  {label:22s}{len(r):6d}{r.mean() * 100:8.1f}%{r.median() * 100:8.1f}%"
          f"{(r > 0).mean() * 100:8.1f}%{r.quantile(0.05) * 100:8.1f}%{r.min() * 100:8.1f}%")


fwd21 = df["spx"].shift(-21) / df["spx"] - 1
fwd63 = df["spx"].shift(-63) / df["spx"] - 1
head = "                          days    mean  median   higher  5th pct   worst"
print("\nS&P 500 over the next 21 trading days, by the ratio on the day")
print(head)
row("all days", fwd21)
for lo, hi, label in ((0, 0.9, "ratio below 0.90"), (0.9, 1, "0.90 to 1.00"),
                      (1, 1.1, "1.00 to 1.10"), (1.1, 9, "above 1.10")):
    row(label, fwd21[(df["ratio"] > lo) & (df["ratio"] <= hi)])

print("\nThe same, on days with the VIX above 25")
print(head)
row("curve inverted", fwd21[(df["vix"] > 25) & inv])
row("curve not inverted", fwd21[(df["vix"] > 25) & ~inv])

fresh = inv & (inv.shift(1).rolling(20).sum() == 0)
dd = df["spx"] / df["spx"].rolling(252, min_periods=1).max() - 1
low = pd.Series({d: min(0, (df["spx"].iloc[i + 1:i + 64] / df["spx"].iloc[i] - 1).min())
                 for i, d in enumerate(df.index) if fresh.iloc[i] and i + 63 < len(df)})
print(f"\nFirst inverted day after at least 20 normal ones: {fresh.sum()} cases, latest {fresh[fresh].index[-1].date()}")
print(f"  S&P 500 below its one-year high on that day: median {dd[fresh].median() * 100:.1f}%")
print(f"  lowest close in the next 63 days against that day: median {low.median() * 100:.1f}%,"
      f" worst {low.min() * 100:.1f}% after {low.idxmin().date()}")
print(head)
row("next 21 days", fwd21[fresh])
row("next 63 days", fwd63[fresh])
