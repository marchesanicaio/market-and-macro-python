# Code from "Where Brazil’s acai goes, and why the official figures miss most of it" by Caio Marchesani
# https://caiomarchesani.com/articles/acai-exports-brazil/

import requests

URL = "https://api-comexstat.mdic.gov.br/general?language=en"
BROAD = ["20098990", "20089900", "08119000", "20079921"]  # juice, prepared, frozen, purée

def query(filters, details):
    body = {"flow": "export", "monthDetail": False,
            "period": {"from": "2025-01", "to": "2025-12"},
            "filters": filters, "details": details,
            "metrics": ["metricFOB", "metricKG"]}
    return requests.post(URL, json=body).json()["data"]["list"]

# 1. The dedicated acai code, whole of Brazil
code = query([{"filter": "ncm", "values": ["20079921"]}], [])
print("Acai code 2007.99.21, Brazil 2025: US$%.2fm"
      % (float(code[0]["metricFOB"]) / 1e6))

# 2. The four-code basket, Pará (state 15)
para = query([{"filter": "state", "values": ["15"]},
              {"filter": "ncm", "values": BROAD}], [])
total = sum(float(r["metricFOB"]) for r in para)
print("Four codes, Pará 2025: US$%.1fm" % (total / 1e6))

# 3. Where it went
rows = query([{"filter": "state", "values": ["15"]},
              {"filter": "ncm", "values": BROAD}], ["country"])
rows.sort(key=lambda r: -float(r["metricFOB"]))
for r in rows[:5]:
    share = 100 * float(r["metricFOB"]) / total
    print("%-16s %4.1f%%" % (r["country"], share))
