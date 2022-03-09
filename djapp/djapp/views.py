from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .authentication import AccountInfoAuthentication, OSAuthentication
from .serializers import (
    NetworkSerializer, UpdateNetworkSerializer, NetworkTenantListSerializer,
    SimpleNetworkSerializer,
    PortSerializer, UpdatePortSerializer,
    FirewallSerializer, FirewallPlatformSerializer,
    StaticRoutingSerializer,
    StaticRoutingDestinationSubnetSerializer,
    UpdateDestinationSubnetSerializer,
    BatchDestroyStaticRoutingsSerializer, BatchCreateStaticRoutingsSerializer,
    KeypairSerializer, ImageSerializer,
    VolumeSerializer, UpdateVolumeSerializer,
    VolumeTypeSerializer,
)
from .filters import (
    NetworkFilter, PortFilter,
    FirewallFilter, SimpleSourceTenantNetworkFilter, SimpleDestinationTenantNetworkFilter,
    StaticRoutingFilter, BatchDestroyStaticRoutingsFilter,
    StaticRoutingDestinationSubnetFilter,
    KeypairFilter, ImageFilter, VolumeFilter, VolumeTypeFilter
)
from .models import (
    Network, Port,
    Firewall, StaticRouting,
    Keypair, Image, Volume, VolumeType
)
import logging
import openstack


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
    Update instance

    destroy:
    drop instance

    tenants:
    set related tenant list for instance

    release:
    remove current tenant from the tenant list of instance

    verbosity:
    Get instance detail info
    """
    authentication_classes = (OSAuthentication,)
    filterset_class = NetworkFilter
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    update_serializer_class = UpdateNetworkSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(Q(is_shared=True) | Q(tenants__contains=[{
                'id': self.request.account_info['tenantId']}]))

        return qs

    @action(detail=True, methods=['post'], serializer_class=NetworkTenantListSerializer)
    def tenants(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def release(self, request, pk=None):
        instance = self.get_object()
        if request.tenant in instance.tenants:
            ports = instance.get_ports_by_tenant_id(request.tenant['id'])
            if ports.exists():
                return Response({
                    "detail": f"{ ports } of servers are in use"
                }, status=status.HTTP_400_BAD_REQUEST)

            instance.tenants.remove(request.tenant)
            instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def verbosity(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            **serializer.data,
            **instance.get_os_network_subnet(request.os_conn)})

    @action(detail=False, serializer_class=SimpleNetworkSerializer, filterset_class=SimpleSourceTenantNetworkFilter)
    def source_networks(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Network.objects.all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, serializer_class=SimpleNetworkSerializer,
            filterset_class=SimpleDestinationTenantNetworkFilter)
    def destination_networks(self, request, pk=None):
        qs = Network.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(tenants__contains=[{'id': self.request.account_info['tenantId']}])

        queryset = self.filter_queryset(qs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
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
            instance.creater = request.user
            instance.save(force_insert=True)
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

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(Q(network__is_shared=True) | Q(network__tenants__contains=[{
                'id': self.request.account_info['tenantId']}]))

        return qs

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
            instance.creater = request.user
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
            serializer.save()
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


class FirewallViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    authentication_classes = (AccountInfoAuthentication,)
    filterset_class = FirewallFilter
    queryset = Firewall.objects.all()
    serializer_class = FirewallSerializer
    staff_serializer_class = FirewallPlatformSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(destination_tenant={
                'id': self.request.account_info.get('tenantId'),
                'name': self.request.account_info.get('tenantName'),
            })

        return qs

    def get_serializer_class(self):
        return self.staff_serializer_class if self.request.user.is_staff else self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.Meta.model(**serializer.validated_data)
            instance.create_rule()
        except Exception as exc:
            logger.error(f"try creating firewall rule {serializer.validated_data}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.creater = request.user
            if not self.request.user.is_staff:
                instance.destination_tenant = self.request.tenant

            instance.save(force_insert=True)
            return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_rule()
        except Exception as exc:
            logger.error(f"try destroying firewall rule {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class StaticRoutingViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    authentication_classes = (OSAuthentication,)
    filterset_class = StaticRoutingFilter
    queryset = StaticRouting.objects.all()
    serializer_class = StaticRoutingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(tenant=self.request.tenant)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.Meta.model(**serializer.validated_data)
            instance.create_routing()
        except Exception as exc:
            logger.error(f"try creating static routing {serializer.validated_data}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.creater = request.user
            instance.save(force_insert=True)
            return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method='put',
        query_serializer=StaticRoutingDestinationSubnetSerializer)
    @action(detail=False, methods=['put'],
            filterset_class=StaticRoutingDestinationSubnetFilter,
            serializer_class=UpdateDestinationSubnetSerializer)
    def update_destination_subnet(self, request, *args, **kwargs):
        logger.info(f"start updating static routing")
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance = queryset.get()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(creater=request.user)
        except Exception as exc:
            logger.error(f"try updating static routing: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"finished updating static routing")
            return Response(StaticRoutingSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_routing()
        except Exception as exc:
            logger.error(f"try destroying static routing {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], serializer_class=BatchCreateStaticRoutingsSerializer)
    def batch_create(self, request, *args, **kwargs):
        logger.info(f"start batch creating static routing")
        serializer = self.get_serializer(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj_list = serializer.validated_data_list
        try:
            StaticRouting.batch_create_static_routing_list(obj_list)
        except Exception as exc:
            logger.error(f"try batch creating static routing: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance_list = StaticRouting.objects.bulk_create(obj_list)
            logger.info(f"finished batch creating static routing")
            return Response(StaticRoutingSerializer(
                instance_list, many=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method='delete',
        query_serializer=BatchDestroyStaticRoutingsSerializer)
    @action(detail=False, methods=['delete'],
            serializer_class=BatchDestroyStaticRoutingsSerializer,
            filterset_class=BatchDestroyStaticRoutingsFilter)
    def batch_destroy(self, request, *args, **kwargs):
        logger.info(f"start batch destroying static routing")
        self.get_serializer(data=request.query_params).is_valid(raise_exception=True)
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            StaticRouting.batch_destroy_static_routing_list(queryset)
        except Exception as exc:
            logger.error(f"try batch destroying static routing: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset.delete()
            logger.info(f"finished batch destroying static routing")
            return Response(status=status.HTTP_204_NO_CONTENT)


class KeypairViewSet(viewsets.ModelViewSet):
    """
            list:
            获取ssh密钥列表

            create:
            创建ssh密钥

            retrieve:
            获取ssh密钥信息

            destroy:
            删除ssh密钥

            destroy_all:
            批量删除ssh密钥
            传入参数：key：value -> keypairs: [uuid1,uuid2,....]
            """
    serializer_class = KeypairSerializer
    queryset = Keypair.objects.all()
    authentication_classes = (OSAuthentication,)
    filter_class = KeypairFilter

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user_id=self.request.account_info['id'])
        return qs

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
        except openstack.exceptions.HttpException as exc:
            logger.error(f"try creating openstack keypair {data['name']} : {exc}")
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
                user_id=request.user.id,
                tenant_id=request.account_info.get('tenantId'),
                tenant_name=request.account_info.get('tenantName'),
            )
            headers = self.get_success_headers(serializer.data)
            if data.get('public_key'):
                return Response(status=status.HTTP_201_CREATED, headers=headers)
            return Response(ssh.private_key, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_keypair(request.os_conn)
        except openstack.exceptions.HttpException as exc:
            logger.error(f"try destroying openstack ssh key {instance.name}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def destroy_all(self, request, *args, **kwargs):
        keypairs = request.data['keypairs'].split(',')
        for keypair_id in keypairs:
            keypair = Keypair.objects.get(id=keypair_id)
            keypair.destroy_keypair(os_conn=request.os_conn)
            self.perform_destroy(keypair)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageViewSet(OSCommonModelMixin, viewsets.ModelViewSet):
    authentication_classes = (OSAuthentication,)
    filterset_class = ImageFilter
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['os_type', 'name', 'visibility', 'status',
                     'user_id', 'tenant_name', 'disk_format']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(Q(tenant_id=self.request.account_info['tenantId']) | Q(visibility="public"))
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            for instance in page:
                image = instance.get_image(request.os_conn)
                if instance.size == image.size and instance.status == image.status:
                    continue
                serializer = ImageSerializer(instance, data=image)
                serializer.is_valid(raise_exception=True)
                serializer.save(
                    status=image.status,
                    updated_at=image.updated_at,
                    size=image.size
                )
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        file = request.data['file']
        dis_for = request.data['disk_format']
        del request.data['disk_format']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            if not self.request.user.is_staff:
                data['visibility'] = 'private'
            else:
                data['visibility'] = 'public'
            image = Image.upload_images(request.os_conn, file, container_format='bare',
                                        disk_format=dis_for, **data)
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try creating openstack image {data}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if image.properties == {}:
                des = ""
            else:
                des = image.properties['description']
            serializer.save(
                name=image.name,
                id=image.id,
                owner=image.owner,
                size=image.size,
                status=image.status,
                disk_format=image.disk_format,
                container_format=image.container_format,
                visibility=image.visibility,
                os_type=image.os_type,
                created_at=image.created_at,
                updated_at=image.updated_at,
                description=des,
                user_name=request.user,
                user_id=request.user.id,
                tenant_id=request.account_info.get('tenantId'),
                tenant_name=request.account_info.get('tenantName')
                )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ImageSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            instance.update_images(request.os_conn, **data)
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
            instance.destroy_image(
                request.os_conn
            )
        except openstack.exceptions.BadRequestException as exc:
            logger.error(f"try destroying openstack image {instance.name}: {exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def destory_all(self, request, *args, **kwargs):
        images = request.data['images']
        for images_id in images:
            image = Image.objects.get(id=images_id)
            image.destroy_image(os_conn=request.os_conn)
            self.perform_destroy(image)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VolumeViewSet(OSCommonModelMixin, viewsets.ModelViewSet):
    """
        list:
        获取云硬盘列表

        create:
        创建云硬盘

        retrieve:
        获取云硬盘信息
        "id":  云硬盘 id
        "name":  云硬盘 名字
        "volume_type":  云硬盘规格（high-ssd(高性能)/ssd(SSD)/normal(普通盘)）
        "size":  云硬盘大小单位GB
        "volume_used":  云硬盘使用量
        "status": 状态（in-use 挂载状态， available 未挂载可使用,状态类型很多）
        "is_bootable": 云硬盘的属性（false对应数据盘 ，true 对应系统盘）
        "attachments":  云硬盘挂载的信息
        "created_at":  创建时间
        "user_name":  用户名
        "user_id":   用户id
        "volume_used": 云硬盘创建人
        "server_id":  挂载的虚机id
        "server_name": 挂载的虚机name
        "device": 挂载的路径
        "updated_at": 更新时间
        "tenant_id"：租户id
        "tenant_name"：租户名

        update:
        更新云硬盘

        destroy:
        删除云硬盘

        attached:
        挂载云硬盘

        detached:
        卸载云硬盘

        extend:
        云硬盘扩容
        需要size字段，单位GB，为扩容到多多少G，非扩容多少G

        """
    authentication_classes = (OSAuthentication,)
    filterset_class = VolumeFilter
    update_serializer_class = UpdateVolumeSerializer
    serializer_class = VolumeSerializer
    queryset = Volume.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            project_id = self.request.account_info['currentTenantCloudRel']['projectId']
            qs = qs.filter(Q(project_id=project_id) & Q(is_bootable="False"))
        return qs

    def create(self, request, *args, **kwargs):
        data_request = request.data.copy()
        data_request.pop('num')
        serializer = self.get_serializer(data=data_request)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return_data = []

        try:
            for num in range(int(request.data['num'])):
                volume = Volume.create_volume(
                    request.os_conn,
                    name=data['name'],
                    size=data['size'],
                    volume_type=data['volume_type'])
                serializer = self.get_serializer(data=data_request)
                serializer.is_valid(raise_exception=True)
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
                    user_name=request.user,
                    tenant_id=request.account_info.get('tenantId'),
                    tenant_name=request.account_info.get('tenantName'),
                )
                return_data.append(serializer.data)

        except openstack.exceptions.HttpException as exc:
            logger.error(f"try create openstack volume {data['name']}:{exc}")
            return Response({
                "detail": f"{exc}"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = self.get_success_headers(serializer.data)
            return Response(return_data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.destroy_volume(request.os_conn)
        except openstack.exceptions.HttpException as exc:
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

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     try:
    #         volume = instance.get_volume(request.os_conn)
    #         if volume.attachments == []:
    #             serializer = UpdateVolumeSerializer(instance, data=volume)
    #             serializer.is_valid(raise_exception=True)
    #             serializer.save(
    #                 cluster_name=volume.host,
    #                 attachments=volume.attachments,
    #                 device=None,
    #                 server_name=None,
    #                 server_id=None,
    #             )
    #         else:
    #             server = instance.get_server(request.os_conn, volume.attachments[0].get('server_id'))
    #             serializer = UpdateVolumeSerializer(instance, data=volume)
    #             serializer.is_valid(raise_exception=True)
    #             serializer.save(
    #                 cluster_name=volume.host,
    #                 attachments=volume.attachments,
    #                 device=volume.attachments[0].get('device'),
    #                 server_name=server.name,
    #                 server_id=volume.attachments[0].get('server_id'),
    #             )
    #         serializer = self.get_serializer(instance)
    #         return Response(serializer.data)
    #     except openstack.exceptions.HttpException as exc:
    #         logger.error(f"try get openstack ssh volume list filed {instance.name}:{exc}")
    #         return Response({
    #             "detail": f"{exc}"
    #         }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            for instance in page:
                try:
                    volume = instance.get_volume(request.os_conn)
                    if instance.status == volume.status:
                        continue
                    if volume.attachments == []:
                        serializer = UpdateVolumeSerializer(instance, data=volume)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(
                            cluster_name=volume.host,
                            attachments=volume.attachments,
                            device=None,
                            server_name=None,
                            server_id=None,
                        )
                    else:
                        server = instance.get_server(request.os_conn, volume.attachments[0].get('server_id'))
                        serializer = UpdateVolumeSerializer(instance, data=volume)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(
                            cluster_name=volume.host,
                            attachments=volume.attachments,
                            device=volume.attachments[0].get('device'),
                            server_name=server.name,
                            server_id=volume.attachments[0].get('server_id'),
                        )
                except:
                    self.perform_destroy(instance)
                    print("ERROR: this volume deleted by cls")
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def attached(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            instance.attached_volume(request.os_conn, data['server_id'])
        except openstack.exceptions.HttpException as exc:
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
                status="attaching",
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
        try:
            instance.detached_volume(request.os_conn, instance.server_id)
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
                status="detaching",
                attachments=volume.attachments,
                device=None,
                server_name=None,
                server_id=None,
            )
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def extend(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            instance.extend_volume(request.os_conn, new_size=data['size'])
        except openstack.exceptions.HttpException as exc:
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
                size=data['size'],
            )
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list_page(self, qs):
        queryset = self.filter_queryset(qs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            for instance in page:
                volume = instance.get_volume(self.request.os_conn)
                if instance.status == volume.status:
                    continue
                serializer = UpdateVolumeSerializer(instance, data=volume)
                serializer.is_valid(raise_exception=True)
                serializer.save(
                    cluster_name=volume.host,
                    attachments=volume.attachments,
                )
            serializer = self.get_serializer(page, many=True)
            return serializer
        serializer = self.get_serializer(queryset, many=True)
        return serializer

    @action(detail=False, methods=['post'])
    def attached_list(self, request, *args, **kwargs):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(Q(tenant_id=self.request.account_info['tenantId']) &
                           (Q(server_id=None) | Q(server_id=request.data['server_id'])))
        serializer = self.list_page(qs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def detached_list(self, request, *args, **kwargs):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(tenant_id=self.request.account_info['tenantId'],
                           server_id=request.data['server_id'])
        serializer = self.list_page(qs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VolumeTypeViewSet(OSCommonModelMixin, viewsets.ModelViewSet):
    """
        list:
        获取云硬盘类型列表

        retrieve:
        获取云硬盘类型列表信息

        """
    authentication_classes = (OSAuthentication,)
    filterset_class = VolumeTypeFilter
    serializer_class = VolumeTypeSerializer
    queryset = VolumeType.objects.all()
