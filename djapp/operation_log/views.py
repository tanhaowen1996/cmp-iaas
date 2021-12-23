from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djapp.authentication import OSAuthentication
from .serializers import OperationLogSerializer
from .models import OperationLog
from .filters import OperationLogFilter


class OperationLogViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    list:
    Get alarm group list

    retrieve:
    Get alarm group detail with id

    log_list:
    获取操作日志接口
    需要传入参数如下：
    type {server or volume}
    type_id {server_id or volume_id}
    type和type_id要是同一资源

    """
    authentication_classes = (OSAuthentication,)
    # authentication_classes = ()
    # permission_classes = ()
    filterset_class = OperationLogFilter
    serializer_class = OperationLogSerializer
    queryset = OperationLog.objects.all()

    @action(detail=False, methods=['post'])
    def log_list(self, request, *args, **kwargs):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(type_id=request.data['type_id'], type=request.data['type'])
        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
