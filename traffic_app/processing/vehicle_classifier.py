# traffic_app/processing/vehicle_classifier.py

def classify_vehicle_type(yolo_class_id):
    """
    Convert YOLO vehicle class IDs into grouped categories.
    """

    CAR_IDS = [2, 3, 5, 7]       # car, motorcycle, bus, truck (depending on model)
    BIKE_IDS = [1, 3]           # motorcycle, scooter
    TRUCK_IDS = [7, 8]
    BUS_IDS = [5, 6]

    if yolo_class_id in CAR_IDS:
        return "car"
    elif yolo_class_id in BIKE_IDS:
        return "bike"
    elif yolo_class_id in TRUCK_IDS:
        return "truck"
    elif yolo_class_id in BUS_IDS:
        return "bus"
    else:
        return "other"
