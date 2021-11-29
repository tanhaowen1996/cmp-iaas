from rest_framework import serializers
from .fields import IPAddressField
from .models import Network, Port, Keypair, Image, Volume, VolumeType


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
            'vlan_id',
            'category',
            'is_shared',
            'tenants',
            'description',
            'created',
            'modified'
        )
        read_only_fields = (
            'id', 'total_interface',
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
            'created',
            'modified',
        )
        read_only_fields = (
            'id', 'network_name',
            'mac_address',
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