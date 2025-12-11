# traffic_app/processing/signal_optimizer.py

def optimize_signal_timing(density_score, avg_vehicles_per_frame):
    """
    Returns (green_extension_seconds: float, pattern: str)
    density_score: expected 0-1 or 0-100 depending on your compute_density function.
    We'll handle both: if >1 assume 0-100 range.
    """
    # Normalize density to 0..1
    d = float(density_score or 0)
    if d > 1:
        d = d / 100.0
    d = max(0.0, min(1.0, d))

    # Simple thresholds (tweak as needed)
    if d < 0.33:
        return 0.0, "Normal flow"
    elif d < 0.66:
        return 10.0, "Moderate congestion - extend green +10s"
    elif d < 0.9:
        return 20.0, "High congestion - extend green +20s"
    else:
        return 30.0, "Severe congestion - emergency +30s"
