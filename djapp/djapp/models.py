from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Network(models.Model):
    CATEGORY_CLUSTER = 'cluster'
    CATEGORY_CONTAINER = 'container'
    CATEGORY_CHOICES = (
        (CATEGORY_CLUSTER, 'cluster'),
        (CATEGORY_CONTAINER, 'container'),
    )
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('network name'))
    cidr = models.CharField(
        unique=True,
        max_length=255)
    total_interface = models.PositiveSmallIntegerField()
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=255)
    is_shared = models.BooleanField()
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    class Meta:
        indexes = (BrinIndex(fields=['modified', 'created']),)
