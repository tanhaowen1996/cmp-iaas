from django_filters import (
    FilterSet,
    CharFilter,
    DateTimeFilter)
from .models import OperationLog


class OperationLogFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    user_name = CharFilter(field_name='user_name', lookup_expr='icontains')
    type_name = CharFilter(field_name='type_name', lookup_expr='icontains')
    created_at = DateTimeFilter(field_name='created_at', lookup_expr='icontains')

    class Meta:
        mode = OperationLog
        filter = ('name', 'user_name', 'type_name', 'created_at')
