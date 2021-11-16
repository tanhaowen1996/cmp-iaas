from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    OrderingFilter,
    TypedChoiceFilter)
from distutils.util import strtobool
from netfields import InetAddressField
from .models import Network, Port, Keypair, Image, Volume


class NetworkFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    category = ChoiceFilter(choices=Network.CATEGORY_CHOICES)
    is_shared = TypedChoiceFilter(
        choices=(('false', 'false'), ('true', 'true')),
        coerce=strtobool)
    o = OrderingFilter(fields=(
        ('name', 'name'),
        ('cidr', 'cidr'),
    ), choices=(
        ('name', 'name asc'),
        ('-name', 'name desc'),
        ('cidr', 'cidr asc'),
        ('-cidr', 'cidr desc'),
    ))

    class Meta:
        model = Network
        fields = ('name',)


class PortFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Port
        fields = ('network_id', 'ip_address', 'is_external')
        filter_overrides = {
            InetAddressField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


class KeypairFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    user_id = CharFilter(field_name='user_id', lookup_expr='icontains')
    fingerprint = CharFilter(field_name='fingerprint', lookup_expr='icontains')
    user_name = CharFilter(field_name='user_name', lookup_expr='icontains')
    project_id = CharFilter(field_name='project_id', lookup_expr='icontains')

    class Meta:
        mode = Keypair
        fields = ('project_id', 'user_id', 'name', 'fingerprint', 'user_name')


class ImageFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    visibility = CharFilter(field_name='visibility', lookup_expr='icontains')
    os_type = CharFilter(field_name='os_type', lookup_expr='icontains')
    status = CharFilter(field_name='status', lookup_expr='icontains')
    user_name = CharFilter(field_name='user_name', lookup_expr='icontains')
    tenant_name = CharFilter(field_name='tenant_name', lookup_expr='icontains')

    class Meta:
        mode = Image
        filter = ('name', 'visibility', 'os_type', 'status', 'user_name', 'tenant_name')


class VolumeFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    user_name = CharFilter(field_name='user_name', lookup_expr='icontains')
    server_name = CharFilter(field_name='server_name', lookup_expr='icontains')
    volume_type = CharFilter(field_name='volume_type', lookup_expr='icontains')
    is_bootable = TypedChoiceFilter(
        choices=(('false', 'false'), ('true', 'true')),
        coerce=strtobool)
    status = CharFilter(field_name='status', lookup_expr='icontains')

    class Meta:
        mode = Volume
        filter = ('name', 'user_name', 'server_name', 'volume_type', 'is_bootable', 'status')
