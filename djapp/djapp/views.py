from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import (
    NetworkSerializer, UpdateNetworkSerializer,
    PortSerializer
)
from .filters import NetworkFilter, PortFilter
from .models import Network, Port
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

    update:
    Update instance (fields: name, description)

    destory
    drop instance
    """
    filterset_class = NetworkFilter
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
            total_interface = data['cidr'].num_addresses - 2
            serializer.save(
                os_network_id=network_id,
                os_subnet_id=subnet_id,
                total_interface=total_interface
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateNetworkSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance.update_os_network_subnet(**serializer.validated_data)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try updating openstack network {instance.id}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_os_network_subnet()
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destorying openstack network {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class PortViewSet(viewsets.ModelViewSet):
    """
    list:
    Get list

    create:
    Create instance

    retrieve:
    Get instance

    update:
    Update instance

    destory
    drop instance
    """
    filterset_class = PortFilter
    queryset = Port.objects.all()
    serializer_class = PortSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            instance = serializer.save()
        except (
            openstack.exceptions.BadRequestException,
            openstack.exceptions.ConflictException
        ) as exc:
            logger.error(f"try creating openstack port with {data}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_os_port()
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destorying openstack port {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
