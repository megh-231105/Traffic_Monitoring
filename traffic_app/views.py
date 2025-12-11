import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings

from .forms import VideoUploadForm
from .models import VideoUpload, ProcessingResult

from .processing.extract_frames import extract_and_sample_frames
from .processing.compute_density import analyze_sampled_frames, compute_congestion

from .analysis import predict_clearing_time, traffic_signal_recommendation
from .processing.signal_optimizer import optimize_signal_timing


def upload_view(request):
    form = VideoUploadForm()  # always defined for GET

    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()

            # get 4 return values (total, sampled, per-frame detections, totals)
            total_frames, sampled_count, detections, breakdown = extract_and_sample_frames(video.video_file.path)

            # totals from breakdown
            car_count = int(breakdown.get("cars", 0))
            bike_count = int(breakdown.get("bikes", 0))
            truck_count = int(breakdown.get("trucks", 0))
            bus_count = int(breakdown.get("buses", 0))

            total_vehicles = car_count + bike_count + truck_count + bus_count
            avg_per_frame = total_vehicles / sampled_count if sampled_count else 0.0

            # density computation: your compute function likely expects list of counts or a score
            # simple placeholder: use sampled per-frame totals if available
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

            # vehicle breakdown fields
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

    return redirect(reverse("traffic_app:results", args=[video.id]))


def results_view(request, pk):
    video = get_object_or_404(VideoUpload, pk=pk)
    result = getattr(video, "result", None)
    return render(request, "traffic_app/results.html", {"video": video, "result": result})
