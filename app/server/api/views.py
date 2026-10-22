from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import Assessment
from .serializers import AssessmentSerializer

@api_view(['GET'])
def health_check(request):
    return Response({
        "status": "success",
        "message": "Django REST API server is up and running!",
        "version": "1.0.0"
    }, status=status.HTTP_200_OK)

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all().order_by('-created_at')
    serializer_class = AssessmentSerializer
