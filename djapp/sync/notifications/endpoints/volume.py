
import logging

from sync.tasks import volume as volume_tasks

from . import base

LOG = logging.getLogger(__name__)


class VolumeEndpoint(base.NotificationEndpoint):
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
        LOG.info("Start process volume notification: %s" % event_type)
        volume_id = payload.get('volume_id', None)
        if not volume_id:
            LOG.error("Failed to got `volume_id` from notification: %s payload: %s "
                      % (event_type, payload))
            return

        # delete volume
        if event_type in ['volume.delete.end']:
            LOG.info("Delete volume: %s" % volume_id)
            volume_tasks.sync_volume_delete.delay(volume_id)

        # create volume
        if event_type in ['volume.create.end', 'volume.create.error']:
            LOG.info("Create volume: %s" % volume_id)
            volume_tasks.sync_volume_create.delay(volume_id)
            return

        # update volume:
        LOG.info("Update volume: %s" % volume_id)
        volume_tasks.sync_volume_update.delay(volume_id)
