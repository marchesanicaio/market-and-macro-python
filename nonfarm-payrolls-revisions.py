# Code from "Non-farm payrolls: the most watched number in markets, and what it actually leads" by Caio Marchesani
# https://caiomarchesani.com/articles/learning-about-trading-indicators-part-5-non-farm-payrolls-a-leading-indicator-for-traders/

import io
import urllib.request

import pandas as pd

ALFRED = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def csv(url):
    with urllib.request.urlopen(url) as r:
        return pd.read_csv(io.BytesIO(r.read()), index_col=0, parse_dates=True)


def vintages(start="2002-12-01"):
    """Payrolls as published on the 1st, 8th, 15th and 22nd of every month."""
    days = [d for d in pd.date_range(start, pd.Timestamp.today())
            if d.day in (1, 8, 15, 22)]
    frames = []
    for i in range(0, len(days), 12):  # ALFRED serves 12 vintages a request
        chunk = [d.strftime("%Y-%m-%d") for d in days[i:i + 12]]
        ids = ",".join(["PAYEMS"] * len(chunk))
        frames.append(csv(f"{ALFRED}?id={ids}&vintage_date={','.join(chunk)}"))
    return pd.concat(frames, axis=1)


def first_and_third(v):
    first, third = {}, {}
    for col in v.columns:
        change = v[col].dropna().diff()
        newest = change.index[-1]
        first.setdefault(newest, change.iloc[-1])
        month = newest - pd.DateOffset(months=2)
        if month in first:
            third.setdefault(month, change[month])
    return pd.Series(first), pd.Series(third)


first, third = first_and_third(vintages())
t = pd.DataFrame({
    "first_print": first,
    "third_print": third,
    "today": csv(f"{FRED}?id=PAYEMS")["PAYEMS"].diff(),
    "recession": csv(f"{FRED}?id=USREC")["USREC"],
}).loc["2003-01-01":].dropna()
t = t[(t.index < "2020-03-01") | (t.index > "2020-12-01")]

print("months compared:", len(t))
print("average revision, first to third print:",
      round((t.third_print - t.first_print).abs().mean()), "thousand")
print("average revision, first print to today:",
      round((t.today - t.first_print).abs().mean()), "thousand")
for flag, name in [(1, "recession"), (0, "expansion")]:
    s = t[t.recession == flag]
    print(f"{name}: today minus first print averages",
          f"{round((s.today - s.first_print).mean()):+} thousand")
y = t.loc["2024-04-01":"2025-03-01"]
print("April 2024 to March 2025, first prints:", round(y.first_print.sum()),
      "thousand; as revised:", round(y.today.sum()), "thousand")
