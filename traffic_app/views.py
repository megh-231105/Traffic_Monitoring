# traffic_app/views.py
import os
import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from datetime import datetime

from .forms import VideoUploadForm
from .models import VideoUpload, ProcessingResult

from .processing.extract_frames import extract_and_sample_frames
from .processing.compute_density import analyze_sampled_frames, compute_congestion

from .analysis import predict_clearing_time, traffic_signal_recommendation
from .processing.signal_optimizer import optimize_signal_timing


def send_n8n_alert(result_data):
    """
    Send alert to n8n webhook when high congestion is detected
    """
    # Configure your n8n webhook URL in settings or here
    N8N_WEBHOOK_URL = getattr(settings, 'N8N_WEBHOOK_URL', 
                               'http://localhost:5678/webhook/traffic-alert')
    
    try:
        payload = {
            "timestamp": datetime.now().isoformat(),
            "congestion_level": result_data.get("congestion"),
            "density_score": result_data.get("density_score"),
            "total_vehicles": result_data.get("total_vehicles"),
            "avg_vehicles_per_frame": result_data.get("avg_vehicles_per_frame"),
            "clearing_time": result_data.get("clearing_time"),
            "signal_recommendation": result_data.get("signal_recommendation"),
            "location": result_data.get("location", "Unknown"),
            "vehicle_breakdown": {
                "cars": result_data.get("count_cars"),
                "bikes": result_data.get("count_bikes"),
                "trucks": result_data.get("count_trucks"),
                "buses": result_data.get("count_buses")
            }
        }
        
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✓ Alert sent to n8n successfully")
            return True
        else:
            print(f"✗ n8n webhook returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to send alert to n8n: {e}")
        return False


def upload_view(request):
    form = VideoUploadForm()

    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()

            # Process video
            total_frames, sampled_count, detections, breakdown = extract_and_sample_frames(
                video.video_file.path
            )

            # Calculate totals
            car_count = int(breakdown.get("cars", 0))
            bike_count = int(breakdown.get("bikes", 0))
            truck_count = int(breakdown.get("trucks", 0))
            bus_count = int(breakdown.get("buses", 0))

            total_vehicles = car_count + bike_count + truck_count + bus_count
            avg_per_frame = total_vehicles / sampled_count if sampled_count else 0.0

            # Density and congestion
            per_frame_totals = [sum(d.values()) for d in (detections or [])] if detections else []
            density = analyze_sampled_frames(per_frame_totals) if per_frame_totals else 0.0
            congestion = compute_congestion(avg_per_frame, density)

            # Predictions and recommendations
            clearing_time = predict_clearing_time(avg_per_frame, density)
            signal_suggestion = traffic_signal_recommendation(density)
            green_ext, pattern = optimize_signal_timing(density, avg_per_frame)

            # Save results
            res, _ = ProcessingResult.objects.get_or_create(video=video)
            res.total_frames = total_frames
            res.sampled_frames = sampled_count
            res.total_vehicles = total_vehicles
            res.avg_vehicles_per_frame = avg_per_frame
            res.density_score = density
            res.congestion = congestion
            res.count_cars = car_count
            res.count_bikes = bike_count
            res.count_trucks = truck_count
            res.count_buses = bus_count
            res.clearing_time = clearing_time
            res.signal_recommendation = signal_suggestion
            res.signal_green_extension = float(green_ext)
            res.signal_pattern = pattern
            res.save()

            video.processed = True
            video.save()

            # Send alert if congestion is MEDIUM or HIGH
            if congestion in ["MEDIUM", "HIGH"]:
                alert_data = {
                    "congestion": congestion,
                    "density_score": density,
                    "total_vehicles": total_vehicles,
                    "avg_vehicles_per_frame": avg_per_frame,
                    "clearing_time": clearing_time,
                    "signal_recommendation": signal_suggestion,
                    "count_cars": car_count,
                    "count_bikes": bike_count,
                    "count_trucks": truck_count,
                    "count_buses": bus_count,
                    "location": video.title or "Traffic Camera"
                }
                send_n8n_alert(alert_data)

            return redirect(reverse("traffic_app:results", args=[video.id]))

    return render(request, "traffic_app/upload.html", {"form": form})


def processing_view(request, pk):
    video = get_object_or_404(VideoUpload, pk=pk)

    if video.processed and hasattr(video, "result"):
        return redirect(reverse("traffic_app:results", args=[video.id]))

    video_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)

    total_frames, sampled_count, detections, breakdown = extract_and_sample_frames(video_path)

    car_count = int(breakdown.get("cars", 0))
    bike_count = int(breakdown.get("bikes", 0))
    truck_count = int(breakdown.get("trucks", 0))
    bus_count = int(breakdown.get("buses", 0))

    total_vehicles = car_count + bike_count + truck_count + bus_count
    avg_per_frame = total_vehicles / sampled_count if sampled_count else 0.0

    per_frame_totals = [sum(d.values()) for d in (detections or [])] if detections else []
    density = analyze_sampled_frames(per_frame_totals) if per_frame_totals else 0.0
    congestion = compute_congestion(avg_per_frame, density)

    clearing_time = predict_clearing_time(avg_per_frame, density)
    signal_suggestion = traffic_signal_recommendation(density)
    green_ext, pattern = optimize_signal_timing(density, avg_per_frame)

    res, _ = ProcessingResult.objects.get_or_create(video=video)
    res.total_frames = total_frames
    res.sampled_frames = sampled_count
    res.total_vehicles = total_vehicles
    res.avg_vehicles_per_frame = avg_per_frame
    res.density_score = density
    res.congestion = congestion
    res.count_cars = car_count
    res.count_bikes = bike_count
    res.count_trucks = truck_count
    res.count_buses = bus_count
    res.clearing_time = clearing_time
    res.signal_recommendation = signal_suggestion
    res.signal_green_extension = float(green_ext)
    res.signal_pattern = pattern
    res.save()

    video.processed = True
    video.save()

    # Send alert if needed
    if congestion in ["MEDIUM", "HIGH"]:
        alert_data = {
            "congestion": congestion,
            "density_score": density,
            "total_vehicles": total_vehicles,
            "avg_vehicles_per_frame": avg_per_frame,
            "clearing_time": clearing_time,
            "signal_recommendation": signal_suggestion,
            "count_cars": car_count,
            "count_bikes": bike_count,
            "count_trucks": truck_count,
            "count_buses": bus_count,
            "location": video.title or "Traffic Camera"
        }
        send_n8n_alert(alert_data)

    return redirect(reverse("traffic_app:results", args=[video.id]))


def results_view(request, pk):
    video = get_object_or_404(VideoUpload, pk=pk)
    result = getattr(video, "result", None)
    
    # Calculate percentages for visualization
    if result:
        total = result.count_cars + result.count_bikes + result.count_trucks + result.count_buses
        vehicle_percentages = {
            "cars": round((result.count_cars / total * 100) if total > 0 else 0, 1),
            "bikes": round((result.count_bikes / total * 100) if total > 0 else 0, 1),
            "trucks": round((result.count_trucks / total * 100) if total > 0 else 0, 1),
            "buses": round((result.count_buses / total * 100) if total > 0 else 0, 1),
        }
    else:
        vehicle_percentages = {"cars": 0, "bikes": 0, "trucks": 0, "buses": 0}
    
    context = {
        "video": video,
        "result": result,
        "vehicle_percentages": vehicle_percentages
    }
    
    return render(request, "traffic_app/results.html", context)