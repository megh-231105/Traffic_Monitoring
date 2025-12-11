# traffic_app/processing/detect.py
import cv2
import numpy as np

def simple_vehicle_count(frame):
    """
    Simple heuristic: convert to gray, background subtract, threshold, find contours.
    Returns an approximate count of moving objects/vehicles in the frame.
    Not as accurate as YOLO, but fast and works for demo/samples.
    """
    # Resize for speed
    h, w = frame.shape[:2]
    scale = 640.0 / max(w, h)
    if scale < 1.0:
        frame = cv2.resize(frame, (int(w*scale), int(h*scale)))

    # Convert and blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Background subtraction with simple adaptive thresholding trick:
    # Use morphological operations to highlight objects
    # (This is a cheap heuristic.)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 15, 7)

    # morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    morphed = cv2.morphologyEx(morphed, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 300:  # tune this threshold depending on resolution
            x,y,w,h = cv2.boundingRect(cnt)
            # filter tiny bounding boxes
            if w*h > 500:
                count += 1
    # return count as approximate vehicles
    return count
