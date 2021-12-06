from rest_framework import serializers
from .fields import IPAddressField
from .models import Network, Port, Firewall, Keypair, Image, Volume, VolumeType


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
            'destination_network_id',
            'destination_network_name',
            'is_allowed',
        )
        read_only_fields = (
            'id',
            'source_network_name',
            'destination_network_name',
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
        fields = FirewallSerializer.Meta.fields + ('destination_tenant',)

    def validate_destination_network_id(self, value):
        return value


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
