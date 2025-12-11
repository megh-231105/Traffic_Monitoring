def predict_clearing_time(avg_vehicles_per_frame, density_score):
    """
    Returns estimated clearing time in minutes
    """
    if density_score >= 0.75:  # HIGH
        # Assume clearing speed: 3% per minute
        estimate = int((density_score / 0.03))
    elif density_score >= 0.4:  # MEDIUM
        # clearing faster
        estimate = int((density_score / 0.05))
    else:
        # Already normal
        estimate = 0

    return max(estimate, 1)
def traffic_signal_recommendation(density_score):
    if density_score >= 0.75:
        return "Increase GREEN signal duration by 20–30% for this road."
    elif density_score >= 0.40:
        return "Slightly increase GREEN duration by 10%."
    else:
        return "Normal signal timing is sufficient."

