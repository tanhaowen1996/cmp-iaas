from django_filters import (
    FilterSet,
    CharFilter

)
from .models import Inform


class PlatformInformFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Inform
        fields = ('name', 'inform_object_type', 'created')
