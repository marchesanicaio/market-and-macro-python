# Code from "How refinery margins work: the 3-2-1 crack spread explained" by Caio Marchesani
# https://caiomarchesani.com/articles/crack-spread-explained/

import yfinance as yf

px = yf.download(["CL=F", "RB=F", "HO=F"], start="2021-11-01", interval="1wk")["Close"]
crack = (2 * px["RB=F"] * 42 + px["HO=F"] * 42 - 3 * px["CL=F"]) / 3

print(crack.describe())
print(crack.groupby(crack.index.month).mean().round(1))
