from django_filters import (
    CharFilter,
    FilterSet,
    DateFilter,
    OrderingFilter,
)
from .models import Topic


class TopicFilter(FilterSet):
    subject = CharFilter(field_name='subject', lookup_expr='icontains')
    created_date_from = DateFilter(field_name='created__date', lookup_expr='gte')
    created_date_to = DateFilter(field_name='created__date', lookup_expr='lte')
    o = OrderingFilter(fields=(
        ('modified', 'modified'),
    ), choices=(
        ('modified', 'modified asc'),
        ('-modified', 'modified desc'),
    ))

    class Meta:
        model = Topic
        fields = ('subject', 'creater_id')
