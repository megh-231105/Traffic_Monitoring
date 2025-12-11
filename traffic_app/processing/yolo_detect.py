# traffic_app/processing/yolo_detect.py
from ultralytics import YOLO

# load model once (yolov8n small & fast)
model = YOLO("yolov8n.pt")

# adjust names mapping if needed by inspecting model.model.names
def detect_vehicles_in_frame(frame):
    """
    Returns dict: {"car": int, "bike": int, "bus": int, "truck": int}
    """
    counts = {"car": 0, "bike": 0, "bus": 0, "truck": 0}

    results = model(frame, verbose=False)
    for r in results:
        # r.boxes is iterable
        for box in r.boxes:
            # box.cls may be a tensor or value
            try:
                cls_id = int(box.cls[0])
            except Exception:
                cls_id = int(box.cls)
            name = model.model.names.get(cls_id, str(cls_id)).lower()

            if name in ("car", "automobile", "vehicle"):
                counts["car"] += 1
            elif name in ("motorcycle", "motorbike", "scooter", "bicycle"):
                counts["bike"] += 1
            elif name in ("bus",):
                counts["bus"] += 1
            elif name in ("truck", "lorry", "van"):
                counts["truck"] += 1
            else:
                # ignore other classes
                pass

    return counts
