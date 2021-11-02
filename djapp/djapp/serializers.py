from rest_framework import serializers
from .models import Network


class NetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Network
        fields = (
            'id',
            'name',
            'cidr',
            'total_interface',
            'category',
            'is_shared',
            'created',
            'modified'
        )
        read_only_fields = (
            'id', 'total_interface',
            'created', 'modified',
        )
