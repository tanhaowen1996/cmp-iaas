from django_filters import (
    FilterSet,
    CharFilter,
    OrderingFilter,
    DateFilter,

)
from .models import Inform


class PlatformInformFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    inform_object_type = CharFilter(field_name='inform_object_type', lookup_expr='icontains')
    created_date_from = DateFilter(field_name='created__date', lookup_expr='gte')
    created_date_to = DateFilter(field_name='created__date', lookup_expr='lte')
    o = OrderingFilter(fields=(
        ('created', 'created'),
    ), choices=(
        ('created', 'created asc'),
        ('-created', 'created desc'),
    ))

    class Meta:
        model = Inform
        fields = ('name', 'inform_object_type',)
