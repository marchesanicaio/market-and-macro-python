# Code from "Durable goods orders as a leading indicator: read the core capex line, not the headline" by Caio Marchesani
# https://caiomarchesani.com/articles/learning-about-trading-indicators-part-4/

import pandas as pd

base = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
m = pd.read_csv(base + "DGORDER,NEWORDER", index_col=0, parse_dates=True)
print(m.pct_change().std() * 100)        # typical monthly move, headline and core

core = m["NEWORDER"].rolling(3).mean().pct_change(12)
eq = pd.read_csv(base + "Y033RC1Q027SBEA", index_col=0, parse_dates=True).squeeze().pct_change(4)
q = core.resample("QS").mean().to_frame("orders").join(eq.rename("equipment")).dropna()
for lead in range(5):
    print(lead, round(q["orders"].corr(q["equipment"].shift(-lead)), 2))
