from rest_framework import serializers
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
    ip_address = serializers.CharField(allow_null=True)
    ip = serializers.CharField(source='ip_address.ip', read_only=True)
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
            'ip',
            'mac_address',
            'is_external'
        )
        read_only_fields = (
            'id', 'network_name',
            'mac_address', 'ip'
        )

    def validate_network_id(self, value):
        if not Network.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Network id: {value} matching query does not exist")
        return value
