from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from ipaddress import IPv4Interface, ip_interface
from .fields import IPAddressField
from .models import (
    Network, Port,
    Firewall, StaticRouting,
    Keypair, Image, Volume, VolumeType
)


class NetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Network
        fields = (
            'id',
            'os_network_id',
            'os_subnet_id',
            'name',
            'cidr',
            'total_interface',
            'total_attached_interface',
            'vlan_id',
            'category',
            'is_shared',
            'tenants',
            'description',
            'created',
            'modified'
        )
        read_only_fields = (
            'id', 'total_interface', 'total_attached_interface',
            'os_network_id', 'os_subnet_id',
            'tenants',
            'created', 'modified',
        )

    def validate_vlan_id(self, value):
        MIN, MAX = 1, 4094
        if not MIN <= value <= MAX:
            raise serializers.ValidationError(f"value must in range [{MIN}, {MAX}]")
        return value


class UpdateNetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Network
        fields = (
            'name',
            'description',
        )


class SimpleNetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Network
        fields = (
            'id',
            'name',
            'cidr',
        )


class TenantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)


class NetworkTenantListSerializer(serializers.ModelSerializer):
    tenants = serializers.ListField(
        child=TenantSerializer()
    )

    class Meta:
        model = Network
        fields = (
            'tenants',
        )

    def validate(self, data):
        if self.instance.is_shared:
            raise serializers.ValidationError(f"the network is shared, nothing need to do.")
        return data


class PortSerializer(serializers.ModelSerializer):
    ip_address = IPAddressField(allow_null=True, protocol='IPv4', required=False)
    network_id = serializers.UUIDField()
    network_name = serializers.CharField(source='network.name', read_only=True)
    creater_name = serializers.CharField(source='creater.get_full_name', read_only=True)

    class Meta:
        model = Port
        fields = (
            'id',
            'name',
            'network_id',
            'network_name',
            'ip_address',
            'mac_address',
            'is_external',
            'server_name',
            'creater_name',
            'created',
            'modified',
        )
        read_only_fields = (
            'id', 'network_name',
            'mac_address',
            'server_name',
            'creater_name',
            'created', 'modified',
        )

    def validate_network_id(self, value):
        if not Network.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Network id: {value} matching query does not exist")
        return value


class UpdatePortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Port
        fields = (
            'name',
        )


class FirewallSerializer(serializers.ModelSerializer):
    source_tenant = TenantSerializer()
    source_network_id = serializers.UUIDField()
    destination_network_id = serializers.UUIDField()

    class Meta:
        model = Firewall
        fields = (
            'id',
            'name',
            'source_tenant',
            'source_network_id',
            'source_network_name',
            'destination_tenant',
            'destination_network_id',
            'destination_network_name',
            'is_allowed',
        )
        read_only_fields = (
            'id',
            'source_network_name',
            'destination_network_name',
            'destination_tenant',
        )

    def validate_destination_network_id(self, value):
        try:
            destination_network = Network.objects.get(id=value, is_shared=False)
        except Network.DoesNotExist as exc:
            raise serializers.ValidationError(f"destination network id {value}: {exc}")
        if self.context['request'].account_info.get('tenantId') not in [t['id'] for t in destination_network.tenants]:
            raise serializers.ValidationError(
                f"the destination network {destination_network} does not belong to current tenant {self.context['request'].account_info.get('tenant_id')}")
        return value

    def validate(self, data):
        try:
            source_network = Network.objects.get(id=data['source_network_id'])
        except Network.DoesNotExist as exc:
            raise serializers.ValidationError(f"source network id {data['source_network_id']}: {exc}")
        if source_network.is_shared is False and data['source_tenant'] not in source_network.tenants:
            raise serializers.ValidationError(
                f"the source network {source_network} is not shared, and does not belong to source tenant {data['source_tenant']['name']}")
        return data


class FirewallPlatformSerializer(FirewallSerializer):
    destination_tenant = TenantSerializer()

    class Meta(FirewallSerializer.Meta):
        read_only_fields = (
            'id',
            'source_network_name',
            'destination_network_name',
        )

    def validate_destination_network_id(self, value):
        return value

    def validate(self, data):
        data = super().validate(data)
        try:
            destination_network = Network.objects.get(id=data['destination_network_id'])
        except Network.DoesNotExist as exc:
            raise serializers.ValidationError(f"destination network id {data['destination_network_id']}: {exc}")
        if data['destination_tenant'] not in destination_network.tenants:
            raise serializers.ValidationError(
                f"the destination network {destination_network} does not belong to destination tenant {data['destination_tenant']['name']}")
        return data


