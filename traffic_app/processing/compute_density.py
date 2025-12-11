# traffic_app/processing/compute_density.py

def analyze_sampled_frames(vehicle_counts):
    """
    Compute a density score between 0 and 1.
    We use normalized average vehicles per frame:
      density = min(1.0, avg / EXPECTED_MAX)
    """
    EXPECTED_MAX = 30.0  # tune for your dataset
    if not vehicle_counts:
        return 0.0
    avg = sum(vehicle_counts) / len(vehicle_counts)
    score = min(1.0, avg / EXPECTED_MAX)
    return round(score, 3)

def compute_congestion(avg_vehicles_per_frame, density_score):
    """
    Simple rule-based classification:
    - HIGH if avg > 20 or density > 0.7
    - MEDIUM if avg > 8 or density > 0.35
    - LOW otherwise
    """
    if avg_vehicles_per_frame > 20 or density_score > 0.7:
        return "HIGH"
    if avg_vehicles_per_frame > 8 or density_score > 0.35:
        return "MEDIUM"
    return "LOW"
