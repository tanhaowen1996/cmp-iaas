from rest_framework import viewsets
from .serializers import NetworkSerializer
from .models import Network


class NetworkViewSet(viewsets.ModelViewSet):
    """
    list:
    Get list

    retrieve:
    Get instance
    """
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
