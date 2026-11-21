# Code from "Implied volatility, and how to back it out of the Black-Scholes formula" by Caio Marchesani
# https://caiomarchesani.com/articles/understanding-implied-volatility-and-calculating-it-using-the-black-scholes-equation/

from math import log, sqrt, exp, erf, pi

def norm_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))

def norm_pdf(x):
    return exp(-x * x / 2) / sqrt(2 * pi)

def bs_call(S, K, T, r, sigma):
    d1 = (log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    return S * norm_cdf(d1) - K * exp(-r * T) * norm_cdf(d2)

def vega(S, K, T, r, sigma):
    d1 = (log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
    return S * sqrt(T) * norm_pdf(d1)

def implied_vol(price, S, K, T, r, sigma=0.2, tol=1e-8):
    # A call is worth at least S minus the discounted strike, and never more than S
    if not max(S - K * exp(-r * T), 0) < price < S:
        raise ValueError("no volatility produces this price")
    # Newton-Raphson first
    for _ in range(50):
        diff = bs_call(S, K, T, r, sigma) - price
        if abs(diff) < tol:
            return sigma
        v = vega(S, K, T, r, sigma)
        if v < 1e-8:
            break
        sigma -= diff / v
        if not 0 < sigma < 5:
            break
    # Bisection if Newton-Raphson stalls (vega near zero)
    lo, hi = 1e-6, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if bs_call(S, K, T, r, mid) > price:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2

S, K, T, r = 100, 100, 30 / 365, 0.04
for s in (0.10, 0.20, 0.30):
    print(f"volatility {s:.0%}: call worth £{bs_call(S, K, T, r, s):.2f}")

print(f"implied volatility at £2.50: {implied_vol(2.50, S, K, T, r):.2%}")
