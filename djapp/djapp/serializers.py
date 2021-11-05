from rest_framework import serializers
from .fields import IPAddressField
from .models import Network, Port


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
