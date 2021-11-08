from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from .serializers import (
    NetworkSerializer, UpdateNetworkSerializer,
    PortSerializer, UpdatePortSerializer,
    KeypairSerializer
)
from .filters import NetworkFilter, PortFilter
from .models import Network, Port, Keypair
import logging
import openstack


logger = logging.getLogger(__package__)


class OSCommonModelMixin:
    update_serializer_class = None

    def get_serializer_class(self):
        return {
            'PUT': self.update_serializer_class
        }.get(self.request.method, self.serializer_class)


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

    destroy
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
            logger.error(f"try destroying openstack network {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class PortViewSet(OSCommonModelMixin, viewsets.ModelViewSet):
    """
    list:
    Get list

    create:
    Create instance

    retrieve:
    Get instance

    update:
    Update instance

    destroy
    drop instance
    """
    filterset_class = PortFilter
    queryset = Port.objects.all()
    serializer_class = PortSerializer
    update_serializer_class = UpdatePortSerializer

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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdatePortSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.save()
        except (
            openstack.exceptions.BadRequestException,
            openstack.exceptions.ConflictException
        ) as exc:
            logger.error(f"try updating openstack port {instance.id}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_update(serializer)
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_os_port()
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destroying openstack port {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class KeypairViewSet(OSCommonModelMixin, viewsets.ModelViewSet):
    serializer_class = KeypairSerializer
    queryset = Keypair.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            if data.get('public_key'):
                ssh = Keypair.create_keypair(key_name=data['name'], key_pub=data['public_key'])
            else:
                ssh = Keypair.create_keypair(key_name=data['name'])
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try creating openstack keypair {data['name']} with {data['public_key']}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save(
                name=ssh.name,
                user_id=ssh.user_id,
                fingerprint=ssh.fingerprint,
                public_key=ssh.public_key,
                type=ssh.type,
                description=data.get('description'),
                project_id=ssh.location.project.id,
            )
            headers = self.get_success_headers(serializer.data)
            return Response(ssh.private_key, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_keypair()
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destroying openstack ssh key {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            ssh_list = instance.get_keypair_list()
            return Response(ssh_list)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try get openstack ssh key list filed {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
