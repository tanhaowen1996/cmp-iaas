from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djapp.authentication import OSAuthentication
from .filters import TopicFilter
from .models import Topic
from .serializers import (
    TopicSerializer, TopicCreationSerializer, MessageSerializer
)


class TopicViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    authentication_classes = (OSAuthentication,)
    filterset_class = TopicFilter
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    create_serializer_class = TopicCreationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(tenant__contains={
                'id': self.request.account_info['tenantId']})

        return qs

    def perform_create(self, serializer):
        serializer.save(creater=self.request.user, tenant={
            'id': self.request.account_info['tenantId'],
            'name': self.request.account_info['tenantName']
        })

    def get_serializer_class(self):
        return {
            'POST': self.create_serializer_class
        }.get(self.request.method, self.serializer_class)

    @action(detail=True, methods=['get'], serializer_class=MessageSerializer)
    def messages(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance.message_set.all(), many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data})

    @action(detail=True, methods=['put'], serializer_class=MessageSerializer)
    def reply(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creater=self.request.user,
                        topic=instance)
        instance.save()
        return Response(serializer.data)
