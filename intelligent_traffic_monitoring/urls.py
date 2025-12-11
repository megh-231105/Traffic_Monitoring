# intelligent_traffic_monitoring/urls.py (append)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("", include("traffic_app.urls", namespace="traffic_app")),
    # ... other patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
