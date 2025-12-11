# traffic_app/urls.py
from django.urls import path
from . import views

app_name = "traffic_app"

urlpatterns = [
    path("", views.upload_view, name="upload"),
    path("processing/<int:pk>/", views.processing_view, name="processing"),
    path("results/<int:pk>/", views.results_view, name="results"),
]
