from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    OrderingFilter,
    TypedChoiceFilter)
from distutils.util import strtobool
from netfields import InetAddressField
from .models import Network, Port


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
    name = CharFilter(field_name='ip_address', lookup_expr='icontains')

    class Meta:
        model = Port
        fields = ('network_id', 'ip_address')
        filter_overrides = {
            InetAddressField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
