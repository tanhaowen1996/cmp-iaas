from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.indexes import BrinIndex
import uuid


class OperationLog(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('operation id')
    )
    name = models.CharField(
        null=True,
        max_length=255
    )
    user_id = models.CharField(
        null=True,
        max_length=100
    )
    user_name = models.CharField(
        null=True,
        max_length=100
    )
    type = models.CharField(
        null=True,
        max_length=255
    )
    type_id = models.UUIDField(
        null=True
    )
    type_name = models.CharField(
        null=True,
        max_length=255
    )
    status = models.CharField(
        null=True,
        max_length=255
    )
    operation_ip = models.GenericIPAddressField(
        null=True
    )
    operation_address = models.CharField(
        null=True,
        max_length=255
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))

    class Meta:
        indexes = (BrinIndex(fields=['created_at']),)
