# models.py
from django.db import models

class Marker(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# serializers.py
from rest_framework import serializers
from .models import Marker

class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ['id', 'name', 'description', 'latitude', 'longitude', 'created_at']

# views.py
from rest_framework import viewsets
from .models import Marker
from .serializers import MarkerSerializer

class MarkerViewSet(viewsets.ModelViewSet):
    queryset = Marker.objects.all()
    serializer_class = MarkerSerializer

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarkerViewSet

router = DefaultRouter()
router.register(r'markers', MarkerViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

# settings.py (add these to your existing settings)
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    # ... other middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Adjust this to your frontend URL
]