# traffic_app/processing/extract_frames.py
import cv2
from .yolo_detect import detect_vehicles_in_frame

def extract_and_sample_frames(video_path, sample_rate=30):
    """
    Extract frames from video and detect vehicles using YOLO.
    
    Args:
        video_path: Path to video file
        sample_rate: Process every Nth frame (default: 30)
    
    Returns:
        total_frames (int): Total number of frames in video
        sampled_count (int): Number of frames analyzed
        detections_list (list): List of detection dicts per frame
        breakdown (dict): Total counts by vehicle type
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        return 0, 0, [], {"cars": 0, "bikes": 0, "trucks": 0, "buses": 0}

    # Get total frame count
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Video info: {total_frames} frames, {fps:.2f} FPS")
    
    frame_index = 0
    sampled = 0
    
    # Storage for detections
    detections_list = []
    
    # Accumulators for totals
    total_cars = 0
    total_bikes = 0
    total_trucks = 0
    total_buses = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Sample every Nth frame
        if frame_index % sample_rate == 0:
            sampled += 1
            
            # Run YOLO detection
            counts = detect_vehicles_in_frame(frame)
            
            # Store per-frame detection
            detections_list.append(counts)
            
            # Accumulate totals
            total_cars += counts.get("car", 0)
            total_bikes += counts.get("bike", 0)
            total_trucks += counts.get("truck", 0)
            total_buses += counts.get("bus", 0)
            
            # Progress indicator
            if sampled % 10 == 0:
                print(f"Processed {sampled} frames...")

        frame_index += 1

    cap.release()
    
    # Prepare breakdown dictionary
    breakdown = {
        "cars": total_cars,
        "bikes": total_bikes,
        "trucks": total_trucks,
        "buses": total_buses,
    }
    
    print(f"Detection complete: {sampled} frames analyzed")
    print(f"Total vehicles detected: {sum(breakdown.values())}")
    print(f"Breakdown - Cars: {total_cars}, Bikes: {total_bikes}, "
          f"Trucks: {total_trucks}, Buses: {total_buses}")

    return total_frames, sampled, detections_list, breakdown