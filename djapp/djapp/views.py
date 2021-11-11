from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .authentication import OSAuthentication
from .serializers import (
    NetworkSerializer, UpdateNetworkSerializer, NetworkTenantListSerializer,
    PortSerializer, UpdatePortSerializer,
    KeypairSerializer, ImageSerializer,
    VolumeSerializer, UpdateVolumeSerializer,
)
from .filters import NetworkFilter, PortFilter, ImageFilter
from .models import Network, Port, Keypair, Image, Volume
import logging
import openstack

from .utils import sess_image

logger = logging.getLogger(__package__)


class OSCommonModelMixin:
    update_serializer_class = None

    def get_serializer_class(self):
        return {
            'PUT': self.update_serializer_class
        }.get(self.request.method, self.serializer_class)


class NetworkViewSet(OSCommonModelMixin, viewsets.ModelViewSet):
    """
    list:
    Get list

    create:
    Create instance

    retrieve:
    Get instance

    update:
    Update instance (fields: name, description)

    destroy:
    drop instance
    """
    authentication_classes = (OSAuthentication,)
    filterset_class = NetworkFilter
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    update_serializer_class = UpdateNetworkSerializer

    @action(detail=True, methods=['post'], serializer_class=NetworkTenantListSerializer)
    def tenants(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.Meta.model(**serializer.validated_data)
            instance.create_os_network_subnet(request.os_conn)
        except openstack.exceptions.HttpException as exc:
            logger.error(f"try creating openstack network {serializer.validated_data}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.save()
            return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance.update_os_network_subnet(request.os_conn, **serializer.validated_data)
        except openstack.exceptions.HttpException as exc:
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
            instance.destroy_os_network_subnet(request.os_conn)
        except openstack.exceptions.HttpException as exc:
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

    destroy:
    drop instance
    """
    authentication_classes = (OSAuthentication,)
    filterset_class = PortFilter
    queryset = Port.objects.all()
    serializer_class = PortSerializer
    update_serializer_class = UpdatePortSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.Meta.model(**serializer.validated_data)
            instance.create_os_port(request.os_conn)
        except openstack.exceptions.HttpException as exc:
            logger.error(f"try creating openstack port with {serializer.validated_data}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.save()
            return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance.update_os_port(request.os_conn, **serializer.validated_data)
        except openstack.exceptions.HttpException as exc:
            logger.error(f"try updating openstack port {instance.id}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.save()
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_os_port(request.os_conn)
        except openstack.exceptions.HttpException as exc:
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
    authentication_classes = (OSAuthentication,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            if data.get('public_key'):
                ssh = Keypair.create_keypair(
                    request.os_conn,
                    key_name=data['name'],
                    key_pub=data['public_key'])
            else:
                ssh = Keypair.create_keypair(
                    request.os_conn,
                    key_name=data['name'])
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try creating openstack keypair {data['name']} with {data['public_key']}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save(
                name=ssh.name,
                fingerprint=ssh.fingerprint,
                public_key=ssh.public_key,
                type=ssh.type,
                description=data.get('description'),
                project_id=ssh.location.project.id,
                user_name=request.user,
                user_id=request.user.id
            )
            headers = self.get_success_headers(serializer.data)
            return Response(ssh.private_key, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_keypair(request.os_conn)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destroying openstack ssh key {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class ImageViewSet(viewsets.ModelViewSet):
    filterset_class = ImageFilter
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        file = request.data['file']
        del request.data['file']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            sess = sess_image()
            image = sess.images.create(**data)
            im_id = image['id']
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try creating openstack image {data}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save(
                name = image.name,
                id = image.id,
                owner = image.owner,
                size = image.size,
                status =image.status,
                disk_format = image.disk_format,
                container_format = image.container_format,
                checksum = image.checksum,
                min_disk = image.min_disk,
                min_ram = image.min_ram ,
                protected = image.protected,
                virtual_size = image.virtual_size,
                visibility = image.visibility,
                os_type = image.os_type,
                created_at = image.created_at,
                updated_at = image.updated_at,
                description = image.description,
                # user_id = "admin"
            )
            sess.images.upload(im_id, file)
            info = sess.images.get(im_id)
            serializer.save(
                size=info.size,
                status=info.status,
                checksum=info.checksum,
                min_disk=info.min_disk,
                min_ram=info.min_ram,
                virtual_size=info.virtual_size,
                visibility=info.visibility,
                updated_at=info.updated_at,
            )
            return Response({"msg":"The mirror image is being uploaded"})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ImageSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance.update_image(**serializer.validated_data)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try updating openstack image {instance.id}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_image()
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destroying openstack port {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class VolumeViewSet(OSCommonModelMixin, viewsets.ModelViewSet):
    authentication_classes = (OSAuthentication,)
    serializer_class = VolumeSerializer
    queryset = Volume.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            volume = Volume.create_volume(
                request.os_conn,
                name=data['name'],
                size=data['size'],
                volume_type=data['volume_type'])
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try create openstack volume {data['name']}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save(
                id=volume.id,
                name=volume.name,
                description=volume.description,
                project_id=volume.location.project.id,
                user_id=request.user.id,
                is_bootable=volume.is_bootable,
                volume_type=volume.volume_type,
                status=volume.status,
                attachments=volume.attachments,
                cluster_name=volume.host,
                user_name=request.user
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_volume(request.os_conn)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destroying openstack volume {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateVolumeSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance.update_volume(request.os_conn, **serializer.validated_data)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try updating openstack network {instance.id}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            volume = instance.get_volume(request.os_conn)
            serializer = UpdateVolumeSerializer(instance, data=volume)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                cluster_name=volume.host
            )
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try get openstack ssh volume list filed {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        try:
            for instance in page:
                volume = instance.get_volume(request.os_conn)
                if instance.status == volume.status:
                    continue
                serializer = UpdateVolumeSerializer(instance, data=volume)
                serializer.is_valid(raise_exception=True)
                serializer.save(
                    cluster_name=volume.host,
                    attachments=volume.attachments,
                )
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except openstack.exceptions.BadRequestException as exc:
            logger.error("try get openstack ssh key list filed")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def attached(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            instance.attached_volume(request.os_conn, data['server_id'])
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try attached openstack volume {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            volume = instance.get_volume(request.os_conn)
            server = instance.get_server(request.os_conn, data['server_id'])
            serializer = VolumeSerializer(instance, data=volume)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                status=volume.status,
                attachments=volume.attachments,
                device=volume.attachments[0].get('device'),
                server_name=server.name,
                server_id=data['server_id'],
            )
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def detached(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            instance.detached_volume(request.os_conn, data['server_id'])
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try detached openstack volume {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            volume = instance.get_volume(request.os_conn)
            serializer = VolumeSerializer(instance, data=volume)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                status=volume.status,
                attachments=volume.attachments,
                device=None,
                server_name=None,
                server_id=None,
            )
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
