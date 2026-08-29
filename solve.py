"""
Solve for theta, M, X in the parametric curve:
    x = t*cos(theta) - e^(M|t|) * sin(0.3t) * sin(theta) + X
    y = 42 + t*sin(theta) + e^(M|t|) * sin(0.3t) * cos(theta)

Key idea
--------
Group terms: (x - X, y - 42) = R(theta) @ (t, e^(M|t|) sin(0.3t))
i.e. the data is just the graph of f(t) = e^(M t) sin(0.3t) (for t>0)
plotted as (t, f(t)), then rotated by theta and translated by (X, 42).

Applying the inverse rotation recovers A = t directly (no need to
search for point correspondences):
    A = (x - X) cos(theta) + (y - 42) sin(theta)      = t
    B = -(x - X) sin(theta) + (y - 42) cos(theta)      = e^(M|t|) sin(0.3 t)

This reduces the problem to an ordinary 3-parameter nonlinear
least-squares fit of B against the model exp(M*A)*sin(0.3*A).
"""

import numpy as np
from scipy.optimize import least_squares

DATA_PATH = "xy_data.csv"


def residuals(params, x, y):
    theta, M, X = params
    A = (x - X) * np.cos(theta) + (y - 42) * np.sin(theta)   # recovered t
    B = -(x - X) * np.sin(theta) + (y - 42) * np.cos(theta)  # recovered e^(M|t|)sin(0.3t)
    pred_B = np.exp(M * np.abs(A)) * np.sin(0.3 * A)
    return B - pred_B


def fit(x, y):
    bounds = ([0.0, -0.05, 0.0], [np.radians(50), 0.05, 100.0])

    best = None
    for theta_deg0 in np.linspace(1, 49, 25):
        for M0 in np.linspace(-0.045, 0.045, 7):
            for X0 in np.linspace(5, 95, 10):
                x0 = [np.radians(theta_deg0), M0, X0]
                res = least_squares(residuals, x0=x0, args=(x, y), bounds=bounds)
                cost = np.sum(res.fun ** 2)
                if best is None or cost < best[0]:
                    best = (cost, res.x)
    return best


def main():
    data = np.loadtxt(DATA_PATH, delimiter=",", skiprows=1)
    x, y = data[:, 0], data[:, 1]

    cost, (theta, M, X) = fit(x, y)

    print(f"theta = {np.degrees(theta):.6f} deg  ({theta:.6f} rad)")
    print(f"M     = {M:.6f}")
    print(f"X     = {X:.6f}")
    print(f"sum of squared residuals = {cost:.3e}")

    # sanity check: reconstruct x, y directly and compare
    A = (x - X) * np.cos(theta) + (y - 42) * np.sin(theta)
    t = A
    x_pred = t * np.cos(theta) - np.exp(M * np.abs(t)) * np.sin(0.3 * t) * np.sin(theta) + X
    y_pred = 42 + t * np.sin(theta) + np.exp(M * np.abs(t)) * np.sin(0.3 * t) * np.cos(theta)
    l1 = np.mean(np.abs(x_pred - x) + np.abs(y_pred - y))
    print(f"mean L1 reconstruction error = {l1:.3e}")
    print(f"recovered t range = [{t.min():.3f}, {t.max():.3f}]")


if __name__ == "__main__":
    main()
