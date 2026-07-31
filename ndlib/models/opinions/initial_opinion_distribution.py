import numpy as np


def _sample_family(size, family, params=None, bounds=None):
    params = params or {}
    bounds = bounds if bounds is not None else [0.0, 1.0]
    if not isinstance(bounds, (list, tuple)) or len(bounds) < 2:
        bounds = [0.0, 1.0]
    low = float(bounds[0])
    high = float(bounds[1])
    if high < low:
        low, high = high, low

    dist = str(family or "uniform").strip().lower()
    if dist in {"normal", "gaussian"}:
        mu = float(params.get("mean", params.get("mu", 0.5)))
        sigma = abs(float(params.get("sigma", 0.15)))
        values = np.random.normal(loc=mu, scale=sigma, size=size)
    elif dist == "bimodal":
        values = np.empty(size, dtype=float)
        mask = np.random.random_sample(size) < float(params.get("mix", 0.5))
        low_count = int(mask.sum())
        high_count = size - low_count
        values[mask] = np.random.normal(loc=float(params.get("low", 0.25)), scale=abs(float(params.get("sigma", 0.08))), size=low_count)
        values[~mask] = np.random.normal(loc=float(params.get("high", 0.75)), scale=abs(float(params.get("sigma", 0.08))), size=high_count)
    elif dist in {"left_skewed", "left-skewed", "skewed_left"}:
        values = np.random.beta(2.0, 5.0, size=size)
    elif dist in {"right_skewed", "right-skewed", "skewed_right"}:
        values = np.random.beta(5.0, 2.0, size=size)
    elif dist == "polarized":
        values = np.empty(size, dtype=float)
        mask = np.random.random_sample(size) < float(params.get("mix", 0.5))
        low_count = int(mask.sum())
        high_count = size - low_count
        values[mask] = np.random.beta(float(params.get("left_alpha", 0.8)), float(params.get("left_beta", 3.5)), size=low_count)
        values[~mask] = np.random.beta(float(params.get("right_alpha", 3.5)), float(params.get("right_beta", 0.8)), size=high_count)
    elif dist in {"beta"}:
        alpha = max(1e-3, float(params.get("alpha", 2.0)))
        beta = max(1e-3, float(params.get("beta", 2.0)))
        values = np.random.beta(alpha, beta, size=size)
    elif dist in {"triangular", "triangle"}:
        mode = float(params.get("mode", 0.5))
        values = np.random.triangular(low, mode, high, size=size)
    else:
        values = np.random.random_sample(size)
    return np.clip(values, low, high)


def sample_initial_opinions(size, distribution="uniform"):
    """
    Sample initial opinions in the [0, 1] interval.

    The continuous opinion models use this helper to seed node opinions from a
    user-selected distribution while keeping the initial values bounded.
    """
    if isinstance(distribution, dict):
        return _sample_family(
            size,
            distribution.get("family", distribution.get("name", "uniform")),
            distribution.get("params", {}),
            distribution.get("bounds", [0.0, 1.0]),
        )
    dist = str(distribution or "uniform").strip().lower()

    return _sample_family(size, dist, {}, [0.0, 1.0])
