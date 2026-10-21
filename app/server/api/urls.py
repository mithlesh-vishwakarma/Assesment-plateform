from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health_check, AssessmentViewSet

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet, basename='assessment')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]
