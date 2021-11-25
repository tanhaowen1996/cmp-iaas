import abc
import logging
import oslo_messaging

from djapp import models

LOG = logging.getLogger(__name__)


class NotificationEndpoint(object):
    """Base Endpoint for plugins that support the notification API."""

    event_types = []
    """List of strings to filter messages on."""

    def __init__(self, forwarder=None):
        if self.event_types:
            self.filter_rule = oslo_messaging.NotificationFilter(
                event_type='|'.join(self.event_types))
        self.forwarder = forwarder

    @abc.abstractmethod
    def process(self, publisher_id, event_type, payload):
        """Return a sequence of Counter instances for the given message.

        :param publisher_id: Publisher.
        :param event_type: Event type.
        :param payload: Message to process.
        """

    def _process_notifications(self, context, publisher_id, event_type, payload, metadata):
        """RPC endpoint for all notification level"""
        _, _ = context, metadata
        try:
            LOG.info("Received: %s -- %s" % (publisher_id, event_type))
            self.process(publisher_id, event_type, payload)
        except Exception as e:
            LOG.exception(e)
            pass

    audit = _process_notifications
    critical = _process_notifications
    debug = _process_notifications
    error = _process_notifications
    info = _process_notifications
    sample = _process_notifications
    warn = _process_notifications


class ImageEndpoint(NotificationEndpoint):
    """Image Notification Process Endpoint."""

    event_types = [
        'image.create',
        'image.update',
        'image.upload',
        'image.delete',
        'image.send'
    ]

    def process(self, publisher_id, event_type, payload):
        pass


class InstanceEndpoint(NotificationEndpoint):
    """Instance Notification Process Endpoint."""

    event_types = [
        'compute.instance.*',
        'instance.*'
    ]

    def process(self, publisher_id, event_type, payload):
        pass


class VolumeEndpoint(NotificationEndpoint):
    """Volume Notification Process Endpoint."""

    event_types = [
        'volume.transfer.*',
        'volume.exists',
        'volume.retype',
        'volume.create.*',
        'volume.delete.*',
        'volume.resize.*',
        'volume.attach.*',
        'volume.detach.*',
        'volume.update.*',
    ]

    def process(self, publisher_id, event_type, payload):
        pass

    def volume_create_end(self, payload):
        volume_id = payload.get('volume_id', None)
        if not volume_id:
            raise Exception("volume_id is None")
        volume = models.Volume.objects.get(pk=volume_id)
        if not volume:
            raise Exception("volume_id %s is not found" % volume_id)
        volume.status = payload.get('status')
        volume.save()


class NetworkEndpoint(NotificationEndpoint):
    """Network Notification Process Endpoint."""

    event_types = [
        'network.*',
        'subnet.*',
        'port.*',
    ]

    def process(self, publisher_id, event_type, payload):
        pass
