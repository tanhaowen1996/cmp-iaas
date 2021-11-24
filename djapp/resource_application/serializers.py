from rest_framework import serializers
from .models import ResourceApplication


class ResourceApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceApplication
        fields = (
            'id',
            'category',
            'creater_id',
            'creater_name',
            'tenant',
            'content',
            'status',
            'reason',
            'created',
            'modified'
        )
        read_only_fields = (
            'id', 'tenant',
            'status',
            'reason',
            'creater_id', 'created_name',
            'created', 'modified',
        )

    def validate_content(self, value):
        if not value:
            raise serializers.ValidationError(f"invalid content `{value}`")
        return value


class ResourceApplicationConfirmationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceApplication
        fields = ('reason',)

    def validate(self, data):
        if self.instance.status in (
            ResourceApplication.STATUS_APPROVED, ResourceApplication.STATUS_DENIED
        ):
            raise serializers.ValidationError(f"the status is already {self.instance.status}")
        return data
