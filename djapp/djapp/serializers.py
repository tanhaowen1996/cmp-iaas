from rest_framework import serializers
from .fields import IPAddressField
from .models import Network, Port, Keypair


class NetworkSerializer(serializers.ModelSerializer):
    tenants = serializers.SerializerMethodField()

    class Meta:
        model = Network
        fields = (
            'id',
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
            'created', 'modified',
        )

    def get_tenants(self, obj):
        return []  # TODO: get related tenants

    def validate_vlan_id(self, value):
        MIN, MAX = 1, 4094
        if not MIN < value < MAX:
            raise serializers.ValidationError(f"value must in range [{MIN}, {MAX}]")
        return value


class UpdateNetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Network
        fields = (
            'name',
            'description',
        )


class PortSerializer(serializers.ModelSerializer):
    ip_address = IPAddressField(allow_null=True)
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
    user_id = serializers.UUIDField(required=False),
    fingerprint = serializers.CharField(required=False),
    public_key = serializers.FileField(required=False),
    project_id = serializers.UUIDField(required=False),
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
            'fingerprint',
            'public_key',
            'type',
            'description',
            'created_at',
            'updated_at'
        )
