from rest_framework import serializers
from .fields import IPAddressField
from .models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False),
    user_id = serializers.CharField(required=False),
    user_name = serializers.CharField(required=False),
    type = serializers.CharField(required=False),
    type_id = serializers.CharField(required=False),
    type_name = serializers.CharField(required=False),
    status = serializers.CharField(required=False),
    operation_ip = serializers.IPAddressField(required=False),
    operation_address = serializers.CharField(required=False),
    created_at = serializers.CharField(required=False)

    class Meta:
        model = OperationLog
        fields = (
            'name',
            'user_id',
            'user_name',
            'type',
            'type_id',
            'type_name',
            'status',
            'operation_ip',
            'operation_address',
            'created_at'
        )

