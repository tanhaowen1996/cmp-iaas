from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    OrderingFilter,
    TypedChoiceFilter)
from distutils.util import strtobool
from .models import Network


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
