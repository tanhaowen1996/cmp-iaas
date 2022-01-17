
import logging
import oslo_messaging

from oslo_config import cfg
from djapp import settings

from . import endpoints

LOG = logging.getLogger(__name__)


class NotificationListener(object):

    def __init__(self):
        self.endpoints = [
            endpoints.InstanceEndpoint(),
            endpoints.VolumeEndpoint(),
            endpoints.NetworkEndpoint(),
        ]

    @staticmethod
    def _get_transport():
        # Init oslo config
        cfg.CONF([])
        return oslo_messaging.get_notification_transport(
            cfg.CONF, url=settings.TRANSPORT_URL)

    def run(self):
        transport = self._get_transport()
        targets = [
            oslo_messaging.Target(topic='versioned_notifications'),
            oslo_messaging.Target(topic='notifications'),
        ]
        server = oslo_messaging.get_notification_listener(
            transport, targets,
            endpoints=self.endpoints,
            executor='threading',
            allow_requeue=True)

        server.start()
        LOG.info("messaging started, waiting to receiving ...")
        server.wait()
        LOG.info("Done!")


def start_listen():
    NotificationListener().run()
