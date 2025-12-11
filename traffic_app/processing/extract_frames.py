import cv2
from .yolo_detect import detect_vehicles_in_frame

def extract_and_sample_frames(video_path, sample_rate=30):
    """
    Returns:
      total_frames (int),
      sampled_count (int),
      detections_list (list of per-frame dicts),
      breakdown (dict: total counts)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0, 0, [], {"cars": 0, "bikes": 0, "trucks": 0, "buses": 0}

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    frame_index = 0
    sampled = 0

    detections_list = []
    cars = []
    bikes = []
    trucks = []
    buses = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % sample_rate == 0:
            sampled += 1
            counts = detect_vehicles_in_frame(frame)
            # keep per-frame dict
            detections_list.append(counts)
            cars.append(counts.get("car", 0))
            bikes.append(counts.get("bike", 0))
            trucks.append(counts.get("truck", 0))
            buses.append(counts.get("bus", 0))

        frame_index += 1

    cap.release()

    breakdown = {
        "cars": int(sum(cars)),
        "bikes": int(sum(bikes)),
        "trucks": int(sum(trucks)),
        "buses": int(sum(buses)),
    }

    return total_frames, sampled, detections_list, breakdown
