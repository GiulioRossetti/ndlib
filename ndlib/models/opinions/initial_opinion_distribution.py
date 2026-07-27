import numpy as np


def sample_initial_opinions(size, distribution="uniform"):
    """
    Sample initial opinions in the [0, 1] interval.

    The continuous opinion models use this helper to seed node opinions from a
    user-selected distribution while keeping the initial values bounded.
    """
    dist = str(distribution or "uniform").strip().lower()

    if dist in {"normal", "gaussian"}:
        values = np.random.normal(loc=0.5, scale=0.15, size=size)
    elif dist == "bimodal":
        values = np.empty(size, dtype=float)
        mask = np.random.random_sample(size) < 0.5
        low_count = int(mask.sum())
        high_count = size - low_count
        values[mask] = np.random.normal(loc=0.25, scale=0.08, size=low_count)
        values[~mask] = np.random.normal(loc=0.75, scale=0.08, size=high_count)
    elif dist in {"left_skewed", "left-skewed", "skewed_left"}:
        values = np.random.beta(2.0, 5.0, size=size)
    elif dist in {"right_skewed", "right-skewed", "skewed_right"}:
        values = np.random.beta(5.0, 2.0, size=size)
    elif dist == "polarized":
        values = np.empty(size, dtype=float)
        mask = np.random.random_sample(size) < 0.5
        low_count = int(mask.sum())
        high_count = size - low_count
        values[mask] = np.random.beta(0.8, 3.5, size=low_count)
        values[~mask] = np.random.beta(3.5, 0.8, size=high_count)
    else:
        values = np.random.random_sample(size)

    return np.clip(values, 0.0, 1.0)
