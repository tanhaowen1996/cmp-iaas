from django_filters import (
    FilterSet,
    DateFilter,
    OrderingFilter,
)
from .models import ResourceApplication


class ResourceApplicationFilter(FilterSet):
    created_date_from = DateFilter(field_name='created__date', lookup_expr='gte')
    created_date_to = DateFilter(field_name='created__date', lookup_expr='lte')
    o = OrderingFilter(fields=(
        ('created', 'created'),
    ), choices=(
        ('created', 'created asc'),
        ('-created', 'created desc'),
    ))

    class Meta:
        model = ResourceApplication
        fields = ('category', 'creater_id')