class StaticRoutingSerializer(serializers.ModelSerializer):
    ip_next_hop_address = IPAddressField(protocol='IPv4')
    tenant = TenantSerializer()

    class Meta:
        model = StaticRouting
        fields = (
            'id', 'name', 'tenant', 'cluster_code',
            'destination_subnet', 'ip_next_hop_address'
        )

    def validate(self, data):
        data = super().validate(data)
        if isinstance(data['ip_next_hop_address'], str):
            data['ip_next_hop_address'] = IPv4Interface(data['ip_next_hop_address'])

        return data


class SimpleStaticRoutingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        allow_blank=True, required=False,
        validators=[UniqueValidator(queryset=StaticRouting.objects.all())]
    )
    ip_next_hop_address = IPAddressField(protocol='IPv4')

    class Meta:
        model = StaticRouting
        fields = (
            'name', 'destination_subnet', 'ip_next_hop_address'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=StaticRouting.objects.all(),
                fields=['destination_subnet', 'ip_next_hop_address']
            )
        ]


class BatchCreateStaticRoutingsSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()
    static_routings = serializers.ListField(
        child=SimpleStaticRoutingSerializer(),
        max_length=50
    )

    class Meta:
        model = StaticRouting
        fields = (
            'tenant', 'cluster_code', 'static_routings'
        )

    def validate_static_routings(self, value):
        # TODO
        return value

    @property
    def validated_data_list(self):
        data = self.validated_data
        return [self.Meta.model(
            name=routing['name'] or 'next {ip_next_hop_address} to {destination_subnet}'.format(**routing),
            tenant=data['tenant'],
            creater=self._context['request'].user,
            cluster_code=data['cluster_code'],
            destination_subnet=routing['destination_subnet'],
            ip_next_hop_address=ip_interface(routing['ip_next_hop_address']),
        ) for routing in data['static_routings']]


class BatchDestroyStaticRoutingsSerializer(serializers.ModelSerializer):
    cluster_code = serializers.CharField(required=False)
    ip_next_hop_address = IPAddressField(protocol='IPv4', required=False)

    class Meta:
        model = StaticRouting
        fields = (
            'cluster_code',
            'ip_next_hop_address'
        )

    def validate(self, data):
        data = super().validate(data)
        if not any(data.values()):
            raise serializers.ValidationError(
                f"the one in (cluster_code, ip_next_hop_address) is required")

        return data


class KeypairSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    name = serializers.CharField(max_length=255),
    user_id = serializers.CharField(required=False),
    fingerprint = serializers.CharField(required=False),
    public_key = serializers.FileField(required=False),
    project_id = serializers.UUIDField(required=False),
    user_name = serializers.CharField(required=False),
    tenant_id = serializers.CharField(required=False),
    tenant_name = serializers.CharField(required=False)
    ssh = 'ssh'
    x509 = 'x509'
    type_list = [
        (ssh, 'ssh'),
        (x509, 'x509')
    ]
    type = serializers.ChoiceField(choices=type_list, default=ssh),
    description = serializers.CharField(required=False)

    class Meta:
        model = Keypair
        fields = (
            'id',
            'name',
            'user_id',
            'user_name',
            'fingerprint',
            'public_key',
            'type',
            'description',
            'created_at',
            'updated_at',
            'tenant_id',
            'tenant_name',
        )


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class VolumeSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False),
    size = serializers.IntegerField(required=False),
    is_bootable = serializers.BooleanField(required=False),
    attachments = serializers.JSONField(required=False),
    created_at = serializers.DateTimeField(required=False),
    user_name = serializers.CharField(required=False),
    user_id = serializers.CharField(required=False),
    server_name = serializers.CharField(required=False),
    server_id = serializers.UUIDField(required=False),
    volume_used = serializers.FloatField(required=False),
    device = serializers.CharField(required=False),
    updated_at = serializers.DateTimeField(required=False),
    volume_type = serializers.CharField(required=False),
    tenant_id = serializers.CharField(required=False),
    tenant_name = serializers.CharField(required=False),
    host = serializers.CharField(required=False),
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Volume
        fields = (
            'id',
            'name',
            'volume_type',
            'size',
            'status',
            'is_bootable',
            'attachments',
            'created_at',
            'user_name',
            'user_id',
            'volume_used',
            'server_id',
            'server_name',
            'device',
            'tenant_id',
            'volume_used',
            'tenant_name',
            'updated_at'
        )


class UpdateVolumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Volume
        fields = (
            'status',
            'size',
            'name',
            'description',
            'status',
            'cluster_name',
            'updated_at'
        )


class VolumeTypeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    name = serializers.CharField(required=False)
    is_public = serializers.BooleanField(required=False)
    description = serializers.CharField(required=False)
    properties = serializers.CharField(required=False)

    class Meta:
        model = VolumeType
        fields = (
            "id",
            "name",
            "is_public",
            "description",
            "properties"
        )
