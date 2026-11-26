# Code from "Refinery yields since 1993: the barrel has moved from 2:1 to 3:2" by Caio Marchesani
# https://caiomarchesani.com/articles/refinery-yield-barrel-of-crude/

import pandas as pd

PAGE = "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s={}&f=M"
CODES = {"gasoline": "MGFRYUS3", "distillate": "MDIRYUS3", "jet": "MKJRYUS3",
         "coke": "MCKRYUS3", "gas liquids": "M_EPL0_YRY_NUS_PER", "still gas": "MSGRYUS3",
         "asphalt": "MAPRYUS3", "residual": "MRERYUS3", "gain": "MPGRYUS3"}


def eia_monthly(code):
    """One EIA refinery-yield series (per cent of refinery input) as a monthly Series."""
    table = pd.read_html(PAGE.format(code), attrs={"class": "FloatTitle"})[0]
    table = table.dropna(subset=["Year"]).set_index("Year").astype(float)
    table.index = table.index.astype(int)
    s = table.stack().dropna()
    s.index = pd.to_datetime([f"{month} {year}" for year, month in s.index],
                             format="%b %Y").to_period("M")
    return s.sort_index()


def mon(period):
    return period.strftime("%b %Y")


y = pd.DataFrame({name: eia_monthly(code) for name, code in CODES.items()})
y["gain"] = -y["gain"]                       # the EIA prints a gain as a negative number
y["ratio"] = y["gasoline"] / y["distillate"]
y["with jet"] = y["gasoline"] / (y["distillate"] + y["jet"])
last = y.index[-1]
print(f"{len(y)} months, {mon(y.index[0])} to {mon(last)}")

# 1. The latest month, in gallons from a 42-gallon barrel
row, named = y.loc[last], list(CODES)[:-1]
print(f"\n{last.strftime('%B %Y')}:")
for name in named:
    print(f"  {name:12} {row[name]:5.1f}%  {0.42 * row[name]:5.1f} gal")
other = 100 + row["gain"] - row[named].sum()
print(f"  {'other':12} {other:5.1f}%  {0.42 * other:5.1f} gal")
print(f"  {'total':12} {100 + row['gain']:5.1f}%  {0.42 * (100 + row['gain']):5.1f} gal")
fuels = row[["gasoline", "distillate", "jet"]].sum()
print(f"  transport fuels {fuels:.1f}% of input ({0.42 * fuels:.1f} gal), the rest {100 + row['gain'] - fuels:.1f}%; "
      f"gasoline to distillate {row['ratio']:.2f}, with jet {row['with jet']:.2f}")

# 2. Year by year (the last year runs to the latest month)
cols = ["gasoline", "distillate", "jet", "residual", "ratio", "with jet"]
year = y.groupby(y.index.year).mean()
two = {"ratio": "{:.2f}".format, "with jet": "{:.2f}".format}
print("\n" + year.loc[[1993, 2000, 2005, 2010, 2015, 2019, 2023, 2024, 2025, 2026], cols]
      .to_string(float_format="{:.1f}".format, formatters=two))
inside = year["gasoline"].between(45.4, 47.9)
print(f"gasoline between 45.4% and 47.9% in {inside.sum()} of {len(year)} years; outside in {list(year.index[~inside])}")
print(f"ratio {year.loc[1993:2004, 'ratio'].min():.2f} to {year.loc[1993:2004, 'ratio'].max():.2f} in 1993-2004, "
      f"last above 2.0 in {year.index[year['ratio'] > 2].max()}, "
      f"{year.loc[2011:, 'ratio'].min():.2f} to {year.loc[2011:, 'ratio'].max():.2f} since 2011")
for yr in (1993, 2026):
    g = 0.42 * year.loc[yr, ["gasoline", "distillate", "jet", "residual"]]
    print(f"{yr}, gallons from 42: gasoline {g['gasoline']:.1f}, distillate {g['distillate']:.1f}, "
          f"jet {g['jet']:.1f}, residual {g['residual']:.1f}, everything {0.42 * (100 + year.loc[yr, 'gain']):.1f}")
print(f"processing gain {year.loc[1993, 'gain']:.1f}% in 1993, {year['gain'].max():.1f}% in {year['gain'].idxmax()}, "
      f"{year.loc[2026, 'gain']:.1f}% in 2026")

# 3. 2026, the records and the calendar
months = len(y.loc["2026"])
print(f"\ngasoline, first {months} months: {y.loc['2025', 'gasoline'].iloc[:months].mean():.1f}% in 2025, "
      f"{y.loc['2026', 'gasoline'].mean():.1f}% in 2026")
april = y.loc["2026-04", "gasoline"]
lower = y.index[y["gasoline"] < april]
print(f"April 2026 gasoline {april:.1f}%; lower in {len(lower)} months: " + ", ".join(mon(p) for p in lower))
summer08 = y.loc["2008-04":"2008-08"]
print(f"April to August 2008: gasoline {summer08['gasoline'].min():.1f}% to {summer08['gasoline'].max():.1f}%, "
      f"distillate {summer08['distillate'].min():.1f}% to {summer08['distillate'].max():.1f}%")
print(f"jet: {y.loc['2026-03', 'jet']:.1f}% in March 2026, lowest since {y.loc['2026-03':, 'jet'].min():.1f}%, "
      f"record {y['jet'].max():.1f}% ({mon(y['jet'].idxmax())}), highest before 2026 {y.loc[:'2025', 'jet'].max():.1f}%")
print(y.loc["2020-01":"2020-05", ["gasoline", "distillate", "jet", "ratio"]].round(2).to_string())
season = y.loc["2010":"2025", "gasoline"]
season = season.groupby(season.index.month).mean()
print(f"gasoline by calendar month, 2010-2025: January {season[1]:.1f}%, April {season[4]:.1f}%, August {season[8]:.1f}%")
print(f"gas liquids: {y.loc['2026-01', 'gas liquids']:.1f}% in January 2026, {y.loc['2026-05', 'gas liquids']:.1f}% in May")

# 4. One week's prices under three weightings (prices from the crack spread article)
rbob, ulsd, wti = 2.7227, 4.1983, 87.96
gasoline_crack, diesel_crack = 42 * rbob - wti, 42 * ulsd - wti
print(f"\ngasoline crack ${gasoline_crack:.2f}, diesel crack ${diesel_crack:.2f} a barrel")
for label, g, d in (("3-2-1", 2, 1), ("5-3-2", 3, 2), ("2-1-1", 1, 1)):
    print(f"  {label}: ${(g * gasoline_crack + d * diesel_crack) / (g + d):.2f}")
