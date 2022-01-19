
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import serializers
from django_celery_results.models import TaskResult

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from sync.tasks import user

LOG = logging.getLogger(__name__)


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskResult
        fields = '__all__'


class TaskViewSet(viewsets.GenericViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskSerializer

    lookup_field = 'task_id'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @staticmethod
    def _get_started_sync_all_task():
        started_tasks = TaskResult.objects.filter(status='STARTED')\
            .filter(task_name='sync.tasks.user.do_all_sync')
        return started_tasks[0] if started_tasks else None

    @action(detail=False, methods=['post'], serializer_class=None)
    def sync_all(self, request, *args, **kwargs):
        LOG.info("Receive sync all command...")
        task = self._get_started_sync_all_task()
        if task is None:
            task = user.do_all_sync.delay()
            LOG.info("Generate a task: %s to process..." % task.task_id)
        else:
            LOG.warning("Already started task: %s to process..."
                        % task.task_id)
        data = {
            'task_id': task.task_id,
        }
        return Response(data=data, status=status.HTTP_202_ACCEPTED)
