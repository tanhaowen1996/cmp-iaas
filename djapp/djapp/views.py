from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import NetworkSerializer
from .models import Network
import logging
import openstack


logger = logging.getLogger(__package__)


class NetworkViewSet(viewsets.ModelViewSet):
    """
    list:
    Get list

    create:
    Create instance

    retrieve:
    Get instance

    destory
    drop instance
    """
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            network_id, subnet_id = Network.create_os_network_subnet(
                data['name'], str(data['cidr']))
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try creating openstack network {data['name']} with {data['cidr']}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            total_interface = len(list(data['cidr'].hosts()))
            serializer.save(
                os_network_id=network_id,
                os_subnet_id=subnet_id,
                total_interface=total_interface
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destory(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destory_os_network_subnet()
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destorying openstack network {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
