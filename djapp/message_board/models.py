from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class BaseModel(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('topic id'))
    creater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT)
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    class Meta:
        abstract = True
        indexes = (BrinIndex(fields=['modified', 'created']),)
        ordering = ('-modified',)

    @property
    def creater_name(self):
        return self.creater.get_full_name()


class Topic(BaseModel):
    tenant = models.JSONField(
        default=dict,
        verbose_name=_('tenant obj with id & name'))
    subject = models.CharField(max_length=255)

    class Meta(BaseModel.Meta):
        abstract = False

    @property
    def latest_message_content(self):
        message = self.message_set.order_by('-created').first()
        return message.content if message else ''


class Message(BaseModel):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta(BaseModel.Meta):
        abstract = False
        ordering = ('created',)
