# traffic_app/processing/detect_vehicles.py

from ultralytics import YOLO
import cv2

# Load YOLO model once
model = YOLO("yolov8n.pt")  # small + fast

VEHICLE_MAP = {
    "car": "car",
    "motorcycle": "bike",
    "bus": "bus",
    "truck": "truck"
}

def detect_vehicles(frame):
    """
    Runs YOLO detection on a single frame and returns categorized counts.
    """

    results = model(frame, verbose=False)
    counts = {"car": 0, "bike": 0, "truck": 0, "bus": 0}

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            name = model.model.names[cls]

            if name in VEHICLE_MAP:
                mapped = VEHICLE_MAP[name]
                counts[mapped] += 1

    return counts
