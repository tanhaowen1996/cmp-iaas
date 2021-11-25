from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djapp.authentication import OSAuthentication
from .filters import ResourceApplicationFilter
from .models import ResourceApplication
from .serializers import (
    ResourceApplicationSerializer, ResourceApplicationConfirmationSerializer
)


class ResourceApplicationViewSet(mixins.CreateModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    authentication_classes = (OSAuthentication,)
    filterset_class = ResourceApplicationFilter
    queryset = ResourceApplication.objects.all()
    serializer_class = ResourceApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(creater=self.request.user, tenant={
            'id': self.request.account_info['tenantId'],
            'name': self.request.account_info['tenantName']
        })

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(tenant__contains={
                'id': self.request.account_info['tenantId']})

        return qs

    @action(detail=True, methods=['post'], serializer_class=ResourceApplicationConfirmationSerializer)
    def approve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=instance.STATUS_APPROVED, reason='')
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=ResourceApplicationConfirmationSerializer)
    def deny(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=instance.STATUS_DENIED)
        return Response(serializer.data)
