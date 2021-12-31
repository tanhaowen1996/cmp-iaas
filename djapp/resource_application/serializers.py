from rest_framework import serializers
from djapp.models import Network
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


class ResourceApplicationNetworkConfirmationSerializer(ResourceApplicationConfirmationSerializer):
    network_id = serializers.UUIDField()
    network_name = serializers.CharField(max_length=255)
    network_description = serializers.CharField(max_length=1024, allow_blank=True, required=False)

    class Meta:
        model = ResourceApplication
        fields = (
            'network_id', 'network_name', 'network_description'
        )

    def validate_network_id(self, value):
        try:
            self.network = Network.objects.get(
                id=value,
                category=self.instance.content[0]['category'],
                is_shared=False)
        except (KeyError, IndexError) as exc:
            raise serializers.ValidationError(
                f'network application content missing { exc }: { self.instance.content }')
        except Network.DoesNotExist:
            raise serializers.ValidationError(
                f"network { value } not found (category type, shared or not)")
        else:
            return value

    def save(self):
        self.network.update_os_network_subnet(
            self.context['request'].os_conn,
            name=self.validated_data['network_name'],
            description=self.validated_data.get('network_description'))
        self.network.name = self.validated_data['network_name']
        if self.validated_data.get('network_description'):
            self.network.description = self.validated_data['network_description']

        if self.instance.tenant not in self.network.tenants:
            self.network.tenants.append(self.instance.tenant)

        self.network.save()
        self.instance.status = self.instance.STATUS_APPROVED
        self.instance.save()
