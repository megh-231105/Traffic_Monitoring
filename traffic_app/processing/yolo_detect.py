# traffic_app/processing/yolo_detect.py
from ultralytics import YOLO
import cv2
import numpy as np

# Load model once (yolov8n small & fast)
model = YOLO("yolov8n.pt")

# COCO dataset class mappings for vehicles
VEHICLE_CLASSES = {
    2: "car",          # car
    3: "bike",         # motorcycle
    5: "bus",          # bus
    7: "truck",        # truck
    1: "bike",         # bicycle (also bike)
}

def detect_vehicles_in_frame(frame):
    """
    Returns dict: {"car": int, "bike": int, "bus": int, "truck": int}
    Uses YOLO detection with proper class mapping
    """
    counts = {"car": 0, "bike": 0, "bus": 0, "truck": 0}
    
    try:
        # Run inference with confidence threshold
        results = model(frame, conf=0.25, verbose=False)
        
        for r in results:
            if r.boxes is None or len(r.boxes) == 0:
                continue
                
            for box in r.boxes:
                # Get class ID
                cls_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                
                # Only count if confidence is high enough and it's a vehicle
                if confidence > 0.3 and cls_id in VEHICLE_CLASSES:
                    vehicle_type = VEHICLE_CLASSES[cls_id]
                    counts[vehicle_type] += 1
                    
    except Exception as e:
        print(f"Error in vehicle detection: {e}")
        # Return zeros on error
        return counts
    
    return counts


def detect_vehicles_with_boxes(frame):
    """
    Returns both counts and bounding boxes for visualization
    Returns: (counts_dict, boxes_list)
    boxes_list format: [{"type": str, "bbox": [x1,y1,x2,y2], "conf": float}, ...]
    """
    counts = {"car": 0, "bike": 0, "bus": 0, "truck": 0}
    boxes = []
    
    try:
        results = model(frame, conf=0.25, verbose=False)
        
        for r in results:
            if r.boxes is None or len(r.boxes) == 0:
                continue
                
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                
                if confidence > 0.3 and cls_id in VEHICLE_CLASSES:
                    vehicle_type = VEHICLE_CLASSES[cls_id]
                    counts[vehicle_type] += 1
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    boxes.append({
                        "type": vehicle_type,
                        "bbox": [int(x1), int(y1), int(x2), int(y2)],
                        "conf": confidence
                    })
                    
    except Exception as e:
        print(f"Error in vehicle detection with boxes: {e}")
    
    return counts, boxes


def draw_detections(frame, boxes):
    """
    Draw bounding boxes on frame for visualization
    """
    colors = {
        "car": (0, 255, 0),      # Green
        "bike": (255, 0, 0),     # Blue
        "bus": (0, 0, 255),      # Red
        "truck": (255, 255, 0)   # Cyan
    }
    
    annotated_frame = frame.copy()
    
    for detection in boxes:
        vehicle_type = detection["type"]
        x1, y1, x2, y2 = detection["bbox"]
        conf = detection["conf"]
        
        color = colors.get(vehicle_type, (255, 255, 255))
        
        # Draw rectangle
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        
        # Add label
        label = f"{vehicle_type}: {conf:.2f}"
        cv2.putText(annotated_frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return annotated_frame