from django_filters import (
    Filter,
    FilterSet,
    CharFilter,
    ChoiceFilter,
    OrderingFilter,
    TypedChoiceFilter)
from django.db.models import Q
from django import forms
from distutils.util import strtobool
from netfields import CidrAddressField, InetAddressField
from .models import (
    Network, Port,
    Firewall, StaticRouting,
    Keypair, Image, Volume, VolumeType
)


address_field_filter = {
    'filter_class': CharFilter,
    'extra': lambda f: {
        'lookup_expr': 'icontains',
    },
}


class TenantIDFilter(Filter):
    field_class = forms.IntegerField


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
    tenant_id = TenantIDFilter(field_name='tenants', method='filter_tenant')

    class Meta:
        model = Network
        fields = ('name',)
    
    def filter_tenant(self, queryset, name, value):
        return queryset.filter(Q(is_shared=True) | Q(tenants__contains=[{'id': value}]))


class SimpleSourceTenantNetworkFilter(FilterSet):
    tenant_id = TenantIDFilter(field_name='tenants', method='filter_source_tenant', required=True)

    class Meta:
        model = Network
        fields = ('tenant_id',)

    def filter_source_tenant(self, queryset, name, value):
        return queryset.filter(Q(is_shared=True) | Q(tenants__contains=[{'id': value}]))


class SimpleDestinationTenantNetworkFilter(FilterSet):
    tenant_id = TenantIDFilter(field_name='tenants', method='filter_destination_tenant')

    class Meta:
        model = Network
        fields = ('tenant_id',)

    def filter_destination_tenant(self, queryset, name, value):
        return queryset.filter(tenants__contains=[{'id': value}])


class PortFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Port
        fields = ('network_id', 'ip_address', 'is_vip', 'in_use')
        filter_overrides = {
            InetAddressField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


class FirewallFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    source_tenant_id = TenantIDFilter(field_name='source_tenant__id')
    destination_tenant_id = TenantIDFilter(field_name='destination_tenant__id')

    class Meta:
        model = Firewall
        fields = ('source_tenant_id', 'destination_tenant_id', 'source_network_id', 'destination_network_id')


class StaticRoutingFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    tenant_id = TenantIDFilter(field_name='tenant__id')

    class Meta:
        model = StaticRouting
        fields = ('destination_subnet', 'ip_next_hop_address', 'cluster_code')
        address_field_filter = {
            'filter_class': CharFilter,
            'extra': lambda f: {
                'lookup_expr': 'icontains',
            },
        }
        filter_overrides = {
            InetAddressField: address_field_filter,
            CidrAddressField: address_field_filter
        }


class StaticRoutingDestinationSubnetFilter(FilterSet):

    class Meta:
        model = StaticRouting
        fields = ('ip_next_hop_address', 'cluster_code')
        filter_overrides = {
            InetAddressField: address_field_filter,
        }


class BatchDestroyStaticRoutingsFilter(FilterSet):

    class Meta:
        model = StaticRouting

        fields = ('ip_next_hop_address', 'cluster_code')
        address_field_filter = {
            'filter_class': CharFilter,
            'extra': lambda f: {
                'lookup_expr': 'exact',
            },
        }
        filter_overrides = {
            InetAddressField: address_field_filter,
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
    user_id = CharFilter(field_name='user_id', lookup_expr='icontains')
    tenant_name = CharFilter(field_name='tenant_name', lookup_expr='icontains')

    class Meta:
        mode = Image
        filter = ('name', 'visibility', 'os_type',
                  'status', 'user_id', 'tenant_name', 'disk_format')


class VolumeFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    user_name = CharFilter(field_name='user_name', lookup_expr='icontains')
    server_name = CharFilter(field_name='server_name', lookup_expr='icontains')
    server_id = CharFilter(field_name='server_id', lookup_expr='isnull')
    volume_type = CharFilter(field_name='volume_type', lookup_expr='exact')
    is_bootable = TypedChoiceFilter(
        choices=(('false', 'false'), ('true', 'true')),
        coerce=strtobool)
    status = CharFilter(field_name='status', lookup_expr='icontains')

    class Meta:
        mode = Volume
        filter = ('name', 'user_name', 'server_name', 'server_id', 'volume_type', 'is_bootable', 'status')


class VolumeTypeFilter(FilterSet):
    id = CharFilter(field_name='id', lookup_expr='icontains')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    is_public = TypedChoiceFilter(
        choices=(('false', 'false'), ('true', 'true')),
        coerce=strtobool)

    class Meta:
        mode = VolumeType
        filter = ('name', 'id', 'is_public')
