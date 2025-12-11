from django.db import models

class VideoUpload(models.Model):
    title = models.CharField(max_length=200, blank=True)
    video_file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title or self.video_file.name} ({self.uploaded_at})"


class ProcessingResult(models.Model):
    video = models.OneToOneField(VideoUpload, on_delete=models.CASCADE, related_name="result")

    total_frames = models.IntegerField(default=0)
    sampled_frames = models.IntegerField(default=0)
    total_vehicles = models.IntegerField(default=0)
    avg_vehicles_per_frame = models.FloatField(default=0.0)
    density_score = models.FloatField(default=0.0)
    congestion = models.CharField(
        max_length=10,
        choices=[("LOW","LOW"),("MEDIUM","MEDIUM"),("HIGH","HIGH")],
        default="LOW"
    )

    # Signal optimization
    signal_green_extension = models.FloatField(default=0.0)
    signal_pattern = models.CharField(max_length=100, default="")
    signal_recommendation = models.CharField(max_length=200, default="")

    # Clearing time
    clearing_time = models.FloatField(default=0.0)

    # Vehicle type breakdown (consistent names)
    count_cars = models.IntegerField(default=0)
    count_bikes = models.IntegerField(default=0)
    count_trucks = models.IntegerField(default=0)
    count_buses = models.IntegerField(default=0)

    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.video_id} - {self.congestion}"
