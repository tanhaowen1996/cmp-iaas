
import logging
import abc
import copy

import oslo_messaging


LOG = logging.getLogger(__name__)


class NotificationEndpoint(metaclass=abc.ABCMeta):
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


class Payload(object):
    def __init__(self, payload):
        self.__dict__.update(**payload)

    def to_dict(self):
        return copy.deepcopy(self.__dict__)
